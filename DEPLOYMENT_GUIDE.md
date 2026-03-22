# Speech Emotion Recognition System - Complete Setup & Deployment Guide

## 📋 Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Backend Configuration](#backend-configuration)
3. [Frontend Setup](#frontend-setup)
4. [Training the Model](#training-the-model)
5. [Deployment to Vercel](#deployment-to-vercel)
6. [Deployment to Netlify](#deployment-to-netlify)
7. [AWS Deployment Guide](#aws-deployment-guide)
8. [Docker Deployment](#docker-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.13.12 (64-bit Windows)
- Node.js 18+ and npm
- Git
- CUDA 12+ (optional, for GPU acceleration)
- FFmpeg (for audio processing)

### Step 1: Install FFmpeg (Windows)
```bash
# Option 1: Using Chocolatey
choco install ffmpeg

# Option 2: Download from https://ffmpeg.org/download.html
# Add to PATH: C:\ffmpeg\bin
```

### Step 2: Clone/Setup Project
```bash
# Create project directory
mkdir emotion-recognition-system
cd emotion-recognition-system

# Clone from repository (if applicable)
git clone <repository-url>

# Or organize folders
mkdir backend frontend docs models
```

### Step 3: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import tensorflow; import librosa; import flask; print('All packages installed!')"
```

### Step 4: Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install Node dependencies
npm install

# Create .env file
echo REACT_APP_API_URL=http://localhost:5000 > .env

# Test build
npm run build
```

---

## Backend Configuration

### Setting Up Environment Variables

Create `.env` file in backend directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
MODEL_PATH=models/best_emotion_model.h5
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

### Creating Uploads Directory

```bash
# In backend folder
mkdir uploads
mkdir models
mkdir logs
```

### Running the Flask Server

```bash
# From backend directory with venv activated
python app.py

# Server will start at http://localhost:5000
# Test API: http://localhost:5000/api/health
```

---

## Frontend Setup

### Running React Development Server

```bash
# From frontend directory
npm start

# Will open automatically at http://localhost:3000
# Hot reload enabled - changes reflect instantly
```

### Building for Production

```bash
# Create optimized production build
npm run build

# Output in: frontend/build/

# Test production build locally
npm install -g serve
serve -s build -l 3000
```

---

## Training the Model

### Preparing Dataset

1. Download RAVDESS dataset:
   - Visit: https://zenodo.org/record/1188976
   - Download `Audio_Speech_Actors_01-24.zip`
   - Extract to `backend/data/RAVDESS/`

2. Folder structure:
```
backend/
├── data/
│   └── RAVDESS/
│       └── Actor_*/
│           └── *.wav
├── models/
├── train_model.py
└── app.py
```

### Training Script

Create `backend/train_model.py`:

```python
import numpy as np
from model import SpeechEmotionModel, prepare_dataset
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

# Prepare dataset
print("Preparing dataset...")
X, y, model = prepare_dataset('data/RAVDESS/')

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=np.argmax(y, axis=1)
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=np.argmax(y_temp, axis=1)
)

# Build and train model
print("Building model...")
model.build_model()

print("Training model...")
history = model.train(X_train, y_train, X_val, y_val, epochs=50, batch_size=32)

# Save model
model.save_model('models/best_emotion_model.h5')

# Evaluate on test set
test_results = model.model.evaluate(X_test, y_test)
print(f"\nTest Accuracy: {test_results[1]:.4f}")
print(f"Test Loss: {test_results[0]:.4f}")

print("Training complete!")
```

### Run Training

```bash
# From backend directory with venv activated
python train_model.py

# Training takes ~30-40 minutes on GPU
# ~2-3 hours on CPU
```

---

## Deployment to Vercel

### Step 1: Prepare Frontend for Vercel

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

### Step 2: Configure Environment Variables in Vercel

1. Go to Vercel Dashboard
2. Select your project
3. Settings → Environment Variables
4. Add:
   - Key: `REACT_APP_API_URL`
   - Value: Your backend API URL (e.g., `https://your-backend.herokuapp.com`)

### Step 3: Configure API Backend

**Option A: Deploy Flask on Heroku**

```bash
# Create Procfile in backend/
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.13.12" > runtime.txt

# Install gunicorn
pip install gunicorn

# Add to requirements.txt
pip freeze > requirements.txt

# Login to Heroku
heroku login

# Create app
heroku create emotion-recognition-api

# Deploy
git push heroku main

# Set environment variables
heroku config:set FLASK_ENV=production
```

### Step 4: Update CORS Settings

In `backend/app.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-vercel-app.vercel.app",
            "localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## Deployment to Netlify

### Step 1: Prepare for Netlify

```bash
cd frontend

# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize
netlify init

# Choose "Deploy site" when prompted
```

### Step 2: Configure Build Settings

Create `netlify.toml` in project root:

```toml
[build]
  command = "npm run build"
  publish = "frontend/build"

[build.environment]
  REACT_APP_API_URL = "https://your-backend-api.com"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[functions]
  directory = "netlify/functions"
  node_bundler = "esbuild"
```

### Step 3: Deploy

```bash
# From project root
netlify deploy --prod

# Or set up continuous deployment
# Push to GitHub, Netlify auto-deploys
```

---

## AWS Deployment Guide

### Architecture Overview
```
Route 53 (Domain) → CloudFront (CDN) → ALB (Load Balancer)
                                          ↓
                    Auto Scaling Group (EC2 instances)
                                          ↓
                    RDS (Database) + S3 (Storage)
```

### Step 1: Setup EC2 Instance

```bash
# Launch EC2 (t3.medium or larger)
# AMI: Ubuntu 22.04 LTS
# Security Group: Allow 80, 443, 5000

# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.13 python3.13-venv python3-pip
sudo apt install -y nodejs npm
sudo apt install -y ffmpeg

# Clone repository
git clone <repository-url>
cd emotion-recognition-system

# Setup backend
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup frontend
cd ../frontend
npm install
npm run build
```

### Step 2: Configure Gunicorn

Create `backend/wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### Step 3: Setup Systemd Service

Create `/etc/systemd/system/emotion-app.service`:
```ini
[Unit]
Description=Speech Emotion Recognition API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/emotion-recognition-system/backend
ExecStart=/home/ubuntu/emotion-recognition-system/backend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 4: Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl start emotion-app
sudo systemctl enable emotion-app
sudo systemctl status emotion-app
```

### Step 5: Setup Nginx Reverse Proxy

Install Nginx:
```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/emotion-recognition`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/emotion-recognition-system/frontend/build/;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/emotion-recognition /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Enable HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl restart nginx
```

### Step 7: Setup Auto Scaling (Optional)

Create AMI from configured instance, then:
1. Create Launch Template
2. Create Auto Scaling Group (min: 1, desired: 2, max: 5)
3. Create Application Load Balancer
4. Configure target groups

---

## Docker Deployment

### Step 1: Create Dockerfile for Backend

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p uploads models logs

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Step 2: Create Dockerfile for Frontend

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Step 3: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MODEL_PATH=models/best_emotion_model.h5
    volumes:
      - ./backend/models:/app/models
      - ./backend/uploads:/app/uploads
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    depends_on:
      - backend
    restart: always

volumes:
  model_data:
  upload_data:
```

### Step 4: Build and Run

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## Troubleshooting

### Issue: "No module named 'tensorflow'"
```bash
# Solution:
pip install --upgrade tensorflow
# or for GPU:
pip install tensorflow[and-cuda]
```

### Issue: "FFmpeg not found"
```bash
# Windows: Download from ffmpeg.org and add to PATH
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### Issue: CORS errors in frontend
```python
# Add to backend/app.py
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

### Issue: Model not loading
```bash
# Check file exists
ls -la models/best_emotion_model.h5

# Check permissions
chmod 644 models/best_emotion_model.h5

# Verify model
python -c "import tensorflow; m = tensorflow.keras.models.load_model('models/best_emotion_model.h5'); print('Model loaded successfully')"
```

### Issue: Port already in use
```bash
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -i :5000
kill -9 <PID>
```

### Issue: Out of Memory during training
```python
# Reduce batch size in train_model.py
history = model.train(X_train, y_train, X_val, y_val, 
                      epochs=50, batch_size=16)  # Changed from 32
```

### Issue: Slow predictions
```python
# Enable GPU in Python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))

# Or quantize model for inference
# See model.py for quantization code
```

---

## Performance Optimization Tips

### Backend Optimization
1. Enable model quantization (FP32 → FP16)
2. Use batch predictions
3. Implement caching for repeated predictions
4. Enable gzip compression in Flask

### Frontend Optimization
1. Code splitting with React.lazy()
2. Image optimization and lazy loading
3. Service workers for offline capability
4. CDN for static assets

### Deployment Optimization
1. Use auto-scaling for varying load
2. Implement caching headers
3. Monitor with CloudWatch/Datadog
4. Setup alerts for errors
5. Regular backup of models

---

## Security Checklist

- [ ] HTTPS enabled everywhere
- [ ] CORS properly configured
- [ ] File upload validation implemented
- [ ] Input sanitization in place
- [ ] Error messages don't expose internals
- [ ] API rate limiting enabled
- [ ] Database credentials in environment variables
- [ ] Model files protected (not publicly accessible)
- [ ] Regular security updates

---

## Monitoring and Logging

### Backend Logging

Add to `app.py`:
```python
import logging

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.before_request
def log_request():
    logging.info(f'{request.method} {request.path}')

@app.after_request
def log_response(response):
    logging.info(f'Response: {response.status_code}')
    return response
```

### AWS CloudWatch

```bash
# Install CloudWatch agent
sudo apt-get install -y awscloudwatchagent

# Configure and start
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c default \
    -s
```

---

## Support and Resources

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **API Documentation**: Swagger/OpenAPI at `/api/docs`
- **Model Card**: `models/README.md`

---

**Last Updated**: 2024
**Version**: 2.0
**Maintainer**: AI/ML Team
