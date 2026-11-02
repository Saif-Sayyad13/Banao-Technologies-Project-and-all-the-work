# 3-minute screen recording: talking points (no slides)

Keep it under 3:00. Say these in your own words. Screen: terminal + browser + `docs/EVIDENCE.md`.

**0:00 – 0:25  What I got and the first thing I checked.** Show `train.csv` and `resolution_log.csv`. "Ritu wants 90% match with the bot's labels. First I checked whether the labels are right: I compared them with the team that actually closed the request." Run the one-liner or show the 77.2% in `docs/EVIDENCE.md`.

**0:25 – 1:05  What I tried.** Show the experiments table. "A model trained on the bot labels scores 95% on her test but 75.6% on reality, worse than the bot. So I trained on where requests really ended up. Four model types all gave about 82.6 to 84.3%, so I picked the simple one that gives confidence and reasons."

**1:05 – 1:45  What I changed.** Show the confidence table. "About 14% of messages are things like 'please call me about my purifier'. Channel, warranty, product and time can't route them (17% vs 14% chance). So I changed the product: below 0.6 confidence it says 'ask the customer' instead of guessing. Above it, 94% right on 86% of requests."

**1:45 – 2:20  The product.** Open `localhost:8000`, click two examples: the "paid extra for installation" one (goes to Installs & Demo, not Billing) and "please call me about my purifier" (needs a human). Show `curl` to `/route` and that no API key is needed.

**2:20 – 2:45  What I threw away.** "Training on bot labels. An LLM, because Farhan doesn't want a per-request bill and vague messages have no signal anyway. The first reasons list that showed filler words. Resolution-time analysis, because Zoho times are in UTC and unconverted."

**2:45 – 3:00  What's wrong and what next.** "The 14% are still guesses in predictions.csv. Money numbers are estimates. Next step is 2 to 4 weeks in shadow mode before switching the bot off."
