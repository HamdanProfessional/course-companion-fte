#!/bin/bash

# Deployment script for Adaptive Learning page
# Course Companion FTE - Production Deployment

set -e

SERVER_USER="root"
SERVER_IP="92.113.147.250"
FRONTEND_PORT="3225"
PROJECT_PATH="/root/CourseCompanionFTE/web-app"
LOCAL_FILE="web-app/src/app/adaptive-learning/page.tsx"
REMOTE_FILE="$PROJECT_PATH/src/app/adaptive-learning/page.tsx"

echo "========================================="
echo "Deploying Adaptive Learning Page"
echo "========================================="
echo "Server: $SERVER_IP:$FRONTEND_PORT"
echo ""

# Step 1: Copy the updated file to server
echo "Step 1: Copying updated page.tsx to server..."
scp "$LOCAL_FILE" "$SERVER_USER@$SERVER_IP:$REMOTE_FILE"
echo "File copied successfully!"
echo ""

# Step 2: Check if frontend is running
echo "Step 2: Checking frontend status..."
ssh "$SERVER_USER@$SERVER_IP" "ps aux | grep 'next-server' | grep -v grep || echo 'Frontend not running'"
echo ""

# Step 3: Restart the frontend service
echo "Step 3: Restarting frontend service..."
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
cd /root/CourseCompanionFTE/web-app

# Kill existing Next.js process
pkill -f 'next-server' || true

# Wait for process to terminate
sleep 2

# Start frontend in background with nohup
nohup npm start > /tmp/frontend.log 2>&1 &

# Wait for service to start
sleep 5

# Check if service is running
if ps aux | grep -v grep | grep 'next-server' > /dev/null; then
    echo "Frontend service restarted successfully!"
    echo "Process ID: $(ps aux | grep 'next-server' | grep -v grep | awk '{print $2}')"
else
    echo "ERROR: Frontend service failed to start!"
    echo "Checking logs..."
    tail -20 /tmp/frontend.log
    exit 1
fi
ENDSSH

echo ""

# Step 4: Health check
echo "Step 4: Running health checks..."
echo "Testing frontend endpoint..."
sleep 3

# Check if frontend is responding
if curl -f -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:$FRONTEND_PORT/ | grep -q "200\|302"; then
    echo "Frontend is responding: OK"
else
    echo "WARNING: Frontend not responding correctly"
fi

echo ""
echo "Testing adaptive learning page..."
ADAPTIVE_STATUS=$(curl -f -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:$FRONTEND_PORT/adaptive-learning || echo "000")

if [ "$ADAPTIVE_STATUS" = "200" ] || [ "$ADAPTIVE_STATUS" = "302" ]; then
    echo "Adaptive Learning page: OK (HTTP $ADAPTIVE_STATUS)"
else
    echo "WARNING: Adaptive Learning page returned HTTP $ADAPTIVE_STATUS"
fi

echo ""
echo "========================================="
echo "Deployment Summary"
echo "========================================="
echo "Updated File: $REMOTE_FILE"
echo "Frontend URL: http://$SERVER_IP:$FRONTEND_PORT"
echo "Adaptive Learning: http://$SERVER_IP:$FRONTEND_PORT/adaptive-learning"
echo ""
echo "Changes Deployed:"
echo "  - Replaced red/orange colors with nebula theme"
echo "  - Added framer-motion animations"
echo "  - Enhanced hover effects and transitions"
echo ""
echo "Next Steps:"
echo "  1. Visit http://$SERVER_IP:$FRONTEND_PORT/adaptive-learning"
echo "  2. Verify animations are working"
echo "  3. Test with different user tiers (FREE, PREMIUM, PRO)"
echo "========================================="
