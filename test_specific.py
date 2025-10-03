#!/usr/bin/env python3
"""
Test the specific question that was failing
"""

def classify_question(question):
    question_lower = question.lower()
    
    # Remembering level keywords
    remembering_keywords = ['what', 'when', 'where', 'who', 'which', 'list', 'name', 'define', 'describe', 'identify', 'recall', 'recognize', 'is', 'are', 'was', 'were']
    
    # Understanding level keywords
    understanding_keywords = ['explain', 'summarize', 'paraphrase', 'interpret', 'classify', 'compare', 'contrast', 'infer', 'predict', 'translate', 'how', 'why', 'understand', 'meaning']
    
    # Applying level keywords
    applying_keywords = ['apply', 'demonstrate', 'execute', 'implement', 'solve', 'use', 'illustrate', 'show', 'calculate', 'compute', 'work', 'function', 'operate']
    
    # Analyzing level keywords
    analyzing_keywords = ['analyze', 'examine', 'investigate', 'compare', 'contrast', 'differentiate', 'distinguish', 'examine', 'experiment', 'question', 'break down', 'separate']
    
    # Evaluating level keywords
    evaluating_keywords = ['evaluate', 'assess', 'judge', 'criticize', 'appraise', 'argue', 'defend', 'justify', 'support', 'recommend', 'rate', 'rank', 'choose']
    
    # Creating level keywords
    creating_keywords = ['create', 'design', 'develop', 'formulate', 'generate', 'invent', 'plan', 'produce', 'construct', 'compose', 'build', 'make', 'write']
    
    # Count keyword matches for each level
    remembering_count = sum(1 for keyword in remembering_keywords if keyword in question_lower)
    understanding_count = sum(1 for keyword in understanding_keywords if keyword in question_lower)
    applying_count = sum(1 for keyword in applying_keywords if keyword in question_lower)
    analyzing_count = sum(1 for keyword in analyzing_keywords if keyword in question_lower)
    evaluating_count = sum(1 for keyword in evaluating_keywords if keyword in question_lower)
    creating_count = sum(1 for keyword in creating_keywords if keyword in question_lower)
    
    # Special case for "HOW" questions - they often indicate Understanding or Applying
    if 'how' in question_lower:
        understanding_count += 2
        applying_count += 1
    
    # Special case for "WHAT IS" questions - they indicate Remembering
    if question_lower.startswith('what is') or question_lower.startswith('what are'):
        remembering_count += 2
    
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
    
    # If no clear match, try to infer from question structure
    if primary_level[1] == 0:
        if '?' in question:
            if question_lower.startswith('what'):
                primary_level = ('Remembering', 1)
            elif question_lower.startswith('how'):
                primary_level = ('Understanding', 1)
            elif question_lower.startswith('why'):
                primary_level = ('Understanding', 1)
            else:
                primary_level = ('Understanding', 1)
        else:
            primary_level = ('Understanding', 1)
    
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

# Test the specific question
question = "HOW PHOTOSYNTHESIS SYSTEM WORSK?"
result = classify_question(question)

print(f"Question: {question}")
print(f"Level: {result['level']}")
print(f"Confidence: {result['confidence']}")
print(f"All Levels: {result['all_levels']}")

# Test the response format
level_descriptions = {
    'Remembering': 'This question requires recalling facts and basic concepts. It tests your ability to remember and recognize information.',
    'Understanding': 'This question requires explaining ideas and concepts. It tests your ability to comprehend and interpret information.',
    'Applying': 'This question requires using information in new situations. It tests your ability to apply knowledge to solve problems.',
    'Analyzing': 'This question requires drawing connections among ideas. It tests your ability to break down information and examine relationships.',
    'Evaluating': 'This question requires justifying a stand or decision. It tests your ability to assess and judge information.',
    'Creating': 'This question requires producing new or original work. It tests your ability to generate, design, and construct new ideas.'
}

response_data = {
    'success': True,
    'level': result['level'],
    'confidence': max(result['confidence'] * 10, 10),
    'description': level_descriptions.get(result['level'], 'This question has been classified based on Bloom\'s Taxonomy levels.')
}

print(f"\nResponse Data: {response_data}")
