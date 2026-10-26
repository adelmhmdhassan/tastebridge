"""agent.py - TasteBridge agent: cultural translation + group negotiation."""
from .qloo_client import QlooClient

DOMAINS = ("dining", "music", "film", "fashion")


class TasteBridgeAgent:
    """Finds equivalents of a home taste in a new city; negotiates group taste."""

    def __init__(self, client=None):
        self.client = client or QlooClient()

    def translate(self, taste, city, domains=None):
        out = []
        for d in (domains or DOMAINS):
            r = self.client.find_equivalents(taste, d, city)
            out.append({"domain": d, "results": r["results"]})
        return {"taste": taste, "city": city, "domains": out}

    def negotiate(self, tastes, city, domain="dining"):
        r = self.client.recommend_for_group(tastes, domain, city)
        return {"tastes": tastes, "city": city, "domain": domain,
                "results": r["results"]}

    @staticmethod
    def explain(item):
        return item.get("why", "")
