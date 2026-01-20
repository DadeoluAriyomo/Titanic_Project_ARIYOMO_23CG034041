# TitanGuard AI - Titanic Survival Prediction System

## Overview
TitanGuard AI is a modern, responsive web application that predicts passenger survival on the Titanic using Machine Learning. The application features a beautiful UI, comprehensive model evaluation metrics, and production-ready safety features.

## Key Features

### 🚀 Core Functionality
- **Intelligent Prediction Engine**: Uses trained Logistic Regression model with feature scaling
- **Real-time Predictions**: Get instant survival predictions with confidence scores
- **Input Validation**: Prevents data drift by validating all inputs against training constraints

### 📊 Model Evaluation
- **Comprehensive Metrics Dashboard**: View accuracy, precision, recall, and F1-score
- **Confusion Matrix Visualization**: Understand model performance across classes
- **Classification Report**: Detailed metrics for each class
- **Metric Explanations**: Built-in guide for understanding each metric

### 🎨 User Interface
- **Modern, Responsive Design**: Works flawlessly on desktop, tablet, and mobile
- **Beautiful Animations**: Smooth transitions and engaging visual effects
- **Touch-Friendly**: Optimized for all device sizes with 44-48px minimum touch targets
- **Dark Ocean Theme**: Professional blue ocean gradient with gold accents

### 🛡️ Production Safety Features
- **Model Persistence**: Singleton pattern prevents model reloading on every request
- **Input Validation**: Comprehensive validation prevents training/serving drift
- **Metadata Storage**: Model metrics saved during training for drift monitoring
- **Environment Configuration**: Port and configuration via environment variables
- **Logging**: Detailed logging for debugging and monitoring

---

## Installation & Setup

### Requirements
- Python 3.8+
- Flask
- scikit-learn
- pandas
- numpy

### Installation Steps

1. **Clone or extract the project**
   ```bash
   cd Titanic_Project_ARIYOMO_23CG034041
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the model (if needed)**
   - Open `model/model_building.ipynb`
   - Run all cells to train and save the model
   - This generates:
     - `model/titanic_survival_model.pkl` (trained model + scaler)
     - `model/model_metadata.json` (evaluation metrics)

4. **Run the application**
   ```bash
   python app.py
   ```
   - Default: http://localhost:10000
   - Custom port: `PORT=5000 python app.py`

---

## Application Structure

### Model Training (`model/model_building.ipynb`)

The notebook performs these steps:

1. **Data Loading**: Loads Titanic dataset from `train.csv`
2. **Feature Selection**: Selects 5 key features
   - `Pclass`: Passenger class (1, 2, 3)
   - `Sex`: Gender (0=male, 1=female)
   - `Age`: Passenger age (0-120)
   - `Fare`: Ticket price (≥0)
   - `Embarked`: Port (0=S, 1=C, 2=Q)

3. **Data Preprocessing**
   - Handles missing values (Age, Embarked)
   - Encodes categorical variables

4. **Model Training**
   - StandardScaler for feature normalization
   - Logistic Regression classifier

5. **Evaluation & Metrics**
   - Calculates: Accuracy, Precision, Recall, F1-Score
   - Generates: Confusion Matrix, Classification Report
   - Saves metadata for drift monitoring

6. **Model Persistence**
   - Pickles model and scaler
   - Saves metrics in JSON format

### Web Application (`app.py`)

**ModelManager (Singleton Pattern)**
- Loads model once at startup
- Reuses loaded model for all predictions
- Prevents unnecessary I/O operations

**Input Validation**
```python
def validate_input(self, pclass, sex, age, fare, embarked):
    # Ensures inputs match training data constraints
    # Prevents training/serving drift
```

**Routes**
- `GET /` - Main prediction interface
- `POST /` - Handle predictions with validation
- `GET /metrics` - Display evaluation metrics
- `GET /api/metrics` - JSON API for metrics

### Frontend Templates

**index.html**
- Prediction form with 5 input fields
- Real-time validation feedback
- Result display with confidence scores
- Navigation to metrics dashboard

**metrics.html**
- Key metrics cards (Accuracy, Precision, Recall, F1)
- Confusion matrix with color-coded cells
- Classification report
- Metric explanations

**style.css**
- Responsive design (6 breakpoints)
- Modern animations
- Ocean theme with gold accents
- Touch-optimized for mobile

---

## Input Validation & Drift Prevention

### Validation Rules

```
Pclass (int): Must be 1, 2, or 3
Sex (int): Must be 0 (male) or 1 (female)
Age (float): Must be between 0 and 120
Fare (float): Must be non-negative (≥ 0)
Embarked (int): Must be 0 (Southampton), 1 (Cherbourg), or 2 (Queenstown)
```

### How It Prevents Drift

1. **Strict Input Validation**: Rejects inputs outside training ranges
2. **Metadata Tracking**: Stores expected features and classes
3. **Logging**: Records all predictions for monitoring
4. **Separation**: Training and serving use identical feature definitions

---

## Model Evaluation Metrics

### Accuracy
- **Definition**: Percentage of correct predictions
- **Formula**: (TP + TN) / (TP + TN + FP + FN)
- **Use Case**: Overall model performance

### Precision
- **Definition**: Of predicted positive, how many were actually positive
- **Formula**: TP / (TP + FP)
- **Use Case**: Minimize false alarms (Type I errors)

### Recall (Sensitivity)
- **Definition**: Of actual positive, how many did we find
- **Formula**: TP / (TP + FN)
- **Use Case**: Minimize missed cases (Type II errors)

### F1-Score
- **Definition**: Harmonic mean of precision and recall
- **Formula**: 2 × (Precision × Recall) / (Precision + Recall)
- **Use Case**: Balanced metric when classes are imbalanced

### Confusion Matrix
```
                Predicted
              Negative | Positive
