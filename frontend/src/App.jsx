import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('upload'); // 'upload', 'record', 'history'
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [apiStatus, setApiStatus] = useState('checking');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingIntervalRef = useRef(null);
  const streamRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, [API_BASE_URL]);

  // Handle recording timer
  useEffect(() => {
    if (isRecording) {
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      setRecordingTime(0);
    }

    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    };
  }, [isRecording]);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      if (response.ok) {
        setApiStatus('connected');
      } else {
        setApiStatus('disconnected');
      }
    } catch (err) {
      setApiStatus('disconnected');
      console.error('API health check failed:', err);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError('Microphone access denied. Please check permissions.');
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = async () => {
    return new Promise((resolve) => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: 'audio/webm;codecs=opus',
          });

          // Stop stream
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
          }

          setIsRecording(false);
          await sendRecordingForPrediction(audioBlob);
          resolve();
        };

        mediaRecorderRef.current.stop();
      }
    });
  };

  const sendRecordingForPrediction = async (audioBlob) => {
    try {
      setLoading(true);
      setError(null);

      // Convert blob to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64data = reader.result.split(',')[1];

        const response = await fetch(
          `${API_BASE_URL}/api/predict-recording`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              audio_data: base64data,
              format: 'webm',
            }),
          }
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();

        if (result.error) {
          setError(result.error);
        } else {
          setPredictions(result);
          addToHistory({
            ...result,
            source: 'microphone',
            timestamp: new Date().toLocaleTimeString(),
          });
        }

        setLoading(false);
      };

      reader.readAsDataURL(audioBlob);
    } catch (err) {
      setError(`Failed to process recording: ${err.message}`);
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    if (!['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/mp4'].includes(file.type)) {
      setError('Please upload a valid audio file (WAV, MP3, OGG, M4A)');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();

      if (result.error) {
        setError(result.error);
      } else {
        setPredictions(result);
        addToHistory({
          ...result,
          filename: file.name,
          source: 'upload',
          timestamp: new Date().toLocaleTimeString(),
        });
      }

      setLoading(false);
      event.target.value = '';
    } catch (err) {
      setError(`Failed to process file: ${err.message}`);
      setLoading(false);
    }
  };

  const addToHistory = (prediction) => {
    setPredictionHistory(prev => [prediction, ...prev.slice(0, 9)]);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getEmotionIcon = (emotion) => {
    const icons = {
      neutral: '😐',
      calm: '😌',
      happy: '😊',
      sad: '😢',
      angry: '😠',
      fearful: '😨',
      disgust: '🤢',
      surprised: '😲',
    };
    return icons[emotion] || '🎤';
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      neutral: '#808080',
      calm: '#87CEEB',
      happy: '#FFD700',
      sad: '#4169E1',
      angry: '#FF6347',
      fearful: '#9932CC',
      disgust: '#32CD32',
      surprised: '#FF69B4',
    };
    return colors[emotion] || '#808080';
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>🎙️ Speech Emotion Recognition</h1>
          <p className="subtitle">Analyze emotions in speech using Advanced Neural Networks</p>
          <div className={`api-status api-${apiStatus}`}>
            <span className="status-dot"></span>
            {apiStatus === 'connected' ? 'API Connected' : 'API Disconnected'}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-container">
        {/* Tabs */}
        <div className="tabs">
          <button
            className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            📁 Upload File
          </button>
          <button
            className={`tab-button ${activeTab === 'record' ? 'active' : ''}`}
            onClick={() => setActiveTab('record')}
          >
            🎙️ Record Audio
          </button>
          <button
            className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            📊 History ({predictionHistory.length})
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span>❌ {error}</span>
            <button onClick={() => setError(null)} className="close-btn">×</button>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="tab-content upload-tab">
            <div className="upload-area">
              <input
                type="file"
                id="file-input"
                accept="audio/*"
                onChange={handleFileUpload}
                disabled={loading}
              />
              <label htmlFor="file-input" className="upload-label">
                <div className="upload-icon">📤</div>
                <h3>Upload Audio File</h3>
                <p>Drag and drop or click to select</p>
                <p className="file-types">Supported: WAV, MP3, OGG, M4A</p>
              </label>
            </div>
          </div>
        )}

        {/* Record Tab */}
        {activeTab === 'record' && (
          <div className="tab-content record-tab">
            <div className="recording-section">
              <div className={`recording-indicator ${isRecording ? 'active' : ''}`}>
                {isRecording && <div className="pulse"></div>}
                <span className="timer">{formatTime(recordingTime)}</span>
              </div>

              <div className="button-group">
                {!isRecording ? (
                  <button
                    className="record-button"
                    onClick={startRecording}
                    disabled={loading}
                  >
                    🎙️ Start Recording
                  </button>
                ) : (
                  <button
                    className="stop-button"
                    onClick={stopRecording}
                    disabled={loading}
                  >
                    ⏹️ Stop Recording
                  </button>
                )}
              </div>

              <p className="recording-info">
                {isRecording
                  ? 'Recording... Click "Stop" when done'
                  : 'Click "Start" to begin recording your audio'}
              </p>
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="tab-content history-tab">
            {predictionHistory.length === 0 ? (
              <div className="empty-state">
                <p>No predictions yet. Upload a file or record audio to get started!</p>
              </div>
            ) : (
              <div className="history-list">
                {predictionHistory.map((item, index) => (
                  <div key={index} className="history-item">
                    <div className="history-header">
                      <span className="emotion-badge" style={{
                        backgroundColor: getEmotionColor(item.emotion)
                      }}>
                        {getEmotionIcon(item.emotion)} {item.emotion.toUpperCase()}
                      </span>
                      <span className="confidence">
                        {(item.confidence * 100).toFixed(1)}%
                      </span>
                      <span className="timestamp">{item.timestamp}</span>
                    </div>
                    {item.filename && (
                      <p className="filename">{item.filename}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Processing audio...</p>
          </div>
        )}

        {/* Results Section */}
        {predictions && !loading && (
          <div className="results-section">
            <div className="emotion-result">
              <div className="emotion-icon">
                {getEmotionIcon(predictions.emotion)}
              </div>
              <div className="emotion-info">
                <h2>Detected Emotion</h2>
                <p className="emotion-name">{predictions.emotion.toUpperCase()}</p>
                <p className="confidence-text">
                  Confidence: <strong>{(predictions.confidence * 100).toFixed(2)}%</strong>
                </p>
              </div>
            </div>

            {/* Graph */}
            {predictions.graph && (
              <div className="graph-container">
                <h3>Emotion Distribution</h3>
                <img
                  src={predictions.graph}
                  alt="Emotion Distribution Graph"
                  className="emotion-graph"
                />
              </div>
            )}

            {/* Emotion Probabilities */}
            <div className="emotion-probabilities">
              <h3>All Emotions</h3>
              <div className="probabilities-grid">
                {predictions.all_emotions &&
                  Object.entries(predictions.all_emotions).map(([emotion, probability]) => (
                    <div key={emotion} className="probability-item">
                      <div className="probability-label">
                        <span>{getEmotionIcon(emotion)}</span>
                        <span>{emotion}</span>
                      </div>
                      <div className="probability-bar">
                        <div
                          className="probability-fill"
                          style={{
                            width: `${probability * 100}%`,
                            backgroundColor: getEmotionColor(emotion),
                          }}
                        ></div>
                      </div>
                      <span className="probability-value">
                        {(probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Audio Analysis */}
            {predictions.audio_analysis && (
              <div className="audio-analysis">
                <h3>Audio Characteristics</h3>
                <div className="analysis-grid">
                  <div className="analysis-item">
                    <span className="label">Duration</span>
                    <span className="value">
                      {predictions.audio_analysis.duration.toFixed(2)}s
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="label">Energy (dB)</span>
                    <span className="value">
                      {predictions.audio_analysis.energy_db.toFixed(2)}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="label">Zero Crossing Rate</span>
                    <span className="value">
                      {predictions.audio_analysis.zero_crossing_rate.toFixed(4)}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="label">Spectral Centroid</span>
                    <span className="value">
                      {predictions.audio_analysis.spectral_centroid.toFixed(0)}Hz
                    </span>
                  </div>
                </div>
              </div>
            )}

            <button
              className="clear-results-button"
              onClick={() => setPredictions(null)}
            >
              Clear Results
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          Built with React + Flask | Powered by TensorFlow & LibROSA | © 2024
        </p>
        <p>
          <a href="#github">GitHub</a> • <a href="#docs">Documentation</a> • <a href="#contact">Contact</a>
        </p>
      </footer>
    </div>
  );
};

export default App;
