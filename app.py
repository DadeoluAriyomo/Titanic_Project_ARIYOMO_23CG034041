from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os
import json
import logging
from pathlib import Path

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== MODEL & SCALER LOADER (SINGLETON PATTERN) =====
class ModelManager:
    """Manages model persistence and prevents reloading on every request"""
    _instance = None
    _model = None
    _scaler = None
    _model_metadata = None
    _model_path = Path("model/titanic_survival_model.pkl")
    _metadata_path = Path("model/model_metadata.json")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._load_model_and_metadata()
        return cls._instance
    
    def _load_model_and_metadata(self):
        """Load model and metadata only once"""
        try:
            # Load trained model and scaler
            with open(self._model_path, "rb") as f:
                self._model, self._scaler = pickle.load(f)
            logger.info(f"✓ Model loaded from {self._model_path}")
            
            # Load model metadata for drift detection
            if self._metadata_path.exists():
                with open(self._metadata_path, "r") as f:
                    self._model_metadata = json.load(f)
                logger.info(f"✓ Model metadata loaded: Accuracy={self._model_metadata.get('accuracy', 'N/A')}")
            else:
                logger.warning(f"⚠ Model metadata not found at {self._metadata_path}")
                self._model_metadata = {}
        
        except FileNotFoundError as e:
            logger.error(f"✗ Model file not found: {e}")
            raise RuntimeError(f"Model file not found: {self._model_path}")
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
            raise RuntimeError(f"Error loading model: {e}")
    
    def get_model(self):
        return self._model
    
    def get_scaler(self):
        return self._scaler
    
    def get_metadata(self):
        return self._model_metadata
    
    def validate_input(self, pclass, sex, age, fare, embarked):
        """Validate input to prevent training/serving drift"""
        errors = []
        
        # Check pclass (1, 2, or 3)
        if pclass not in [1, 2, 3]:
            errors.append(f"Pclass must be 1, 2, or 3. Got: {pclass}")
        
        # Check sex (0=male, 1=female)
        if sex not in [0, 1]:
            errors.append(f"Sex must be 0 (male) or 1 (female). Got: {sex}")
        
        # Check age (must be realistic, 0-120)
        if not (0 <= age <= 120):
            errors.append(f"Age must be between 0 and 120. Got: {age}")
        
        # Check fare (non-negative)
        if fare < 0:
            errors.append(f"Fare must be non-negative. Got: {fare}")
        
        # Check embarked (0=S, 1=C, 2=Q)
        if embarked not in [0, 1, 2]:
            errors.append(f"Embarked must be 0 (S), 1 (C), or 2 (Q). Got: {embarked}")
        
        return errors
    
    def predict(self, pclass, sex, age, fare, embarked):
        """Make prediction with validation"""
        # Validate inputs
        errors = self.validate_input(pclass, sex, age, fare, embarked)
        if errors:
            return None, errors
        
        try:
            input_data = np.array([[pclass, sex, age, fare, embarked]])
            input_scaled = self._scaler.transform(input_data)
            result = self._model.predict(input_scaled)[0]
            probability = self._model.predict_proba(input_scaled)[0]
            
            return {
                'prediction': int(result),
                'survived': result == 1,
                'probability_not_survived': float(probability[0]),
                'probability_survived': float(probability[1])
            }, None
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None, [str(e)]

# Initialize model manager (loads once at startup)
model_manager = ModelManager()

@app.route("/", methods=["GET", "POST"])
def index():
    """Main prediction interface"""
    prediction = None
    error = None

    if request.method == "POST":
        try:
            pclass = int(request.form.get("pclass"))
            sex = int(request.form.get("sex"))
            age = float(request.form.get("age"))
            fare = float(request.form.get("fare"))
            embarked = int(request.form.get("embarked"))
            
            result, errors = model_manager.predict(pclass, sex, age, fare, embarked)
            
            if errors:
                error = ", ".join(errors)
                logger.warning(f"Validation error: {error}")
            else:
                survived = result['survived']
                probability = result['probability_survived']
                if survived:
                    prediction = f"🟢 Survived ({probability*100:.1f}% confidence)"
                else:
                    prediction = f"🔴 Did Not Survive ({(1-probability)*100:.1f}% confidence)"
                logger.info(f"Prediction made: {prediction}")
        
        except (ValueError, KeyError) as e:
            error = f"Invalid input: {str(e)}"
            logger.error(f"Input error: {error}")
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            logger.error(f"Unexpected error: {error}")

    return render_template("index.html", prediction=prediction, error=error)

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """API endpoint for model evaluation metrics"""
    metadata = model_manager.get_metadata()
    
    if not metadata:
        return jsonify({
            'status': 'error',
            'message': 'Model metadata not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'accuracy': metadata.get('accuracy', 'N/A'),
        'precision': metadata.get('precision', 'N/A'),
        'recall': metadata.get('recall', 'N/A'),
        'f1_score': metadata.get('f1_score', 'N/A'),
        'confusion_matrix': metadata.get('confusion_matrix', 'N/A'),
        'classification_report': metadata.get('classification_report', 'N/A')
    })

@app.route("/metrics", methods=["GET"])
def metrics():
    """Display model evaluation metrics and confusion matrix"""
    metadata = model_manager.get_metadata()
    
    if not metadata:
        return render_template("metrics.html", 
                            error="Model metadata not found. Please retrain the model.")
    
    return render_template("metrics.html",
                        accuracy=metadata.get('accuracy', 'N/A'),
                        precision=metadata.get('precision', 'N/A'),
                        recall=metadata.get('recall', 'N/A'),
                        f1_score=metadata.get('f1_score', 'N/A'),
                        confusion_matrix=metadata.get('confusion_matrix', 'N/A'),
                        classification_report=metadata.get('classification_report', 'N/A'))

if __name__ == "__main__":
    # Get port from environment variable with fallback to 10000
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting TitanGuard AI on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