Actual
Negative    | TN       | FP
Positive    | FN       | TP
```
- **TN**: Correct negative predictions
- **TP**: Correct positive predictions
- **FP**: Incorrect positive predictions (false alarm)
- **FN**: Incorrect negative predictions (missed case)

---

## Deployment

### Environment Variables

```bash
PORT=10000              # Server port (default: 10000)
```

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Deploy:
```bash
docker build -t titanguard-ai .
docker run -p 5000:10000 -e PORT=10000 titanguard-ai
```

### Using Flask Development Server

```bash
# For development only
flask run --port 5000

# For production, use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:10000 app:app
```

---

## API Reference

### POST /
**Make a Prediction**

Request body (form data):
```
pclass=1&sex=1&age=25&fare=100&embarked=0
```

Response:
```html
<!-- Rendered HTML with prediction result -->
```

### GET /metrics
**View Model Evaluation Dashboard**

Response:
```html
<!-- Interactive metrics dashboard -->
```

### GET /api/metrics
**Get Metrics as JSON**

Response:
```json
{
  "status": "success",
  "accuracy": 0.8213,
  "precision": 0.7845,
  "recall": 0.8421,
  "f1_score": 0.8126,
  "confusion_matrix": [[100, 20], [15, 105]],
  "classification_report": "..."
}
```

---

## File Structure

```
Titanic_Project_ARIYOMO_23CG034041/
├── app.py                          # Flask application with ModelManager
├── requirements.txt                # Python dependencies
├── train.csv                       # Training dataset
├── model/
│   ├── model_building.ipynb       # Model training notebook
│   ├── titanic_survival_model.pkl # Trained model (generated)
│   └── model_metadata.json        # Model metrics (generated)
├── templates/
│   ├── index.html                 # Main prediction interface
│   └── metrics.html               # Evaluation metrics dashboard
├── static/
│   └── style.css                  # Responsive styling
└── README.md                       # This file
```

---

## Development Notes

### Model Training
- Ensure `train.csv` is in the project root
- Features and target variable are defined in the notebook
- Metrics are automatically saved to `model_metadata.json`

### Adding New Features
1. Retrain the model in the notebook
2. Update validation rules in `ModelManager.validate_input()`
3. Update feature list in metadata
4. Update HTML form with new inputs

### Monitoring
- Check logs for prediction errors
- Monitor API response times
- Track validation failures
- Review metric trends over time

---

## Troubleshooting

### Model Not Loading
- Ensure `model/titanic_survival_model.pkl` exists
- Check file permissions
- Verify pickle file integrity

### Metrics Dashboard Not Loading
- Ensure `model/model_metadata.json` exists
- Run all cells in `model_building.ipynb`
- Check JSON file format

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :10000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :10000
kill -9 <PID>
```

### Input Validation Errors
- Check input ranges against validation rules
- Verify numeric values are numbers (not strings)
- Ensure categorical values match expected codes

---

## Performance

### Optimization Features
1. **Model Persistence**: Model loaded once, reused for all requests
2. **Feature Scaling**: Scaler saved during training
3. **Minimal Dependencies**: Only essential ML libraries
4. **Efficient Prediction**: Single forward pass per request

### Expected Performance
- **Startup Time**: ~1-2 seconds
- **Prediction Latency**: <100ms
- **Memory Usage**: ~50-100MB
- **Throughput**: 1000+ predictions/second

---

## Future Enhancements

- [ ] User authentication and prediction history
- [ ] Batch prediction API
- [ ] Model retraining pipeline
- [ ] Advanced data visualization
- [ ] A/B testing framework
- [ ] Model serving with TensorFlow/ONNX
- [ ] Database integration for logging

---

## Author
**Dadeolu Ariyomo** (23CG034041)

---

## License
Educational Project - January 2026

---

## Support
For issues or questions, refer to the troubleshooting section or check the application logs.
