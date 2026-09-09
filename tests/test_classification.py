#!/usr/bin/env python3
"""
Test script for Bloom's Taxonomy classification
"""

def classify_question(question):
    question_lower = question.lower()
    
    # Remembering level keywords
    remembering_keywords = ['what', 'when', 'where', 'who', 'which', 'list', 'name', 'define', 'describe', 'identify', 'recall', 'recognize']
    
    # Understanding level keywords
    understanding_keywords = ['explain', 'summarize', 'paraphrase', 'interpret', 'classify', 'compare', 'contrast', 'infer', 'predict', 'translate']
    
    # Applying level keywords
    applying_keywords = ['apply', 'demonstrate', 'execute', 'implement', 'solve', 'use', 'illustrate', 'show', 'calculate', 'compute']
    
    # Analyzing level keywords
    analyzing_keywords = ['analyze', 'examine', 'investigate', 'compare', 'contrast', 'differentiate', 'distinguish', 'examine', 'experiment', 'question']
    
    # Evaluating level keywords
    evaluating_keywords = ['evaluate', 'assess', 'judge', 'criticize', 'appraise', 'argue', 'defend', 'justify', 'support', 'recommend']
    
    # Creating level keywords
    creating_keywords = ['create', 'design', 'develop', 'formulate', 'generate', 'invent', 'plan', 'produce', 'construct', 'compose']
    
    # Count keyword matches for each level
    remembering_count = sum(1 for keyword in remembering_keywords if keyword in question_lower)
    understanding_count = sum(1 for keyword in understanding_keywords if keyword in question_lower)
    applying_count = sum(1 for keyword in applying_keywords if keyword in question_lower)
    analyzing_count = sum(1 for keyword in analyzing_keywords if keyword in question_lower)
    evaluating_count = sum(1 for keyword in evaluating_keywords if keyword in question_lower)
    creating_count = sum(1 for keyword in creating_keywords if keyword in question_lower)
    
    # Determine the primary level
    levels = [
        ('Remembering', remembering_count),
        ('Understanding', understanding_count),
        ('Applying', applying_count),
        ('Analyzing', analyzing_count),
        ('Evaluating', evaluating_count),
        ('Creating', creating_count)
    ]
    
    primary_level = max(levels, key=lambda x: x[1])
    
    # If no clear match, default to Understanding
    if primary_level[1] == 0:
        primary_level = ('Understanding', 0)
    
    return {
        'question': question,
        'level': primary_level[0],
        'confidence': primary_level[1],
        'all_levels': {
            'Remembering': remembering_count,
            'Understanding': understanding_count,
            'Applying': applying_count,
            'Analyzing': analyzing_count,
            'Evaluating': evaluating_count,
            'Creating': creating_count
        }
    }

def test_classification():
    test_questions = [
        "WHAT IS SUBSTITUTION CIPHER?",
        "Explain how photosynthesis works",
        "Apply the Pythagorean theorem to solve this problem",
        "Analyze the causes of World War II",
        "Evaluate the effectiveness of renewable energy sources",
        "Create a new algorithm for sorting data"
    ]
    
    print("Testing Bloom's Taxonomy Classification")
    print("=" * 50)
    
    for question in test_questions:
        result = classify_question(question)
        print(f"\nQuestion: {question}")
        print(f"Level: {result['level']}")
        print(f"Confidence: {result['confidence']}")
        print(f"All Levels: {result['all_levels']}")
        print("-" * 30)

if __name__ == "__main__":
    test_classification()
