"""qloo_client.py - Qloo adapter: mock now, real harness when the key arrives."""
import json
import os
import re as _re
import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor

TRACE = []
TRACE_LOCK = threading.Lock()


def _trace(op, ms):
    with TRACE_LOCK:
        TRACE.append({"op": op, "ms": int(ms)})


def drain_trace():
    with TRACE_LOCK:
        out = list(TRACE)
        TRACE.clear()
        return out

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
           "grill", "kitchen", "bakery", "shawarma", "pizza", "bistro", "koshar")


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
    t0 = time.time()
    full = (["cmd", "/c"] + cmd) if os.name == "nt" else cmd
    out = subprocess.run(full, capture_output=True, text=True, timeout=12, encoding="utf-8")
    _trace(cmd[1] if cmd[0] == "qloo" else " ".join(cmd[2:4]), (time.time() - t0) * 1000)
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
    raw = ([(p.get("image") or {}).get("url")] + [im.get("url") for im in (p.get("images") or [])])
    imgs = []
    seen = set()
    for u in raw:
        if not u:
            continue
        key = _re.sub(r"-\d+x-[a-zA-Z]+", "", u)
        if key not in seen:
            seen.add(key)
            imgs.append(u)
    img = imgs[0] if imgs else None
    city_name = geo.get("city") or ""
    hay = _hay(e)
    return {
        "name": e.get("name", ""),
        "id": e.get("entity_id", ""),
        "address": p.get("address", ""),
        "lat": (e.get("location") or {}).get("lat"),
        "lon": (e.get("location") or {}).get("lon"),
        "why": p.get("description") or p.get("short_description") or "",
        "affinity": round(q.get("affinity") or e.get("popularity") or 0, 4),
        "rating": p.get("business_rating"),
        "image": img,
        "images": imgs,
        "city": city_name,
        "_city_match": (city.lower() in hay) if city else True,
    }


def _seed_for(taste, type_, city=""):
    city_en = _norm_city(city)
    queries = ([taste + " " + city_en, taste] if city_en else [taste])
    last_hits = []
    for q in queries:
        hits = _qloo_json(["qloo", "api", "search", "--query", q, "--json"])[:8]
        last_hits = hits
        typed = [h for h in hits if any(type_ in (t or "") for t in h.get("types", []))]
        if city_en:
            in_city = [h for h in typed if city_en in _hay(h)]
            if type_ == "place":
                foodish = [h for h in in_city if _is_foodish(h)]
                if foodish:
                    return foodish[0]
            elif in_city:
                return in_city[0]
        elif typed:
            return typed[0]
    typed = [h for h in last_hits if any(type_ in (t or "") for t in h.get("types", []))]
    if city_en and type_ == "place":
        in_city = [h for h in typed if city_en in _hay(h)]
        foodish = [h for h in in_city if _is_foodish(h)]
        if foodish:
            return foodish[0]
        if in_city:
            return in_city[0]
    if typed:
        return typed[0]
    return last_hits[0] if last_hits else None


MOCK_HEATMAP = [
    {"lat": 25.2048, "lon": 55.2708, "affinity": 0.95},
    {"lat": 25.1857, "lon": 55.2522, "affinity": 0.88},
    {"lat": 25.0805, "lon": 55.1403, "affinity": 0.76},
    {"lat": 25.0657, "lon": 55.1711, "affinity": 0.64},
]


def _exec_json(op, payload):
    t0 = time.time()
    cmd = ["qloo", "exec", op, "--input", json.dumps(payload)]
    full = (["cmd", "/c"] + cmd) if os.name == "nt" else cmd
    out = subprocess.run(full, capture_output=True, text=True, timeout=12, encoding="utf-8")
    _trace("exec " + op, (time.time() - t0) * 1000)
    if out.returncode != 0:
        raise RuntimeError(f"qloo exec failed: {out.stderr.strip()[:300]}")
    data = json.loads(out.stdout)
    if isinstance(data, dict) and data.get("status") == "needs_input":
        return {"needs_input": True, "summary": data.get("summary", "")}
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(str(data["error"])[:200])
    return data


