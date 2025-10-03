#!/usr/bin/env python3
"""
Test script to verify Bloom's Taxonomy Classifier setup
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    packages = [
        ('flask', 'Flask'),
        ('flask_login', 'Flask-Login'),
        ('pymongo', 'PyMongo'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
        ('requests', 'requests'),
        ('jwt', 'PyJWT')
    ]
    
    failed_imports = []
    
    for package, display_name in packages:
        try:
            __import__(package)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name}")
            failed_imports.append(display_name)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All packages imported successfully!")
        return True

def test_env_file():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    load_dotenv()
    
    required_vars = [
        ('SECRET_KEY', 'Flask secret key'),
        ('JWT_SECRET_KEY', 'JWT secret key'),
        ('MONGO_URI', 'MongoDB connection string')
    ]
    
    missing_vars = []
    
    for var, description in required_vars:
        value = os.getenv(var)
        if value and value != f'your-{var.lower().replace("_", "-")}-here':
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Environment configuration complete!")
        return True

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\nTesting MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        load_dotenv()
        
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/blooms_taxonomy')
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

def test_flask_app():
    """Test Flask application creation"""
    print("\nTesting Flask application...")
    
    try:
        from flask import Flask
        from flask_login import LoginManager
        import jwt
        
        app = Flask(__name__)
        app.secret_key = os.getenv('SECRET_KEY', 'test-key')
        
        login_manager = LoginManager()
        login_manager.init_app(app)
        
        print("✅ Flask app creation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Bloom's Taxonomy Classifier - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_env_file,
        test_mongodb_connection,
        test_flask_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Results: {}/{} tests passed".format(sum(results), len(results)))
    
    if all(results):
        print("✅ All tests passed! Setup is complete.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("Refer to the README.md for troubleshooting.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
