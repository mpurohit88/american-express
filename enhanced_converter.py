#!/usr/bin/env python3
"""
Enhanced PHP Quiz Data to MySQL Relational Tables Converter

This script provides additional features like:
- Environment variable support
- Better error handling
- Progress tracking
- Data validation
- Flexible configuration

Author: AI Assistant
"""

import pymysql
import phpserialize
import logging
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import re
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import configuration
from config import DATABASE_CONFIG, SOURCE_CONFIG, PROCESSING_CONFIG, QUIZ_CONFIG

@dataclass
class QuizData:
    """Enhanced data class to hold parsed quiz information"""
    question_id: int
    title: str
    quiz_id: int
    question_type: str
    selected_answers: List[int] = field(default_factory=list)
    answers: List[Dict[str, Any]] = field(default_factory=list)
    extra_text: str = ""
    tooltip: str = ""
    featured_image: str = ""
    paginate: bool = False
    
    def __post_init__(self):
        """Validate and clean data after initialization"""
        self.title = self.clean_text(self.title)
        self.extra_text = self.clean_html(self.extra_text)
        
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and validate text content"""
        if not text:
            return ""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', str(text)).strip()
        # Limit length
        return text[:QUIZ_CONFIG['max_title_length']]
    
    @staticmethod
    def clean_html(html: str) -> str:
        """Clean HTML content but preserve structure"""
        if not html:
            return ""
        # Basic HTML cleaning - you might want to use BeautifulSoup for more advanced cleaning
        html = str(html).strip()
        return html

class DatabaseManager:
    """Database connection and transaction manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            # Override config with environment variables if available
            config = {
                'host': os.getenv('DB_HOST', self.config['host']),
                'user': os.getenv('DB_USER', self.config['user']),
                'password': os.getenv('DB_PASSWORD', self.config['password']),
                'database': os.getenv('DB_NAME', self.config['database']),
                'port': int(os.getenv('DB_PORT', self.config.get('port', 3306))),
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor,
                'autocommit': False
            }
            
            self.connection = pymysql.connect(**config)
            logging.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Execute a query with error handling"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except Exception as e:
            logging.error(f"Query execution failed: {query[:100]}... Error: {e}")
            raise
    
    def commit(self):
        """Commit transaction"""
        self.connection.commit()
        
    def rollback(self):
        """Rollback transaction"""
        self.connection.rollback()

