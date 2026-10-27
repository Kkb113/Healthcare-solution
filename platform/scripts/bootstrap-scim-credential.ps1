# One-time encrypted bridge: browser-visible credential -> CLI stdin -> Key Vault.
# No credential arguments, files, environment variables, transcript or stdout.
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$rsa = [System.Security.Cryptography.RSA]::Create(2048)
try {
    # Only a public key and encrypted ciphertext may cross tool outputs.
    Write-Output (@{ publicKeySpkiBase64 = [Convert]::ToBase64String($rsa.ExportSubjectPublicKeyInfo()) } | ConvertTo-Json -Compress)
    $encrypted = [Console]::ReadLine()
    if (-not $encrypted -or $encrypted.Length -gt 1024) { throw 'Invalid encrypted message size' }
    $payload = [Text.Encoding]::UTF8.GetString($rsa.Decrypt([Convert]::FromBase64String($encrypted), [System.Security.Cryptography.RSAEncryptionPadding]::OaepSHA256))
    if (-not $payload -or $payload.Length -gt 1024) { throw 'Invalid credential message size' }
    $start = [System.Diagnostics.ProcessStartInfo]::new()
    $start.FileName = Join-Path $taskRoot 'platform/.venv/Scripts/python.exe'
    $start.ArgumentList.Add('-B')
    $start.ArgumentList.Add((Join-Path $taskRoot 'platform/scripts/configure_foundation_identity.py'))
    $start.ArgumentList.Add('bootstrap-token')
    $start.WorkingDirectory = $taskRoot
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $child = [System.Diagnostics.Process]::Start($start)
    $child.StandardInput.WriteLine($payload)
    $child.StandardInput.Close()
    $payload = $null
    $safeOutput = $child.StandardOutput.ReadToEnd()
    $diagnostic = $child.StandardError.ReadToEnd()
    $child.WaitForExit()
    if ($child.ExitCode -ne 0) { throw ('Credential bootstrap failed: ' + ($diagnostic -replace 'dsapi[A-Za-z0-9]+', '[REDACTED_TOKEN]')) }
    Write-Output $safeOutput
} finally {
    $rsa.Dispose()
}