def _first_number(obj):
    if isinstance(obj, (int, float)):
        return round(float(obj), 3)
    if isinstance(obj, dict):
        for v in obj.values():
            r = _first_number(v)
            if r is not None:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = _first_number(v)
            if r is not None:
                return r
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


    def next_stops(self, entity_id, city, limit=3):
        """recommend: what comes next after the winning pick."""
        if self.mode == "mock":
            return {"stops": MOCK_EQUIVALENTS.get("dining", [])[:2]}
        d = _exec_json("recommend", {"target_type": "place", "signals": [entity_id],
                                     "signal_location": city, "explain": True, "limit": limit})
        rs = d.get("results") or []
        return {"stops": [_to_card(e, city) for e in rs]}

    def evening_plan(self, taste, city, steps=3):
        """Chain recommends: dinner -> coffee -> sweets/music (first-evening plan)."""
        if self.mode == "mock":
            return {"plan": MOCK_EQUIVALENTS.get("dining", [])[:steps]}
        try:
            seed = _seed_for(taste, "place", city)
        except Exception:
            seed = None
        if not seed:
            return {"plan": []}
        stops, current = [], seed["entity_id"]
        for _ in range(steps):
            try:
                r = self.next_stops(current, city, limit=5)
            except Exception:
                break
            cands = [c for c in r["stops"]
                     if c.get("id") and c["id"] != current
                     and all(c["id"] != s.get("id") for s in stops)]
            cands.sort(key=lambda c: c.get("affinity") or 0, reverse=True)
            picked = cands[0] if cands else None
            if not picked:
                break
            stops.append(picked)
            current = picked["id"]
        return {"plan": stops}

    def extras(self, taste, city):
        """entity_tags + audience_demographics for the seed entity."""
        if self.mode == "mock":
            return {"dna": [{"name": "Middle Eastern", "affinity": 0.99}, {"name": "Late Night", "affinity": 0.9}],
                    "who": {"ages": ["25-29", "30-34"], "gender": "mixed"}}
        try:
            seed = _seed_for(taste, "place", city)
        except Exception:
            seed = None
        if not seed:
            return {"dna": [], "who": None}
        sid = seed["entity_id"]

        def get_tags():
            d = _exec_json("entity_tags", {"entities": [sid], "limit": 10})
            rs = d.get("results") or []
            keep = [t for t in rs if any(k in (t.get("type") or "") for k in ("genre", "cuisine", "dish", "ambience", "atmosphere"))]
            pool = keep or rs
            return [{"name": t.get("name"), "affinity": round(t.get("affinity") or 0, 3)} for t in pool[:10]]

        def get_demo():
            d = _exec_json("audience_demographics", {"entity": sid})
            rs = (d.get("results") or [{}])[0]
            q = rs.get("query") or {}
            ages = sorted((q.get("age") or {}).items(), key=lambda kv: kv[1], reverse=True)
            top_ages = [k.replace("_", "-").replace("and", "+") for k, v in ages if v > 0][:2]
            g = q.get("gender") or {}
            gender = "mixed"
            if (g.get("male") or 0) > 0.05 and (g.get("female") or 0) < -0.05:
                gender = "male-leaning"
            elif (g.get("female") or 0) > 0.05 and (g.get("male") or 0) < -0.05:
                gender = "female-leaning"
            return {"ages": top_ages, "gender": gender}

        with ThreadPoolExecutor(max_workers=2) as ex:
            f_tags = ex.submit(get_tags)
            f_demo = ex.submit(get_demo)
            try:
                dna = f_tags.result()
            except Exception:
                dna = []
            try:
                who = f_demo.result()
            except Exception:
                who = None
        return {"dna": dna, "who": who}

    def compare_tastes(self, tastes, city):
        """compare_audiences: each taste against the rest of the group."""
        if self.mode == "mock":
            return [{"taste": t, "fit": round(0.9 - i * 0.05, 2)} for i, t in enumerate(tastes)]
        seeds = []
        for t in tastes:
            try:
                s = _seed_for(t, "place", city)
            except Exception:
                s = None
            seeds.append(s)
        out = []
        for i, t in enumerate(tastes):
            if not seeds[i]:
                continue
            others = [s["entity_id"] for j, s in enumerate(seeds) if s and j != i]
            if not others:
                out.append({"taste": t, "fit": 1.0})
                continue
            try:
                d = _exec_json("compare_audiences", {"group_a": [seeds[i]["entity_id"]],
                                                    "group_b": others, "target_type": "place"})
                out.append({"taste": t, "fit": _first_number(d.get("results"))})
            except Exception:
                out.append({"taste": t, "fit": None})
        return out

    def heatmap(self, entity_id, within, limit=12):
        if self.mode == "mock":
            return {"mode": self.mode, "points": MOCK_HEATMAP[:limit]}
        data = _exec_json("where_popular", {"entity": entity_id, "within": within, "limit": limit})
        if data.get("needs_input"):
            return {"mode": self.mode, "points": [], "needs_input": True}
        pts = [{"lat": p["location"]["latitude"], "lon": p["location"]["longitude"],
                "affinity": round((p.get("query") or {}).get("affinity") or 0, 4)}
               for p in data.get("results", []) if p.get("location")]
        return {"mode": self.mode, "points": pts}

    def heatmap_taste(self, taste, within):
        if self.mode == "mock":
            return {"taste": taste, "city": within, "mode": self.mode,
                    "points": MOCK_HEATMAP, "cards": MOCK_EQUIVALENTS.get("dining", [])}
        seed = _seed_for(taste, "place", within)
        if not seed:
            return {"taste": taste, "city": within, "mode": self.mode, "points": [], "cards": []}
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_h = ex.submit(self.heatmap, seed["entity_id"], within)
            f_c = ex.submit(self.find_equivalents, taste, "dining", within)
            r = f_h.result()
            cards = f_c.result()["results"]
        nxt = []
        if cards and cards[0].get("id"):
            try:
                nxt = self.next_stops(cards[0]["id"], within)["stops"]
            except Exception:
                nxt = []
        return {"taste": taste, "city": within, "seed": seed.get("name"),
                "cards": cards, "next": nxt, **r}


if __name__ == "__main__":
    c = QlooClient()
    print(json.dumps(c.find_equivalents("grandfather cafes", "dining", "Dubai"), ensure_ascii=False, indent=1))
