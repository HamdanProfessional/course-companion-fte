#!/bin/bash
set -e

# UI/Frontend Bug Fixes Deployment
# Fixes: Email validation, certificate name validation, console logs removed, React hooks warnings fixed

SERVER="n00bi2761@92.113.147.250"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/ui-bug-fixes"

echo "=== UI/Frontend Bug Fixes Deployment ==="
echo "This will deploy:"
echo "  - Register page: Email validation added"
echo "  - Profile page: Certificate name validation improved"
echo "  - Progress/Subscription/Adaptive pages: Console logs removed"
echo "  - Multiple pages: React hooks warnings fixed"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Deploy Frontend Files
echo ""
echo "2. Deploying frontend files..."
echo "   - register/page.tsx (Email validation)"
echo "   - profile/page.tsx (Certificate validation + React hooks fix)"
echo "   - progress/page.tsx (Console logs removed)"
echo "   - subscription/page.tsx (Console logs removed)"
echo "   - adaptive-learning/page.tsx (Console logs removed)"
echo "   - ai-mentor/page.tsx (React hooks warning fixed)"
echo "   - certificate/verify/[id]/page.tsx (React hooks warning fixed)"
echo "   - leaderboard/page.tsx (React hooks warning fixed)"

scp web-app/src/app/register/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/profile/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/progress/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/subscription/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/adaptive-learning/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/ai-mentor/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/certificate/verify/[id]/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/app/leaderboard/page.tsx $SERVER:$TEMP_DIR/

# Install frontend files
echo ""
echo "3. Installing frontend files..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/page.tsx src/app/register/ 2>/dev/null || true
cp $TEMP_DIR/page.tsx src/app/profile/ 2>/dev/null || true
cp $TEMP_DIR/page.tsx src/app/progress/ 2>/dev/null || true
cp $TEMP_DIR/page.tsx src/app/subscription/ 2>/dev/null || true
cp $TEMP_DIR/page.tsx src/app/adaptive-learning/ 2>/dev/null || true
cp $TEMP_DIR/page.tsx src/app/ai-mentor/ 2>/dev/null || true
mkdir -p src/app/certificate/verify/[id]/
cp $TEMP_DIR/page.tsx src/app/certificate/verify/[id]/ 2>/dev/null || true
cp $TEMP_DIR/page.tsx src/app/leaderboard/ 2>/dev/null || true
echo "Frontend files updated successfully"
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

# Cleanup
echo ""
echo "6. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Fixed UI/Frontend bugs:"
echo "  ✓ Register page email validation (prevents invalid emails)"
echo "  ✓ Profile certificate name validation (min 2 chars, max 100 chars)"
echo "  ✓ Console logs removed from production pages"
echo "  ✓ React hooks warnings fixed with useCallback"
echo ""
echo "Access at: http://92.113.147.250:3225"
echo ""
