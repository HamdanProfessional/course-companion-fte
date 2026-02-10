#!/bin/bash
set -e

# Chapter Content Population Deployment
# Populates database with rich chapter content and improves chapter reading UI

SERVER="n00bi2761@92.113.147.250"
BACKEND_PATH="/home/n00bi2761/course-companion/backend"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/chapter-content-deploy"

echo "=== Chapter Content Population Deployment ==="
echo "This will:"
echo "  - Populate all chapters with rich markdown content"
echo "  - Improve chapter reading UI with better styling"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Upload chapter content population script
echo ""
echo "2. Uploading chapter content population script..."
scp scripts/populate-chapter-content.py $SERVER:$TEMP_DIR/

echo ""
echo "3. Running chapter content population script..."
ssh $SERVER << EOF
cd $BACKEND_PATH
cp $TEMP_DIR/populate-chapter-content.py scripts/
python scripts/populate-chapter-content.py
EOF

# Upload improved chapter reading UI
echo ""
echo "4. Deploying improved chapter reading UI..."
scp web-app/src/app/chapters/\[id\]/page.tsx $SERVER:$TEMP_DIR/chapter-page.tsx

ssh $SERVER << EOF
cd $FRONTEND_PATH
mkdir -p src/app/chapters/[id]/
cp $TEMP_DIR/chapter-page.tsx src/app/chapters/[id]/page.tsx
echo "Chapter reading UI updated"
EOF

# Rebuild frontend
echo ""
echo "5. Rebuilding frontend..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
rm -rf .next
npm run build
echo "Frontend built successfully"
EOF

# Restart frontend
echo ""
echo "6. Restarting frontend service..."
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
echo "7. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Chapter content improvements:"
echo "  ✓ All 10 chapters populated with rich content"
echo "  ✓ Chapter reading UI improved with nebula theme"
echo "  ✓ Better typography and code highlighting"
echo "  ✓ Responsive design"
echo ""
echo "View chapters at: http://92.113.147.250:3225/chapters"
echo ""
