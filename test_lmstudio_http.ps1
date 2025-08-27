Write-Host "Testing LM Studio connection..."

$url = "http://localhost:1234/v1/models"

# Try to connect to LM Studio
try {
    $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
    
    Write-Host "✅ Successfully connected to LM Studio!" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response:"
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} 
catch [System.Net.WebException] {
    Write-Host "❌ Could not connect to LM Studio. Please ensure:" -ForegroundColor Red
    Write-Host "1. LM Studio is running"
    Write-Host "2. The local server is enabled in LM Studio"
    Write-Host "3. The server is configured to listen on http://localhost:1234"
    Write-Host ""
    Write-Host "To enable the server in LM Studio:"
    Write-Host "1. Go to the 'Local Server' tab"
    Write-Host "2. Make sure 'Server' is toggled ON"
    Write-Host "3. Verify the URL matches: http://localhost:1234"
}
catch {
    Write-Host "❌ An error occurred: $_" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
