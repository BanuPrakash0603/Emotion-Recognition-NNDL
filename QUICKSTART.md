# 🚀 QUICK START GUIDE

## Before You Begin

Make sure you have:
- ✅ Python 3.13.12 (64-bit) - Download from https://www.python.org/
- ✅ Node.js 18+ (for frontend) - Download from https://nodejs.org/
- ✅ FFmpeg (for audio processing)
  - Windows: Download from https://ffmpeg.org/download.html
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
- ✅ Git (optional, for version control)

---

## Setup (One-Time)

### **Windows Users**
```bash
# 1. Open Command Prompt
# 2. Navigate to project directory
# 3. Run setup script
setup.bat

# That's it! The script will set up everything
```

### **Linux/macOS Users**
```bash
# 1. Open Terminal
# 2. Navigate to project directory
# 3. Make script executable and run it
chmod +x setup.sh
./setup.sh

# That's it! The script will set up everything
```

### **Manual Setup (If Scripts Don't Work)**
```bash
# Backend setup
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

---

## Running the Application

### **Method 1: Using Command Terminals (Recommended for Development)**

**Terminal 1 - Backend:**
```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Start Flask server
python app.py

# You should see:
# * Running on http://127.0.0.1:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend

# Start React development server
npm start

# Browser should open automatically at http://localhost:3000
# If not, visit http://localhost:3000 manually
```

**Then:**
- Open http://localhost:3000 in your browser
- Start uploading audio files or recording with your microphone!

### **Method 2: Using Docker (Easiest)**

```bash
# Make sure Docker is installed and running

# Build and start all services
docker-compose up -d

# Access at http://localhost (port 80)
# Backend API at http://localhost:5000

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Method 3: Production Build (For Deployment)**

```bash
# Build frontend
cd frontend
npm run build

# This creates optimized files in frontend/build/
# These can be deployed to Vercel, Netlify, AWS, etc.
```

---

## Using the Application

### **Upload Audio File**
1. Click the "📁 Upload File" tab
2. Select an audio file (WAV, MP3, OGG, M4A)
3. Click "Upload Audio File" or drag and drop
4. Wait for processing (usually 1-3 seconds)
5. View results with emotion predictions and graph

### **Record Audio**
1. Click the "🎙️ Record Audio" tab
2. Click "🎙️ Start Recording" button
3. Speak or play audio in front of microphone (at least 3-5 seconds)
4. Click "⏹️ Stop Recording" when done
5. Results appear automatically

### **View History**
1. Click the "📊 History" tab
2. See all your previous predictions
3. Check confidence scores and emotions detected

---

## Troubleshooting

### **Backend won't start**
```bash
# Error: "Port 5000 already in use"
# Solution: Kill the process using port 5000

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -i :5000
kill -9 <PID>
```

### **Frontend won't start**
```bash
# Error: "npm not found"
# Solution: Install Node.js from https://nodejs.org/

# Error: "Module not found"
# Solution: Delete node_modules and reinstall
cd frontend
rm -rf node_modules
npm install
npm start
```

### **Audio processing error**
```bash
# Error: "FFmpeg not found"
# Solution: Install FFmpeg for your OS
# Windows: https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg

# Error: "No microphone access"
# Solution: Allow browser microphone permission
# Click the lock icon in address bar → Allow microphone
```

### **Model not loading**
```bash
# Error: "Model file not found"
# Solution: Train the model first
cd backend
python train_model.py
# This requires RAVDESS dataset (see DEPLOYMENT_GUIDE.md)
```

### **Out of memory error**
```bash
# Solution: Reduce batch size in training
# In train_model.py, change:
# batch_size=32 to batch_size=16
```

---

## Training Your Own Model

To train on RAVDESS dataset:

```bash
# 1. Download dataset from https://zenodo.org/record/1188976
# 2. Extract to backend/data/RAVDESS/
# 3. Run training script
cd backend
source venv/bin/activate
python train_model.py

# Training takes:
# - GPU: 30-40 minutes
# - CPU: 2-3 hours

# Output model saved to: models/best_emotion_model.h5
```

