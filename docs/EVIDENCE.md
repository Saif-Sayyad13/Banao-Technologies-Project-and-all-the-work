# Evidence: how do we know it works, and how often it does not

All numbers are produced by `python evaluate.py` (saved in `docs/metrics.json`). Target throughout is **where the request was actually resolved** (`final_team`), with the two renamed teams mapped to their new names.

## 1. The bot's labels are not the truth
- Bot label = team where the request first landed in 100% of rows. It equals the team that closed the request in only **77.2%** of 10,822 requests. By quarter: 78.2 / 75.9 / 77.5 / 77.5 / 76.7%. So it is steady, not getting better.
- Where it goes wrong: patterns Meenal described. "Paid for installation" sent to Billing (146 cases ended in Installs), purifier breakdowns sent to Consumables (315 ended in Repairs), and a pile of vague messages dumped into Repairs.
- Training a model on the bot labels (what was asked for) gives **94.9%** "match" with those labels on the newest quarter, so the 90% bar is easy to pass, but only **75.6%** against where requests ended up. The old bot scores 76.7% on the same rows. Matching the labels copies the bot.

## 2. Validation: by time, never random
Train on everything before a quarter, test on that quarter (rolling origin, 3 quarters):

| Test quarter | Train rows | Test rows | Model accuracy | Macro-F1 | Old bot |
|---|---|---|---|---|---|
| Oct–Dec 2025 | 4,320 | 2,199 | 83.2% | 0.828 | 77.5% |
| Jan–Mar 2026 | 6,519 | 2,168 | 84.5% | 0.841 | 77.5% |
| Apr–Jun 2026 | 8,687 | 2,135 | 83.9% | 0.835 | 76.7% |
| **Pooled** | | **6,502** | **83.9%** (95% CI 83.0–84.8) | **0.834** | **77.2%** |

Per-team F1 (pooled): Repairs 0.87, Billing 0.84, Product Advice 0.84, Returns 0.84, Installs & Demo 0.82, Warranty 0.82, Filters & Consumables 0.81. No team is much worse than the rest.

## 3. Confidence: how much can be automated
| Confidence cut-off | Share of requests automated | Accuracy on those | Old bot on the same rows |
|---|---|---|---|
| none (route all) | 100% | 83.9% | 77.2% |
| ≥ 0.5 | 88.7% | 92.0% | 84.3% |
| **≥ 0.6 (chosen)** | **85.7%** | **94.2%** | 85.7% |
| ≥ 0.7 | 82.9% | 96.0% | 86.8% |
| ≥ 0.8 | 81.0% | 96.8% | 87.4% |

On the actual test file 14.4% of requests fall under 0.6, in line with the 14.3% seen in validation, so there is no sign the new months look different.

## 4. What it gets wrong
- **Vague messages** ("please call me about my purifier", "complaint about robot vacuum", "someone contact me about heater"). 11.3% of validation requests have confidence under 0.5; on those the model is right **20%** of the time (chance for 7 teams is 14%) and the bot 23%. They produce **56% of all errors**.
- Could anything else in the record route them? I trained a model on channel, warranty status, product and hour of day, only on those vague rows (1,268 in train): **17%** accuracy against 14% chance. No. They need a question to the customer.
- **Two problems in one message** ("want to reschedule installation of water purifier, payment deducted but order not placed"): in the error samples I read, these ended up in either team; the model has to pick one. I did not measure how common they are.
- Rest is a small tail of confident-but-wrong cases (8% error among confident ones). I did not find a rule that explains them.

## 5. What I tried (newest quarter as test, trained on earlier quarters)
| Experiment | Accuracy vs real outcome |
|---|---|
| Old bot itself | 76.7% |
| Model trained on bot labels | 75.6% (but 94.9% vs bot labels) |
| Naive Bayes | 82.6% |
| TF-IDF words + logistic regression | 83.8% |
| **TF-IDF words + character n-grams + logistic regression (chosen)** | **83.9%** |
| Linear SVM | 84.3% |

Four different model families land within about 1.7 points of each other, and the leftover errors are the vague messages, so a bigger model (or an LLM) is unlikely to fix them. The SVM was 0.4 points better on one quarter; I kept logistic regression because it gives a usable confidence and reasons.

## 6. Money (estimates, from policy §4 and the log)
- ~8,700 requests a year (721 a month in the history; the test file has 701–741 a month).
- Wrong-team request (first team ≠ final team): 22.8% of requests, 1.44 transfers each, so 1.44 × Rs 305 + Rs 260 = **Rs 698**.
- Bot today: Rs 13.8 lakh of misroute cost + Rs 3.2 lakh licence = **Rs 17.0 lakh/yr**.
- Route everything with the model: error 16.1% → **Rs 9.8 lakh/yr** (saves Rs 7.3 lakh).
- Model with triage desk (14.3% to a human at an assumed Rs 260 each): **Rs 6.2 lakh/yr** (saves Rs 10.8 lakh). Break-even at about Rs 543 per triaged request.

## 7. Headcount hint (Ritu asked which teams are busiest)
Share of requests by where they actually end up, vs the bot's label: Repairs 23.4% (bot 28.9%), Installs & Demo 14.7% (10.9%), Returns 14.2% (10.8%), Product Advice 12.8% (10.9%), Warranty 12.7% (9.6%), Billing 12.2% (15.3%), Filters & Consumables 9.9% (13.5%).

## 8. Data problems found and handled
- 480 training messages with broken characters from the Zoho migration (`Ã©`, `â€¦`): repaired in `kestrel/text.py`. 4,320 rows come from `legacy_zoho`.
- Two renamed teams (15 Jan 2026): mapped to the new names.
- Order/request numbers inside the text (SR…, KO…): removed, they carry no signal.
- The `resolved_at` times for Zoho rows are in UTC and were never converted (policy §9). I do not use resolution times at all, so this does not affect the model.
- 663 repeated message texts in train; 11.8% of test messages appear verbatim in train. This slightly flatters any score on repeated templates; time-split validation has the same ~10% overlap.
