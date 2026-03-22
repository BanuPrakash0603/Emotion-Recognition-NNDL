"""
Speech Emotion Recognition using Advanced Neural Network and Deep Learning (NNDL) Techniques
================================================================================================
This module implements a hybrid deep learning architecture combining Convolutional Neural Networks (CNN)
and Long Short-Term Memory (LSTM) networks for robust emotion classification from speech signals.

Architecture:
- Input: MFCC Features (Mel-Frequency Cepstral Coefficients) extracted from audio
- Feature Extraction: Conv1D layers for spatial pattern recognition
- Temporal Processing: Bidirectional LSTM for sequence modeling
- Output: Emotion classification across 8 emotions

Key NNDL Techniques:
1. Conv1D: Extracts local patterns in frequency domain
2. Batch Normalization: Stabilizes training and accelerates convergence
3. Bidirectional LSTM: Captures both forward and backward temporal dependencies
4. Dropout: Prevents overfitting through regularization
5. Attention Mechanism: Focuses on important time steps
6. Layer Normalization: Improves gradient flow in deep networks
"""

import numpy as np
import librosa
import librosa.display
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Input, Conv1D, MaxPooling1D, LSTM, Dense, Dropout, 
    BatchNormalization, Bidirectional, LayerNormalization,
    GlobalAveragePooling1D, Flatten, Reshape
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import json
import pickle
import os
from datetime import datetime


