"""Find who you really compete with in search, from SERP exports.

A business competitor is not always a search competitor. This module reads
SERP exports (keyword, position, URL, volume), estimates the clicks every
domain earns with a position CTR curve and ranks domains by share of voice.
"""
from urllib.parse import urlparse

import pandas as pd

from .report import find_column, to_number

# Typical organic CTR by position (industry averages). Used to turn rankings
# into estimated clicks, so a #1 on a big keyword outweighs a #9 on a small one.
CTR = {1: 0.28, 2: 0.16, 3: 0.11, 4: 0.08, 5: 0.06, 6: 0.05, 7: 0.04, 8: 0.033, 9: 0.027, 10: 0.024}

# Sites that rank for almost everything. They take clicks, but you can't
# "beat" them the way you beat a direct competitor, so they are labelled.
PLATFORMS = {
    "wikipedia.org", "youtube.com", "reddit.com", "quora.com", "amazon.com", "facebook.com",
    "linkedin.com", "instagram.com", "pinterest.com", "x.com", "twitter.com", "tiktok.com",
    "medium.com", "forbes.com", "nytimes.com", "yelp.com", "tripadvisor.com", "github.com",
    "google.com", "apple.com", "microsoft.com", "indeed.com", "glassdoor.com", "ebay.com",
    "g2.com", "capterra.com", "trustpilot.com", "hubspot.com",
}


