#!/bin/bash
set -e

echo "========================================="
echo "Course Companion FTE Deployment Status"
echo "========================================="
echo ""

SERVER_USER="n00bi2761@92.113.147.250"
FRONTEND_PORT=3225
BACKEND_PORT=3505

echo "🔍 1. Checking Backend Processes..."
ssh $SERVER_USER "ps aux | grep -E 'uvicorn|python.*main' | grep -v grep | wc -l" | xargs echo "   Backend processes running:"
echo ""

echo "🔍 2. Checking Frontend Processes..."
ssh $SERVER_USER "ps aux | grep next-server | grep -v grep | wc -l" | xargs echo "   Frontend processes running:"
echo ""

echo "🔍 3. Checking Port Bindings..."
ssh $SERVER_USER "netstat -tulpn | grep -E '$FRONTEND_PORT|$BACKEND_PORT' | grep LISTEN"
echo ""

echo "🔍 4. Testing Backend Health..."
curl -s --max-time 5 http://92.113.147.250:$BACKEND_PORT/health || echo "   ❌ Backend health check failed"
echo ""

echo "🔍 5. Testing Frontend..."
curl -I --max-time 5 http://92.113.147.250:$FRONTEND_PORT 2>&1 | head -3
echo ""

echo "🔍 6. Testing API Endpoint..."
curl -s --max-time 5 http://92.113.147.250:$BACKEND_PORT/api/v1/chapters | head -100 || echo "   ❌ API test failed"
echo ""

echo "🔍 7. Recent Backend Logs (last 10 lines)..."
ssh $SERVER_USER "tail -10 /tmp/backend.log 2>/dev/null || echo 'No backend logs available'"
echo ""

echo "========================================="
echo "✅ Deployment Verification Complete!"
echo "========================================="
echo ""
echo "Frontend URL: http://92.113.147.250:$FRONTEND_PORT"
echo "Backend URL:  http://92.113.147.250:$BACKEND_PORT"
echo "Health:       http://92.113.147.250:$BACKEND_PORT/health"
echo ""
