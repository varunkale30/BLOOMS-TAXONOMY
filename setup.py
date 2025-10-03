#!/usr/bin/env python3
"""
Setup script for Bloom's Taxonomy Classifier with Google OAuth and MongoDB
"""

import os
import sys
import secrets
from dotenv import load_dotenv

def create_env_file():
    """Create .env file with required environment variables"""
    print("=== Bloom's Taxonomy Classifier Setup ===")
    
    # Generate secret keys
    secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    
    # Get MongoDB URI
    mongo_uri = input("Enter MongoDB URI (or press Enter for default localhost): ").strip()
    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017/blooms_taxonomy"
    
    # Create .env content
    env_content = f"""# Flask Secret Key
SECRET_KEY={secret_key}

# JWT Secret Key
JWT_SECRET_KEY={jwt_secret_key}

# MongoDB Connection String
MONGO_URI={mongo_uri}
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start MongoDB server")
    print("3. Run the application: python app.py")
    print("4. Open http://localhost:5000 in your browser")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_login',
        'pymongo',
        'PyPDF2',
        'docx',
        'requests',
        'dotenv',
        'jwt'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

if __name__ == "__main__":
    if not check_dependencies():
        exit(1)
    
    create_env_file()
