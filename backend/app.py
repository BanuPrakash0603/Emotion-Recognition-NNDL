"""
Flask Backend for Speech Emotion Recognition System
====================================================
Provides REST API endpoints for emotion prediction from uploaded audio files
and real-time microphone recordings.

Endpoints:
- POST /api/predict: Predict emotion from uploaded audio file
- POST /api/predict-recording: Predict emotion from recorded audio
- GET /api/emotions: Get list of supported emotions
- GET /api/health: Check API health status
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
import matplotlib
import io
import json
from datetime import datetime
import traceback
from model import SpeechEmotionModel, AudioFeatureExtractor
import pickle
import base64

# Use non-interactive backend for matplotlib
matplotlib.use('Agg')

# Flask app configuration
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Global model
emotion_model = None
feature_extractor = None


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_model():
    """Load the pre-trained emotion recognition model."""
    global emotion_model, feature_extractor
    
    try:
        emotion_model = SpeechEmotionModel()
        emotion_model.build_model()
        feature_extractor = AudioFeatureExtractor()
        print("Model initialized successfully")
    except Exception as e:
        print(f"Error loading model: {str(e)}")


def generate_emotion_graph(prediction_results):
    """
    Generate a visualization of emotion predictions.
    
    Returns:
        base64_encoded_image: Image encoded as base64 string
    """
    try:
        emotions = list(prediction_results['all_emotions'].keys())
        probabilities = list(prediction_results['all_emotions'].values())
        
        # Create color map based on emotions
        colors = {
            'neutral': '#808080',
            'calm': '#87CEEB',
            'happy': '#FFD700',
            'sad': '#4169E1',
            'angry': '#FF6347',
            'fearful': '#9932CC',
            'disgust': '#32CD32',
            'surprised': '#FF69B4'
        }
        
        bar_colors = [colors.get(emotion, '#808080') for emotion in emotions]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(emotions, probabilities, color=bar_colors, edgecolor='black', linewidth=1.5)
        
        # Customize plot
        ax.set_ylabel('Confidence Score', fontsize=12, fontweight='bold')
        ax.set_xlabel('Emotions', fontsize=12, fontweight='bold')
        ax.set_title('Emotion Recognition Results - Confidence Distribution', 
                     fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar, prob in zip(bars, probabilities):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{prob:.2%}',
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert to base64
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        img.seek(0)
        graph_data = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{graph_data}"
    
    except Exception as e:
        print(f"Error generating graph: {str(e)}")
        return None


def process_audio(audio_path):
    """
    Process audio file and return prediction with visualizations.
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        dict: Prediction results with graphs and metadata
    """
    try:
        # Extract features
        features, metadata = feature_extractor.extract_features(audio_path)
        
        if features is None:
            return {'error': 'Failed to extract audio features'}
        
        # Get model prediction
        prediction = emotion_model.predict(audio_path)
        
        if prediction is None:
            return {'error': 'Model prediction failed'}
        
        # Generate visualization
        graph = generate_emotion_graph(prediction)
        
        # Extract additional audio characteristics
        y, sr = librosa.load(audio_path, sr=22050)
        
        # Compute energy
        S = librosa.feature.melspectrogram(y=y, sr=sr)
        energy = np.mean(librosa.power_to_db(S, ref=np.max))
        
        # Compute zero crossing rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        
        # Compute spectral centroid
        spec_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        
        # Combine results
        result = {
            'success': True,
            'emotion': prediction['emotion'],
            'confidence': prediction['confidence'],
            'all_emotions': prediction['all_emotions'],
            'graph': graph,
            'audio_analysis': {
                'duration': float(metadata['duration']),
                'sample_rate': metadata['sr'],
                'energy_db': float(energy),
                'zero_crossing_rate': float(zcr),
                'spectral_centroid': float(spec_centroid)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    except Exception as e:
        return {'error': str(e), 'traceback': traceback.format_exc()}


# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Check API health status."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': emotion_model is not None
    })


@app.route('/api/emotions', methods=['GET'])
def get_emotions():
    """Get list of supported emotions."""
    return jsonify({
        'emotions': SpeechEmotionModel.EMOTIONS,
        'count': len(SpeechEmotionModel.EMOTIONS)
    })


@app.route('/api/predict', methods=['POST'])
def predict_from_file():
    """
    Predict emotion from uploaded audio file.
    
    Request:
        - File: audio file (wav, mp3, ogg, m4a)
    
    Response:
        - emotion: Predicted emotion
        - confidence: Confidence score (0-1)
        - all_emotions: Dictionary with all emotion probabilities
        - graph: Base64 encoded emotion distribution graph
        - audio_analysis: Additional audio characteristics
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process audio
        result = process_audio(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/predict-recording', methods=['POST'])
def predict_from_recording():
    """
    Predict emotion from recorded audio (base64 encoded).
    
    Request:
        - audio_data: Base64 encoded audio data
        - format: Audio format (wav, mp3, etc.)
    
    Response:
        - emotion: Predicted emotion
        - confidence: Confidence score
        - all_emotions: All emotion probabilities
        - graph: Emotion distribution visualization
    """
    try:
        data = request.get_json()
        
        if not data or 'audio_data' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio
        audio_data = data['audio_data']
        audio_format = data.get('format', 'wav')
        
        # Remove data URI prefix if present
        if ',' in audio_data:
            audio_data = audio_data.split(',')[1]
        
        # Decode base64
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            return jsonify({'error': f'Invalid base64 data: {str(e)}'}), 400
        
        # Save temporary file
        filename = f"recording_{datetime.now().timestamp()}.{audio_format}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(audio_bytes)
        
        # Process audio
        result = process_audio(filepath)
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """
    Process multiple audio files at once.
    
    Request:
        - files: Multiple audio files
    
    Response:
        - results: List of predictions for each file
        - summary: Overall statistics
    """
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        results = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                result = process_audio(filepath)
                result['filename'] = file.filename
                results.append(result)
                
                try:
                    os.remove(filepath)
                except:
                    pass
        
        # Calculate summary statistics
        emotions = [r['emotion'] for r in results if 'emotion' in r]
        emotion_counts = {emotion: emotions.count(emotion) 
                         for emotion in SpeechEmotionModel.EMOTIONS}
        
        summary = {
            'total_files': len(files),
            'processed': len(results),
            'emotion_distribution': emotion_counts,
            'average_confidence': np.mean([r['confidence'] for r in results if 'confidence' in r])
        }
        
        return jsonify({
            'results': results,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get information about the model architecture."""
    try:
        return jsonify({
            'model_name': 'Speech Emotion Recognition - CNN-LSTM',
            'emotions': SpeechEmotionModel.EMOTIONS,
            'architecture': 'Convolutional Neural Network + Bidirectional LSTM',
            'features_used': ['MFCC', 'Delta MFCC', 'Delta-Delta MFCC'],
            'input_shape': '(n_frames, 120)',
            'total_emotions': len(SpeechEmotionModel.EMOTIONS),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors."""
    return jsonify({'error': f'File too large. Maximum size: {MAX_CONTENT_LENGTH} bytes'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
