<div align="center">

# 🥊 serp-competitor-finder

### Find who you *really* compete with in Google, and how much of the page they own.

[![tests](https://github.com/marketing-MEER/serp-competitor-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/serp-competitor-finder/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

Your business competitors and your **search** competitors are rarely the same list. The sites that take your clicks are often a review platform, a publisher, or a small rival you've never heard of.

`serp-competitor-finder` reads a SERP export (the top 10 results for your keywords) and ranks every domain by **share of voice**: the share of estimated clicks it wins across your keyword set. Then it shows who sits above you, and which keywords your rivals rank for while you don't.

- ✅ Competitors ranked by share of voice, labelled **direct**, **partial**, **platform / publisher** or **niche**
- ✅ Counts how often each domain holds **2+ spots on the same results page**
- ✅ A head-to-head table and a "keywords you're missing" list with the competitor URL to study
- ✅ Free, MIT licensed, no API keys. No live scraping: it works from the exports you already have

## 📊 Why this matters

> **What Takes Up The First Page of Google Search Results** · NP Digital, June 2025 (1,000 keywords per query type)
> - Informational queries are 62% organic, 11% AI Overview, and 14% branded content.
> - Transactional queries are 56% organic, 13% paid, 18% zero-click.
> - *"Owning a single listing isn't enough anymore. If you're not on the page multiple times, you're invisible."* (Neil Patel)
>
> Data: [Neil Patel marketing stats](https://neilpatel.com/marketing-stats/serp-real-estate-google-first-page/)

**How serp-competitor-finder uses this:** organic space on page 1 is shrinking. One ranking per competitor doesn't show who owns the page. So the tool weights every result by an estimated click share instead of just counting rankings, and it counts `multi listing keywords`: SERPs where a domain holds two or more of the ten spots.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/serp-competitor-finder.git
cd serp-competitor-finder
pip install -e .
serp-competitor-finder examples/serp_export.csv --domain brightcrm.io
```

This writes **`serp_competitors.html`** (a formatted report you can open, share or print to PDF) and **`serp_competitors.xlsx`** (all the data).

> [!TIP]
> If the `serp-competitor-finder` command isn't found, use `python -m serp_competitor_finder`.

## 📥 Input

One or more CSV files with **one row per search result**: keyword, position and URL. Search volume is optional but recommended.

| Source | How to export | Columns detected |
|---|---|---|
| Ahrefs | Keywords Explorer → SERP overview → Export | `Keyword`, `Position`, `URL`, `Volume` |
| Semrush | Keyword Overview / Position Tracking → SERP → Export | `Keyword`, `Position`, `URL`, `Search Volume` |
| Any rank tracker or SERP API | Your own CSV | `keyword` / `query`, `position` / `rank`, `url` / `landing page`, `volume` / `impressions` |

Pass several files at once (e.g. one per keyword group). The tool merges them and keeps each domain's best position per keyword.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Normalise domains**: `www.` is removed and subdomains are folded into the main domain (`blog.site.co.uk` → `site.co.uk`).
2. **Count multiple listings**: if a domain has 2+ URLs on the same SERP, that keyword counts toward `multi listing keywords`.
3. **Estimate clicks**: volume × typical CTR for the position (28% at #1 down to 2.4% at #10). This makes a #1 on a big keyword outweigh a #9 on a small one.
4. **Share of voice** = a domain's estimated clicks ÷ all estimated clicks in the top N.
5. **Label each domain** by how many of *your* keywords it also ranks for:
   - **direct competitor**: 30%+ overlap
   - **partial competitor**: 10–30%
   - **platform / publisher**: YouTube, Reddit, Wikipedia, G2, Forbes and similar sites that rank for almost everything
   - **niche / occasional**: under 10%
6. **Head to head**: for each keyword you rank for, it shows who is above you and the clicks you'd gain at #1.
7. **Missing keywords**: keywords where direct or partial competitors rank and you don't, sorted by how many rivals rank for each (proven demand), then by volume.

### Options

| Option | Default | What it does |
|---|---|---|
| `--domain`, `-d` | *(required)* | Your domain, e.g. `example.com` |
| `--top` | `10` | Only count results in the top N positions |
| `-o`, `--output` | `serp_competitors` | Report name; writes `.html` and `.xlsx` |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Keywords analysed, your share of voice and rank, number of direct competitors, number of missing keywords |
| Benchmark panel | The Neil Patel data behind the method |
| **Competitors** | Every domain: keywords in top 10, top-3 count, multi-listing keywords, average position, estimated clicks, share of voice, overlap with you, how often it outranks you, and its label |
| **Head to head** | Your keywords: your position and URL, how many domains sit above you, the top domain, clicks you'd gain at #1 |
| **Missing keywords** | Keywords your rivals rank for and you don't, with the best competitor URL to study |

<details>
<summary>📄 Example: real output from <code>examples/serp_export.csv</code> (fictional CRM market)</summary>

**Competitors** (top 6 of 22). The "you" site, `brightcrm.io`, comes 9th with 4.61% share of voice.

| rank | domain | keywords top10 | multi listing keywords | share of voice % | overlap with you % | outranks you on | type |
|---|---|---|---|---|---|---|---|
| 1 | pipelinehq.com | 11 | 7 | 14.06 | 85.7 | 3 | direct competitor |
| 2 | forbes.com | 4 | 0 | 13.76 | 42.9 | 3 | platform / publisher |
| 3 | salesdeck.io | 10 | 0 | 13.3 | 71.4 | 2 | direct competitor |
| 4 | reddit.com | 7 | 0 | 11.61 | 57.1 | 0 | platform / publisher |
| 5 | youtube.com | 7 | 0 | 7.53 | 71.4 | 3 | platform / publisher |
| 6 | closeflow.app | 5 | 0 | 6.76 | 28.6 | 2 | partial competitor |

**Missing keywords**

| keyword | volume | competitors ranking | best competitor | best position |
|---|---|---|---|---|
| best crm software | 14,800 | 5 | pipelinehq.com | 3 |
| what is a crm | 6,600 | 5 | pipelinehq.com | 1 |
| hubspot alternatives | 2,900 | 4 | crmguide.net | 4 |
| crm vs erp | 1,300 | 4 | salesdeck.io | 1 |
| sales forecasting tool | 880 | 4 | closeflow.app | 1 |

**Head to head** (top 4)

| keyword | your position | domains above you | top domain | clicks if you were #1 |
|---|---|---|---|---|
| crm for small business | 6 | 5 | forbes.com | 2,277 |
| free crm | 4 | 3 | salesdeck.io | 1,620 |
| lead management software | 7 | 5 | youtube.com | 576 |
| crm pricing | 3 | 2 | hubspot.com | 408 |

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- **keyword-gap-analyzer**: missing, weak and untapped keywords against competitors
- **backlink-gap-finder**: domains that link to competitors but not to you
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>Why are YouTube and Reddit in my competitor list?</b></summary>

Because they take clicks on your keywords. They're labelled **platform / publisher** so you can filter them out, or use them as a signal: if Reddit ranks, people want real opinions; if YouTube ranks, a video may win that spot.
</details>

<details><summary><b>How accurate is "estimated clicks"?</b></summary>

It's a benchmark, not a measurement. It uses average CTR by position, and real CTR changes with SERP features and AI Overviews. It's meant for comparing domains fairly, not for forecasting your traffic.
</details>

<details><summary><b>Can I compare more than 10 positions?</b></summary>

Yes. Export the top 20 and run with `--top 20`. CTR beyond #10 is close to zero, so share of voice barely changes, but overlap and missing keywords will include page 2.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

No. It reads your CSV files and writes the report on your computer. It makes no network requests.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers, quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
