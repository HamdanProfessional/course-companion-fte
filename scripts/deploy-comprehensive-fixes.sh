#!/bin/bash
set -e

# Comprehensive Fixes Deployment
# - Remove emojis from achievements
# - Combine subscription into profile page
# - Enable Phase 2 LLM (fix 503 error)
# - Deploy chapter content and improved UI

SERVER="n00bi2761@92.113.147.250"
BACKEND_PATH="/home/n00bi2761/course-companion/backend"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/comprehensive-fixes-$(date +%s)"

echo "=== Comprehensive Fixes Deployment ==="
echo ""
echo "This will deploy:"
echo "  1. Backend: Achievement icons (text instead of emojis)"
echo "  2. Backend: Enable Phase 2 LLM (fix 503 error)"
echo "  3. Frontend: Progress page with proper icons"
echo "  4. Frontend: Profile page with subscription management"
echo "  5. Frontend: Improved chapter reading UI"
echo "  6. Database: Populate chapter content"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR/{backend,frontend,scripts}"

# Deploy backend fixes
echo ""
echo "2. Deploying backend fixes..."

# Upload progress.py with text icons
scp backend/src/api/v3/tutor/progress.py $SERVER:$TEMP_DIR/backend/progress.py
ssh $SERVER << EOF
cd $BACKEND_PATH
cp $TEMP_DIR/backend/progress.py src/api/v3/tutor/progress.py
echo "Backend progress.py updated (achievement icons fixed)"
EOF

# Enable Phase 2 LLM in backend .env
echo ""
echo "3. Enabling Phase 2 LLM in backend..."
ssh $SERVER << 'EOF'
cd $BACKEND_PATH
# Enable Phase 2 LLM
if grep -q "ENABLE_PHASE_2_LLM=" .env 2>/dev/null; then
    sed -i 's/ENABLE_PHASE_2_LLM=.*/ENABLE_PHASE_2_LLM=True/' .env
else
    echo "ENABLE_PHASE_2_LLM=True" >> .env
fi
echo "Phase 2 LLM enabled"
EOF

# Deploy frontend fixes
echo ""
echo "4. Deploying frontend fixes..."

# Upload progress page
scp web-app/src/app/progress/page.tsx $SERVER:$TEMP_DIR/frontend/progress-page.tsx
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/frontend/progress-page.tsx src/app/progress/page.tsx
echo "Progress page updated (proper icons)"
EOF

# Upload profile page
scp web-app/src/app/profile/page.tsx $SERVER:$TEMP_DIR/frontend/profile-page.tsx
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/frontend/profile-page.tsx src/app/profile/page.tsx
echo "Profile page updated (with subscription)"
EOF

# Upload chapter page
scp web-app/src/app/chapters/\[id\]/page.tsx $SERVER:$TEMP_DIR/frontend/chapter-page.tsx
ssh $SERVER << EOF
cd $FRONTEND_PATH
mkdir -p src/app/chapters/[id]/
cp $TEMP_DIR/frontend/chapter-page.tsx src/app/chapters/[id]/page.tsx
echo "Chapter reading UI updated (improved)"
EOF

# Deploy chapter content script
echo ""
echo "5. Deploying chapter content population script..."
scp scripts/populate-chapter-content.py $SERVER:$TEMP_DIR/scripts/
ssh $SERVER << 'EOF'
cd $BACKEND_PATH
cp $TEMP_DIR/scripts/populate-chapter-content.py scripts/
chmod +x scripts/populate-chapter-content.py
echo "Chapter content script deployed"
EOF

# Run chapter content population
echo ""
echo "6. Populating chapter content..."
ssh $SERVER << 'EOF'
cd $BACKEND_PATH
source venv/bin/activate
python scripts/populate-chapter-content.py
EOF

# Restart backend
echo ""
echo "7. Restarting backend service..."
ssh $SERVER << EOF
cd $BACKEND_PATH
pm2 restart course-companion-backend || true
sleep 3
pm2 status course-companion-backend
echo "Backend restarted"
EOF

# Rebuild frontend
echo ""
echo "8. Rebuilding frontend..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
rm -rf .next
npm run build
echo "Frontend built successfully"
EOF

# Restart frontend
echo ""
echo "9. Restarting frontend service..."
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
echo "10. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Deployed fixes:"
echo "  ✓ Achievement icons now use text instead of emojis"
echo "  ✓ Phase 2 LLM enabled (fixes 503 error)"
echo "  ✓ Progress page with proper Lucide icons"
echo "  ✓ Profile page with subscription management"
echo "  ✓ Chapter reading UI improved with nebula theme"
echo "  ✓ All 10 chapters populated with rich content"
echo ""
echo "Test at:"
echo "  - http://92.113.147.250:3225/progress"
echo "  - http://92.113.147.250:3225/profile"
echo "  - http://92.113.147.250:3225/chapters"
echo "  - API: http://92.113.147.250:3505/api/v3/tutor/ai/adaptive/recommendations?user_id=<id>"
echo ""
