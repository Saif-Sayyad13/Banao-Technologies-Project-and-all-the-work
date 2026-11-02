**To:** Ritu Deshpande, Head of D2C Operations, Kestrel Home

**From:** Saif Sayyad  |  **Date:** 2 November 2026

**Subject:** Replacing the routing bot – yes, but not against the 90% test

## The decision
Yes, you can switch the bot off. But not by copying its labels. Those labels match where requests actually ended up only **77%** of the time. About 1 request in 4 goes to the wrong team first, and that has not improved in any quarter. A system trained to copy the labels can score 95% on "match the labels" and still repeat the same mistakes. So I built the replacement to predict where a request really ends up (the team that closes it), and measured it on that.

## The number
On 6,500 past requests it had not seen (tested forward in time, quarter by quarter), the new router picks the right team **84% of the time, against 77% for the bot**. When it is confident (86% of requests) it is right **94%** of the time. The remaining 14% are messages like "please call me about my purifier". Nobody, human or software, can tell where those go without asking; our best guess is right about 1 time in 5. For these the tool says "ask the customer" and sends them to a small triage desk (about 100 a month) instead of guessing.

## The rupees (yearly, from your own 15 months of data)
| | Wrong-team cost | Licence | Total | Saving vs today |
|---|---|---|---|---|
| Today (bot) | Rs 13.8 lakh | Rs 3.2 lakh | **Rs 17.0 lakh** | – |
| New router, routes everything | Rs 9.8 lakh | – | **Rs 9.8 lakh** | **Rs 7.3 lakh** |
| New router + triage desk | Rs 3.0 lakh + Rs 3.2 lakh desk | – | **Rs 6.2 lakh** | **Rs 10.8 lakh** |

Each wrong-team request costs about Rs 700 (1.4 transfers at Rs 305, plus Rs 260 for the extra customer contact). The triage row assumes a call-back costs Rs 260; it still wins as long as one costs under about Rs 540. **For Farhan:** there is no per-request charge, because it uses no paid AI service. The only running cost is hosting a small server. I estimate a couple of thousand rupees a month but have not priced it, so please get a quote from Tanmay before switching. These are estimates, not guarantees.

## What to do next week
1. **Run it in shadow mode for 2 to 4 weeks.** It suggests a team for every request while the bot keeps routing. Switch the bot off only if the 84% and 94% hold on live requests.
2. **Ask Meenal to set up a triage desk** of one or two people for the roughly 100 vague requests a month.
3. **Change the first question** in IVR, chat and WhatsApp to "what is wrong, in one line?". I expect this to shrink the vague pile, but I have not tested it.
4. **Plan headcount on where requests really end up**, not on the bot's labels: Repairs 23%, Installs & Demo 15%, Returns & Replacement 14%, Product Advice 13%, Warranty Claims 13%, Billing 12%, Filters & Consumables 10%. The bot over-sends to Repairs, Billing and Filters.
