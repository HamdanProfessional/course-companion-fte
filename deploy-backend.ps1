# =============================================================================
# Course Companion FTE - Backend Deployment Script (PowerShell)
# Deploys DeepSeek LLM provider support to production server
# =============================================================================

$ErrorActionPreference = "Stop"

$SERVER = "n00bi2761@92.113.147.250"
$SERVER_BACKEND_PATH = "/home/n00bi2761/course-companion/backend"
$PROJECT_ROOT = "C:\Users\User\Desktop\PIAIC_HACKATHON_1\Hackathon_4"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Course Companion FTE Backend Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Timestamp: $TIMESTAMP" -ForegroundColor Gray
Write-Host ""

# Check if we're in a git repository
Write-Host "[1/7] Verifying local git repository..." -ForegroundColor Yellow
Set-Location $PROJECT_ROOT
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a git repository" -ForegroundColor Red
    exit 1
}
Write-Host "Git repository verified" -ForegroundColor Green
Write-Host ""

# Check latest commit
Write-Host "[2/7] Checking latest commit..." -ForegroundColor Yellow
$LATEST_COMMIT = git log -1 --oneline
Write-Host "Latest commit: $LATEST_COMMIT" -ForegroundColor Gray
Write-Host ""

# Get changed files
Write-Host "[3/7] Preparing files for deployment..." -ForegroundColor Yellow
$CHANGED_FILES = git diff --name-only HEAD~1 HEAD | Where-Object { $_ -like 'backend/*' }

if (-not $CHANGED_FILES) {
    Write-Host "Checking for uncommitted changes..." -ForegroundColor Gray
    $UNCOMMITTED = git diff --name-only | Where-Object { $_ -like 'backend/*' }
    if ($UNCOMMITTED) {
        $CHANGED_FILES = $UNCOMMITTED
    }
}

if (-not $CHANGED_FILES) {
    Write-Host "No backend changes to deploy" -ForegroundColor Yellow
    # Still deploy the .env.example update
    $CHANGED_FILES = @("backend/.env.example")
}

Write-Host "Files to deploy:" -ForegroundColor Gray
$CHANGED_FILES | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
Write-Host ""

# Create deployment package
Write-Host "[4/7] Creating deployment package..." -ForegroundColor Yellow
$TEMP_DIR = "$env:TEMP\hackathon_deploy"
if (-not (Test-Path $TEMP_DIR)) {
    New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
}

$PACKAGE_FILE = "$TEMP_DIR\backend-deepseek-$TIMESTAMP.tar.gz"

