# TitanGuard AI - Deployment Guide

## Quick Reference

### Local Development
```bash
python app.py
# Visit http://localhost:10000
```

### Production with Custom Port
```bash
PORT=8000 python app.py
```

### With Gunicorn (Recommended for Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## Deployment Platforms

### Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.10.10" > runtime.txt

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create titanguard-ai
git push heroku main

# Set port (Heroku does this automatically)
# Your app will be at: https://titanguard-ai.herokuapp.com
```

### AWS (EC2)
```bash
# SSH into instance
ssh -i key.pem ec2-user@instance-ip

# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip -y
pip install -r requirements.txt

# Run with Gunicorn
nohup gunicorn -w 4 -b 0.0.0.0:8000 app:app > app.log 2>&1 &

# Access via: http://instance-ip:8000
```

### Docker
```bash
# Build image
docker build -t titanguard-ai .

# Run container
docker run -p 8000:8000 -e PORT=8000 titanguard-ai

# Run with volume mount (for production)
docker run -p 8000:8000 \
  -e PORT=8000 \
  -v $(pwd)/model:/app/model \
  titanguard-ai

# Docker Compose (optional)
docker-compose up -d
```

### Google Cloud Run
```bash
# Create Dockerfile (included)
# Deploy
gcloud run deploy titanguard-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Set port
gcloud run deploy titanguard-ai \
  --set-env-vars PORT=8080
```

### Azure App Service
```bash
# Create requirements.txt (done)
# Deploy via GitHub, Azure CLI, or web upload
# Set startup command: python -m gunicorn app:app
```

---

## Environment Setup

### Required Environment Variables
```bash
# Port (optional, defaults to 10000)
PORT=8000

# Flask settings (optional)
FLASK_ENV=production
FLASK_DEBUG=0
```

### Optional Enhancements
```bash
# For monitoring/logging
LOG_LEVEL=INFO
```

---

## Pre-Deployment Checklist

- [ ] Model file exists: `model/titanic_survival_model.pkl`
- [ ] Metadata file exists: `model/model_metadata.json`
- [ ] All dependencies in `requirements.txt`
- [ ] Test locally: `python app.py`
- [ ] Test metrics: Visit `http://localhost:10000/metrics`
- [ ] Test prediction: Submit form on main page
- [ ] Check logs: Look for any errors
- [ ] Set debug=False in production
- [ ] Configure PORT via environment variable

---

## Health Checks

### Simple Health Check
```bash
curl http://localhost:10000/
```

### Metrics Endpoint (JSON)
```bash
curl http://localhost:10000/api/metrics
```

### Expected Responses
```
GET / → 200 OK (HTML form)
POST / → 200 OK (HTML with prediction)
GET /metrics → 200 OK (HTML dashboard)
GET /api/metrics → 200 OK (JSON)
```

---

## Troubleshooting Deployment

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Model File Not Found
```bash
# Check file exists
ls -la model/titanic_survival_model.pkl

# Check working directory
pwd

# Ensure relative path is correct
```

### Metadata Missing
```bash
# Retrain model
jupyter notebook model/model_building.ipynb
# Run all cells to regenerate model_metadata.json
```

### Permission Denied
```bash
# Fix permissions
chmod +x app.py
chmod 755 model/
```

### Connection Refused
```bash
# Check if app is running
ps aux | grep python

# Check logs
tail -f app.log

# Restart application
```

---

## Monitoring in Production

### Log Rotation
```python
# Add to app.py for production logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('titanguard.log', 
                              maxBytes=10000000, 
                              backupCount=10)
app.logger.addHandler(handler)
```

### Performance Monitoring
```bash
# Check response times
time curl http://localhost:8000/

# Load testing with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/

# Monitor with htop
htop -p $(pgrep -f gunicorn)
```

### Metrics Tracking
```bash
# Monitor predictions
tail -f logs.txt | grep "Prediction made"

# Check error rates
tail -f logs.txt | grep "ERROR"
```

---

## Scaling Recommendations

### Single Server (current setup)
- Gunicorn with 4 workers
- ~1000-2000 predictions/minute
- ~50-100MB memory

### Multiple Servers
```bash
# Load balancer config (nginx example)
upstream titanguard {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://titanguard;
    }
}
```

### Containerized Scaling (Kubernetes)
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: titanguard-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: titanguard-ai
  template:
    metadata:
      labels:
        app: titanguard-ai
    spec:
      containers:
      - name: titanguard-ai
        image: titanguard-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
```

---

## Security Checklist

- [ ] Set `debug=False` in production
- [ ] Use HTTPS/SSL certificates
- [ ] Validate all inputs (done)
- [ ] Don't expose error details to users
- [ ] Use strong SECRET_KEY if adding sessions
- [ ] Run as non-root user
- [ ] Set proper file permissions
- [ ] Keep dependencies updated
- [ ] Use firewall rules
- [ ] Monitor for suspicious activity

---

## Backup & Recovery

### Backup Model Files
```bash
# Backup before deployment
cp model/titanic_survival_model.pkl model/backup/
cp model/model_metadata.json model/backup/

# Version control
git add model/
git commit -m "Backup production model"
git push
```

### Recovery Procedure
```bash
# If model corrupted
cp model/backup/titanic_survival_model.pkl model/
cp model/backup/model_metadata.json model/
# Restart application
```

---

## Rollback Procedure

### If Something Goes Wrong
```bash
# Stop current deployment
docker stop titanguard-ai

# Switch to previous version
git checkout previous-commit
docker build -t titanguard-ai:previous .
docker run -p 8000:8000 titanguard-ai:previous

# Or restore from backup
git reset --hard HEAD~1
python app.py
```

---

## Success Indicators

✓ Application starts without errors
✓ Prediction page loads
✓ Metrics dashboard displays correctly
✓ Predictions work with valid inputs
✓ Invalid inputs show error messages
✓ Logs show successful operations
✓ Memory usage is stable
✓ Response times are consistent

---

## Support & Debugging

### Enable Debug Mode (Development Only)
```python
app.run(debug=True)  # NOT FOR PRODUCTION
```

### Increase Logging Detail
```python
logging.basicConfig(level=logging.DEBUG)
```

### Test API Directly
```bash
curl -X POST http://localhost:8000/ \
  -d "pclass=1&sex=1&age=25&fare=100&embarked=0"

curl http://localhost:8000/api/metrics | jq
```

---

## Version History

- v2.0 (Production Ready) - Current
  - Singleton model pattern
  - Full metrics dashboard
  - Input validation
  - Drift prevention

- v1.0 (Initial Release)
  - Basic prediction
  - Simple UI

---

## Contact & Issues

For deployment issues:
1. Check logs: `tail -f app.log`
2. Verify model files exist
3. Test locally first
4. Review this guide
5. Check error messages carefully

---

**Last Updated**: January 20, 2026
**Status**: Production Ready ✅
