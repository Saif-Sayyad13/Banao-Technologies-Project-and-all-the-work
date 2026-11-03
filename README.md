# Kestrel Home – service-request router (Variant B)

Routes a customer message to one of Kestrel's 7 teams, says why, and says **"ask the customer"** when the message is too vague to route.
No paid API, no internet, no per-request cost. Runs on a laptop CPU.

## Run it (clean machine, ~1 minute)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                                          # opens on http://localhost:8000
```

Open <http://localhost:8000> for the screen, or call the endpoint:

```bash
curl -X POST localhost:8000/route -H 'Content-Type: application/json' \
  -d '{"request_text":"installer did not turn up for my air fryer","channel":"chat","warranty_status":"in_warranty","product_family":"Air Fryer"}'
```

Only `request_text` is required. `channel` = ivr|chat|whatsapp|email, `warranty_status` = in_warranty|shield|out_of_warranty.
Response: `team`, `confidence`, `needs_triage`, `action`, `second_choice`, `reasons` (plain-English, for a service-desk agent).
Bad input returns a polite 400 with a message; any internal failure returns "route this by hand" instead of a stack trace.
The trained model (`model/model.joblib`, 200 KB) is in the repo, so nothing needs the client data to *run*.

Tests: `python -m pytest -q tests`

## What is in here

| File | What |
|---|---|
| `predictions.csv` | Team for every row of `test_unlabelled.csv`, in the `sample_submission.csv` shape (new team names). |
| `app.py`, `static/index.html` | The endpoint (`POST /route`) and the screen. |
| `kestrel/` | Text clean-up (mojibake, ids, accents), model definition, serving + explanations. |
| `evaluate.py` → `docs/metrics.json` | All the evidence: time-split validation, error analysis, experiments, rupees. |
| `docs/EVIDENCE.md` | The same evidence, written up. |
| `memo/memo-to-ritu.pdf` (+ `.md`) | One-page memo for the client. |
| `SUBMISSION_FORM.md` | Draft answers for the submission form. |
| `train.py`, `make_predictions.py` | Retrain on `data/` and regenerate `predictions.csv`. |
| `docs/predictions_with_confidence.csv` | Extra: the confidence and triage flag for each test row. |

## Retrain / reproduce

Put the client's `train.csv`, `test_unlabelled.csv`, `resolution_log.csv`, `sample_submission.csv` in `./data/` (git-ignored on purpose, see below), then:

```bash
python evaluate.py && python train.py && python make_predictions.py
```

## Decisions I made where the brief was unclear

1. **Target = the team that actually closed the request (`final_team`), not the bot's `team_label`.** The bot's label matches the outcome only 77% of the time. Training on it scores 95% on "match the labels" but only 76% on reality, no better than the bot. See `docs/EVIDENCE.md`.
2. **New team names** (*Installs & Demo*, *Filters & Consumables*) in all output, because the test period is after 15 Jan 2026. Old names in the training data are mapped to the new ones.
3. **Vague requests get a "needs triage" flag** (confidence below 0.6, about 14% of requests). `predictions.csv` still holds the model's best guess for them because the format needs one team per row.
4. **No LLM.** Finance asked for no bill that grows per request, and the vague requests have no signal an LLM could find either (see evidence).
5. **Client data is not in this repo.** Ops policy §10 forbids putting customer/operational data in public repositories. Only the 200 KB model and `predictions.csv` (request ids + team) are committed. The model keeps word patterns, not customer records. I checked the text for phone numbers and emails: none.

## Known limits (details in `SUBMISSION_FORM.md`)

About 11–14% of requests are too vague to route from the text, and the model is right on those only about 1 time in 5. Not production hardened: Flask dev server, no login, no request logging, no monitoring, no retraining schedule.
