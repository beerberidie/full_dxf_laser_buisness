# Create ZIP archive of UI package
# PowerShell script to compress ui_package directory

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "laser_os_ui_package_$timestamp.zip"

Write-Host "=== Creating UI Package ZIP Archive ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Source Directory: ui_package/"
Write-Host "Destination: $zipName"
Write-Host ""

# Count files
Write-Host "Counting files..."
$fileCount = (Get-ChildItem -Path "ui_package" -Recurse -File | Measure-Object).Count
Write-Host "Files to archive: $fileCount"
Write-Host ""

# Create ZIP archive
Write-Host "Creating ZIP archive..."
Compress-Archive -Path "ui_package\*" -DestinationPath $zipName -CompressionLevel Optimal -Force
Write-Host "ZIP archive created successfully!" -ForegroundColor Green
Write-Host ""

# Get archive details
Write-Host "=== Archive Details ===" -ForegroundColor Cyan
$zipFile = Get-Item $zipName
$fileName = $zipFile.Name
$sizeInMB = [math]::Round($zipFile.Length / 1MB, 2)
$sizeInBytes = $zipFile.Length
$created = $zipFile.CreationTime
$location = $zipFile.FullName

Write-Host "File Name:" $fileName
Write-Host "File Size:" $sizeInMB "MB"
Write-Host "File Size (bytes):" $sizeInBytes
Write-Host "Created:" $created
Write-Host "Location:" $location
Write-Host ""

# Verify archive contents
Write-Host "Verifying archive contents..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipFile.FullName)
$entryCount = $zip.Entries.Count
$zip.Dispose()

Write-Host "Entries in ZIP: $entryCount"
Write-Host ""

if ($entryCount -eq $fileCount) {
    Write-Host "Verification PASSED: All files included!" -ForegroundColor Green
} else {
    Write-Host "Warning: File count mismatch" -ForegroundColor Yellow
    Write-Host "Expected:" $fileCount
    Write-Host "Found:" $entryCount
}

Write-Host ""
Write-Host "=== Archive Ready for Sharing! ===" -ForegroundColor Green
Write-Host ""
Write-Host "You can now share this ZIP file with the AI enhancement tool."
Write-Host ""

