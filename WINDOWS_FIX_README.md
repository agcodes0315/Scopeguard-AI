# ScopeGuard AI v1.2.1 — Windows test and evidence fix

This clean project archive fixes: SQLite schema initialization on new Windows temp databases and topic-specific agreement evidence lookup (a generic "page" must not override the more relevant contact/color/text clauses).

## Upgrade without losing data
1. Do not overwrite an existing running project. Extract this archive to **C:\Users\Lenovo\ScopeGuard-AI-v1.2.1** or another new folder.
2. The archive contains no customer database and no `.venv`. Keep the old project as a backup.
3. In VS Code open the *extracted* `ScopeGuard-AI-v1.2.1` folder. The terminal path must end with that folder, **not** `scopeguard-ai`.
4. Run `powershell -ExecutionPolicy Bypass -File .\start.ps1` in one terminal and keep it running. Ollama is required for real analysis.
5. Open a new terminal and run `.\.venv\Scripts\python.exe -m pytest -q`.
6. For in-scope demo, use the agreement and request provided in the earlier conversation; expect included findings and no add-on proposal.

**Never send real client documents through this prototype.** It has token-based customer links but no account authentication or production-grade privacy protections.

### Diagnosing mixed project versions
Run `Get-Location` and `Get-Content .\backend\workflow.py | Select-String 'Commit schema immediately'`. If the phrase is missing, you're testing an older/mixed project copy.
