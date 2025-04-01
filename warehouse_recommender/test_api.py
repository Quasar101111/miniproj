import requests
import json

def test_price_prediction():
    # Test data for Kalamassery warehouse
    test_data = {
        "area": 5000.0,
        "latitude": 10.0521676,
        "longitude": 76.3199033
    }
    
    # API endpoint with direct IP and port
    url = "http://127.0.0.2:8001/predict/price"
    
    try:
        # Make the request
        print("Sending request to FastAPI service...")
        print("Request data:", json.dumps(test_data, indent=2))
        
        response = requests.post(url, json=test_data)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the response data
        data = response.json()
        
        print("\nReceived response from FastAPI service:")
        print(json.dumps(data, indent=2))
        
        # Format the output nicely
        print("\nPrice Prediction Results:")
        print(f"Optimal Price: ₹{data['optimal_price']:,.2f}")
        print(f"Price Range: ₹{data['price_range']['low']:,.2f} - ₹{data['price_range']['high']:,.2f}")
        print(f"Price per sqft: ₹{data['price_per_sqft']:,.2f}")
        print(f"Confidence Level: {data['confidence']:.1f}%")
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_price_prediction() 