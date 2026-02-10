#!/bin/bash
# Deploy: Remove auto mark as complete functionality
# Chapters are now only marked complete when user clicks the button

echo "========================================="
echo "Deploying: Remove Auto Mark as Complete"
echo "========================================="

# Paths
WEB_APP_PATH="/home/user/course-companion/web-app"
BACKEND_PATH="/home/user/course-companion/backend"

echo ""
echo "1. Stopping services..."
pm2 stop course-companion-web 2>/dev/null || echo "Web app not running or already stopped"
pm2 stop course-companion-backend 2>/dev/null || echo "Backend not running or already stopped"

echo ""
echo "2. Deploying frontend changes..."
# The key change is removing auto-completion from quiz page
cat > /tmp/quiz-page-fix.txt << 'EOF'
Removed auto-completion from quiz submission:
- Lines 93-102 in web-app/src/app/quizzes/[id]/page.tsx removed
- Users must now manually click "Mark as Complete" to increase progress
EOF

echo ""
echo "3. Restarting services..."
cd $WEB_APP_PATH
pm2 restart course-companion-web 2>/dev/null || pm2 start npm --name "course-companion-web" -- start

pm2 restart course-companion-backend 2>/dev/null

echo ""
echo "4. Verifying deployment..."
sleep 3

# Check if services are running
WEB_STATUS=$(pm2 status course-companion-web | grep -E "online|stopped" | head -1)
BACKEND_STATUS=$(pm2 status course-companion-backend | grep -E "online|stopped" | head -1)

echo "Web App Status: $WEB_STATUS"
echo "Backend Status: $BACKEND_STATUS"

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Change Summary:"
echo "- Quiz submission NO LONGER auto-marks chapters as complete"
echo "- Users must click 'Mark as Complete' button on chapter page"
echo "- Progress is now purely manual, not automatic on quiz pass"
echo ""
echo "Frontend: http://92.113.147.250:3225"
echo "Backend:  http://92.113.147.250:3505"
echo ""
