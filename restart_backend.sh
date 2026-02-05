#!/bin/bash
# Auto-generated SSH script for backend restart

sshpass -p "2763" ssh -o StrictHostKeyChecking=no n00bi2761@92.113.147.250 << 'ENDSSH'
cd ~/course-companion-fte
echo "Pulling latest code..."
git pull origin master

echo "Installing dependencies..."
pip install bcrypt==4.2.0

echo "Running migration..."
python scripts/migrate_add_role.py

echo "Restarting backend server..."
pkill -f uvicorn
sleep 2
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 3505 > backend.log 2>&1 &

echo "Backend restarted successfully!"
sleep 3
ps aux | grep uvicorn | grep -v grep
ENDSSH
