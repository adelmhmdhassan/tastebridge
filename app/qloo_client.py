"""qloo_client.py - Qloo adapter: mock now, real harness when the key arrives."""
import json
import os
import subprocess

BASE_URL = "https://hackathon.api.qloo.com"  # ONLY this base works with hackathon keys

MOCK_EQUIVALENTS = {
    "dining": [
        {"name": "Al Sultan Dubai", "why": "old-city courtyard dining, family recipes", "affinity": 0.91},
        {"name": "Zaroob", "why": "street-food energy, late-night shawarma culture", "affinity": 0.87},
    ],
    "music": [
        {"name": "Umm Kulthum tribute nights at Dubai Opera", "why": "tarab-era repertoire", "affinity": 0.93},
        {"name": "Arabic indie playlists - Molham", "why": "modern arabic indie lineage", "affinity": 0.82},
    ],
    "film": [
        {"name": "Cinema Akil", "why": "independent arab cinema programming", "affinity": 0.89},
    ],
    "fashion": [
        {"name": "The Modist", "why": "modest-fashion contemporary houses", "affinity": 0.84},
    ],
}


class QlooClient:
    """Thin adapter: mock mode until the hackathon key arrives, then harness mode."""

    def __init__(self, mode=None):
        self.mode = mode or os.environ.get("QLOO_MODE", "mock")

    def _harness(self, args):
        out = subprocess.check_output(["qloo"] + args, text=True, encoding="utf-8")
        return json.loads(out)

    def find_equivalents(self, taste, domain, city):
        if self.mode == "mock":
            return {"taste": taste, "domain": domain, "city": city,
                    "results": MOCK_EQUIVALENTS.get(domain, [])}
        return self._harness(["exec", "--json", "taste", "equivalents",
                              "--taste", taste, "--domain", domain, "--city", city])

    def recommend_for_group(self, tastes, domain):
        if self.mode == "mock":
            return {"tastes": tastes, "domain": domain,
                    "results": MOCK_EQUIVALENTS.get(domain, [])[:3]}
        return self._harness(["exec", "--json", "taste", "recommend",
                              "--tastes", json.dumps(tastes), "--domain", domain])


if __name__ == "__main__":
    c = QlooClient()
    print(json.dumps(c.find_equivalents("grandfather cafes", "dining", "Dubai"), ensure_ascii=False, indent=1))
