#!/bin/bash
set -e

# =============================================================================
# Course Companion FTE - Backend Deployment Script
# Deploys DeepSeek LLM provider support to production server
# =============================================================================

SERVER="n00bi2761@92.113.147.250"
SERVER_BACKEND_PATH="/home/n00bi2761/course-companion/backend"
LOCAL_PROJECT_PATH="/c/Users/User/Desktop/PIAIC_HACKATHON_1/Hackathon_4"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "Course Companion FTE Backend Deployment"
echo "=========================================="
echo "Timestamp: $TIMESTAMP"
echo ""

# Step 1: Verify we're in the right directory
echo "[1/7] Verifying local git repository..."
cd "$LOCAL_PROJECT_PATH"
if [ ! -d ".git" ]; then
    echo "ERROR: Not in a git repository"
    exit 1
fi
echo "✓ Git repository verified"
echo ""

# Step 2: Check latest commit
echo "[2/7] Checking latest commit..."
LATEST_COMMIT=$(git log -1 --oneline)
echo "Latest commit: $LATEST_COMMIT"
echo ""

# Step 3: Create deployment package
echo "[3/7] Creating deployment package..."
PACKAGE_FILE="/tmp/backend-deepseek-$TIMESTAMP.tar.gz"

# Get list of changed files in latest commit
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD | grep '^backend/')

if [ -z "$CHANGED_FILES" ]; then
    echo "No backend changes detected in latest commit"
    echo "Checking for uncommitted changes..."
    UNCOMMITTED=$(git diff --name-only | grep '^backend/' || true)
    if [ -z "$UNCOMMITTED" ]; then
        echo "ERROR: No backend changes to deploy"
        exit 1
    fi
    CHANGED_FILES="$UNCOMMITTED"
fi

echo "Files to deploy:"
echo "$CHANGED_FILES"
echo ""

# Create tarball with changed files
echo "Creating deployment package..."
tar -czf "$PACKAGE_FILE" -C /c/Users/User/Desktop/PIAIC_HACKATHON_1/Hackathon_4 $CHANGED_FILES backend/.env.example
echo "✓ Package created: $PACKAGE_FILE"
echo ""

# Step 4: Upload to server
echo "[4/7] Uploading to server..."
scp "$PACKAGE_FILE" "$SERVER:/tmp/"
echo "✓ Upload complete"
echo ""

# Step 5: Extract and apply changes on server
echo "[5/7] Applying changes on server..."
ssh "$SERVER" << ENDSSH
set -e

cd "$SERVER_BACKEND_PATH"

# Create backup of current backend code
echo "Creating backup..."
BACKUP_DIR="/home/n00bi2761/course-companion/backups"
mkdir -p "\$BACKUP_DIR"
BACKUP_FILE="\$BACKUP_DIR/backend-pre-deepseek-$TIMESTAMP.tar.gz"
tar -czf "\$BACKUP_FILE" src/ .env.example 2>/dev/null || true
echo "✓ Backup created: \$BACKUP_FILE"

# Extract new files
echo "Extracting deployment package..."
tar -xzf "/tmp/backend-deepseek-$TIMESTAMP.tar.gz" -C "$SERVER_BACKEND_PATH"
echo "✓ Files extracted"

# Update .env if needed
echo "Checking .env configuration..."
if grep -q "DEEPSEEK_API_KEY" .env; then
    echo "✓ DeepSeek configuration already exists in .env"
else
    echo ""
    echo "⚠ WARNING: DeepSeek configuration not found in .env"
    echo "Adding DeepSeek configuration to .env..."
    cat >> .env << 'ENVEOF'

# DeepSeek Configuration (if LLM_PROVIDER=deepseek)
# Get API key from: https://platform.deepseek.com/
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
ENVEOF
    echo "✓ DeepSeek configuration added to .env"
    echo ""
    echo "IMPORTANT: You need to:"
    echo "1. Get a DeepSeek API key from https://platform.deepseek.com/"
    echo "2. Update DEEPSEEK_API_KEY in .env"
    echo "3. Change LLM_PROVIDER to 'deepseek' if you want to use it"
    echo ""
fi

ENDSSH
echo ""

# Step 6: Restart backend service
echo "[6/7] Restarting backend service..."
ssh "$SERVER" << ENDSSH
set -e

cd "$SERVER_BACKEND_PATH"

echo "Stopping current backend service..."
pkill -f 'uvicorn.*3505' || true
sleep 2

# Check if any process is still using port 3505
if netstat -tuln 2>/dev/null | grep -q ':3505 '; then
    echo "WARNING: Port 3505 still in use, forcing cleanup..."
    fuser -k 3505/tcp 2>/dev/null || true
    sleep 1
fi

echo "Starting backend service..."
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &
echo "✓ Backend service started"
sleep 3

# Verify service is running
if ps aux | grep -v grep | grep -q 'uvicorn.*3505'; then
    echo "✓ Backend process is running"
else
    echo "✗ ERROR: Backend process not found"
    tail -20 /tmp/backend.log
    exit 1
fi

ENDSSH
echo ""

# Step 7: Health check
echo "[7/7] Running health checks..."
sleep 3

# Check backend health endpoint
if curl -sf http://92.113.147.250:3505/health > /dev/null 2>&1; then
    echo "✓ Backend health check passed"
else
    echo "⚠ WARNING: Backend health check failed"
    echo "Checking if service is responding..."
    curl -v http://92.113.147.250:3505/health 2>&1 | head -20
fi

# Check if backend is listening on port 3505
if ssh "$SERVER" "netstat -tuln 2>/dev/null | grep -q ':3505 '"; then
    echo "✓ Backend is listening on port 3505"
else
    echo "⚠ WARNING: Backend not detected on port 3505"
fi

echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo "Status: Deployed"
echo "Timestamp: $TIMESTAMP"
echo "Changes:"
echo "$CHANGED_FILES"
echo ""
echo "Next Steps:"
echo "1. Get DeepSeek API key from https://platform.deepseek.com/"
echo "2. SSH into server: ssh $SERVER"
echo "3. Edit .env: cd $SERVER_BACKEND_PATH && nano .env"
echo "4. Update DEEPSEEK_API_KEY with your key"
echo "5. Optionally change LLM_PROVIDER to 'deepseek'"
echo "6. Restart backend: pkill -f 'uvicorn.*3505' && nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &"
echo ""
echo "Monitoring Commands:"
echo "- View logs: ssh $SERVER 'tail -f /tmp/backend.log'"
echo "- Check process: ssh $SERVER 'ps aux | grep uvicorn'"
echo "- Health check: curl http://92.113.147.250:3505/health"
echo ""
