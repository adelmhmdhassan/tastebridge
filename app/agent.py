"""agent.py - TasteBridge agent: cultural translation + group negotiation."""
from concurrent.futures import ThreadPoolExecutor

from .qloo_client import QlooClient, drain_trace

DOMAINS = ("dining", "music", "film", "fashion")


class TasteBridgeAgent:
    """Finds equivalents of a home taste in a new city; negotiates group taste."""

    def __init__(self, client=None):
        self.client = client or QlooClient()

    def translate(self, taste, city, domains=None):
        doms = list(domains or DOMAINS)
        with ThreadPoolExecutor(max_workers=4) as ex:
            rs = list(ex.map(lambda d: self.client.find_equivalents(taste, d, city), doms))
        out = [{"domain": d, "results": r["results"]} for d, r in zip(doms, rs)]
        extras = self.client.extras(taste, city)
        nxt = []
        dining = next((b for b in out if b["domain"] == "dining"), None)
        top = (dining["results"][0] if dining and dining["results"] else None)
        if top and top.get("id"):
            try:
                nxt = self.client.next_stops(top["id"], city)["stops"]
            except Exception:
                nxt = []
        return {"taste": taste, "city": city, "mode": self.client.mode,
                "domains": out, "extras": extras, "next": nxt, "trace": drain_trace()}

    def negotiate(self, tastes, city, domain="dining"):
        r = self.client.recommend_for_group(tastes, domain, city)
        compare = self.client.compare_tastes(tastes, city) if len(tastes) >= 2 else []
        return {"tastes": tastes, "city": city, "domain": domain,
                "mode": self.client.mode, "results": r["results"],
                "compare": compare, "trace": drain_trace()}

    def heatmap(self, taste, city):
        r = self.client.heatmap_taste(taste, city)
        r["trace"] = drain_trace()
        return r

    @staticmethod
    def explain(item):
        return item.get("why", "")
