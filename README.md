# TasteBridge - ثقافتي

A cultural-translation agent for expats and travelers: tell it what you love
from home, and it finds the closest living equivalents in your new city across
dining, music, film, and fashion - then negotiates one plan for groups whose
tastes conflict.

## Why Qloo is the product

Generic LLMs guess. TasteBridge grounds every recommendation in Qloo taste
graph affinity data (250M+ entities): each result carries a measured affinity
score instead of a hallucination. Remove Qloo and the app collapses into
generic advice - that is the point.

## Features

- Translate mode: one home taste -> equivalents across four domains
- Group negotiation: merge several tastes into one ranked shortlist
- Bilingual Arabic/English interface with RTL/LTR switching
- FastAPI backend agent -> Qloo harness (mock mode until the hackathon key activates)

## Run locally

    pip install fastapi uvicorn
    python -m uvicorn main:app --port 8000

## Architecture

    static/index.html   bilingual single-page UI
    main.py             FastAPI endpoints
    app/agent.py        agent logic (translate + negotiate)
    app/qloo_client.py  Qloo adapter: mock now, harness mode behind QLOO_MODE
    tests/              unittest suite (4 tests)

## License

MIT - see LICENSE
