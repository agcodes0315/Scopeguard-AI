# GitHub PR and merge workflow — step by step

A PR = Pull Request: a reviewable proposal to merge code from a feature branch into `main`. **Do not create artificial/empty PRs or claim reviews you did not receive.** This downloadable ZIP is one integrated snapshot; PRs must represent *actual separate commits/work*.

## 0. Push the tested baseline (one time)
Open VS Code PowerShell IN THE NEW v2 extracted folder. Inspect `.gitignore` and `git status` first; do not upload private contract data or database files.

```powershell
git init
git add .
git status
git commit -m "feat: ScopeGuard v2 local-first workspace and AI safeguards"
git branch -M main
git remote add origin https://github.com/agcodes0315/Scopeguard-AI.git
git push -u origin main
```

**If repository already has commits on GitHub, DO NOT force push.** Safest path: clone existing GitHub repo into another directory, copy just the v2 source files into it (excluding `.git`, `.venv`, `.env`, `data/`, secrets), then commit and push as a feature branch before creating PR. `git remote add origin` fails when remote exists; use `git remote set-url origin <url>` only if necessary.

## 1. Recommended safer flow if GitHub already contains v1.2/v1.3

```powershell
cd C:\Users\Lenovo
git clone https://github.com/agcodes0315/Scopeguard-AI.git Scopeguard-AI-repo
cd Scopeguard-AI-repo
git switch -c feature/v2-local-workspace
```

Copy the downloaded v2 *source* files into this clone using File Explorer/VS Code, preserving `.git/`; overwrite existing application code only after backing up your previous local folder. **Never copy** `.venv`, `data`, `.env`, caches, or a nested `.git` directory. Then:

```powershell
python -m pytest -q
git add .
git diff --cached --stat
git commit -m "feat: agreement vault, scope inbox and response drafts"
git push -u origin feature/v2-local-workspace
```

Open `https://github.com/agcodes0315/Scopeguard-AI/pulls`, click **New pull request**, select `base: main` and `compare: feature/v2-local-workspace`. Review the diff, wait for Actions tests, then **Squash and merge**.

## 2. Later feature PRs (genuine future changes)

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/evidence-span-validation
# Implement code, tests and document results.
python -m pytest -q
git add .
git commit -m "fix: improve clause-span evidence verification"
git push -u origin feature/evidence-span-validation
```

Open a PR and merge only when its changes are tested. Repeat for future real integrations: `feature/sentry-traces`, `feature/secure-invitations`, `feature/render-demo`.

## 3. Resolve a merge conflict (if Git reports one)

```powershell
git status
# Open conflicted files, reconcile <<<<<<< and >>>>>>> markers manually.
# Keep intended code from both changes and remove markers.
python -m pytest -q
git add .
git commit
```

If this was a merge in progress, `git merge --abort` reverts the in-progress merge. Ask for review before changing financial/security logic.

## 4. CI and branch protection
`.github/workflows/tests.yml` runs automated tests on PR and main. After the first workflow run, configure GitHub Repository Settings -> Rules / Branches to require a PR and the test check before merging, if available on your repository plan.

## 5. Important category distinction
A PR and GitHub Actions **do not** automatically qualify for **Best Use of GitHub Copilot**. You must actually use and document the eligible Copilot coding agent, CLI, or app if claiming that partner prize.
