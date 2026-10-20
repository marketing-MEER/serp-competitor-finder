import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from serp_competitor_finder import cli, core

HERE = Path(__file__).parent
EXAMPLE = HERE.parent / "examples" / "serp_export.csv"

SERP = """Keyword,Volume,Position,URL
crm software,1000,1,https://rival.com/a
crm software,1000,2,https://www.me.com/a
crm software,1000,3,https://rival.com/b
crm software,1000,4,https://youtube.com/x
free crm,500,1,https://me.com/free
free crm,500,2,https://rival.com/free
crm pricing,300,1,https://rival.com/pricing
crm pricing,300,2,https://other.net/pricing
crm pricing,300,11,https://me.com/pricing
"""


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = Path(self.tmp.name) / "serp.csv"
        self.csv.write_text(SERP, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_domains_are_normalised(self):
        self.assertEqual(core.root_domain(core.domain_of("https://www.blog.me.co.uk/x")), "me.co.uk")
        self.assertEqual(core.root_domain(core.domain_of("me.com/page")), "me.com")

    def test_competitors(self):
        result = core.run([self.csv], "me.com")
        comp = result["competitors"].set_index("domain")
        self.assertEqual(comp.loc["rival.com", "keywords_top10"], 3)
        self.assertEqual(comp.loc["rival.com", "multi_listing_keywords"], 1)  # two URLs on "crm software"
        self.assertEqual(comp.loc["rival.com", "type"], "direct competitor")
        self.assertEqual(comp.loc["youtube.com", "type"], "platform / publisher")
        self.assertEqual(comp.loc["me.com", "type"], "you")
        self.assertEqual(comp.loc["rival.com", "outranks_you_on"], 1)
        self.assertAlmostEqual(result["competitors"]["share_of_voice_pct"].sum(), 100, delta=0.1)

    def test_position_11_is_outside_top_10(self):
        result = core.run([self.csv], "me.com")
        self.assertNotIn("crm pricing", result["head_to_head"]["keyword"].tolist())
        # ranking at 11 still counts as "ranking", so it is not a missing keyword either
        self.assertNotIn("crm pricing", result["missing"]["keyword"].tolist())

    def test_head_to_head(self):
        h2h = core.run([self.csv], "me.com")["head_to_head"].set_index("keyword")
        self.assertEqual(h2h.loc["crm software", "top_domain"], "rival.com")
        self.assertEqual(h2h.loc["crm software", "clicks_if_you_were_1"], round(1000 * (0.28 - 0.16)))
        self.assertEqual(h2h.loc["free crm", "top_domain"], "you")


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report"
            res = CliRunner().invoke(cli.main, [str(EXAMPLE), "--domain", "brightcrm.io", "-o", str(out)])
            self.assertEqual(res.exit_code, 0, res.output)
            html = out.with_suffix(".html").read_text(encoding="utf-8")
            self.assertIn("SERP competitor report", html)
            self.assertIn("neilpatel.com/marketing-stats", html)
            self.assertTrue(out.with_suffix(".xlsx").stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
