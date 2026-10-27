# TasteBridge — ثقافتي

**A Qloo-grounded cultural translation agent for expats and travelers.**
_Live demo: https://tastebridge-ar.onrender.com_

> "I love X from back home — what's the equivalent here?"
> Users tell the agent what they love from home ("my grandfather's old cafes", "my mother's playlist", "my favorite street-food vibe") and it finds the closest living equivalents in their new city across **dining, music, film and fashion** — powered by Qloo's taste graph, not generic LLM guessing.

## The problem

An Egyptian moves to Dubai. He can Google "restaurants near me" — but he doesn't want _any_ restaurant; he wants _the feeling_ of Friday koshary at Abou Tarek. Generic LLMs hallucinate confident generic answers. Only a cross-domain taste graph can translate _taste_ across cultures.

## What it does

| Mode                     | Flow                                                                                                                                                                       |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Solo — "وحدك"**        | Type a taste + new city → equivalents across 4 domains, each with a live affinity score, real venue descriptions, ratings and images                                       |
| **Group — "مع مجموعتك"** | Each family member adds a taste as chips (dad, me, the kids) → the agent merges them through Qloo's audience affinities and negotiates **one plan everyone actually fits** |

Everything is bilingual **Arabic-first / English** with full RTL↔LTR flipping — including a visible **agent reasoning panel** (what was asked, which domains were queried, how results were ranked) and honest **live/demo data labeling**.

## Architecture

```
browser (Arabic/English UI, RTL/LTR)
   │ POST /api/translate | /api/negotiate
FastAPI ──► TasteBridgeAgent ──► QlooClient
                                    │  qloo harness CLI (subprocess)
                                    ▼
                     https://hackathon.api.qloo.com
                        api search  →  resolve entity IDs
                        insights    →  audience affinity ranking
```

- **Backend**: FastAPI, Python 3.12, Docker (Python + Node 24 + `@qloo/qloo-harness`)
- **Agent pipeline**: search → entity resolution (city-aware, venue-type-aware seed) → `/insights` affinity ranking → client-side geocode filtering
- **Deployment**: Render, always-on instance ($7/mo)

## Showcasing Qloo (judging criteria mapping)

1. **Cross-domain affinities**: one taste input fans out to 4 entity types (`place`, `artist`, `movie`, `brand`) — the core differentiator vs. any LLM.
2. **Audience affinity over keywords**: results are _people-who-like-X-also-like-Y_, visible per result as a real affinity score (e.g. 98%).
3. **Entity enrichment**: every card carries Qloo's descriptions, ratings, images and tags — real data, zero fabrication.
4. **Group taste negotiation**: multiple seeds merged into one ranked shortlist — a genuinely hard problem for LLM-only tools.

## Privacy-first by design

- **No personal identifying data** is collected, stored or sent to Qloo — only the taste string the user typed and city names.
- All taste profiles live **client-side** (session only). The server holds only the Qloo key.
- Qloo responses are used transiently and never persisted to the public repository.

## Honest limitations & recommendations (for Qloo)

We pushed the API hard and hit real edges — documented here as product feedback:

1. **Arabic search normalization is inconsistent.** The same dish returns different results across spellings (`كشري` vs `كشرى`), and mixed-script queries (`كشرى dubai`) rank landmarks above restaurants. Our workaround: multi-query retries + venue-type-aware seed selection. _Recommendation: script normalization and language-aware ranking in `/search`._
2. **No location filter on `/search`.** City relevance is inferred from the seed entity's geocode; we implemented client-side geocode filtering (`properties.geocode` + `localities`). _Recommendation: a `filter.location` parameter on search._
3. **No human-readable "why" per insight.** Affinity scores are exposed, but the explanation is left to the integrator. _Recommendation: expose `feature.explainability`-style reason strings._
4. **Rate ceilings** for agentic multi-domain flows (2 req/min documented) shape our sequential-call design. _Recommendation: a batch insights endpoint or hackathon-tier quota._

None of these block the demo — they define a roadmap.

## Why Qloo is the product

Strip Qloo away and the same UI collapses into an LLM's hallucinated generic list ("visit the Dubai Mall!"). With Qloo, "كشرى → Dubai" returns Hamor seafood grills, Al Aumdah, Al Amoor — venues _ranked by measured cultural affinity_. The taste graph is the product.

## Run locally

```powershell
pip install -r requirements.txt
$env:QLOO_API_KEY = "..."   # hackathon key
$env:QLOO_MODE = "harness"
uvicorn main:app --port 8000
```

`QLOO_MODE=mock` runs the full UI offline with hand-written sample data (clearly labeled).

## Repository

MIT · FastAPI + vanilla JS (no build step) · `app/agent.py` agent layer · `app/qloo_client.py` adapter (mock/harness) · `tests/` unit tests