def domain_of(url: str) -> str:
    host = urlparse(url if "://" in str(url) else "https://" + str(url)).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def root_domain(domain: str) -> str:
    parts = domain.split(".")
    # keep co.uk / com.au style endings together
    if len(parts) > 2 and parts[-2] in {"co", "com", "org", "net", "gov", "ac"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def load_serps(paths) -> pd.DataFrame:
    """Read one or more SERP exports and normalise to keyword, position, url, domain, volume."""
    frames = []
    for path in paths:
        raw = pd.read_csv(path)
        kw = find_column(raw, ["keyword", "query", "search term", "keywords"])
        pos = find_column(raw, ["position", "rank", "pos", "serp position", "current position"])
        url = find_column(raw, ["url", "ranking url", "landing page", "page", "result url", "link"])
        vol = find_column(raw, ["volume", "search volume", "avg. monthly searches", "impressions", "sv"])
        if not all([kw, pos, url]):
            raise ValueError(f"{path}: need keyword, position and URL columns. Found: {list(raw.columns)}")
        df = pd.DataFrame({
            "keyword": raw[kw].astype(str).str.strip().str.lower(),
            "position": to_number(raw[pos]).astype(int),
            "url": raw[url].astype(str).str.strip(),
            "volume": to_number(raw[vol]) if vol else 1,
        })
        frames.append(df)
    serps = pd.concat(frames, ignore_index=True)
    serps = serps[(serps["position"] > 0) & (serps["url"] != "")]
    serps["domain"] = serps["url"].map(domain_of).map(root_domain)
    serps = serps.drop_duplicates(["keyword", "url"])
    # How many spots each domain holds on the same SERP (NP: serp-real-estate-google-first-page,
    # "if you're not on the page multiple times ... you're invisible").
    serps["listings"] = serps.groupby(["keyword", "domain"])["url"].transform("count")
    # Then keep each domain's best position per keyword.
    serps = serps.sort_values("position").drop_duplicates(["keyword", "domain"])
    # Volume is per keyword: use the max seen so a missing value in one file doesn't zero it.
    serps["volume"] = serps.groupby("keyword")["volume"].transform("max")
    return serps.reset_index(drop=True)


def ctr_for(position: int) -> float:
    return CTR.get(int(position), 0.0)


def competitors(serps: pd.DataFrame, my_domain: str, top_n: int = 10) -> pd.DataFrame:
    """Rank every domain by estimated share of voice in the top `top_n` results."""
    me = root_domain(domain_of(my_domain))
    top = serps[serps["position"] <= top_n].copy()
    top["est_clicks"] = top["volume"] * top["position"].map(ctr_for)
    my_keywords = set(top.loc[top["domain"] == me, "keyword"])
    my_pos = top[top["domain"] == me].set_index("keyword")["position"]
    total_clicks = top["est_clicks"].sum() or 1

    rows = []
    for domain, g in top.groupby("domain"):
        kws = set(g["keyword"])
        shared = kws & my_keywords
        beats_me = sum(1 for k in shared if g.set_index("keyword").at[k, "position"] < my_pos[k])
        overlap_pct = round(len(shared) / len(my_keywords) * 100, 1) if my_keywords else 0.0
        rows.append({
            "domain": domain,
            "is_you": domain == me,
            "keywords_top10": len(kws),
            "top3": int((g["position"] <= 3).sum()),
            "multi_listing_keywords": int((g["listings"] >= 2).sum()),
            "avg_position": round(g["position"].mean(), 1),
            "est_clicks": round(g["est_clicks"].sum()),
            "share_of_voice_pct": round(g["est_clicks"].sum() / total_clicks * 100, 2),
            "shared_keywords": len(shared),
            "overlap_with_you_pct": overlap_pct,
            "outranks_you_on": beats_me,
            "type": competitor_type(domain, me, overlap_pct),
        })
    df = pd.DataFrame(rows).sort_values("share_of_voice_pct", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def competitor_type(domain: str, me: str, overlap_pct: float) -> str:
    if domain == me:
        return "you"
    if domain in PLATFORMS:
        return "platform / publisher"
    if overlap_pct >= 30:
        return "direct competitor"
    if overlap_pct >= 10:
        return "partial competitor"
    return "niche / occasional"


def head_to_head(serps: pd.DataFrame, my_domain: str, top_n: int = 10) -> pd.DataFrame:
    """For every keyword you rank for: who sits above you and how many clicks that costs."""
    me = root_domain(domain_of(my_domain))
    top = serps[serps["position"] <= top_n]
    mine = top[top["domain"] == me].set_index("keyword")
    rows = []
    for kw, g in top.groupby("keyword"):
        if kw not in mine.index:
            continue
        my_position = int(mine.at[kw, "position"])
        above = g[(g["position"] < my_position) & (g["domain"] != me)].sort_values("position")
        best = above.iloc[0] if not above.empty else None
        volume = float(g["volume"].iloc[0])
        rows.append({
            "keyword": kw,
            "volume": volume,
            "your_position": my_position,
            "your_url": mine.at[kw, "url"],
            "domains_above_you": len(above),
            "top_domain": best["domain"] if best is not None else "you",
            "top_position": int(best["position"]) if best is not None else my_position,
            "clicks_if_you_were_1": round(volume * (CTR[1] - ctr_for(my_position))),
        })
    df = pd.DataFrame(rows, columns=["keyword", "volume", "your_position", "your_url", "domains_above_you",
                                     "top_domain", "top_position", "clicks_if_you_were_1"])
    return df.sort_values("clicks_if_you_were_1", ascending=False)


def missing_keywords(serps: pd.DataFrame, my_domain: str, comp: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Keywords where direct/partial competitors rank in the top N and you don't rank at all."""
    me = root_domain(domain_of(my_domain))
    rivals = set(comp.loc[comp["type"].isin(["direct competitor", "partial competitor"]), "domain"])
    top = serps[serps["position"] <= top_n]
    mine = set(serps.loc[serps["domain"] == me, "keyword"])
    rows = []
    for kw, g in top.groupby("keyword"):
        if kw in mine:
            continue
        hits = g[g["domain"].isin(rivals)].sort_values("position")
        if hits.empty:
            continue
        rows.append({
            "keyword": kw,
            "volume": float(g["volume"].iloc[0]),
            "competitors_ranking": len(hits),
            "best_competitor": hits.iloc[0]["domain"],
            "best_position": int(hits.iloc[0]["position"]),
            "their_url": hits.iloc[0]["url"],
        })
    df = pd.DataFrame(rows, columns=["keyword", "volume", "competitors_ranking", "best_competitor",
                                     "best_position", "their_url"])
    # Keywords that several rivals rank for are proven demand: sort by that first, then volume.
    return df.sort_values(["competitors_ranking", "volume"], ascending=False)


def run(paths, my_domain: str, top_n: int = 10) -> dict:
    serps = load_serps(paths)
    comp = competitors(serps, my_domain, top_n)
    return {
        "serps": serps,
        "competitors": comp,
        "head_to_head": head_to_head(serps, my_domain, top_n),
        "missing": missing_keywords(serps, my_domain, comp, top_n),
    }
