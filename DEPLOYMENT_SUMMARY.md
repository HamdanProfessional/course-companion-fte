# Backend Deployment Summary - DeepSeek LLM Provider Support

**Deployment Date:** 2026-02-14
**Server:** 92.113.147.250
**Backend Path:** /home/n00bi2761/course-companion/backend
**Status:** SUCCESS

---

## Changes Deployed

### Files Updated
1. `backend/src/api/v3/tutor/ai.py` - AI tutor endpoints with DeepSeek support
2. `backend/src/core/config.py` - DeepSeek configuration settings
3. `backend/src/core/llm.py` - DeepSeek LLM provider implementation
4. `backend/src/core/llm_v2.py` - DeepSeek LLM v2 provider implementation
5. `backend/.env.example` - Updated with DeepSeek configuration template

### Configuration Added to .env
```bash
# DeepSeek Configuration (if LLM_PROVIDER=deepseek)
# Get API key from: https://platform.deepseek.com/
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

---

## Deployment Verification

### Service Status
- **Backend Service:** Running (PID: 862213, 862571)
- **Port 3505:** Listening (0.0.0.0:3505)
- **Health Endpoint:** HTTP 200 OK
- **Uptime:** Since 2026-02-14 08:19 UTC

### Health Check Result
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-14T08:22:07.466777"
}
```

### Current Configuration
- **LLM Provider:** glm (Zhipu AI)
- **LLM Model:** glm-4.5-air
- **Phase 3 LLM Integration:** Enabled

### Backup Location
- **Backup File:** /home/n00bi2761/course-companion/backups/backend-pre-deepseek-*.tar.gz

---

## Next Steps - Enable DeepSeek Provider

To activate DeepSeek as the LLM provider:

### Step 1: Get DeepSeek API Key
1. Visit https://platform.deepseek.com/
2. Sign up for an account (free tier available)
3. Generate an API key

### Step 2: Update Production Configuration
```bash
# SSH into server
ssh n00bi2761@92.113.147.250

# Navigate to backend
cd /home/n00bi2761/course-companion/backend

# Edit .env file
nano .env

# Update these values:
# 1. Change LLM_PROVIDER from 'glm' to 'deepseek'
# 2. Replace DEEPSEEK_API_KEY with your actual API key

# Example:
# LLM_PROVIDER=deepseek
# DEEPSEEK_API_KEY=sk-1234567890abcdef
# DEEPSEEK_MODEL=deepseek-chat
# DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### Step 3: Restart Backend Service
```bash
# Stop current backend
pkill -f 'uvicorn.*3505'

# Start backend with new configuration
cd /home/n00bi2761/course-companion/backend
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &

# Verify
sleep 3
ps aux | grep uvicorn
curl http://92.113.147.250:3505/api/v3/tutor/ai/status
```

---

## Monitoring Commands

### View Backend Logs
```bash
ssh n00bi2761@92.113.147.250 'tail -f /tmp/backend.log'
```

### Check Process Status
```bash
ssh n00bi2761@92.113.147.250 'ps aux | grep uvicorn'
```

### Check Port Listening
```bash
ssh n00bi2761@92.113.147.250 'netstat -tuln | grep 3505'
```

### Health Check
```bash
curl http://92.113.147.250:3505/health
```

### AI Status Check
```bash
curl http://92.113.147.250:3505/api/v3/tutor/ai/status
```

---

## Rollback Procedure

If issues occur after switching to DeepSeek:

### Option 1: Switch Back to Previous Provider
```bash
ssh n00bi2761@92.113.147.250
cd /home/n00bi2761/course-companion/backend
nano .env
# Change LLM_PROVIDER back to 'glm' or 'openai'
pkill -f 'uvicorn.*3505'
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &
```

### Option 2: Restore from Backup
```bash
ssh n00bi2761@92.113.147.250
cd /home/n00bi2761/course-companion/backend
# Find latest backup
ls -lt /home/n00bi2761/course-companion/backups/
# Extract backup (replace with actual backup file)
tar -xzf /home/n00bi2761/course-companion/backups/backend-pre-deepseek-[TIMESTAMP].tar.gz
# Restart service
pkill -f 'uvicorn.*3505'
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &
```

---

## DeepSeek Information

### Pricing (as of 2026-02-14)
- **Free Tier:** Available for new users
- **deepseek-chat:** Competitive pricing vs OpenAI/Anthropic
- **deepseek-coder:** Optimized for code generation
- See https://platform.deepseek.com/ for current pricing

### Models Supported
- `deepseek-chat` - General purpose chat model (recommended)
- `deepseek-coder` - Code-specialized model
- `deepseek-reasoner` - Advanced reasoning model

### API Features
- OpenAI-compatible API
- Streaming support
- Function calling support
- Context window up to 128K tokens

---

## Troubleshooting

### Issue: Backend not responding
```bash
# Check if process is running
ssh n00bi2761@92.113.147.250 'ps aux | grep uvicorn'

# If not running, check logs
ssh n00bi2761@92.113.147.250 'tail -50 /tmp/backend.log'

# Restart service
cd /home/n00bi2761/course-companion/backend
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &
```

### Issue: DeepSeek API errors
```bash
# Verify API key is set correctly
ssh n00bi2761@92.113.147.250 'cd /home/n00bi2761/course-companion/backend && grep DEEPSEEK .env'

# Check API key format (should start with 'sk-')
# Verify account has credits at https://platform.deepseek.com/
```

### Issue: Port 3505 already in use
```bash
# Kill process using port
ssh n00bi2761@92.113.147.250 'fuser -k 3505/tcp'

# Restart backend
ssh n00bi2761@92.113.147.250 'cd /home/n00bi2761/course-companion/backend && nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &'
```

---

## Deployment Files Created

1. **deploy-backend.sh** - Bash deployment script (for Git Bash/WSL)
2. **deploy-backend.ps1** - PowerShell deployment script (for Windows)
3. **DEPLOYMENT_SUMMARY.md** - This document

---

## Contact & Support

For issues or questions:
- Check backend logs: `/tmp/backend.log`
- Review configuration: `/home/n00bi2761/course-companion/backend/.env`
- Test API endpoints: `http://92.113.147.250:3505/docs`

---

**Deployment completed successfully!** The backend is now ready to use DeepSeek as an LLM provider. Follow the "Next Steps" section to activate it.
