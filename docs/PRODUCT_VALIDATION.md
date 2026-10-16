# ScopeGuard — customer validation and measurable impact

## One problem, one target user

**Target user:** a solo freelance website developer working on fixed-price small-business sites.

**Trigger:** the client asks for something not clearly documented in the original agreement.

**Problem in plain English:** both people remember a different promise. The freelancer needs to check the contract, avoid a surprise bill and ask the client for an explicit decision.

**Product promise:** a reviewed reply and proposal with the specific agreement wording attached; price set by the freelancer; customer choice recorded.

## Primary product metric

**Time to a correct, reviewed, usable reply** (seconds from receiving a new request until a freelancer accepts the reply after editing). Also track false positive extra-charge suggestions: **target zero** in the tested cases, not a universal safety guarantee.

## Pilot protocol (minimum 5 volunteers; 3 scenarios each)

1. Recruit freelance developers or small agency workers; note their actual role and ask consent. Don't upload real contracts to this MVP.
2. Use three synthetic scenarios: (A) extra Testimonials page, (B) included text typo correction, (C) ambiguous performance request.
3. Counterbalance order: half start manual, half start ScopeGuard. Use equivalent but independently worded contracts/requests to limit learning bias.
4. Manual: give same agreement and message; time until a usable client reply. ScopeGuard: time until reviewed usable reply. Stop and record times, not estimates.
5. Independently label each scenario against the contract. Record incorrect extra-charge suggestion count, usability of the final reply (1 or 0), and required edits.
6. One CSV row per participant/scenario pair using `evaluation/pilot_results_TEMPLATE.csv`. Copy to `evaluation/pilot_results.csv`. **Never populate with invented numbers.**
7. Run `python tools/impact_benchmark.py --input evaluation/pilot_results.csv`. A JSON summary appears in `evaluation/pilot_summary.json`. Share only aggregated data with user consent.

## Interview questions

- Tell me about the last time a customer asked for work beyond your written scope. What happened?
- Where do you look to confirm which work was promised?
- What part of preparing the reply feels uncomfortable or slow?
- What would make you distrust an AI classification?
- Would you pay for this workflow? What current tool or workaround would you replace? (Treat answers as stated preference, not confirmed purchases.)

## Published background evidence vs customer evidence

PMI's Pulse of the Profession 2024 reports a 30% average scope-creep rate for its 2023 project sample (the *project management* population, not freelancers). Source: https://www.pmi.org/-/media/pmi/documents/public/pdf/learning/thought-leadership/pmi-pulse-of-the-profession-2024-report.pdf

This demonstrates a wider project-management problem; it does not establish ScopeGuard's impact. Publish pilot results only after real tests.

## Economic model (explicitly hypothetical)

For one assumed out-of-scope request: 4 hours × INR 1,000/hour = INR 4,000 in *proposed* additional value. It is **not revenue recovered**; even an approved proposal does not guarantee payment. Do not extrapolate market size from this example.
