// Bloom's Taxonomy Classifier - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Application loaded successfully');
    
    // Tab Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Tab switching functionality
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            console.log('Tab clicked:', targetTab);
            
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show corresponding content
            const targetContent = document.getElementById(targetTab + '-tab');
            if (targetContent) {
                targetContent.classList.add('active');
                console.log('Showing tab:', targetTab);
            }
            
            // Clear any existing results when switching tabs
            const resultSection = document.getElementById('resultSection');
            const fileResultSection = document.getElementById('fileResultSection');
            if (resultSection) resultSection.classList.add('hidden');
            if (fileResultSection) fileResultSection.classList.add('hidden');
        });
    });
    
    // Single Question Classification
    const classifyBtn = document.getElementById('classifyBtn');
    const questionInput = document.getElementById('questionInput');
    const resultSection = document.getElementById('resultSection');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (classifyBtn && questionInput) {
        classifyBtn.addEventListener('click', function() {
            const question = questionInput.value.trim();
            
            if (!question) {
                showMessage('Please enter a question to classify', 'error');
                return;
            }
            
            // Show loading
            loadingOverlay.classList.remove('hidden');
            document.getElementById('loadingText').textContent = 'Analyzing your question...';
            
            // Send classification request
            fetch('/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                loadingOverlay.classList.add('hidden');
                
                if (data.success) {
                    // Display results
                    document.getElementById('resultLevel').textContent = data.level;
                    document.getElementById('resultDescription').textContent = data.description;
                    document.getElementById('displayQuestion').textContent = data.question;
                    
                    // Set level color
                    const resultLevel = document.getElementById('resultLevel');
                    resultLevel.style.color = data.color;
                    
                    // Show result section
                    resultSection.classList.remove('hidden');
                    
                    // Scroll to result
                    resultSection.scrollIntoView({ behavior: 'smooth' });
                    
                    showMessage('Question classified successfully!', 'success');
                } else {
                    showMessage(data.error || 'Failed to classify question', 'error');
                }
            })
            .catch(error => {
                loadingOverlay.classList.add('hidden');
                showMessage('An error occurred while classifying the question', 'error');
                console.error('Error:', error);
            });
        });
        
        // Enter key support
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                classifyBtn.click();
            }
        });
    }
    
    // Report Upload Functionality
    const reportFileInput = document.getElementById('reportFileInput');
    const reportUploadArea = document.getElementById('reportUploadArea');
    const fileResultSection = document.getElementById('fileResultSection');
    
    
    // Spreadsheet Upload Functionality
    if (reportFileInput && reportUploadArea) {
        // Click to browse for report files
        const reportBrowseBtn = reportUploadArea.querySelector('.browse-btn');
        if (reportBrowseBtn) {
            reportBrowseBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                reportFileInput.click();
            });
        }
        
        // Click on upload area (but not on the browse button)
        reportUploadArea.addEventListener('click', function(e) {
            if (e.target !== reportBrowseBtn && !reportBrowseBtn.contains(e.target)) {
                reportFileInput.click();
            }
        });
        
        // Drag and drop for report files
        reportUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        reportUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        reportUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                reportFileInput.files = files;
                handleSpreadsheetUpload();
            }
        });
        
        // Report file input change
        reportFileInput.addEventListener('change', handleSpreadsheetUpload);
    }
    
    // Download PDF button functionality
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', function() {
            window.location.href = '/download_report/pdf';
        });
    }
    
    
    function handleSpreadsheetUpload() {
        const file = reportFileInput.files[0];
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['.xlsx', '.xls', '.csv'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            showMessage('Please select a valid file type (XLSX, XLS, CSV)', 'error');
            return;
        }
        
        // Validate file size (16MB)
        if (file.size > 16 * 1024 * 1024) {
            showMessage('File size must be less than 16MB', 'error');
            return;
        }
        
        // Show loading
        loadingOverlay.classList.remove('hidden');
        document.getElementById('loadingText').textContent = 'Processing your questions file...';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Send request
        fetch('/upload_report', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading
            loadingOverlay.classList.add('hidden');
            
            console.log('Report upload response:', data);
            
            if (data.success) {
                // Update file result section
                const fileNameElement = document.getElementById('fileName');
                if (fileNameElement) {
                    fileNameElement.textContent = file.name;
                }
                
                // Extract data from the analysis structure
                const analysis = data.analysis;
                const totalQuestionsElement = document.getElementById('totalQuestions');
                if (totalQuestionsElement) {
                    totalQuestionsElement.textContent = analysis.total_questions || 0;
                }
                
                // Find most common level
                let mostCommonLevel = '-';
                let maxCount = 0;
                if (analysis.level_counts) {
                    for (const [level, count] of Object.entries(analysis.level_counts)) {
                        if (count > maxCount) {
                            maxCount = count;
                            mostCommonLevel = level;
                        }
                    }
                }
                const highestLevelElement = document.getElementById('highestLevel');
                if (highestLevelElement) {
                    highestLevelElement.textContent = mostCommonLevel;
                }
                
                
                // Display level distribution
                if (analysis.level_percentages) {
                    displayLevelDistribution(analysis.level_percentages);
                }
                
                // Display individual questions
                if (analysis.questions) {
                    displayQuestions(analysis.questions);
                }
                
                // Show download actions for spreadsheet uploads (PDF download available)
                const downloadActions = document.getElementById('downloadActions');
                if (downloadActions) {
                    downloadActions.style.display = 'block';
                }
                
                // Show file result section
                if (fileResultSection) {
                    fileResultSection.classList.remove('hidden');
                    // Scroll to result
                    fileResultSection.scrollIntoView({ behavior: 'smooth' });
                }
                
                showMessage('Questions processed successfully! You can now download the PDF report.', 'success');
            } else {
                showMessage(data.error || 'Failed to process file', 'error');
            }
        })
        .catch(error => {
            loadingOverlay.classList.add('hidden');
            showMessage('An error occurred while processing the file', 'error');
            console.error('Error:', error);
        });
    }
    
    // Function to display level distribution
    function displayLevelDistribution(levelPercentages) {
        const chartContainer = document.getElementById('distributionChart');
        if (!chartContainer) return;
        
        // Clear existing content
        chartContainer.innerHTML = '';
        
        // Create distribution bars with new design
        Object.entries(levelPercentages).forEach(([level, data]) => {
            if (data.count > 0) {
                const barContainer = document.createElement('div');
                barContainer.className = 'distribution-bar';
                
                // Level info section
                const levelInfo = document.createElement('div');
                levelInfo.className = 'level-info';
                
                const levelName = document.createElement('div');
                levelName.className = 'level-name';
                levelName.textContent = level.replace('L', 'Level ').replace('-', ': ');
                
                const levelStats = document.createElement('div');
                levelStats.className = 'level-stats';
                
                const percentageBadge = document.createElement('span');
                percentageBadge.className = 'percentage-badge';
                percentageBadge.textContent = `${data.percentage}%`;
                
                levelStats.appendChild(percentageBadge);
                levelInfo.appendChild(levelName);
                levelInfo.appendChild(levelStats);
                
                // Progress container
                const progressContainer = document.createElement('div');
                progressContainer.className = 'progress-container';
                
                const progressFill = document.createElement('div');
                progressFill.className = 'progress-fill';
                progressFill.style.width = `${data.percentage}%`;
                progressFill.style.background = `linear-gradient(90deg, ${getLevelColor(level)}, ${getLevelColor(level)}dd)`;
                
                progressContainer.appendChild(progressFill);
                
                // Question count
                const questionCount = document.createElement('div');
                questionCount.className = 'question-count';
                questionCount.textContent = `${data.count} question${data.count !== 1 ? 's' : ''}`;
                
                barContainer.appendChild(levelInfo);
                barContainer.appendChild(progressContainer);
                barContainer.appendChild(questionCount);
                chartContainer.appendChild(barContainer);
            }
        });
    }
    
    // Function to display individual questions with multi-level support
    function displayQuestions(questions) {
        const container = document.getElementById('questionsContainer');
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        questions.forEach((question, index) => {
            const questionItem = document.createElement('div');
            questionItem.className = 'question-item';
            questionItem.style.border = '1px solid #e1e5e9';
            questionItem.style.borderRadius = '10px';
            questionItem.style.padding = '15px';
            questionItem.style.marginBottom = '15px';
            questionItem.style.backgroundColor = 'white';
            
            // Add multi-level indicator if applicable
            if (question.is_multi_level) {
                questionItem.style.borderLeft = '4px solid #ff9500';
                questionItem.style.backgroundColor = '#fffbf7';
            }
            
            const questionHeader = document.createElement('div');
            questionHeader.style.display = 'flex';
            questionHeader.style.justifyContent = 'space-between';
            questionHeader.style.alignItems = 'center';
            questionHeader.style.marginBottom = '10px';
            
            const questionNumber = document.createElement('span');
            questionNumber.style.fontWeight = '600';
            questionNumber.style.color = '#333';
            questionNumber.textContent = `Question ${question.question_number}`;
            
            // Add multi-level indicator
            if (question.is_multi_level) {
                const multiLevelBadge = document.createElement('span');
                multiLevelBadge.style.fontSize = '0.7rem';
                multiLevelBadge.style.backgroundColor = '#ff9500';
                multiLevelBadge.style.color = 'white';
                multiLevelBadge.style.padding = '2px 6px';
                multiLevelBadge.style.borderRadius = '10px';
                multiLevelBadge.style.marginLeft = '8px';
                multiLevelBadge.textContent = 'MULTI-LEVEL';
                questionNumber.appendChild(multiLevelBadge);
            }
            
            // Level display - show multiple levels if applicable
            const levelContainer = document.createElement('div');
            levelContainer.style.display = 'flex';
            levelContainer.style.gap = '5px';
            levelContainer.style.alignItems = 'center';
            
            if (question.is_multi_level && question.all_levels && question.all_levels.length > 1) {
                // Display multiple level badges
                question.all_levels.forEach((levelData, idx) => {
                    const levelBadge = document.createElement('span');
                    levelBadge.style.padding = '4px 8px';
                    levelBadge.style.borderRadius = '15px';
                    levelBadge.style.fontSize = '0.7rem';
                    levelBadge.style.fontWeight = '500';
                    levelBadge.style.color = 'white';
                    levelBadge.style.backgroundColor = levelData.color;
                    levelBadge.style.opacity = idx === 0 ? '1' : '0.8';
                    levelBadge.textContent = levelData.level.split('-')[1];
                    levelContainer.appendChild(levelBadge);
                });
            } else {
                // Single level display
                const questionLevel = document.createElement('span');
                questionLevel.style.padding = '5px 12px';
                questionLevel.style.borderRadius = '20px';
                questionLevel.style.fontSize = '0.8rem';
                questionLevel.style.fontWeight = '500';
                questionLevel.style.color = 'white';
                questionLevel.style.backgroundColor = question.color || getLevelColor(question.level);
                questionLevel.textContent = question.level_display || question.level;
                levelContainer.appendChild(questionLevel);
            }
            
            questionHeader.appendChild(questionNumber);
            questionHeader.appendChild(levelContainer);
            
            const questionText = document.createElement('div');
            questionText.style.marginBottom = '8px';
            questionText.style.color = '#333';
            questionText.style.lineHeight = '1.4';
            questionText.textContent = question.question;
            
            const questionDescription = document.createElement('div');
            questionDescription.style.fontSize = '0.9rem';
            questionDescription.style.color = '#666';
            questionDescription.style.marginBottom = '8px';
            questionDescription.textContent = question.description;
            
            questionItem.appendChild(questionHeader);
            questionItem.appendChild(questionText);
            questionItem.appendChild(questionDescription);
            
            container.appendChild(questionItem);
        });
    }
    
    // Function to display report preview table
    function displayReportPreview(questions) {
        const tbody = document.getElementById('reportPreviewBody');
        if (!tbody) return;
        
        // Clear existing content
        tbody.innerHTML = '';
        
        // Show only first 10 questions as preview
        const previewQuestions = questions.slice(0, 10);
        
        previewQuestions.forEach(question => {
            const row = document.createElement('tr');
            
            const questionCell = document.createElement('td');
            questionCell.textContent = question.question.length > 100 ? 
                question.question.substring(0, 100) + '...' : question.question;
            
            const levelCell = document.createElement('td');
            const levelSpan = document.createElement('span');
            levelSpan.textContent = question.level;
            levelSpan.style.padding = '4px 8px';
            levelSpan.style.borderRadius = '12px';
            levelSpan.style.fontSize = '0.8rem';
            levelSpan.style.fontWeight = '500';
            levelSpan.style.color = 'white';
            levelSpan.style.backgroundColor = question.color || getLevelColor(question.level);
            levelCell.appendChild(levelSpan);
            
            const descriptionCell = document.createElement('td');
            descriptionCell.textContent = question.description;
            descriptionCell.style.fontSize = '0.9rem';
            
            row.appendChild(questionCell);
            row.appendChild(levelCell);
            row.appendChild(descriptionCell);
            
            tbody.appendChild(row);
        });
        
        // Add note if there are more questions
        if (questions.length > 10) {
            const noteRow = document.createElement('tr');
            const noteCell = document.createElement('td');
            noteCell.colSpan = 3;
            noteCell.textContent = `... and ${questions.length - 10} more questions (download full report to see all)`;
            noteCell.style.textAlign = 'center';
            noteCell.style.fontStyle = 'italic';
            noteCell.style.color = '#666';
            noteCell.style.padding = '15px';
            noteRow.appendChild(noteCell);
            tbody.appendChild(noteRow);
        }
    }
    
    // Helper function to get level colors
    function getLevelColor(level) {
        const colors = {
            'Remember': '#FF6B6B',
            'Understand': '#4ECDC4',
            'Apply': '#45B7D1',
            'Analyze': '#96CEB4',
            'Evaluate': '#FFEAA7',
            'Create': '#DDA0DD'
        };
        return colors[level] || '#666';
    }
    
    // Level card interactions
    const levelCards = document.querySelectorAll('.level-card');
    levelCards.forEach(card => {
        card.addEventListener('click', function() {
            const level = this.getAttribute('data-level');
            const description = this.querySelector('p').textContent;
            
            // Update question input with example
            if (questionInput) {
                questionInput.value = `Example ${level.toLowerCase()} question...`;
                questionInput.focus();
            }
        });
    });
});

// Utility function to show messages
function showMessage(message, type = 'info') {
    console.log(`Showing message: ${message} (${type})`);
    
    // Remove any existing messages
    const existingMessages = document.querySelectorAll('.alert');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Set background color based on type
    if (type === 'error') {
        messageDiv.style.backgroundColor = '#dc3545';
    } else if (type === 'success') {
        messageDiv.style.backgroundColor = '#28a745';
    } else {
        messageDiv.style.backgroundColor = '#17a2b8';
    }
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}
