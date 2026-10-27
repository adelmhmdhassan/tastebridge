# NOTES.md - TasteBridge (مشروع Gloo Agentic Hackathon)

## 2026-10-17 20:57 — Deployment achieved + full product plan approved

### Shipped today (verified end-to-end)

- Render service LIVE: https://tastebridge-ar.onrender.com (Free/Oregon).
  CAUTION: tastebridge.onrender.com belongs to a STRANGER (same-name coincidence) — our URL is tastebridge-ar only.
- Fix commit 17d5e62: STATIC path bug (parent.parent -&gt; parent).
- index.html fatal bug FIXED: unterminated string literal in card() killed the whole &lt;script&gt; (SyntaxError = all buttons dead). Verified: node --check fail before / pass after.
- Live verified: homepage serves Arabic UI; POST /api/translate returns structured mock results.

### Environment lesson (CRITICAL)

- A fresh terminal activated the WRONG venv (codeGenerator_fresh, Python 3.8) -&gt; false TypeError on `list[str] | None` (needs 3.10+).
- Project env is D:\Projects\tastebridge\venv (Python 3.12) — same as Render runtime. Always verify `python --version` first.

### Approved plan: C + X1 + X6 + X8 + Y1 (Y3 optional, Y4 deferred) — target ~96/100

- Phase 1 (pre-Qloo-key, 4-5 evenings): full i18n (buttons/tabs/domains/empty states), tooltips + input helper examples, button rename (اكتشف نظيرك / وحدك / مع مجموعتك / اتفقوا على خطة), X1 one-click demo presets, X6 agent-reasoning panel (keywords + affinity score + call trace), Y1 "demo data" badge on mock results.
- Phase 2 (with Qloo key, 4-5 evenings): Taste Passport (local-only structured taste profile — privacy-first 15 pts), city taste heatmap (Leaflet), parallel calls + caching (X7).
- Phase 3 (Oct 29-30): X8 accessibility (ARIA/keyboard/contrast), full test pass, polish.
- Render Free-&gt;Paid upgrade Oct 25 (reminder set 09:00) — cold start ~50s risk for judges.
- Deadline: Oct 31 5:45 AM. Requirements: live hosted app + public repo (MIT) + written explanation. No video needed.

### Competitive scan (published Qloo Agentic projects)

- Chinese-brands GTM agent (tastebridge.onrender.com): visible agent trace + evidence citations + Leaflet map + openai_compat planner. Est ~70/100.
- Appmuseme: day-by-day taste itineraries + playlists + vibe maps. Est ~72/100.
- Taste-Context Brief (MCP): honest fixtures labeling (adopted as Y1). Est ~58/100.
- Qlooful Host (party planner, Oct 15): early. Est ~54/100.
- Our unique space: expat cultural translation + Arabic-first RTL + group negotiation + local-only Taste Passport. Overlap is tool-level only (expected) — idea-level uniqueness intact.

**الهاكاثون:** Qloo Agentic - $25,000 ($15k/$6k/$4k) - Deadline: 31 أكتوبر 2026 5:45 صباحاً
**الفكرة:** وكيل ترجمة ثقافية للمغتربين: "أحب X من بلدي - ما نظيره هنا؟" عبر المطاعم والموسيقى والأفلام والموضة + تفاوض ذوق المجموعات - واجهة عربية/إنجليزية
**الركن التقني:** Qloo API عبر qloo harness (subprocess من FastAPI) - القيمة الجوهرية من taste graph (250M+ كيان)

## البنية

app\ باك إند FastAPI + منطق الوكيل
static\ واجهة صفحة واحدة (عربي/إنجليزي)
tests\ اختبارات
venv\ بايثون 3.12 (معزول)

## المتطلبات الجوهرية (من صفحة الهاكاثون)

- تطبيق حي مُستضاف علناً (Render/Fly.io) - repo عام برخصة MIT - بلا فيديو
- الحكام يجرّبون التطبيق فعلياً: load | chat | reasoning | tools | context | speed

## آخر موقف

- 2026-10-17: المشروع أُنشئ، البيئة 3.12، git محلي مبدئي. التالي: ترقية Node 22+ وتركيب qloo harness واصطياد المفتاح.

## تحديث (2026-10-17 10:45)

- طلب مفتاح Qloo مُرسل (بانتظار البريد - أيام عمل).
- المفتاح يعمل فقط على base URL: https://hackathon.api.qloo.com (أي URL آخر = 401 - الدرس الأشهر).
- qloo harness 0.1.26 مثبت. Node مُرقى. البيئة 3.12 جاهزة.
- الخطة أثناء الانتظار: بناء الباك إند والواجهة بطبقة Mock لـ Qloo - عند وصول المفتاح نستبدلها بمحوّل رفيع (يوم واحد).
