#!/bin/bash
set -e

# Adaptive Learning Page Fix - Replace stub data with real backend API calls
# Fixes: Knowledge gap analysis and recommendations now fetch from backend

SERVER="n00bi2761@92.113.147.250"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/adaptive-learning-fix"

echo "=== Adaptive Learning Page - Remove Placeholder Data ==="
echo "This will deploy:"
echo "  - Frontend: api-v3.ts - Updated to call real backend endpoints"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Deploy Frontend Files
echo ""
echo "2. Deploying frontend files..."
echo "   - lib/api-v3.ts (getKnowledgeAnalysis, getRecommendations, getAIStatus now use backend)"

# Copy frontend files
scp web-app/src/lib/api-v3.ts $SERVER:$TEMP_DIR/

# Install frontend files
echo ""
echo "3. Installing frontend files..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/api-v3.ts src/lib/
echo "Frontend api-v3.ts updated successfully"
EOF

# Rebuild frontend
echo ""
echo "4. Rebuilding frontend..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
rm -rf .next
npm run build
echo "Frontend built successfully"
EOF

# Restart frontend
echo ""
echo "5. Restarting frontend service..."
ssh $SERVER << EOF
pkill -f 'next-server' || true
cd $FRONTEND_PATH
NODE_OPTIONS="--max-old-space-size=384" nohup npm start > /tmp/frontend.log 2>&1 &
sleep 5
ps aux | grep next-server | grep -v grep
echo "Frontend restarted successfully"
EOF

# Verify deployment
echo ""
echo "6. Verifying deployment..."
echo "   Testing AI status endpoint..."
ssh $SERVER << EOF
echo "GET /api/v3/tutor/ai/status/:"
curl -s -o /dev/null -w "  HTTP %{http_code}\n" "http://localhost:3505/api/v3/tutor/ai/status/"
EOF

# Cleanup
echo ""
echo "7. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Fixed adaptive learning endpoints:"
echo "  - GET /api/v3/tutor/ai/status/ (AI features status)"
echo "  - GET /api/v3/tutor/ai/adaptive/analysis/?user_id={id} (Knowledge gap analysis)"
echo "  - GET /api/v3/tutor/ai/adaptive/recommendations/?user_id={id} (Chapter recommendations)"
echo ""
echo "The page now fetches real data from the backend instead of stub data."
echo ""
echo "Access at: http://92.113.147.250:3225/adaptive-learning"
echo ""
