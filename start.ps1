$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv\Scripts\python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) { py -m venv .venv }
    else { python -m venv .venv }
}
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
# Choose first free port; never kill another service.
$port = $null
foreach ($candidate in @(8001, 8002, 8003, 8004, 8005)) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $candidate)
    try { $listener.Start(); $port = $candidate; break }
    catch [System.Net.Sockets.SocketException] { continue }
    finally { $listener.Stop() }
}
if ($null -eq $port) { throw 'Ports 8001-8005 are occupied. Close extra app terminals and retry.' }
Write-Host "ScopeGuard is starting at http://127.0.0.1:$port" -ForegroundColor Green
Write-Host 'Keep this terminal open. Ollama must also be running.'
& .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port $port