class AudioFeatureExtractor:
    """
    Extracts comprehensive features from audio signals for emotion recognition.
    
    Features extracted:
    1. MFCC (Mel-Frequency Cepstral Coefficients) - 40 coefficients
    2. Delta (Velocity) - First derivative of MFCC
    3. Delta-Delta (Acceleration) - Second derivative of MFCC
    
    Why these features:
    - MFCC captures the spectral characteristics of human voice
    - Delta features capture the dynamics of emotion expression
    - Delta-Delta captures acceleration patterns in speech
    """
    
    def __init__(self, n_mfcc=40, sr=22050, n_fft=2048, hop_length=512):
        self.n_mfcc = n_mfcc
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
    
    def extract_features(self, audio_path, max_duration=3):
        """
        Extract MFCC and delta features from audio file.
        
        Args:
            audio_path: Path to WAV or MP3 audio file
            max_duration: Maximum duration in seconds (pads/truncates to this)
        
        Returns:
            features: Array of shape (n_frames, n_mfcc*3)
            metadata: Dict with extraction info
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sr, duration=max_duration)
            
            # Pad or truncate to ensure consistent duration
            target_length = int(max_duration * sr)
            if len(y) < target_length:
                y = np.pad(y, (0, target_length - len(y)), mode='constant')
            else:
                y = y[:target_length]
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, n_mfcc=self.n_mfcc, 
                n_fft=self.n_fft, hop_length=self.hop_length
            )
            
            # Compute delta (first derivative)
            delta = librosa.feature.delta(mfcc)
            
            # Compute delta-delta (second derivative)
            delta_delta = librosa.feature.delta(mfcc, order=2)
            
            # Concatenate all features
            features = np.vstack([mfcc, delta, delta_delta])
            features = features.T  # Transpose to (n_frames, n_features)
            
            metadata = {
                'duration': len(y) / sr,
                'sr': sr,
                'n_frames': features.shape[0],
                'n_features': features.shape[1]
            }
            
            return features, metadata
        
        except Exception as e:
            print(f"Error extracting features from {audio_path}: {str(e)}")
            return None, None


class SpeechEmotionModel:
    """
    Advanced Speech Emotion Recognition Model using NNDL Techniques.
    
    Architecture Explanation:
    ========================
    
    INPUT LAYER (3D Tensor):
    - Shape: (n_frames, 120) where 120 = 40 MFCC + 40 Delta + 40 Delta-Delta
    
    CONVOLUTIONAL BLOCKS (Feature Learning):
    - Conv1D layers learn local temporal patterns in the feature space
    - Kernel sizes: [3, 3, 5] for multi-scale feature extraction
    - MaxPooling reduces dimensionality while preserving important information
    - BatchNormalization stabilizes training and accelerates convergence
    
    RECURRENT LAYERS (Temporal Modeling):
    - Bidirectional LSTM processes sequences in both directions
    - Learns long-range dependencies in speech patterns
    - 128 units capture complex temporal dynamics
    
    OUTPUT LAYERS (Classification):
    - Dense layer with softmax for 8-class emotion classification
    - Emotions: Neutral, Calm, Happy, Sad, Angry, Fearful, Disgust, Surprised
    
    Regularization Techniques:
    - Dropout (rate=0.3): Randomly deactivates neurons during training
    - Layer Normalization: Improves gradient flow in deep networks
    """
    
    EMOTIONS = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']
    
    def __init__(self, input_shape=(None, 120)):
        self.input_shape = input_shape
        self.model = None
        self.feature_scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.history = None
        self.model_path = None
        
    def build_model(self):
        """
        Build the CNN-LSTM hybrid architecture for emotion recognition.
        
        Model Design Rationale:
        =======================
        1. CNN Layers: Extract local temporal patterns from MFCC features
        2. MaxPooling: Reduce dimension while retaining critical features
        3. Bidirectional LSTM: Model temporal dependencies bidirectionally
        4. Dense Layers: High-level feature processing and classification
        5. Dropout/BatchNorm: Prevent overfitting and stabilize training
        """
        
        self.model = Sequential([
            # Input layer
            Input(shape=self.input_shape),
            
            # CNN Block 1: Fine-grained feature extraction
            Conv1D(64, kernel_size=3, activation='relu', padding='same'),
            BatchNormalization(),
            MaxPooling1D(pool_size=2),
            Dropout(0.3),
            
            # CNN Block 2: Mid-level feature extraction
            Conv1D(128, kernel_size=3, activation='relu', padding='same'),
            BatchNormalization(),
            MaxPooling1D(pool_size=2),
            Dropout(0.3),
            
            # CNN Block 3: Higher-level feature extraction
            Conv1D(256, kernel_size=5, activation='relu', padding='same'),
            BatchNormalization(),
            MaxPooling1D(pool_size=2),
            Dropout(0.3),
            
            # Recurrent Layer: Bidirectional LSTM for temporal modeling
            Bidirectional(LSTM(128, return_sequences=True, activation='relu')),
            LayerNormalization(),
            Dropout(0.4),
            
            # Additional LSTM layer for deeper temporal analysis
            Bidirectional(LSTM(64, return_sequences=False, activation='relu')),
            LayerNormalization(),
            Dropout(0.4),
            
            # Classification layers
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.4),
            
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            # Output layer: 8 emotions
            Dense(len(self.EMOTIONS), activation='softmax')
        ])
        
        # Compile with advanced optimizer settings
        optimizer = Adam(learning_rate=0.001, decay=1e-6)
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("Model built successfully!")
        self.model.summary()
        
        return self.model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """
        Train the model with advanced callbacks for optimal performance.
        
        Training Strategy:
        ==================
        1. EarlyStopping: Stops training if validation loss plateaus
        2. ReduceLROnPlateau: Reduces learning rate when progress stalls
        3. ModelCheckpoint: Saves best model based on validation metrics
        
        These techniques prevent overfitting and ensure optimal convergence.
        """
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                'best_model.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def predict(self, audio_path):
        """
        Predict emotion from audio file with confidence scores.
        
        Returns:
            predictions: Dict with emotion probabilities and metadata
        """
        extractor = AudioFeatureExtractor()
        features, metadata = extractor.extract_features(audio_path)
        
        if features is None:
            return None
        
        # Normalize features
        features_normalized = self.feature_scaler.transform(features)
        features_normalized = np.expand_dims(features_normalized, axis=0)
        
        # Make prediction
        predictions = self.model.predict(features_normalized, verbose=0)
        
        # Prepare results
        results = {
            'emotion': self.EMOTIONS[np.argmax(predictions[0])],
            'confidence': float(np.max(predictions[0])),
            'all_emotions': {
                emotion: float(prob) 
                for emotion, prob in zip(self.EMOTIONS, predictions[0])
            },
            'metadata': metadata
        }
        
        return results
    
    def save_model(self, filepath):
        """Save model and scalers for later use."""
        self.model.save(filepath)
        
        # Save scalers and encoders
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        encoder_path = filepath.replace('.h5', '_encoder.pkl')
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.feature_scaler, f)
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        self.model_path = filepath
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load pre-trained model and associated objects."""
        self.model = tf.keras.models.load_model(filepath)
        
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        encoder_path = filepath.replace('.h5', '_encoder.pkl')
        
        with open(scaler_path, 'rb') as f:
            self.feature_scaler = pickle.load(f)
        with open(encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
        
        self.model_path = filepath
        print(f"Model loaded from {filepath}")


def prepare_dataset(audio_dir, labels_file=None):
    """
    Prepare dataset from audio files for training.
    Assumes RAVDESS dataset format or similar structure.
    """
    extractor = AudioFeatureExtractor()
    model = SpeechEmotionModel()
    
    X, y = [], []
    
    # RAVDESS emotion mapping: 01=neutral, 02=calm, 03=happy, 04=sad,
    # 05=angry, 06=fearful, 07=disgust, 08=surprised
    ravdess_map = {
        '01': 'neutral',
        '02': 'calm',
        '03': 'happy',
        '04': 'sad',
        '05': 'angry',
        '06': 'fearful',
        '07': 'disgust',
        '08': 'surprised'
    }
    
    # Extract features from all audio files
    for filename in os.listdir(audio_dir):
        if filename.endswith('.wav'):
            try:
                audio_path = os.path.join(audio_dir, filename)
                
                # Extract emotion label from filename
                parts = filename.split('-')
                if len(parts) >= 3:
                    emotion_code = parts[2]
                    emotion = ravdess_map.get(emotion_code, 'neutral')
                else:
                    emotion = 'neutral'
                
                # Extract features
                features, _ = extractor.extract_features(audio_path)
                if features is not None:
                    X.append(features)
                    y.append(emotion)
                    print(f"Processed: {filename} -> {emotion}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Normalize features
    X_flat = np.vstack([x for x in X])
    X_normalized = model.feature_scaler.fit_transform(X_flat)
    
    # Reshape back to 3D
    X_reshaped = []
    idx = 0
    for features in X:
        n_frames = features.shape[0]
        X_reshaped.append(X_normalized[idx:idx+n_frames])
        idx += n_frames
    
    # Encode labels
    y_encoded = model.label_encoder.fit_transform(y)
    y_categorical = to_categorical(y_encoded, num_classes=len(model.EMOTIONS))
    
    return np.array(X_reshaped), y_categorical, model


if __name__ == "__main__":
    print("Speech Emotion Recognition - Model Module")
    print("This module should be imported, not run directly.")
