"""Command line entry point: `serp-competitor-finder SERP_CSV... --domain yoursite.com`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STAT
from .report import Report, write_excel


@click.command()
@click.argument("serp_csv", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--domain", "-d", required=True, help="Your domain, e.g. example.com")
@click.option("--top", default=10, show_default=True, help="Only count results in the top N positions.")
@click.option("-o", "--output", default="serp_competitors", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(serp_csv, domain, top, output):
    """Find who you really compete with in search, from one or more SERP exports.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    result = core.run(serp_csv, domain, top)
    comp, h2h, missing = result["competitors"], result["head_to_head"], result["missing"]
    me = comp[comp["is_you"]]
    rivals = comp[comp["type"] == "direct competitor"]
    keywords = result["serps"]["keyword"].nunique()

    report = Report(title="SERP competitor report",
                    subtitle=f"{core.root_domain(core.domain_of(domain))} · {keywords} keywords · top {top}",
                    tool="serp-competitor-finder")
    report.add_cards([
        ("Keywords analysed", keywords),
        ("Your share of voice", f"{me['share_of_voice_pct'].iloc[0]}%" if not me.empty else "not ranking", "warn"),
        ("Your rank by share of voice", int(me["rank"].iloc[0]) if not me.empty else "-"),
        ("Direct competitors", len(rivals), "bad" if len(rivals) else "good"),
        ("Keywords you're missing", len(missing), "warn" if len(missing) else "good"),
    ])
    report.add_benchmark(STAT, how_used="Domains that hold 2+ spots on the same results page are counted in "
                                         "'multi_listing_keywords'. They own more of the page than one ranking shows.")
    report.add_table("Competitors by share of voice", comp.drop(columns="is_you"),
                     note="Share of voice = estimated clicks from your keyword set, using a position CTR curve.",
                     sheet="Competitors")
    report.add_table("Head to head: who sits above you", h2h,
                     note="Sorted by the clicks you would gain at position 1.", sheet="Head to head")
    report.add_table("Keywords competitors rank for and you don't", missing,
                     note="Keywords several rivals rank for are proven demand: start there.", sheet="Missing keywords")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(comp.drop(columns="is_you").head(8).to_string(index=False))


if __name__ == "__main__":
    main()
