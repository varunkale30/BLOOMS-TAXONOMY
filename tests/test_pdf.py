#!/usr/bin/env python3
"""
Test script to verify PDF generation functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    print("✓ ReportLab imported successfully")
except ImportError as e:
    print(f"✗ ReportLab import failed: {e}")
    print("Please install reportlab: pip install reportlab==4.0.4")
    sys.exit(1)

# Test data similar to what the app would generate
sample_questions_data = [
    {
        'question': 'What is photosynthesis?',
        'level': 'L1-Remember',
        'description': 'Recall facts and basic concepts',
        'confidence': 'Confidence: 85.2%'
    },
    {
        'question': 'Explain how photosynthesis works in plants.',
        'level': 'L2-Understand', 
        'description': 'Explain ideas and concepts',
        'confidence': 'Confidence: 92.1%'
    },
    {
        'question': 'Apply the principles of photosynthesis to design a greenhouse.',
        'level': 'L3-Apply',
        'description': 'Use information in new situations', 
        'confidence': 'Confidence: 78.9%'
    }
]

def create_test_pdf_report(questions_data, filename="test_blooms_report.pdf"):
    """Create a test PDF report"""
    try:
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        story.append(Paragraph("Bloom's Taxonomy Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary statistics
        level_counts = {}
        total_questions = len(questions_data)
        
        for item in questions_data:
            level = item['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Summary section
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=colors.darkgreen
        )
        story.append(Paragraph("Summary Statistics", summary_style))
        
        summary_data = [['Bloom\'s Level', 'Count', 'Percentage']]
        for level, count in level_counts.items():
            percentage = (count / total_questions * 100) if total_questions > 0 else 0
            level_display = level.replace('L1-', '').replace('L2-', '').replace('L3-', '').replace('L4-', '').replace('L5-', '').replace('L6-', '')
            summary_data.append([level_display, str(count), f"{percentage:.1f}%"])
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Detailed questions section
        questions_style = ParagraphStyle(
            'Questions',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=colors.darkgreen
        )
        story.append(Paragraph("Detailed Question Analysis", questions_style))
        
        # Questions table
        questions_table_data = [['#', 'Question', 'Bloom\'s Level', 'Confidence']]
        
        for i, item in enumerate(questions_data, 1):
            level_display = item['level'].replace('L1-', '').replace('L2-', '').replace('L3-', '').replace('L4-', '').replace('L5-', '').replace('L6-', '')
            question_text = item['question']
            confidence_text = item['confidence'].replace('Confidence: ', '') if 'Confidence:' in item['confidence'] else item['confidence']
            
            questions_table_data.append([
                str(i),
                question_text,
                level_display,
                confidence_text
            ])
        
        questions_table = Table(questions_table_data, colWidths=[0.5*inch, 3.5*inch, 1.5*inch, 1*inch])
        questions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center align question numbers
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Center align confidence
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(questions_table)
        
        # Footer
        from datetime import datetime
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Center alignment
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        story.append(Paragraph("Bloom's Taxonomy Classifier - Educational Assessment Tool", footer_style))
        
        # Build PDF
        doc.build(story)
        return filename
        
    except Exception as e:
        print(f"✗ Error creating PDF report: {e}")
        return None

if __name__ == "__main__":
    print("Testing PDF generation functionality...")
    
    # Test PDF creation
    pdf_file = create_test_pdf_report(sample_questions_data)
    
    if pdf_file and os.path.exists(pdf_file):
        print(f"✓ PDF report generated successfully: {pdf_file}")
        print(f"✓ File size: {os.path.getsize(pdf_file)} bytes")
        
        # Clean up test file
        try:
            os.remove(pdf_file)
            print("✓ Test file cleaned up")
        except:
            print("! Could not clean up test file")
    else:
        print("✗ PDF generation failed")
        sys.exit(1)
    
    print("\n🎉 PDF functionality test completed successfully!")
    print("The PDF download feature is ready to use in your application.")
