# ============================================================================
# Laser OS - Windows Firewall Configuration Script
# ============================================================================
# This script creates a Windows Firewall rule to allow inbound connections
# on port 5000 for the Laser OS Flask application.
#
# IMPORTANT: This script must be run as Administrator
#
# Usage:
#   1. Open PowerShell as Administrator
#   2. Navigate to the project directory
#   3. Run: .\scripts\configure_firewall.ps1
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "LASER OS - WINDOWS FIREWALL CONFIGURATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "  2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "  3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Configuration
$ruleName = "Laser OS Flask Server (Port 5000)"
$port = 5000
$protocol = "TCP"

# Check if rule already exists
Write-Host "Checking for existing firewall rule..." -ForegroundColor Yellow
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "⚠ Firewall rule already exists!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you want to remove and recreate it? (Y/N): " -ForegroundColor Cyan -NoNewline
    $response = Read-Host
    
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "Removing existing rule..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName $ruleName
        Write-Host "✓ Existing rule removed" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "Keeping existing rule. Exiting..." -ForegroundColor Yellow
        exit 0
    }
}

# Create new firewall rule
Write-Host "Creating new firewall rule..." -ForegroundColor Yellow
Write-Host "  Rule Name: $ruleName" -ForegroundColor Gray
Write-Host "  Port: $port" -ForegroundColor Gray
Write-Host "  Protocol: $protocol" -ForegroundColor Gray
Write-Host "  Direction: Inbound" -ForegroundColor Gray
Write-Host "  Action: Allow" -ForegroundColor Gray
Write-Host "  Profile: Domain, Private" -ForegroundColor Gray
Write-Host ""

try {
    New-NetFirewallRule `
        -DisplayName $ruleName `
        -Direction Inbound `
        -Protocol $protocol `
        -LocalPort $port `
        -Action Allow `
        -Profile Domain,Private `
        -Description "Allows inbound connections to Laser OS Flask development server on port 5000 for local network access"
    
    Write-Host "✓ Firewall rule created successfully!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "✗ Failed to create firewall rule!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Verify the rule was created
Write-Host "Verifying firewall rule..." -ForegroundColor Yellow
$verifyRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($verifyRule) {
    Write-Host "✓ Firewall rule verified!" -ForegroundColor Green
    Write-Host ""
    
    # Display rule details
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "FIREWALL RULE DETAILS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "Display Name:  $($verifyRule.DisplayName)" -ForegroundColor White
    Write-Host "Enabled:       $($verifyRule.Enabled)" -ForegroundColor White
    Write-Host "Direction:     $($verifyRule.Direction)" -ForegroundColor White
    Write-Host "Action:        $($verifyRule.Action)" -ForegroundColor White
    Write-Host "Profile:       $($verifyRule.Profile)" -ForegroundColor White
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
} else {
    Write-Host "⚠ Warning: Could not verify firewall rule!" -ForegroundColor Yellow
    Write-Host ""
}

# Get local IP addresses
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "YOUR LOCAL NETWORK IP ADDRESSES" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" }

foreach ($ip in $ipAddresses) {
    $adapter = Get-NetAdapter -InterfaceIndex $ip.InterfaceIndex
    Write-Host "$($adapter.Name): $($ip.IPAddress)" -ForegroundColor White
}

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Display access instructions
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure your Flask server is running:" -ForegroundColor Yellow
Write-Host "   python run.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Share this URL with your colleagues:" -ForegroundColor Yellow

# Find the most likely Wi-Fi IP
$wifiIP = ($ipAddresses | Where-Object { 
    $adapter = Get-NetAdapter -InterfaceIndex $_.InterfaceIndex
    $adapter.Name -like "*Wi-Fi*" -or $adapter.Name -like "*Wireless*"
} | Select-Object -First 1).IPAddress

if ($wifiIP) {
    Write-Host "   http://$($wifiIP):5000" -ForegroundColor Green
} else {
    # Fallback to first non-loopback IP
    $firstIP = ($ipAddresses | Select-Object -First 1).IPAddress
    if ($firstIP) {
        Write-Host "   http://$($firstIP):5000" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "3. Test credentials:" -ForegroundColor Yellow
Write-Host "   Username: garason" -ForegroundColor Gray
Write-Host "   Password: test123" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "SECURITY NOTE:" -ForegroundColor Yellow
Write-Host "  - This firewall rule only allows connections from Domain and Private networks" -ForegroundColor Gray
Write-Host "  - Public networks are blocked for security" -ForegroundColor Gray
Write-Host "  - The Flask development server is NOT suitable for production use" -ForegroundColor Gray
Write-Host ""

