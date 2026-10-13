*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

## What I Built

**ScopeGuard AI: Protect the work. Recover the value.**

A freelancer agrees to a five-page website, two revisions and a fixed fee. The client requests two more pages and one more revision, but nobody makes the scope change explicit. This is a small, common source of conflict and unbilled effort.

ScopeGuard uses locally runnable Gemma to compare what was promised with what was newly requested. It surfaces potential changes and supporting excerpts, helps the freelancer attach human-approved prices, and gives the client a decision page.

## Demo

[Add a real demo video URL and screenshots; show analysis, estimate, approval and PDF.]

## Code

[Add your real GitHub repo URL.]

## How I Built It

The UI is served by FastAPI. The analysis endpoint passes agreement and requested-change text to Gemma 3 4B running through local Ollama, validates JSON and checks the model's quoted evidence against source text. When evidence does not verify, the result is flagged for review. Numeric pricing remains deterministic: a user enters hours and an hourly rate. SQLite records proposal and customer decisions; ReportLab exports the proposal as PDF. Pytest and GitHub Actions validate the core workflow.

## Why Does Open Innovation Matter?

The core reasoning can run on a freelancer's computer without uploading their complete contracts to a proprietary model provider. The model can be replaced or benchmarked while preserving business logic. That matters when privacy, predictable cost, and customization affect whether the product is commercially feasible.

[After testing, report your actual model latency, correctness metrics, and limitations. Never invent benchmarks.]

## My Agent Session

[Optional: add a genuine agent session link or remove.]

## My First User

[Insert actual consented user feedback, willingness to pay, and improvements made, or remove.]

## Prize Categories

- Best Use of Gemma — implemented through local Ollama inference.
- Best Use of Render — **only add after the app is actually deployed there**.
- Best Use of GitHub Copilot / Sentry — **only add if genuinely used according to the rules**.
