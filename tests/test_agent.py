import unittest

from app.agent import TasteBridgeAgent
from app.qloo_client import QlooClient


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = TasteBridgeAgent(QlooClient(mode="mock"))

    def test_translate_covers_all_domains(self):
        r = self.agent.translate("grandfather cafes", "Dubai")
        domains = [d["domain"] for d in r["domains"]]
        for expected in ("dining", "music", "film", "fashion"):
            self.assertIn(expected, domains)

    def test_translate_dining_has_results(self):
        r = self.agent.translate("x", "Dubai", domains=["dining"])
        self.assertGreaterEqual(len(r["domains"][0]["results"]), 1)

    def test_negotiate_returns_shortlist(self):
        r = self.agent.negotiate(["a", "b"], "Dubai")
        self.assertIn("results", r)
        self.assertLessEqual(len(r["results"]), 3)

    def test_unknown_domain_empty(self):
        r = self.agent.translate("x", "Nowhere", domains=["books"])
        self.assertEqual(r["domains"][0]["results"], [])


if __name__ == "__main__":
    unittest.main()
