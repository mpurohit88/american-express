#!/usr/bin/env python3
"""
Test script to verify PHP serialized data parsing
"""

import sys
from php_to_mysql_converter import PHPDataParser

def test_sample_data():
    """Test with the sample data provided"""
    sample_data = '''a:11:{s:11:"question_id";a:5:{s:4:"name";s:11:"question_id";s:4:"type";s:7:"integer";s:8:"required";s:0:"";s:5:"value";i:96;s:3:"tab";s:0:"";}s:5:"title";a:5:{s:4:"name";s:5:"title";s:4:"type";s:5:"title";s:8:"required";s:8:"required";s:5:"value";s:41:"What is Relative Humidity dependent upon?";s:3:"tab";s:0:"";}s:7:"quiz_id";a:5:{s:4:"name";s:7:"quiz_id";s:4:"type";s:7:"integer";s:8:"required";s:4:"true";s:5:"value";i:1361;s:3:"tab";s:0:"";}s:13:"question_type";a:5:{s:4:"name";s:13:"question_type";s:4:"type";s:6:"select";s:8:"required";s:8:"required";s:5:"value";s:20:"multiple_choice_text";s:3:"tab";s:4:"main";}s:8:"selected";a:5:{s:4:"name";s:8:"selected";s:4:"type";s:7:"correct";s:8:"required";s:0:"";s:5:"value";a:1:{i:0;i:1;}s:3:"tab";s:0:"";}s:7:"answers";a:5:{s:4:"name";s:7:"answers";s:4:"type";s:7:"answers";s:8:"required";s:0:"";s:5:"value";a:10:{i:0;a:2:{s:6:"answer";s:43:"Moisture content and temperature of the air";s:5:"image";i:0;}i:1;a:2:{s:6:"answer";s:22:"Temperature of the air";s:5:"image";i:0;}i:2;a:2:{s:6:"answer";s:24:"Temperature and pressure";s:5:"image";i:0;}i:3;a:2:{s:6:"answer";s:27:"Moisture content of the air";s:5:"image";i:0;}i:4;a:2:{s:6:"answer";s:0:"";s:5:"image";i:0;}i:5;a:2:{s:6:"answer";s:0:"";s:5:"image";i:0;}i:6;a:2:{s:6:"answer";s:0:"";s:5:"image";i:0;}i:7;a:2:{s:6:"answer";s:0:"";s:5:"image";i:0;}i:8;a:2:{s:6:"answer";s:0:"";s:5:"image";i:0;}i:9;a:2:{s:6:"answer";s:0:"";s:5:"image";i:0;}}s:3:"tab";s:4:"main";}s:8:"paginate";a:5:{s:4:"name";s:8:"paginate";s:4:"type";s:8:"checkbox";s:8:"required";s:0:"";s:3:"tab";s:5:"extra";s:5:"value";a:1:{i:0;s:0:"";}}s:7:"tooltip";a:5:{s:4:"name";s:7:"tooltip";s:4:"type";s:4:"text";s:8:"required";s:0:"";s:5:"value";s:0:"";s:3:"tab";s:5:"extra";}s:14:"featured_image";a:5:{s:4:"name";s:14:"featured_image";s:4:"type";s:5:"image";s:8:"required";s:0:"";s:5:"value";s:0:"";s:3:"tab";s:5:"extra";}s:10:"extra_text";a:5:{s:4:"name";s:10:"extra_text";s:4:"type";s:6:"editor";s:8:"required";s:0:"";s:5:"value";s:1800:"Relative Humidity is a term used to describe the quantity of water vapour that exists in a gaseous mixture of air and water. Relative humidity is expressed as a percentage and is calculated using the formula below. More simply, the relative humidity is the amount of water vapour present in a volume of air divided by the maximum amount of water vapour which that volume could hold at that temperature expressed as a percentage.\n\n<img class=\"alignnone size-medium wp-image-11074 jetpack-lazy-image jetpack-lazy-image--handled\" src=\"https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?resize=300,35&amp;ssl=1\" alt=\"\" width=\"300\" height=\"35\" data-attachment-id=\"11074\" data-permalink=\"https://eatpl.in/35f819a9-3688-4119-94a0-60a50e0679cd/\" data-orig-file=\"https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?fit=1016,120&amp;ssl=1\" data-orig-size=\"1016,120\" data-comments-opened=\"1\" data-image-meta=\"{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;1&quot;}\" data-image-title=\"35F819A9-3688-4119-94A0-60A50E0679CD\" data-image-description=\"\" data-image-caption=\"\" data-medium-file=\"https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?fit=300,35&amp;ssl=1\" data-large-file=\"https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?fit=1016,120&amp;ssl=1\" data-recalc-dims=\"1\" data-lazy-loaded=\"1\" />";s:3:"tab";s:5:"extra";}s:7:"quizzes";a:5:{s:4:"name";s:7:"quizzes";s:4:"type";s:10:"categories";s:8:"required";s:0:"";s:5:"value";a:1:{i:0;i:1361;}s:3:"tab";s:7:"quizzes";}}'''
    
    print("Testing PHP serialized data parsing...")
    print("=" * 50)
    
    question_data = PHPDataParser.parse_php_data(sample_data)
    
    if question_data:
        print("✅ Parsing successful!")
        print(f"Question ID: {question_data.question_id}")
        print(f"Quiz ID: {question_data.quiz_id}")
        print(f"Title: {question_data.title}")
        print(f"Question Type: {question_data.question_type}")
        print(f"Correct Answers: {question_data.correct_answers}")
        print(f"Number of Answers: {len(question_data.answers)}")
        
        print("\nAnswers:")
        for i, answer in enumerate(question_data.answers):
            is_correct = "✓" if answer['index'] in question_data.correct_answers else "✗"
            print(f"  {i+1}. [{is_correct}] {answer['text']}")
        
        print(f"\nExtra Text Length: {len(question_data.extra_text)} characters")
        if question_data.extra_text:
            print(f"Extra Text Preview: {question_data.extra_text[:100]}...")
        
        print("\n" + "=" * 50)
        print("Sample conversion output:")
        print("=" * 50)
        
        print("QUIZ TABLE:")
        print(f"  quiz_id: {question_data.quiz_id}")
        print(f"  title: Quiz {question_data.quiz_id}")
        print(f"  slug: quiz-{question_data.quiz_id}")
        
        print("\nQUESTION TABLE:")
        print(f"  question_id: {question_data.question_id}")
        print(f"  text: {question_data.title}")
        print(f"  explanation: {question_data.extra_text[:50]}..." if question_data.extra_text else "  explanation: NULL")
        
        print("\nQUESTION_OPTIONS TABLE:")
        for answer in question_data.answers:
            is_correct = answer['index'] in question_data.correct_answers
            print(f"  option_text: {answer['text'][:50]}{'...' if len(answer['text']) > 50 else ''}")
            print(f"  is_correct: {is_correct}")
            print(f"  option_order: {answer['index']}")
            print("  ---")
        
    else:
        print("❌ Parsing failed!")
        return False
    
    return True

if __name__ == "__main__":
    if test_sample_data():
        print("Test completed successfully!")
        sys.exit(0)
    else:
        print("Test failed!")
        sys.exit(1)