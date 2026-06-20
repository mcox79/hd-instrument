# Per-session Claude Code launcher with CLAUDE_SESSION_NAME env-var set for the new process.
# Each VS Code window launched via this gets the correct session-name for the Phase 1 hardening hooks.
#
# Usage:
#   pwsh -File tools\launch_claude_session.ps1 testbed
#   pwsh -File tools\launch_claude_session.ps1 research
#   pwsh -File tools\launch_claude_session.ps1 exp_dev
#   pwsh -File tools\launch_claude_session.ps1 orchestrator
#   pwsh -File tools\launch_claude_session.ps1 skunkworks
#
# Effect: opens VS Code at the hd-instrument project root with CLAUDE_SESSION_NAME set in the
# spawned process environment. The Claude Code extension inherits the env var. Stop hook +
# StopFailure hook then activate for the named session.
#
# To reload a currently-running VS Code window with the env var:
#   1. Close that VS Code window
#   2. Launch from here with the session name
# Or:
#   1. Set the env var temporarily in a parent shell, launch VS Code, then "Developer: Reload Window"
#      doesn't help if the parent shell didn't have the env -- the inherited env is from VS Code's
#      original launch. So a fresh VS Code launch via this script is the reliable path.
#
# Coexistence: doesn't touch the hooks themselves; doesn't modify any other process.
# Reversible: launching without this script (just `code D:\AI\hd-instrument`) -> no env var ->
#             hook is no-op = original behavior.

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('testbed','research','exp_dev','orchestrator','skunkworks')]
    [string]$Session
)

$projectRoot = 'D:\AI\hd-instrument'
$env:CLAUDE_SESSION_NAME = $Session

Write-Output ('Launching VS Code for session: ' + $Session)
Write-Output ('CLAUDE_SESSION_NAME=' + $env:CLAUDE_SESSION_NAME)
Write-Output ('Project: ' + $projectRoot)
Write-Output 'The Claude Code extension in this VS Code window will inherit the env var.'
Write-Output ''

# Launch VS Code with the project; -n forces a new window so it doesn't reuse an existing one
$codePath = 'code'
& $codePath -n $projectRoot
