# Bloom's Taxonomy Classifier

A web application that classifies educational questions according to Bloom's Taxonomy levels using AI-powered analysis. Users can analyze individual questions or upload entire question papers (PDF/DOCX) for comprehensive analysis.

## Features

- **Question Classification**: Analyze individual questions using Bloom's Taxonomy
- **File Upload**: Upload PDF and DOCX files for batch analysis
- **User Authentication**: Secure JWT-based authentication system
- **User Dashboard**: Personalized dashboard with analysis history
- **Statistics**: View detailed statistics and level distribution
- **MongoDB Integration**: Persistent storage of user data and analysis results

## Prerequisites

- Python 3.7+
- MongoDB (local or cloud)
- Modern web browser

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blooms-taxonomy-classifier
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   python setup.py
   ```
   This will create a `.env` file with the necessary configuration.

4. **Start MongoDB**
   - **Local MongoDB**: Start your MongoDB service
   - **MongoDB Atlas**: Use the connection string from your cloud database

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Project Structure

```
blooms-taxonomy-classifier/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script for environment configuration
├── test_setup.py         # Setup verification script
├── .env                  # Environment variables (created by setup)
├── templates/            # HTML templates
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── classifier.html   # Main classification interface
│   └── profile.html      # User profile page
└── README.md            # This file
```

## How to Use

### 1. Registration and Login
- Visit the application and click "Sign up" to create an account
- Use your email and password to log in
- JWT tokens are automatically managed for secure sessions

### 2. Question Analysis
- Navigate to the Classifier page
- Enter a question in the text area
- Click "Analyze" to get the Bloom's Taxonomy classification
- View the confidence level and all taxonomy levels

### 3. File Upload
- Use the file upload section to analyze question papers
- Supported formats: PDF, DOCX
- The system will extract questions and analyze each one
- View comprehensive results with statistics

### 4. Dashboard
- Access your personalized dashboard
- View recent analyses
- Quick access to all features

### 5. Profile
- View your analysis statistics
- See level distribution charts
- Track your progress over time

## Bloom's Taxonomy Levels

The application classifies questions into six levels:

1. **Remembering**: Recall facts and basic concepts
2. **Understanding**: Explain ideas and concepts
3. **Applying**: Use information in new situations
4. **Analyzing**: Draw connections among ideas
5. **Evaluating**: Justify a stand or decision
6. **Creating**: Produce new or original work

## Technical Details

### Backend
- **Framework**: Flask
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: MongoDB with PyMongo
- **File Processing**: PyPDF2, python-docx
- **Security**: Password hashing with Werkzeug

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Async/await for API calls
- **Responsive Design**: Works on desktop and mobile

### Database Schema

#### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "hashed_string",
  "created_at": "datetime"
}
```

#### Analyses Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "analysis_type": "single_question|file_upload",
  "content": "string",
  "results": "array|object",
  "created_at": "datetime"
}
```

## Environment Variables

The `.env` file contains:

```env
# Flask Secret Key
SECRET_KEY=your-secret-key-here

# JWT Secret Key
JWT_SECRET_KEY=your-jwt-secret-key-here

# MongoDB Connection String
MONGO_URI=mongodb://localhost:27017/blooms_taxonomy
```

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check the connection string in `.env`
- For MongoDB Atlas, use the full connection string

### JWT Authentication Issues
- Verify JWT_SECRET_KEY is set in `.env`
- Check browser console for token errors
- Clear browser storage if needed

### File Upload Issues
- Ensure files are PDF or DOCX format
- Check file size (max 16MB)
- Verify file is not corrupted

### General Issues
- Run `python test_setup.py` to verify setup
- Check application logs for error messages
- Ensure all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