# Create tar.gz with changed files
$FILES_TO_PACK = $CHANGED_FILES | ForEach-Object { $_.Replace('/', '\') }

# Using tar if available (Windows 10+), otherwise warn
if (Get-Command tar -ErrorAction SilentlyContinue) {
    Push-Location $PROJECT_ROOT
    $FILES_ARG = $FILES_TO_PACK -join ' '
    Invoke-Expression "tar -czf `"$PACKAGE_FILE`" $FILES_ARG backend/.env.example"
    Pop-Location
    Write-Host "Package created: $PACKAGE_FILE" -ForegroundColor Green
} else {
    Write-Host "ERROR: tar command not available. Please install Git Bash or use WSL." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Upload to server
Write-Host "[5/7] Uploading to server..." -ForegroundColor Yellow
$SCP_CMD = "scp `"$PACKAGE_FILE`" ${SERVER}:/tmp/"
Invoke-Expression $SCP_CMD
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to upload package to server" -ForegroundColor Red
    Write-Host "Make sure SSH is available and you have access to $SERVER" -ForegroundColor Red
    exit 1
}
Write-Host "Upload complete" -ForegroundColor Green
Write-Host ""

# Apply changes on server
Write-Host "[6/7] Applying changes on server..." -ForegroundColor Yellow
$SSH_APPLY = @"
cd $SERVER_BACKEND_PATH || exit 1

# Create backup
echo "Creating backup..."
BACKUP_DIR="/home/n00bi2761/course-companion/backups"
mkdir -p `"\`$BACKUP_DIR`"
BACKUP_FILE=`"\`$BACKUP_DIR/backend-pre-deepseek-$TIMESTAMP.tar.gz`"
tar -czf `"\`$BACKUP_FILE`" src/ .env.example 2>/dev/null || true
echo "Backup created"

# Extract new files
echo "Extracting deployment package..."
tar -xzf /tmp/backend-deepseek-$TIMESTAMP.tar.gz -C $SERVER_BACKEND_PATH
echo "Files extracted"

# Check .env for DeepSeek config
echo "Checking .env configuration..."
if grep -q "DEEPSEEK_API_KEY" .env 2>/dev/null; then
    echo "DeepSeek configuration already exists"
else
    echo ""
    echo "Adding DeepSeek configuration to .env..."
    cat >> .env << 'ENVEOF'

# DeepSeek Configuration (if LLM_PROVIDER=deepseek)
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
ENVEOF
    echo "DeepSeek configuration added"
fi
"@

ssh $SERVER $SSH_APPLY
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to apply changes on server" -ForegroundColor Red
    exit 1
}
Write-Host "Changes applied successfully" -ForegroundColor Green
Write-Host ""

# Restart backend service
Write-Host "[7/7] Restarting backend service..." -ForegroundColor Yellow
$SSH_RESTART = @"
cd $SERVER_BACKEND_PATH || exit 1

echo "Stopping current backend..."
pkill -f 'uvicorn.*3505' || true
sleep 2

# Force cleanup if needed
if netstat -tuln 2>/dev/null | grep -q ':3505 '; then
    echo "Cleaning up port 3505..."
    fuser -k 3505/tcp 2>/dev/null || true
    sleep 1
fi

echo "Starting backend service..."
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &
sleep 3

# Verify
if ps aux | grep -v grep | grep -q 'uvicorn.*3505'; then
    echo "Backend process is running"
else
    echo "ERROR: Backend process not found"
    tail -20 /tmp/backend.log
    exit 1
fi
"@

ssh $SERVER $SSH_RESTART
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Backend restart had issues" -ForegroundColor Yellow
    Write-Host "Check logs: ssh $SERVER 'tail -50 /tmp/backend.log'" -ForegroundColor Gray
} else {
    Write-Host "Backend service restarted successfully" -ForegroundColor Green
}
Write-Host ""

# Health checks
Write-Host "Running health checks..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $HEALTH = Invoke-WebRequest -Uri "http://92.113.147.250:3505/health" -TimeoutSec 5 -ErrorAction Stop
    if ($HEALTH.StatusCode -eq 200) {
        Write-Host "Backend health check: PASSED" -ForegroundColor Green
    }
} catch {
    Write-Host "Backend health check: FAILED" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Status: Deployed" -ForegroundColor Green
Write-Host "Timestamp: $TIMESTAMP" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Get DeepSeek API key from https://platform.deepseek.com/" -ForegroundColor White
Write-Host "2. SSH into server: ssh $SERVER" -ForegroundColor White
Write-Host "3. Edit .env: cd $SERVER_BACKEND_PATH && nano .env" -ForegroundColor White
Write-Host "4. Update DEEPSEEK_API_KEY with your key" -ForegroundColor White
Write-Host "5. Change LLM_PROVIDER to 'deepseek' to use DeepSeek" -ForegroundColor White
Write-Host "6. Restart backend: pkill -f 'uvicorn.*3505' &&" -ForegroundColor White
Write-Host "   nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &" -ForegroundColor White
Write-Host ""
Write-Host "Monitoring Commands:" -ForegroundColor Yellow
Write-Host "- View logs:      ssh $SERVER 'tail -f /tmp/backend.log'" -ForegroundColor Gray
Write-Host "- Check process:  ssh $SERVER 'ps aux | grep uvicorn'" -ForegroundColor Gray
Write-Host "- Health check:   curl http://92.113.147.250:3505/health" -ForegroundColor Gray
Write-Host ""
