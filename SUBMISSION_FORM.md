# Submission form: draft answers

Fields in **[BRACKETS]** are things only you can fill in. Edit anything that is not true for you, especially the AI-use answer. Answers marked "can only raise your score" should stay honest and specific.

---

**1. What did you build, and what business outcome does it move? State the number and the money.**
A router that reads a customer message and picks one of Kestrel's 7 teams, explains why in plain words, and flags vague messages for a human instead of guessing. On 6,502 past requests it had not seen (tested forward in time), it picks the right team 83.9% of the time against 77.2% for the old bot. For the 85.7% of requests where it is confident, it is right 94.2% of the time. Estimated money: about Rs 7.3 lakh a year saved if it routes everything, about Rs 10.8 lakh a year with a small triage desk for the vague 14% (assumes Rs 260 per call-back). Both include dropping the Rs 3.2 lakh licence. No per-request cost: it uses no paid AI service.

**2. What score do you expect predictions.csv to get on the hidden outcomes, on which metric, and why that metric? Say how you estimated it.**
Accuracy of about **0.84** (I would not be surprised by 0.82 to 0.86), macro-F1 about 0.83, scored against the team that actually closed each request. Accuracy is the metric because every wrong-team request costs about the same (Rs 698) and the 7 teams are reasonably balanced (10–23% each), so accuracy translates directly into rupees; macro-F1 is there to show no team is being sacrificed. Estimate: three rolling forward-in-time tests (train on the past, score the next quarter) over 6,502 requests gave 83.2%, 84.5%, 83.9%. I kept the confidence-based cut-off (0.6) out of the headline accuracy, which is for all rows. If the hidden outcome were instead the bot's own label, I would expect only about 78%, because I deliberately did not train on it.

**3. How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.**
6,502 test requests across three quarters (Oct 2025 to Jun 2026), each scored by a model trained only on earlier data. Error rate 16.1% overall; 5.8% on the confident 85.7%. The kind it gets wrong: vague messages like "please call me about my purifier" (11% of requests; right only 20% of the time; 56% of all errors), and messages with two problems in one. I checked whether channel, warranty, product or time of day could rescue the vague ones: 17% vs 14% chance, so no. Details: `docs/EVIDENCE.md`.

**4. Did you change, narrow, or push back on the client's ask? What, when, and why.** *(can only raise your score)*
Yes, at the start, after comparing the bot's `team_label` with `resolution_log.csv`. The 90% "match the labels" bar is the wrong target: the labels agree with where requests ended up only 77% of the time, and a model trained to copy them scored 94.9% on matching but 75.6% on real outcomes, worse than the bot. I trained and measured on the team that actually closed the request instead, and told Ritu in the memo not to use the 90% bar. I also narrowed the promise: about 14% of requests cannot be routed from the text, so the product flags them for a triage desk rather than claiming 90% on everything. I also widened the answer to Ritu's headcount question using real resolution data, not bot labels.

**5. What is wrong with what you are handing us?** *(can only raise your score)*
- About 14% of predictions are close to guesses. `predictions.csv` needs one team per row, so they hold a best guess that is right about 1 time in 5. `docs/predictions_with_confidence.csv` marks them.
- The 0.6 cut-off was chosen on the same three test quarters I report results on, so the 94.2% is slightly optimistic. The confidence number is not formally calibrated.
- The rupee figures are estimates: yearly volume extrapolated from 15 months, the Rs 260 triage-call cost is my assumption, and I counted all transfers in the log as cost even though about 350 rows show one transfer but the same first and final team, which looks odd and I did not investigate.
- Hosting cost is not priced. I only say "a couple of thousand rupees a month", which is a guess.
- The "reasons" in the screen are the words that pushed the model towards its answer. They are not a rule, and sometimes include filler like "my air".
- Not production-ready: Flask development server, no login, no logging, no monitoring, no retraining schedule, no check that the model still works after Kestrel's wording changes.
- I assumed the hidden score uses the team that closed the request; that is my reading of the brief, not something stated.
- 11.8% of test messages appear word-for-word in the training data, which makes any score a little easier than on completely new wording.

**6. What did you deliberately leave out, and why that rather than something else?**
An LLM or embeddings: Finance said no bill that grows with volume, four model types landed within 1.7 points of each other, and the biggest error source (vague messages) has no information to find. Resolution-time analysis: the Zoho times are in UTC and unconverted, and the task is routing. Login/monitoring/retraining: a small thing that runs beat a large thing that does not. Customer data in the repo: ops policy §10 forbids public repositories, so only the 200 KB model and `predictions.csv` are committed. I chose these over polishing the UI because the decision for Ritu depends on the numbers, not the screen.

**7. Anything you built or found that nobody asked for?**
(a) The bot label vs outcome gap (77%) and that "Repairs" is its dumping ground. (b) A "needs triage" mode with a rupee break-even (Rs 543 per call-back). (c) A real busiest-teams ranking for headcount, which differs from what the bot labels suggest (e.g. Repairs 23% not 29%, Installs & Demo 15% not 11%). (d) A mojibake repair for the Zoho text. (e) A file with confidence for each test row.

**8. What did you use AI for? Which tools and models, where they helped, where they wasted your time, what you threw away. Link your three-minute screen recording here.**
**[EDIT THIS TO MATCH WHAT YOU REALLY DID.]** I used Claude (Anthropic) in the claude.ai chat to explore the data, write the code (cleaning, model, evaluation, Flask service, screen, tests) and draft the memo and these answers. It helped most in finding the label-vs-outcome gap and in building the evaluation quickly. I did not use any paid API inside the product. Cost: **[your plan cost, or "free tier / Rs 0"]**. Discarded: training on the bot labels (scores well on the client's metric, poorly in reality), Naive Bayes and SVM (not better or no usable confidence), and a first version of the screen's explanations that showed filler words and internal tokens. **[Add what you personally checked or changed.]** Video: **[LINK]**

---

**Someone picks this up on Monday and you are unreachable. The three things they need to know.**
1. Run `pip install -r requirements.txt && python app.py`; the model is in `model/`, no keys needed. To retrain, put the client CSVs in `data/` (never commit them) and run `python evaluate.py && python train.py && python make_predictions.py`.
2. The target is the team that closed the request, not the bot's label. Do not switch to bot labels to hit the 90% number. Run 2 to 4 weeks in shadow mode and compare with real outcomes before switching the bot off.
3. About 14% of requests are unroutable from the text. They need a triage desk or a better first question; the cut-off is in `model/config.json`.

**Honest hours spent.** **[YOUR NUMBER]**

**Your Public Google Drive Link** **[LINK to the screen recording, set to "anyone with the link can view"]**

**Github Repo Link** **[LINK, public]**
