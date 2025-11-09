# Fetch and process Gmail messages
# Usage: .\fetch_emails.ps1

Write-Host "Fetching emails from Gmail..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/gmail/fetch/2" -Method POST
    $result = $response.Content | ConvertFrom-Json

    Write-Host "`nSuccess!" -ForegroundColor Green
    Write-Host "Fetched: $($result.fetched) messages" -ForegroundColor Yellow
    Write-Host "Processed: $($result.processed) new messages" -ForegroundColor Yellow

    if ($result.message_ids.Count -gt 0) {
        Write-Host "`nProcessed message IDs:" -ForegroundColor Cyan
        $result.message_ids | ForEach-Object { Write-Host "  - $_" }
    }

    Write-Host "`nCheck the orders at: http://localhost:5173" -ForegroundColor Magenta

} catch {
    Write-Host "`nError: $($_.Exception.Message)" -ForegroundColor Red
}

