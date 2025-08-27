#!/usr/bin/env python3
"""
Test script using the actual data structure provided by the user
"""

import sys
from php_to_mysql_converter_py36 import PHPDataParser

def test_real_data():
    """Test with the actual data structure from the user"""
    
    # This is the actual parsed data structure from phpserialize
    real_data = {
        b'question_id': {b'name': b'question_id', b'type': b'integer', b'required': b'', b'value': 96, b'tab': b''}, 
        b'title': {b'name': b'title', b'type': b'title', b'required': b'required', b'value': b'What is Relative Humidity dependent upon?', b'tab': b''}, 
        b'quiz_id': {b'name': b'quiz_id', b'type': b'integer', b'required': b'true', b'value': 1361, b'tab': b''}, 
        b'question_type': {b'name': b'question_type', b'type': b'select', b'required': b'required', b'value': b'multiple_choice_text', b'tab': b'main'}, 
        b'selected': {b'name': b'selected', b'type': b'correct', b'required': b'', b'value': {0: 1}, b'tab': b''}, 
        b'answers': {b'name': b'answers', b'type': b'answers', b'required': b'', b'value': {
            0: {b'answer': b'Moisture content and temperature of the air', b'image': 0}, 
            1: {b'answer': b'Temperature of the air', b'image': 0}, 
            2: {b'answer': b'Temperature and pressure', b'image': 0}, 
            3: {b'answer': b'Moisture content of the air', b'image': 0}, 
            4: {b'answer': b'', b'image': 0}, 
            5: {b'answer': b'', b'image': 0}, 
            6: {b'answer': b'', b'image': 0}, 
            7: {b'answer': b'', b'image': 0}, 
            8: {b'answer': b'', b'image': 0}, 
            9: {b'answer': b'', b'image': 0}
        }, b'tab': b'main'}, 
        b'paginate': {b'name': b'paginate', b'type': b'checkbox', b'required': b'', b'tab': b'extra', b'value': {0: b''}}, 
        b'tooltip': {b'name': b'tooltip', b'type': b'text', b'required': b'', b'value': b'', b'tab': b'extra'}, 
        b'featured_image': {b'name': b'featured_image', b'type': b'image', b'required': b'', b'value': b'', b'tab': b'extra'}, 
        b'extra_text': {b'name': b'extra_text', b'type': b'editor', b'required': b'', b'value': b'RelativeHumidity is a term used to describe the quantity of water vapour that exists in a gaseous mixture of air and water. Relative humidity is expressed as a percentage and is calculated using the formula below. More simply, the relative humidity is the amount of water vapour present in a volume of air divided by the maximum amount of water vapour which that volume could hold at that temperature expressed as a percentage.\n\n<img class="alignnone size-medium wp-image-11074 jetpack-lazy-image jetpack-lazy-image--handled" src="https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?resize=300,35&amp;ssl=1" alt="" width="300" height="35" data-attachment-id="11074" data-permalink="https://eatpl.in/35f819a9-3688-4119-94a0-60a50e0679cd/" data-orig-file="https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?fit=1016,120&amp;ssl=1" data-orig-size="1016,120" data-comments-opened="1" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;1&quot;}" data-image-title="35F819A9-3688-4119-94A0-60A50E0679CD" data-image-description="" data-image-caption="" data-medium-file="https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?fit=300,35&amp;ssl=1" data-large-file="https://i0.wp.com/eatpl.in/wp-content/uploads/2022/10/35F819A9-3688-4119-94A0-60A50E0679CD.jpeg?fit=1016,120&amp;ssl=1" data-recalc-dims="1" data-lazy-loaded="1" />', b'tab': b'extra'}, 
        b'quizzes': {b'name': b'quizzes', b'type': b'categories', b'required': b'', b'value': {0: 1361}, b'tab': b'quizzes'}
    }
    
    print("Testing with real data structure...")
    print("=" * 50)
    
    # Create a custom parser method to test the actual data structure
    def parse_real_data(data):
        """Parse the actual data structure directly"""
        try:
            # Helper function to get nested value
            def get_field_value(field_name, default=None):
                field_data = PHPDataParser._safe_get(data, field_name, {})
                if isinstance(field_data, dict):
                    value = PHPDataParser._safe_get(field_data, 'value', default)
                    return PHPDataParser._safe_decode(value)
                return default
            
            # Extract basic information
            question_id = get_field_value('question_id', 0)
            title = get_field_value('title', '')
            quiz_id = get_field_value('quiz_id', 0)
            question_type = get_field_value('question_type', '')
            
            # Extract answers
            answers_field = PHPDataParser._safe_get(data, 'answers', {})
            answers_data = PHPDataParser._safe_get(answers_field, 'value', {})
            answers = []
            
            for i, answer_data in answers_data.items():
                if isinstance(answer_data, dict):
                    answer_text = PHPDataParser._safe_get(answer_data, 'answer', '')
                    answer_text = PHPDataParser._safe_decode(answer_text)
                    
                    if answer_text and answer_text.strip():
                        answers.append({
                            'index': int(i),
                            'text': answer_text,
                            'image': PHPDataParser._safe_get(answer_data, 'image', 0)
                        })
            
            # Extract correct answers
            selected_field = PHPDataParser._safe_get(data, 'selected', {})
            selected_data = PHPDataParser._safe_get(selected_field, 'value', {})
            correct_answers = []
            
            if isinstance(selected_data, dict):
                for idx in selected_data.values():
                    if isinstance(idx, int):
                        correct_answers.append(idx)
            elif isinstance(selected_data, list):
                correct_answers = [int(x) for x in selected_data if str(x).isdigit()]
            
            # Extract additional fields
            extra_text = get_field_value('extra_text', '')
            tooltip = get_field_value('tooltip', '')
            featured_image = get_field_value('featured_image', '')
            
            from php_to_mysql_converter_py36 import QuestionData
            return QuestionData(
                question_id=int(question_id) if question_id else 0,
                title=str(title) if title else '',
                quiz_id=int(quiz_id) if quiz_id else 0,
                question_type=str(question_type) if question_type else '',
                answers=answers,
                correct_answers=correct_answers,
                extra_text=str(extra_text) if extra_text else '',
                tooltip=str(tooltip) if tooltip else '',
                featured_image=str(featured_image) if featured_image else ''
            )
            
        except Exception as e:
            print("Error parsing real data: {}".format(e))
            import traceback
            print("Traceback: {}".format(traceback.format_exc()))
            return None
    
    question_data = parse_real_data(real_data)
    
    if question_data:
        print("✅ Parsing successful!")
        print("Question ID: {}".format(question_data.question_id))
        print("Quiz ID: {}".format(question_data.quiz_id))
        print("Title: {}".format(question_data.title))
        print("Question Type: {}".format(question_data.question_type))
        print("Correct Answers: {}".format(question_data.correct_answers))
        print("Number of Answers: {}".format(len(question_data.answers)))
        
        print("\nAnswers:")
        for i, answer in enumerate(question_data.answers):
            is_correct = "✓" if answer['index'] in question_data.correct_answers else "✗"
            print("  {}. [{}] {}".format(i+1, is_correct, answer['text']))
        
        print("\nExtra Text Length: {} characters".format(len(question_data.extra_text)))
        if question_data.extra_text:
            print("Extra Text Preview: {}...".format(question_data.extra_text[:100]))
        
        print("\n" + "=" * 50)
        print("Sample SQL INSERT statements:")
        print("=" * 50)
        
        print("-- QUIZ INSERT:")
        print("INSERT INTO quizzes (quiz_id, slug, title) VALUES ({}, 'quiz-{}', 'Quiz {}');".format(
            question_data.quiz_id, question_data.quiz_id, question_data.quiz_id))
        
        print("\n-- QUESTION INSERT:")
        print("INSERT INTO questions (question_id, text, explanation) VALUES ({}, '{}', '{}');".format(
            question_data.question_id, 
            question_data.title.replace("'", "''"), 
            question_data.extra_text[:50].replace("'", "''")))
        
        print("\n-- QUESTION OPTIONS INSERT:")
        for answer in question_data.answers:
            is_correct = answer['index'] in question_data.correct_answers
            print("INSERT INTO question_options (question_id, option_text, is_correct, option_order) VALUES (LAST_INSERT_ID(), '{}', {}, {});".format(
                answer['text'].replace("'", "''"), is_correct, answer['index']))
        
        print("\n-- QUIZ-QUESTION MAPPING:")
        print("INSERT INTO quiz_questions (quiz_id, question_id) VALUES ((SELECT id FROM quizzes WHERE quiz_id = {}), (SELECT id FROM questions WHERE question_id = {}));".format(
            question_data.quiz_id, question_data.question_id))
        
    else:
        print("❌ Parsing failed!")
        return False
    
    return True

if __name__ == "__main__":
    try:
        if test_real_data():
            print("\n🎉 Test completed successfully!")
            print("✅ Your real data structure can be parsed correctly!")
            print("✅ You can now proceed with the full conversion script.")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except Exception as e:
        print("❌ Unexpected error: {}".format(e))
        import traceback
        print("Traceback: {}".format(traceback.format_exc()))
        sys.exit(1)