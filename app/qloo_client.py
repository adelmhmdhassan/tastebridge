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


AR_CITIES = {
    "دبي": "dubai", "دبى": "dubai", "القاهرة": "cairo", "القاهره": "cairo",
    "لندن": "london", "الدوحة": "doha", "الدوحه": "doha", "باريس": "paris",
    "نيويورك": "new york", "الرياض": "riyadh", "جدة": "jeddah", "جده": "jeddah",
    "أبوظبي": "abu dhabi", "ابوظبي": "abu dhabi", "عمّان": "amman", "عمان": "amman",
}


FOODISH = ("restaurant", "cafe", "café", "eatery", "food", "dining",
           "grill", "kitchen", "bakery", "shawarma", "pizza", "bistro")


def _is_foodish(h):
    p = h.get("properties", {}) or {}
    pg = p.get("primary_genre") or {}
    blob = " ".join([pg.get("id") or "", pg.get("name") or "",
                     p.get("description") or "", p.get("short_description") or ""]).lower()
    return any(k in blob for k in FOODISH)


def _norm_city(city):
    c = (city or "").strip()
    return AR_CITIES.get(c, c).lower()


def _hay(entity):
    p = entity.get("properties", {}) or {}
    geo = p.get("geocode", {}) or {}
    parts = [geo.get("city") or "", geo.get("admin1_region") or "", geo.get("name") or "",
             p.get("address") or ""]
    for loc in (p.get("localities") or []):
        parts.append(loc.get("name") or "")
    return " | ".join(parts).lower()


DOMAIN_TYPES = {"dining": "place", "music": "artist", "film": "movie", "fashion": "brand"}


def _qloo_json(cmd):
    # Windows: qloo is an npm .cmd shim (not .exe) -> subprocess needs cmd /c
    full = (["cmd", "/c"] + cmd) if os.name == "nt" else cmd
    out = subprocess.run(full, capture_output=True, text=True, timeout=90, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(f"qloo failed: {out.stderr.strip()[:300]}")
    data = json.loads(out.stdout)
    if isinstance(data, dict) and data.get("error"):
        return []
    return data if isinstance(data, list) else []


def _to_card(e, city=""):
    p = e.get("properties", {}) or {}
    geo = p.get("geocode", {}) or {}
    q = e.get("query", {}) or {}
    img = (p.get("image") or {}).get("url")
    if not img and p.get("images"):
        img = p["images"][0].get("url")
    city_name = geo.get("city") or ""
    hay = _hay(e)
    return {
        "name": e.get("name", ""),
        "why": p.get("description") or p.get("short_description") or "",
        "affinity": round(q.get("affinity") or e.get("popularity") or 0, 4),
        "rating": p.get("business_rating"),
        "image": img,
        "city": city_name,
        "_city_match": (city.lower() in hay) if city else True,
    }


def _seed_for(taste, type_, city=""):
    city_en = _norm_city(city)
    queries = ([taste + " " + city_en, taste] if city_en else [taste])
    for q in queries:
        hits = _qloo_json(["qloo", "api", "search", "--query", q, "--json"])[:8]
        typed = [h for h in hits if any(type_ in (t or "") for t in h.get("types", []))]
        if not typed and hits:
            typed = hits[:1]
        if city_en:
            in_city = [h for h in typed if city_en in _hay(h)]
            if in_city:
                if type_ == "place":
                    foodish = [h for h in in_city if _is_foodish(h)]
                    if foodish:
                        return foodish[0]
                return in_city[0]
        if typed:
            return typed[0]
    return None


class QlooClient:
    """Thin adapter: mock mode until the hackathon key arrives, then harness mode."""

    def __init__(self, mode=None):
        self.mode = mode or os.environ.get("QLOO_MODE", "mock")

    def _harness(self, args):
        out = subprocess.check_output(["qloo"] + args, text=True, encoding="utf-8")
        return json.loads(out)

    def find_equivalents(self, taste, domain, city):
        if self.mode == "mock":
            return {"taste": taste, "domain": domain, "city": city, "mode": self.mode,
                    "results": MOCK_EQUIVALENTS.get(domain, [])}
        type_ = DOMAIN_TYPES.get(domain, "place")
        seed = _seed_for(taste, type_, city)
        if not seed:
            return {"taste": taste, "domain": domain, "city": city, "mode": self.mode, "results": []}
        ranked = _qloo_json(["qloo", "insights", "--type", type_,
                             "--signal-entities", seed["entity_id"], "--json"])
        cards = [_to_card(e, city) for e in ranked]
        in_city = [c for c in cards if c.get("_city_match")]
        return {"taste": taste, "domain": domain, "city": city, "mode": self.mode,
                "seed": seed.get("name"), "results": (in_city or cards)[:6]}

    def recommend_for_group(self, tastes, domain, city=""):
        if self.mode == "mock":
            return {"tastes": tastes, "domain": domain, "mode": self.mode,
                    "results": MOCK_EQUIVALENTS.get(domain, [])[:3]}
        type_ = DOMAIN_TYPES.get(domain, "place")
        ids = []
        for t in tastes:
            s = _seed_for(t, type_, city)
            if s:
                ids.append(s["entity_id"])
        if not ids:
            return {"tastes": tastes, "domain": domain, "city": city, "mode": self.mode, "results": []}
        try:
            ranked = _qloo_json(["qloo", "insights", "--type", type_,
                                 "--signal-entities", ",".join(ids[:3]), "--json"])
        except Exception:
            ranked = _qloo_json(["qloo", "insights", "--type", type_,
                                 "--signal-entities", ids[0], "--json"])
        cards = [_to_card(e, city) for e in ranked]
        in_city = [c for c in cards if c.get("_city_match")]
        return {"tastes": tastes, "domain": domain, "city": city, "mode": self.mode,
                "results": (in_city or cards)[:3]}


if __name__ == "__main__":
    c = QlooClient()
    print(json.dumps(c.find_equivalents("grandfather cafes", "dining", "Dubai"), ensure_ascii=False, indent=1))
