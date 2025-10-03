#!/usr/bin/env python3
"""
Simple test script for the Bloom's Taxonomy Classifier
"""

import requests
import json

def test_classification():
    """Test the classification endpoint with various questions"""
    
    base_url = "http://localhost:5000"
    
    # Test questions for each Bloom's level
    test_questions = [
        ("What is the capital of France?", "Remember"),
        ("Explain how photosynthesis works.", "Understand"),
        ("How would you solve this math problem?", "Apply"),
        ("Compare and contrast democracy and monarchy.", "Analyze"),
        ("Evaluate the effectiveness of this argument.", "Evaluate"),
        ("Design a new product for sustainable living.", "Create")
    ]
    
    print("🧪 Testing Bloom's Taxonomy Classifier")
    print("=" * 50)
    
    for question, expected_level in test_questions:
        try:
            response = requests.post(
                f"{base_url}/classify",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_level = data['level']
                confidence = data['confidence']
                
                status = "✅" if actual_level == expected_level else "❌"
                print(f"{status} Question: {question}")
                print(f"   Expected: {expected_level}")
                print(f"   Actual: {actual_level}")
                print(f"   Confidence: {confidence}")
                print()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                print()
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to the server. Make sure the Flask app is running.")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

def test_api_endpoints():
    """Test the API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🔗 Testing API Endpoints")
    print("=" * 30)
    
    # Test levels endpoint
    try:
        response = requests.get(f"{base_url}/api/levels")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/levels - Found {len(data)} levels")
            for level in data.keys():
                print(f"   - {level}")
        else:
            print(f"❌ /api/levels - {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing /api/levels: {e}")
    
    print()

if __name__ == "__main__":
    print("Starting tests...")
    print()
    
    test_api_endpoints()
    test_classification()
    
    print("🎉 Testing completed!")
    print("\nTo use the web interface, open: http://localhost:5000")
