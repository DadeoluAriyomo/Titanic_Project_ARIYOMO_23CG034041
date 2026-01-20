#!/usr/bin/env python3
"""
TitanGuard AI - Example API Usage
Demonstrates how to interact with the application programmatically
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:10000"

def get_metrics():
    """Fetch model evaluation metrics as JSON"""
    print("\n" + "="*60)
    print("FETCHING MODEL METRICS")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/metrics")
    
    if response.status_code == 200:
        metrics = response.json()
        print(json.dumps(metrics, indent=2))
        return metrics
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def make_prediction(pclass, sex, age, fare, embarked):
    """Make a survival prediction"""
    print("\n" + "="*60)
    print("MAKING PREDICTION")
    print("="*60)
    
    data = {
        'pclass': pclass,
        'sex': sex,
        'age': age,
        'fare': fare,
        'embarked': embarked
    }
    
    print(f"Input Data: {data}")
    
    response = requests.post(f"{BASE_URL}/", data=data)
    
    if response.status_code == 200:
        print("✓ Prediction successful!")
        print(f"Response Status: {response.status_code}")
        # Note: Response is HTML, but you can parse it if needed
        return response.text
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        return None


def validate_input_locally(pclass, sex, age, fare, embarked):
    """Validate input before sending to server"""
    print("\n" + "="*60)
    print("VALIDATING INPUT")
    print("="*60)
    
    errors = []
    
    # Pclass validation
    if pclass not in [1, 2, 3]:
        errors.append(f"✗ Pclass must be 1, 2, or 3. Got: {pclass}")
    else:
        print(f"✓ Pclass valid: {pclass}")
    
    # Sex validation
    if sex not in [0, 1]:
        errors.append(f"✗ Sex must be 0 (male) or 1 (female). Got: {sex}")
    else:
        sex_label = "Female" if sex == 1 else "Male"
        print(f"✓ Sex valid: {sex_label}")
    
    # Age validation
    if not (0 <= age <= 120):
        errors.append(f"✗ Age must be 0-120. Got: {age}")
    else:
        print(f"✓ Age valid: {age}")
    
    # Fare validation
    if fare < 0:
        errors.append(f"✗ Fare must be non-negative. Got: {fare}")
    else:
        print(f"✓ Fare valid: £{fare}")
    
    # Embarked validation
    ports = {0: "Southampton", 1: "Cherbourg", 2: "Queenstown"}
    if embarked not in [0, 1, 2]:
        errors.append(f"✗ Embarked must be 0, 1, or 2. Got: {embarked}")
    else:
        print(f"✓ Embarked valid: {ports[embarked]}")
    
    if errors:
        print("\nValidation Errors:")
        for error in errors:
            print(f"  {error}")
        return False
    
    return True


def example_predictions():
    """Run example predictions"""
    print("\n" + "="*70)
    print("TITANGUARD AI - EXAMPLE PREDICTIONS")
    print("="*70)
    
    examples = [
        {
            'name': 'Example 1: Female, 1st Class, Age 25',
            'pclass': 1,
            'sex': 1,     # Female
            'age': 25,
            'fare': 200,
            'embarked': 0  # Southampton
        },
        {
            'name': 'Example 2: Male, 3rd Class, Age 35',
            'pclass': 3,
            'sex': 0,     # Male
            'age': 35,
            'fare': 10,
            'embarked': 0  # Southampton
        },
        {
            'name': 'Example 3: Female, 2nd Class, Age 45',
            'pclass': 2,
            'sex': 1,     # Female
            'age': 45,
            'fare': 50,
            'embarked': 1  # Cherbourg
        },
        {
            'name': 'Example 4: Male, 1st Class, Age 60',
            'pclass': 1,
            'sex': 0,     # Male
            'age': 60,
            'fare': 250,
            'embarked': 2  # Queenstown
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}")
        print("-" * 70)
        
        if validate_input_locally(
            example['pclass'],
            example['sex'],
            example['age'],
            example['fare'],
            example['embarked']
        ):
            make_prediction(
                example['pclass'],
                example['sex'],
                example['age'],
                example['fare'],
                example['embarked']
            )


def example_invalid_inputs():
    """Test invalid input handling"""
    print("\n" + "="*70)
    print("TESTING INVALID INPUTS")
    print("="*70)
    
    invalid_examples = [
        {
            'name': 'Invalid Pclass (4)',
            'pclass': 4,
            'sex': 1,
            'age': 25,
            'fare': 100,
            'embarked': 0
        },
        {
            'name': 'Invalid Age (150)',
            'pclass': 1,
            'sex': 1,
            'age': 150,
            'fare': 100,
            'embarked': 0
        },
        {
            'name': 'Invalid Fare (-50)',
            'pclass': 1,
            'sex': 1,
            'age': 25,
            'fare': -50,
            'embarked': 0
        },
        {
            'name': 'Invalid Sex (5)',
            'pclass': 1,
            'sex': 5,
            'age': 25,
            'fare': 100,
            'embarked': 0
        }
    ]
    
    for example in invalid_examples:
        print(f"\n{example['name']}")
        print("-" * 70)
        
        validate_input_locally(
            example['pclass'],
            example['sex'],
            example['age'],
            example['fare'],
            example['embarked']
        )


if __name__ == "__main__":
    try:
        # 1. Get metrics
        metrics = get_metrics()
        
        # 2. Run example predictions
        example_predictions()
        
        # 3. Test invalid inputs
        example_invalid_inputs()
        
        print("\n" + "="*70)
        print("TESTING COMPLETE")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print(f"  Is the server running at {BASE_URL}?")
        print("  Start it with: python app.py")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


# Alternative: Simple curl commands
"""
# Get metrics as JSON
curl http://localhost:10000/api/metrics

# Make a prediction via form data
curl -X POST http://localhost:10000/ \
  -d "pclass=1&sex=1&age=25&fare=100&embarked=0"

# View metrics dashboard
curl http://localhost:10000/metrics

# Check if server is running
curl http://localhost:10000/
"""
