#!/usr/bin/env python3
"""
PHP Quiz Data to MySQL Relational Tables Converter

This script converts PHP-serialized quiz data from a single table to multiple 
relational tables (quizzes, questions, question_options, quiz_questions).

Author: AI Assistant
Requirements: pymysql, phpserialize
"""

import pymysql
import phpserialize
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sys
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quiz_conversion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QuizData:
    """Data class to hold parsed quiz information"""
    question_id: int
    title: str
    quiz_id: int
    question_type: str
    selected_answers: List[int]
    answers: List[Dict[str, Any]]
    extra_text: str
    tooltip: str = ""
    featured_image: str = ""

class QuizConverter:
    """Main converter class for PHP quiz data to MySQL relational tables"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with database configuration"""
        self.config = config
        self.connection = None
        self.processed_questions = set()  # Track processed question IDs
        self.processed_quizzes = set()    # Track processed quiz IDs
        
    def connect_database(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            logger.info("Database connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def close_database(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def parse_php_data(self, php_serialized_data: str) -> Optional[QuizData]:
        """Parse PHP serialized data into QuizData object"""
        try:
            # Decode PHP serialized data
            data = phpserialize.loads(php_serialized_data.encode('utf-8'))
            
            # Extract required fields with defaults
            question_id = int(data.get('question_id', {}).get('value', 0))
            title = data.get('title', {}).get('value', '')
            quiz_id = int(data.get('quiz_id', {}).get('value', 0))
            question_type = data.get('question_type', {}).get('value', '')
            
            # Parse selected answers (correct answers)
            selected_raw = data.get('selected', {}).get('value', [])
            selected_answers = []
            if isinstance(selected_raw, dict):
                selected_answers = [int(v) for v in selected_raw.values() if str(v).isdigit()]
            elif isinstance(selected_raw, list):
                selected_answers = [int(v) for v in selected_raw if str(v).isdigit()]
            
            # Parse answers/options
            answers_raw = data.get('answers', {}).get('value', {})
            answers = []
            if isinstance(answers_raw, dict):
                for key, answer_data in answers_raw.items():
                    if isinstance(answer_data, dict) and answer_data.get('answer', '').strip():
                        answers.append({
                            'index': int(key),
                            'text': answer_data.get('answer', '').strip(),
                            'image': answer_data.get('image', 0)
                        })
            
            # Extract extra fields
            extra_text = data.get('extra_text', {}).get('value', '')
            tooltip = data.get('tooltip', {}).get('value', '')
            featured_image = data.get('featured_image', {}).get('value', '')
            
            return QuizData(
                question_id=question_id,
                title=title,
                quiz_id=quiz_id,
                question_type=question_type,
                selected_answers=selected_answers,
                answers=answers,
                extra_text=extra_text,
                tooltip=tooltip,
                featured_image=featured_image
            )
            
        except Exception as e:
            logger.error(f"Failed to parse PHP data: {e}")
            return None
    
    def insert_quiz(self, quiz_id: int, title: str) -> int:
        """Insert or get quiz record, return database ID"""
        try:
            cursor = self.connection.cursor()
            
            # Check if quiz already exists
            cursor.execute("SELECT id FROM quizzes WHERE quiz_id = %s", (quiz_id,))
            result = cursor.fetchone()
            
            if result:
                return result['id']
            
            # Create slug from title
            slug = title.lower().replace(' ', '-').replace('?', '').replace(',', '')[:255]
            
            # Insert new quiz
            cursor.execute("""
                INSERT INTO quizzes (quiz_id, slug, title, created_at) 
                VALUES (%s, %s, %s, %s)
            """, (quiz_id, slug, title, datetime.now()))
            
            quiz_db_id = cursor.lastrowid
            self.processed_quizzes.add(quiz_id)
            logger.info(f"Inserted quiz: {quiz_id} -> DB ID: {quiz_db_id}")
            return quiz_db_id
            
        except Exception as e:
            logger.error(f"Failed to insert quiz {quiz_id}: {e}")
            raise
    
    def insert_question(self, quiz_data: QuizData) -> int:
        """Insert or get question record, return database ID"""
        try:
            cursor = self.connection.cursor()
            
            # Check if question already exists
            cursor.execute("SELECT id FROM questions WHERE question_id = %s", (quiz_data.question_id,))
            result = cursor.fetchone()
            
            if result:
                return result['id']
            
            # Prepare explanation data
            explanation = quiz_data.extra_text if quiz_data.extra_text else None
            explanation_image = quiz_data.featured_image if quiz_data.featured_image else None
            
            # Insert new question
            cursor.execute("""
                INSERT INTO questions (question_id, text, explanation, explanation_image, created_at) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                quiz_data.question_id,
                quiz_data.title,
                explanation,
                explanation_image,
                datetime.now()
            ))
            
            question_db_id = cursor.lastrowid
            self.processed_questions.add(quiz_data.question_id)
            logger.info(f"Inserted question: {quiz_data.question_id} -> DB ID: {question_db_id}")
            return question_db_id
            
        except Exception as e:
            logger.error(f"Failed to insert question {quiz_data.question_id}: {e}")
            raise
    
    def insert_question_options(self, question_db_id: int, quiz_data: QuizData):
        """Insert question options"""
        try:
            cursor = self.connection.cursor()
            
            # Delete existing options for this question
            cursor.execute("DELETE FROM question_options WHERE question_id = %s", (question_db_id,))
            
            # Insert new options
            for answer in quiz_data.answers:
                is_correct = answer['index'] in quiz_data.selected_answers
                
                cursor.execute("""
                    INSERT INTO question_options (question_id, option_text, is_correct) 
                    VALUES (%s, %s, %s)
                """, (question_db_id, answer['text'], is_correct))
            
            logger.info(f"Inserted {len(quiz_data.answers)} options for question DB ID: {question_db_id}")
            
        except Exception as e:
            logger.error(f"Failed to insert options for question {question_db_id}: {e}")
            raise
    
    def insert_quiz_question_mapping(self, quiz_db_id: int, question_db_id: int, position: Optional[int] = None):
        """Insert quiz-question mapping"""
        try:
            cursor = self.connection.cursor()
            
            # Check if mapping already exists
            cursor.execute("""
                SELECT id FROM quiz_questions 
                WHERE quiz_id = %s AND question_id = %s
            """, (quiz_db_id, question_db_id))
            
            if cursor.fetchone():
                return  # Mapping already exists
            
            # Insert new mapping
            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, question_id, position) 
                VALUES (%s, %s, %s)
            """, (quiz_db_id, question_db_id, position))
            
            logger.debug(f"Mapped quiz {quiz_db_id} -> question {question_db_id}")
            
        except Exception as e:
            logger.error(f"Failed to insert quiz-question mapping: {e}")
            raise
    
    def process_single_record(self, record: Dict[str, Any]) -> bool:
        """Process a single database record"""
        try:
            # Assume the PHP serialized data is in a column (adjust column name as needed)
            php_data = record.get('serialized_data', '') or record.get('data', '') or record.get('meta_value', '')
            
            if not php_data:
                logger.warning(f"No serialized data found in record ID: {record.get('id', 'unknown')}")
                return False
            
            # Parse PHP data
            quiz_data = self.parse_php_data(php_data)
            if not quiz_data:
                return False
            
            # Validate required fields
            if not quiz_data.question_id or not quiz_data.title or not quiz_data.quiz_id:
                logger.warning(f"Missing required fields in record: {record.get('id', 'unknown')}")
                return False
            
            # Start transaction
            cursor = self.connection.cursor()
            
            try:
                # Insert quiz (if not exists)
                quiz_db_id = self.insert_quiz(quiz_data.quiz_id, quiz_data.title)
                
                # Insert question (if not exists)
                question_db_id = self.insert_question(quiz_data)
                
                # Insert question options
                if quiz_data.answers:
                    self.insert_question_options(question_db_id, quiz_data)
                
                # Insert quiz-question mapping
                self.insert_quiz_question_mapping(quiz_db_id, question_db_id)
                
                # Commit transaction
                self.connection.commit()
                return True
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"Transaction failed for record {record.get('id', 'unknown')}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process record {record.get('id', 'unknown')}: {e}")
            return False
    
    def fetch_and_convert(self, source_table: str, source_column: str, batch_size: int = 1000):
        """Fetch data from source table and convert to relational format"""
        try:
            cursor = self.connection.cursor()
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM {source_table}")
            total_records = cursor.fetchone()['total']
            logger.info(f"Total records to process: {total_records}")
            
            processed = 0
            failed = 0
            
            # Process in batches
            offset = 0
            while offset < total_records:
                logger.info(f"Processing batch: {offset + 1} to {min(offset + batch_size, total_records)}")
                
                # Fetch batch
                cursor.execute(f"""
                    SELECT id, {source_column} as serialized_data 
                    FROM {source_table} 
                    ORDER BY id 
                    LIMIT %s OFFSET %s
                """, (batch_size, offset))
                
                records = cursor.fetchall()
                
                # Process each record
                for record in records:
                    if self.process_single_record(record):
                        processed += 1
                    else:
                        failed += 1
                    
                    if (processed + failed) % 100 == 0:
                        logger.info(f"Progress: {processed + failed}/{total_records} "
                                  f"(Success: {processed}, Failed: {failed})")
                
                offset += batch_size
            
            logger.info(f"Conversion completed! Total: {processed + failed}, "
                       f"Success: {processed}, Failed: {failed}")
            logger.info(f"Unique questions processed: {len(self.processed_questions)}")
            logger.info(f"Unique quizzes processed: {len(self.processed_quizzes)}")
            
        except Exception as e:
            logger.error(f"Failed to fetch and convert data: {e}")
            raise

def main():
    """Main function"""
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'your_database'
    }
    
    # Source table configuration
    source_table = 'wp_postmeta'  # Adjust this to your actual table name
    source_column = 'meta_value'  # Adjust this to your actual column name
    
    # Initialize converter
    converter = QuizConverter(config)
    
    try:
        # Connect to database
        if not converter.connect_database():
            sys.exit(1)
        
        # Run conversion
        converter.fetch_and_convert(source_table, source_column, batch_size=500)
        
    except KeyboardInterrupt:
        logger.info("Conversion interrupted by user")
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)
    finally:
        converter.close_database()

if __name__ == "__main__":
    main()