class EnhancedQuizConverter:
    """Enhanced converter with better error handling and features"""
    
    def __init__(self, db_config: Dict[str, Any], source_config: Dict[str, Any]):
        self.db_config = db_config
        self.source_config = source_config
        self.stats = {
            'processed': 0,
            'failed': 0,
            'questions_created': 0,
            'quizzes_created': 0,
            'options_created': 0,
            'mappings_created': 0
        }
        self.processed_questions = set()
        self.processed_quizzes = set()
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup enhanced logging"""
        log_level = getattr(logging, PROCESSING_CONFIG['log_level'].upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(PROCESSING_CONFIG['log_file']),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def parse_php_data(self, php_serialized_data: str) -> Optional[QuizData]:
        """Enhanced PHP data parsing with better error handling"""
        try:
            if not php_serialized_data or not php_serialized_data.strip():
                return None
                
            # Handle different encodings
            if isinstance(php_serialized_data, str):
                php_serialized_data = php_serialized_data.encode('utf-8', errors='ignore')
            
            # Decode PHP serialized data
            data = phpserialize.loads(php_serialized_data)
            
            if not isinstance(data, dict):
                self.logger.warning("PHP data is not a dictionary")
                return None
            
            # Extract and validate required fields
            question_id = self._extract_field(data, 'question_id', int, 0)
            title = self._extract_field(data, 'title', str, '')
            quiz_id = self._extract_field(data, 'quiz_id', int, 0)
            question_type = self._extract_field(data, 'question_type', str, QUIZ_CONFIG['default_question_type'])
            
            # Validate required fields
            if not question_id or not title.strip() or not quiz_id:
                self.logger.warning(f"Invalid required fields: qid={question_id}, title='{title[:50]}', quiz_id={quiz_id}")
                return None
            
            # Parse selected answers (correct answers)
            selected_answers = self._parse_selected_answers(data.get('selected', {}))
            
            # Parse answers/options
            answers = self._parse_answers(data.get('answers', {}))
            
            # Extract optional fields
            extra_text = self._extract_field(data, 'extra_text', str, '')
            tooltip = self._extract_field(data, 'tooltip', str, '')
            featured_image = self._extract_field(data, 'featured_image', str, '')
            
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
            self.logger.error(f"Failed to parse PHP data: {e}")
            self.logger.debug(f"Problematic data: {php_serialized_data[:200]}...")
            return None
    
    def _extract_field(self, data: dict, field_name: str, field_type: type, default_value: Any) -> Any:
        """Extract and validate field from PHP data structure"""
        try:
            field_data = data.get(field_name, {})
            if isinstance(field_data, dict) and 'value' in field_data:
                value = field_data['value']
                if field_type == int:
                    return int(value) if str(value).isdigit() else default_value
                elif field_type == str:
                    return str(value).strip() if value else default_value
                else:
                    return value
            return default_value
        except (ValueError, TypeError):
            return default_value
    
    def _parse_selected_answers(self, selected_data: dict) -> List[int]:
        """Parse selected answers (correct answer indices)"""
        try:
            value = selected_data.get('value', [])
            selected_answers = []
            
            if isinstance(value, dict):
                selected_answers = [int(v) for v in value.values() if str(v).isdigit()]
            elif isinstance(value, list):
                selected_answers = [int(v) for v in value if str(v).isdigit()]
            
            return selected_answers
        except Exception:
            return []
    
    def _parse_answers(self, answers_data: dict) -> List[Dict[str, Any]]:
        """Parse answer options"""
        try:
            value = answers_data.get('value', {})
            answers = []
            
            if isinstance(value, dict):
                for key, answer_data in value.items():
                    if isinstance(answer_data, dict):
                        answer_text = answer_data.get('answer', '').strip()
                        if answer_text:  # Only include non-empty answers
                            answers.append({
                                'index': int(key),
                                'text': answer_text,
                                'image': answer_data.get('image', 0)
                            })
            
            return answers
        except Exception:
            return []
    
    def create_quiz_slug(self, title: str) -> str:
        """Create URL-friendly slug from title"""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        # Replace spaces with hyphens
        slug = re.sub(r'[-\s]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        # Limit length
        return slug[:QUIZ_CONFIG['max_slug_length']]
    
    def run_conversion(self, batch_size: int = None):
        """Run the complete conversion process"""
        batch_size = batch_size or PROCESSING_CONFIG['batch_size']
        
        with DatabaseManager(self.db_config) as db:
            try:
                self._convert_data(db, batch_size)
                self._print_statistics()
                
            except KeyboardInterrupt:
                self.logger.info("Conversion interrupted by user")
                db.rollback()
            except Exception as e:
                self.logger.error(f"Conversion failed: {e}")
                db.rollback()
                raise
    
    def _convert_data(self, db: DatabaseManager, batch_size: int):
        """Convert data from source table to relational tables"""
        # Build query with optional filter
        base_query = f"SELECT {self.source_config['id_column']}, {self.source_config['data_column']} FROM {self.source_config['table_name']}"
        
        if 'filter_condition' in self.source_config:
            base_query += f" WHERE {self.source_config['filter_condition']}"
        
        # Get total count
        count_query = base_query.replace(f"SELECT {self.source_config['id_column']}, {self.source_config['data_column']}", "SELECT COUNT(*)")
        cursor = db.execute_query(count_query)
        total_records = cursor.fetchone()['COUNT(*)']
        
        self.logger.info(f"Total records to process: {total_records}")
        
        # Process in batches
        offset = 0
        while offset < total_records:
            self.logger.info(f"Processing batch: {offset + 1} to {min(offset + batch_size, total_records)}")
            
            # Fetch batch
            query = f"{base_query} ORDER BY {self.source_config['id_column']} LIMIT {batch_size} OFFSET {offset}"
            cursor = db.execute_query(query)
            records = cursor.fetchall()
            
            # Process batch
            for record in records:
                self._process_record(db, record)
            
            offset += batch_size
            
            # Progress update
            self.logger.info(f"Progress: {min(offset, total_records)}/{total_records} "
                           f"(Success: {self.stats['processed']}, Failed: {self.stats['failed']})")
    
    def _process_record(self, db: DatabaseManager, record: Dict[str, Any]):
        """Process a single record"""
        try:
            # Get serialized data
            serialized_data = record.get(self.source_config['data_column'], '')
            
            if not serialized_data:
                self.stats['failed'] += 1
                return
            
            # Parse PHP data
            quiz_data = self.parse_php_data(serialized_data)
            if not quiz_data:
                self.stats['failed'] += 1
                return
            
            # Process with transaction
            if PROCESSING_CONFIG['enable_transaction']:
                try:
                    self._insert_quiz_data(db, quiz_data)
                    db.commit()
                    self.stats['processed'] += 1
                except Exception as e:
                    db.rollback()
                    self.logger.error(f"Transaction failed for record {record.get(self.source_config['id_column'])}: {e}")
                    self.stats['failed'] += 1
            else:
                self._insert_quiz_data(db, quiz_data)
                self.stats['processed'] += 1
                
        except Exception as e:
            self.logger.error(f"Failed to process record {record.get(self.source_config['id_column'])}: {e}")
            self.stats['failed'] += 1
    
    def _insert_quiz_data(self, db: DatabaseManager, quiz_data: QuizData):
        """Insert quiz data into relational tables"""
        # Insert quiz
        quiz_db_id = self._insert_quiz(db, quiz_data.quiz_id, quiz_data.title)
        
        # Insert question
        question_db_id = self._insert_question(db, quiz_data)
        
        # Insert options
        if quiz_data.answers:
            self._insert_question_options(db, question_db_id, quiz_data)
        
        # Insert quiz-question mapping
        self._insert_quiz_question_mapping(db, quiz_db_id, question_db_id)
    
    def _insert_quiz(self, db: DatabaseManager, quiz_id: int, title: str) -> int:
        """Insert or get quiz record"""
        if PROCESSING_CONFIG['skip_duplicates'] and quiz_id in self.processed_quizzes:
            cursor = db.execute_query("SELECT id FROM quizzes WHERE quiz_id = %s", (quiz_id,))
            result = cursor.fetchone()
            return result['id'] if result else None
        
        # Check if exists
        cursor = db.execute_query("SELECT id FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        result = cursor.fetchone()
        
        if result:
            self.processed_quizzes.add(quiz_id)
            return result['id']
        
        # Insert new quiz
        slug = self.create_quiz_slug(title)
        cursor = db.execute_query("""
            INSERT INTO quizzes (quiz_id, slug, title, created_at) 
            VALUES (%s, %s, %s, %s)
        """, (quiz_id, slug, title, datetime.now()))
        
        quiz_db_id = cursor.lastrowid
        self.processed_quizzes.add(quiz_id)
        self.stats['quizzes_created'] += 1
        return quiz_db_id
    
    def _insert_question(self, db: DatabaseManager, quiz_data: QuizData) -> int:
        """Insert or get question record"""
        if PROCESSING_CONFIG['skip_duplicates'] and quiz_data.question_id in self.processed_questions:
            cursor = db.execute_query("SELECT id FROM questions WHERE question_id = %s", (quiz_data.question_id,))
            result = cursor.fetchone()
            return result['id'] if result else None
        
        # Check if exists
        cursor = db.execute_query("SELECT id FROM questions WHERE question_id = %s", (quiz_data.question_id,))
        result = cursor.fetchone()
        
        if result:
            self.processed_questions.add(quiz_data.question_id)
            return result['id']
        
        # Insert new question
        cursor = db.execute_query("""
            INSERT INTO questions (question_id, text, explanation, explanation_image, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (
            quiz_data.question_id,
            quiz_data.title,
            quiz_data.extra_text or None,
            quiz_data.featured_image or None,
            datetime.now()
        ))
        
        question_db_id = cursor.lastrowid
        self.processed_questions.add(quiz_data.question_id)
        self.stats['questions_created'] += 1
        return question_db_id
    
    def _insert_question_options(self, db: DatabaseManager, question_db_id: int, quiz_data: QuizData):
        """Insert question options"""
        # Delete existing options
        db.execute_query("DELETE FROM question_options WHERE question_id = %s", (question_db_id,))
        
        # Insert new options
        for answer in quiz_data.answers:
            is_correct = answer['index'] in quiz_data.selected_answers
            
            db.execute_query("""
                INSERT INTO question_options (question_id, option_text, is_correct) 
                VALUES (%s, %s, %s)
            """, (question_db_id, answer['text'], is_correct))
            
            self.stats['options_created'] += 1
    
    def _insert_quiz_question_mapping(self, db: DatabaseManager, quiz_db_id: int, question_db_id: int):
        """Insert quiz-question mapping"""
        # Check if mapping exists
        cursor = db.execute_query("""
            SELECT id FROM quiz_questions 
            WHERE quiz_id = %s AND question_id = %s
        """, (quiz_db_id, question_db_id))
        
        if cursor.fetchone():
            return  # Mapping already exists
        
        # Insert new mapping
        db.execute_query("""
            INSERT INTO quiz_questions (quiz_id, question_id, position) 
            VALUES (%s, %s, %s)
        """, (quiz_db_id, question_db_id, None))
        
        self.stats['mappings_created'] += 1
    
    def _print_statistics(self):
        """Print conversion statistics"""
        self.logger.info("=" * 50)
        self.logger.info("CONVERSION COMPLETED!")
        self.logger.info("=" * 50)
        self.logger.info(f"Total records processed: {self.stats['processed']}")
        self.logger.info(f"Failed records: {self.stats['failed']}")
        self.logger.info(f"Quizzes created: {self.stats['quizzes_created']}")
        self.logger.info(f"Questions created: {self.stats['questions_created']}")
        self.logger.info(f"Options created: {self.stats['options_created']}")
        self.logger.info(f"Quiz-Question mappings created: {self.stats['mappings_created']}")
        self.logger.info(f"Unique questions: {len(self.processed_questions)}")
        self.logger.info(f"Unique quizzes: {len(self.processed_quizzes)}")
        self.logger.info("=" * 50)

def main():
    """Main function"""
    print("PHP Quiz Data to MySQL Converter")
    print("=" * 40)
    
    # Initialize converter
    converter = EnhancedQuizConverter(DATABASE_CONFIG, SOURCE_CONFIG)
    
    try:
        # Run conversion
        converter.run_conversion()
        
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()