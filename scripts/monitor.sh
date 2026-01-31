#!/bin/bash

# Course Companion FTE - Health Check & Monitoring Script
# Run this script periodically (cron job) to monitor system health

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="https://92.113.147.250"
WEB_APP_URL="https://web-app-ebon-mu.vercel.app"
ALERT_EMAIL="" # Add your email for alerts
LOG_FILE="/var/log/course-companion-health.log"

# Create log file if doesn't exist
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | sudo tee -a "$LOG_FILE"
}

# Function to send alert
send_alert() {
    local message="$1"
    log "⚠️  ALERT: $message"

    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "Course Companion Alert" "$ALERT_EMAIL"
    fi
}

# Health check counters
checks_passed=0
checks_failed=0

echo "========================================"
echo "Course Companion FTE - Health Check"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

# ========================================
# 1. Backend Health Check
# ========================================
echo -n "Backend Health... "

backend_health=$(curl -s -k -w "%{http_code}" -o /tmp/backend_health.json "$BACKEND_URL/health")

if [ "$backend_health" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (HTTP 200)"
    backend_status=$(cat /tmp/backend_health.json)
    backend_version=$(echo "$backend_status" | jq -r '.version')
    echo "  Version: $backend_version"
    ((checks_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (HTTP $backend_health)"
    send_alert "Backend health check failed (HTTP $backend_health)"
    ((checks_failed++))
fi

# ========================================
# 2. API Endpoints Check
# ========================================
echo -n "Chapters API... "

chapters_status=$(curl -s -k -w "%{http_code}" -o /tmp/chapters.json "$BACKEND_URL/api/v1/chapters")

if [ "$chapters_status" = "200" ]; then
    chapter_count=$(cat /tmp/chapters.json | jq '. | length')
    echo -e "${GREEN}✓ OK${NC} ($chapter_count chapters)"
    ((checks_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (HTTP $chapters_status)"
    send_alert "Chapters API check failed (HTTP $chapters_status)"
    ((checks_failed++))
fi

# ========================================
# 3. Database Connectivity
# ========================================
echo -n "Database Connection... "

# Check if backend can connect to database
db_status=$(curl -s -k "$BACKEND_URL/api/v1/chapters" | jq '. | length' 2>/dev/null)

if [ -n "$db_status" ] && [ "$db_status" -gt 0 ]; then
    echo -e "${GREEN}✓ OK${NC}"
    ((checks_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (Database unreachable)"
    send_alert "Database connection check failed"
    ((checks_failed++))
fi

# ========================================
# 4. Docker Container Status
# ========================================
echo -n "Docker Container... "

if docker ps | grep -q "course-backend"; then
    container_status=$(docker inspect course-backend | jq -r '.[0].State.Status')
    container_health=$(docker inspect course-backend | jq -r '.[0].State.Health.Status')

    if [ "$container_status" = "running" ]; then
        echo -e "${GREEN}✓ OK${NC} ($container_status, health: $container_health)"
        ((checks_passed++))
    else
        echo -e "${RED}✗ FAILED${NC} ($container_status)"
        send_alert "Docker container not running (status: $container_status)"
        ((checks_failed++))
    fi
else
    echo -e "${RED}✗ FAILED${NC} (Container not found)"
    send_alert "Docker container 'course-backend' not found"
    ((checks_failed++))
fi

# ========================================
# 5. Nginx Status
# ========================================
echo -n "Nginx Status... "

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ OK${NC} (running)"
    ((checks_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (not running)"
    send_alert "Nginx is not running"
    ((checks_failed++))
fi

# ========================================
# 6. Disk Space Check
# ========================================
echo -n "Disk Space... "

disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$disk_usage" -lt 80 ]; then
    echo -e "${GREEN}✓ OK${NC} (${disk_usage}% used)"
    ((checks_passed++))
elif [ "$disk_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} (${disk_usage}% used)"
    log "⚠️  Disk space warning: ${disk_usage}% used"
    ((checks_passed++))
else
    echo -e "${RED}✗ CRITICAL${NC} (${disk_usage}% used)"
    send_alert "Disk space critical: ${disk_usage}% used"
    ((checks_failed++))
fi

# ========================================
# 7. Memory Check
# ========================================
echo -n "Memory Usage... "

mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2*100}')

if [ "$mem_usage" -lt 80 ]; then
    echo -e "${GREEN}✓ OK${NC} (${mem_usage}% used)"
    ((checks_passed++))
elif [ "$mem_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} (${mem_usage}% used)"
    log "⚠️  Memory usage warning: ${mem_usage}% used"
    ((checks_passed++))
else
    echo -e "${RED}✗ CRITICAL${NC} (${mem_usage}% used)"
    send_alert "Memory usage critical: ${mem_usage}% used"
    ((checks_failed++))
fi

# ========================================
# 8. Web App Check (Vercel)
# ========================================
echo -n "Web App (Vercel)... "

web_app_status=$(curl -s -w "%{http_code}" -o /dev/null "$WEB_APP_URL")

if [ "$web_app_status" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (HTTP 200)"
    ((checks_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (HTTP $web_app_status)"
    send_alert "Web app check failed (HTTP $web_app_status)"
    ((checks_failed++))
fi

# ========================================
# 9. SSL Certificate Check
# ========================================
echo -n "SSL Certificate... "

cert_expiry=$(openssl x509 -in /etc/ssl/certs/backend-selfsigned.crt -noout -text | grep "Not After" | cut -d: -f2- | awk '{print $1, $2, $4}')

cert_expiry_date=$(date -d "$cert_expiry" +%s)
current_date=$(date +%s)
days_until_expiry=$(( ($cert_expiry_date - $current_date) / 86400 ))

if [ $days_until_expiry -gt 30 ]; then
    echo -e "${GREEN}✓ OK${NC} (expires in $days_until_expiry days)"
    ((checks_passed++))
elif [ $days_until_expiry -gt 7 ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} (expires in $days_until_expiry days)"
    log "⚠️  SSL certificate expires in $days_until_expiry days"
    ((checks_passed++))
else
    echo -e "${RED}✗ CRITICAL${NC} (expires in $days_until_expiry days)"
    send_alert "SSL certificate expires in $days_until_expiry days"
    ((checks_failed++))
fi

# ========================================
# 10. Phase 2 Status Check (Optional)
# ========================================
echo -n "Phase 2 Status... "

phase2_status=$(curl -s -k "$BACKEND_URL/api/v1/adaptive/status" | jq -r '.phase_2_enabled')

if [ "$phase2_status" = "true" ]; then
    llm_provider=$(curl -s -k "$BACKEND_URL/api/v1/adaptive/status" | jq -r '.llm_provider')
    echo -e "${GREEN}✓ ENABLED${NC} (provider: $llm_provider)"
    ((checks_passed++))
else
    echo -e "${YELLOW}⚠ DISABLED${NC}"
    ((checks_passed++))
fi

# ========================================
# Summary
# ========================================
echo ""
echo "========================================"
echo "Summary:"
echo -e "  ${GREEN}Passed: $checks_passed${NC}"
echo -e "  ${RED}Failed: $checks_failed${NC}"
echo "========================================"

if [ $checks_failed -eq 0 ]; then
    log "✅ All health checks passed"
    exit 0
else
    log "❌ $checks_failed health check(s) failed"
    exit 1
fi