---

## API Usage (For Developers)

### **Predict from File**
```bash
curl -X POST -F "file=@audio.wav" http://localhost:5000/api/predict
```

### **Get Emotions List**
```bash
curl http://localhost:5000/api/emotions
```

### **Health Check**
```bash
curl http://localhost:5000/api/health
```

See DEPLOYMENT_GUIDE.md for complete API documentation.

---

## Next Steps

1. **Train on Your Data**: See "Training Your Own Model" section
2. **Deploy to Cloud**: See DEPLOYMENT_GUIDE.md
3. **Read Documentation**: Open Speech_Emotion_Recognition_Documentation.docx
4. **Customize Frontend**: Edit frontend/src/App.jsx and App.css
5. **Modify Backend**: Edit backend/model.py and app.py

---

## File Structure

```
emotion-recognition-advanced/
├── backend/              # Python Flask backend
│   ├── app.py           # API endpoints
│   ├── model.py         # NNDL model code
│   └── requirements.txt  # Python packages
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx      # Main component
│   │   └── App.css      # Styling
│   └── package.json     # NPM packages
├── docs/                # Documentation
│   └── Speech_Emotion_Recognition_Documentation.docx
├── README.md            # Full README
├── DEPLOYMENT_GUIDE.md  # Deployment instructions
├── setup.bat            # Windows setup script
├── setup.sh             # Linux/macOS setup script
└── docker-compose.yml   # Docker configuration
```

---

## Getting Help

- 📖 **Documentation**: Read Speech_Emotion_Recognition_Documentation.docx
- 🚀 **Deployment**: See DEPLOYMENT_GUIDE.md
- 📝 **README**: Check README.md for detailed info
- 🐛 **Issues**: Check GitHub Issues or create a new one

---

## Performance Tips

### **Faster Predictions**
- Use GPU if available
- Process multiple files together (batch prediction)
- Keep audio files under 10MB

### **Better Accuracy**
- Use high-quality audio recordings
- Avoid background noise
- Speak clearly and naturally

### **Faster Training**
- Use GPU with CUDA
- Reduce dataset size for testing
- Adjust batch size and learning rate

---

## Security Notes

- ✅ Never upload sensitive audio publicly
- ✅ Audio files are deleted after processing
- ✅ No data is stored by default
- ✅ CORS configured for localhost only by default

---

## What Emotions Can It Detect?

1. **Neutral** - No obvious emotion (😐)
2. **Calm** - Peaceful, serene tone (😌)
3. **Happy** - Joyful, upbeat tone (😊)
4. **Sad** - Sorrowful, down tone (😢)
5. **Angry** - Irritated, aggressive tone (😠)
6. **Fearful** - Anxious, scared tone (😨)
7. **Disgust** - Repulsive, annoyed tone (🤢)
8. **Surprised** - Astonished, shocked tone (😲)

---

## Requirements by OS

### **Windows**
- Python 3.13.12 (64-bit)
- Node.js 18+ (for frontend)
- FFmpeg
- 4GB RAM minimum
- 10GB disk space

### **Linux**
- Python 3.13.12
- Node.js 18+
- FFmpeg (apt-get install ffmpeg)
- 4GB RAM minimum
- 10GB disk space

### **macOS**
- Python 3.13.12
- Node.js 18+
- FFmpeg (brew install ffmpeg)
- 4GB RAM minimum
- 10GB disk space

---

## Ports Used

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Docker Frontend**: http://localhost (port 80)
- **Docker Backend**: http://localhost:5000

---

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ Internet Explorer: Not supported

---

## License

MIT License - Free to use for educational and commercial purposes

---

## Support

For issues or questions:
1. Check this guide first
2. Read DEPLOYMENT_GUIDE.md
3. Check GitHub Issues
4. Contact the development team

---

**Happy Emotion Recognizing! 🎉**

For questions or issues, please refer to the documentation or create a GitHub issue.

Last Updated: 2024
Version: 2.0
