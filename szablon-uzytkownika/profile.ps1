# Profil PowerShell konta agenta (wzor z repo kuznia-kodu, szablon-uzytkownika/profile.ps1).
# Czerwony znak zachety [AGENT@MASZYNA]: test jako agent (instaluj\windows.ps1 -TestAgenta) wolno robic tylko
# w takim oknie. Test w oknie administratora daje falszywe DOSTEP.
function prompt {
    Write-Host ('[AGENT@' + $env:COMPUTERNAME + '] ') -NoNewline -ForegroundColor Red
    return ('PS ' + (Get-Location) + '> ')
}
Set-Location $HOME
