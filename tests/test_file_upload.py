#!/usr/bin/env python3
"""
Test script for file upload functionality
"""

import requests
import os

def test_file_upload():
    """Test the file upload endpoint with the sample question paper"""
    
    base_url = "http://localhost:5000"
    sample_file = "sample_question_paper.txt"
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file {sample_file} not found")
        return
    
    print("📁 Testing File Upload Functionality")
    print("=" * 40)
    
    try:
        with open(sample_file, 'rb') as file:
            files = {'file': (sample_file, file, 'text/plain')}
            
            response = requests.post(
                f"{base_url}/upload",
                files=files
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    analysis = data['analysis']
                    
                    print(f"✅ File uploaded successfully: {data['filename']}")
                    print(f"📊 Total questions found: {analysis['total_questions']}")
                    print(f"📈 Level distribution:")
                    
                    for level, stats in analysis['level_percentages'].items():
                        print(f"   - {level}: {stats['count']} questions ({stats['percentage']}%)")
                    
                    print(f"\n📋 Sample questions analyzed:")
                    for i, question in enumerate(analysis['questions'][:5], 1):
                        print(f"   {i}. {question['question'][:50]}... → {question['level']}")
                    
                    if len(analysis['questions']) > 5:
                        print(f"   ... and {len(analysis['questions']) - 5} more questions")
                    
                else:
                    print(f"❌ Upload failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_single_question():
    """Test single question classification"""
    
    base_url = "http://localhost:5000"
    
    print("\n🧪 Testing Single Question Classification")
    print("=" * 40)
    
    test_questions = [
        "What is the capital of France?",
        "Explain how photosynthesis works.",
        "Design a new product for sustainable living."
    ]
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/classify",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ '{question[:30]}...' → {data['level']} ({data['confidence']})")
            else:
                print(f"❌ Error classifying: {question}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting file upload tests...")
    print()
    
    test_single_question()
    test_file_upload()
    
    print("\n🎉 Testing completed!")
    print("\nTo use the web interface, open: http://localhost:5000")
    print("Try uploading the sample_question_paper.txt file to test the file analysis feature!")
