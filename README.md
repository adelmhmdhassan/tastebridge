# TasteBridge — ثقافتي

**A Qloo-grounded cultural translation agent for expats and travelers — Arabic-first, English-ready.**
_Live: https://tastebridge-ar.onrender.com_

> "I love X from back home — what's the equivalent here?"
> Tell the agent what you love from home ("my grandfather's old cafes", "my mother's playlist") and it finds the closest living equivalents in your new city across **dining, music, film and fashion** — powered by Qloo's taste graph, not generic LLM guessing.

## What it does

| Mode                     | Flow                                                                                                                                                                                                                               |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Solo — "وحدك"**        | Taste + new city → equivalents across 4 domains with live affinity scores, photos (navigable galleries), addresses, ratings and one-click Google Maps                                                                              |
| **Group — "مع مجموعتك"** | Each family member adds tastes as chips (dad, me, the kids) → Qloo audience affinities merged into **one plan everyone fits** — with a per-person "fit with the group" score                                                       |
| **City Map**             | Live `where_popular` heatmap of where your taste concentrates — click any circle to bring its venues to the top; cards link back to their circle                                                                                   |
| **First Evening**        | One click builds a chained night: dinner 7PM → coffee 9PM → sweets 10:30PM, each stop recommended from the previous one                                                                                                            |
| **Taste Intelligence**   | Every answer adds Taste DNA chips (entity_tags), "who loves it" demographics (audience_demographics), a visible agent-reasoning panel with **every Qloo call traced**, and a built-in "see the difference without Qloo" comparison |

Everything is bilingual **Arabic/English with full RTL↔LTR**, shareable URLs per tab, honest live/demo labeling, and clear error states.

## Design philosophy: clarity over clutter

We deliberately chose **one focused screen and progressive disclosure** over dense dashboards: the judge can follow the whole story in 30 seconds — type, results, intelligence, plan. Advanced value (comparison, evening plan, map linking) appears **on demand**, not all at once. A demo is _understood_, not merely admired.

## Architecture

```javascript
browser (Arabic-first UI, RTL/LTR, galleries, Leaflet map)
   │ POST /api/translate | /api/negotiate | /api/heatmap | /api/plan
FastAPI ──► TasteBridgeAgent (parallel domain fan-out) ──► QlooClient
                                                              │ qloo harness CLI (subprocess, timed+traced)
                                                              ▼
                                      https://hackathon.api.qloo.com
```

**Qloo services used (7):** entity search · insights (affinity ranking) · where_popular (heatmaps) · entity_tags (Taste DNA) · audience_demographics · compare_audiences (group fit) · recommend (What's next + chained evening plan). Docker: Python 3.12 + Node 24 + `@qloo/qloo-harness`, always-on Render ($7/mo), key in env vars only.

## Privacy-first by design

No personal identifying data is collected or stored — only the typed taste string and city reach Qloo; profiles live client-side per session; responses are transient and never committed to the public repo.

## Honest limitations & recommendations (for Qloo)

1. **Arabic search normalization is inconsistent** (`كشري` vs `كشرى` differ; mixed-script queries rank landmarks above restaurants). Our workaround: multi-query retries + venue-type-aware seed selection. _Recommendation: script normalization + language-aware ranking in `/search`._
2. **No location filter on `/search`** — city relevance inferred from seed geocode; we do client-side geocode filtering. _Recommendation: `filter.location` on search._
3. **Rate ceilings** shape our sequential-chain design for the evening plan. _Recommendation: batch insights or higher hackathon quota._
   (Update: `recommend` exposes `explain` — native explainability partially answers our earlier ask.)

## Why Qloo is the product

Strip Qloo away and the same UI collapses into a generic LLM list ("visit the Dubai Mall!"). With Qloo, "كشرى → Dubai" returns Hamor, Al Aumdah, Al Amoor — venues ranked by measured cultural affinity, with the audience behind each one made visible. The taste graph is the product.

## Run locally

```powershell
pip install -r requirements.txt
$env:QLOO_API_KEY = "..."   # hackathon key
$env:QLOO_MODE = "harness"
uvicorn main:app --port 8000
```

`QLOO_MODE=mock` runs the full UI offline with clearly-labeled sample data. MIT · FastAPI + vanilla JS · `app/agent.py` · `app/qloo_client.py` (mock/harness) · `tests/`
