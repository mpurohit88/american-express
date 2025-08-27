#!/usr/bin/env python3
"""
PHP Serialized Data to MySQL Relational Schema Converter (Python 3.6 Compatible)

This script converts PHP serialized quiz data from a single table 
to a normalized relational schema with separate tables for:
- quizzes
- questions  
- question_options
- quiz_questions (mapping table)
"""

import pymysql
import phpserialize
import logging
import sys
from typing import Dict, List, Any, Optional
import argparse
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuestionData:
    """Data class to hold parsed question information (Python 3.6 compatible)"""
    
    def __init__(self, question_id: int, title: str, quiz_id: int, question_type: str, 
                 answers: List[Dict[str, Any]], correct_answers: List[int], 
                 extra_text: str, tooltip: str = "", featured_image: str = ""):
        self.question_id = question_id
        self.title = title
        self.quiz_id = quiz_id
        self.question_type = question_type
        self.answers = answers
        self.correct_answers = correct_answers
        self.extra_text = extra_text
        self.tooltip = tooltip
        self.featured_image = featured_image

class DatabaseManager:
    """Handles database connections and operations"""
    
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            logger.info("Database connection established")
            return True
        except Exception as e:
            logger.error("Error connecting to database: {}".format(e))
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute a single query"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error("Error executing query: {}".format(e))
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[tuple]:
        """Fetch all results from a query"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error("Error fetching data: {}".format(e))
            return []

class PHPDataParser:
    """Handles parsing of PHP serialized data"""
    
    @staticmethod
    def _safe_get(data, key, default=None):
        """Safely get data from dict, handling both string and byte keys"""
        if isinstance(key, str):
            # Try both string and byte versions of the key
            return data.get(key, data.get(key.encode('utf-8'), default))
        return data.get(key, default)
    
    @staticmethod
    def _safe_decode(value):
        """Safely decode bytes to string"""
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value
    
    @staticmethod
    def parse_php_data(serialized_data) -> Optional[QuestionData]:
        """Parse PHP serialized data into QuestionData object"""
        try:
            # Handle different input types
            if isinstance(serialized_data, dict):
                # Data is already parsed
                data = serialized_data
            elif isinstance(serialized_data, str):
                # Data is a string, need to parse
                serialized_data = serialized_data.encode('utf-8')
                data = phpserialize.loads(serialized_data)
            elif isinstance(serialized_data, bytes):
                # Data is bytes, parse directly
                data = phpserialize.loads(serialized_data)
            else:
                logger.error("Unsupported data type: {}".format(type(serialized_data)))
                return None
            
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
            logger.error("Error parsing PHP data: {}".format(e))
            import traceback
            logger.error("Traceback: {}".format(traceback.format_exc()))
            return None

class QuizConverter:
    """Main converter class that handles the migration process"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.processed_questions = set()
        self.processed_quizzes = set()
        self.stats = {
            'total_records': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'questions_created': 0,
            'options_created': 0,
            'quizzes_created': 0,
            'mappings_created': 0
        }
    
    def create_schema(self):
        """Create the target database schema"""
        schemas = [
            """
            CREATE TABLE IF NOT EXISTS quizzes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                quiz_id INT NOT NULL UNIQUE,
                slug VARCHAR(255) NOT NULL,
                title VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_quiz_id (quiz_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id INT NOT NULL UNIQUE,
                text TEXT NOT NULL,
                explanation TEXT NULL,
                explanation_image VARCHAR(500) NULL,
                tooltip TEXT NULL,
                featured_image VARCHAR(500) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_question_id (question_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS question_options (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id INT NOT NULL,
                option_text VARCHAR(1000) NOT NULL,
                is_correct BOOLEAN DEFAULT FALSE,
                option_order INT DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                INDEX idx_question_options_qid (question_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                quiz_id INT NOT NULL,
                question_id INT NOT NULL,
                position INT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                UNIQUE KEY uq_quiz_question (quiz_id, question_id),
                INDEX idx_quiz_questions_qzid (quiz_id),
                INDEX idx_quiz_questions_qid (question_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        ]
        
        for schema in schemas:
            if not self.db.execute_query(schema):
                logger.error("Failed to create schema")
                return False
        
        logger.info("Database schema created successfully")
        return True
    
    def insert_quiz(self, quiz_id: int, title: str) -> Optional[int]:
        """Insert quiz if not exists and return quiz table ID"""
        if quiz_id in self.processed_quizzes:
            # Get existing quiz ID
            result = self.db.fetch_all(
                "SELECT id FROM quizzes WHERE quiz_id = %s", 
                (quiz_id,)
            )
            return result[0][0] if result else None
        
        # Generate slug from title
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')[:255]
        
        query = """
        INSERT IGNORE INTO quizzes (quiz_id, slug, title) 
        VALUES (%s, %s, %s)
        """
        
        if self.db.execute_query(query, (quiz_id, slug, title)):
            self.processed_quizzes.add(quiz_id)
            self.stats['quizzes_created'] += 1
            
            # Get the inserted ID
            result = self.db.fetch_all(
                "SELECT id FROM quizzes WHERE quiz_id = %s", 
                (quiz_id,)
            )
            return result[0][0] if result else None
        
        return None
    
    def insert_question(self, question_data: QuestionData) -> Optional[int]:
        """Insert question if not exists and return question table ID"""
        if question_data.question_id in self.processed_questions:
            # Get existing question ID
            result = self.db.fetch_all(
                "SELECT id FROM questions WHERE question_id = %s", 
                (question_data.question_id,)
            )
            return result[0][0] if result else None
        
        query = """
        INSERT IGNORE INTO questions 
        (question_id, text, explanation, explanation_image, tooltip, featured_image) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Clean extra_text for explanation (remove HTML if needed)
        explanation = question_data.extra_text if question_data.extra_text else None
        
        params = (
            question_data.question_id,
            question_data.title,
            explanation,
            None,  # explanation_image - can be extracted from extra_text if needed
            question_data.tooltip if question_data.tooltip else None,
            question_data.featured_image if question_data.featured_image else None
        )
        
        if self.db.execute_query(query, params):
            self.processed_questions.add(question_data.question_id)
            self.stats['questions_created'] += 1
            
            # Get the inserted ID
            result = self.db.fetch_all(
                "SELECT id FROM questions WHERE question_id = %s", 
                (question_data.question_id,)
            )
            return result[0][0] if result else None
        
        return None
    
    def insert_question_options(self, question_table_id: int, question_data: QuestionData) -> bool:
        """Insert question options"""
        query = """
        INSERT INTO question_options 
        (question_id, option_text, is_correct, option_order) 
        VALUES (%s, %s, %s, %s)
        """
        
        success_count = 0
        for answer in question_data.answers:
            is_correct = answer['index'] in question_data.correct_answers
            params = (
                question_table_id,
                answer['text'],
                is_correct,
                answer['index']
            )
            
            if self.db.execute_query(query, params):
                success_count += 1
                self.stats['options_created'] += 1
        
        return success_count == len(question_data.answers)
    
    def insert_quiz_question_mapping(self, quiz_table_id: int, question_table_id: int) -> bool:
        """Insert quiz-question mapping"""
        query = """
        INSERT IGNORE INTO quiz_questions (quiz_id, question_id) 
        VALUES (%s, %s)
        """
        
        if self.db.execute_query(query, (quiz_table_id, question_table_id)):
            self.stats['mappings_created'] += 1
            return True
        return False
    
    def process_record(self, record: tuple) -> bool:
        """Process a single record from source table"""
        try:
            # Debug: Print record structure for first few records
            if self.stats['total_records'] < 3:
                logger.info("DEBUG: Record structure - Length: {}, Types: {}".format(
                    len(record), [type(x).__name__ for x in record]
                ))
                for i, value in enumerate(record):
                    if isinstance(value, (str, bytes)) and len(str(value)) > 50:
                        logger.info("  [{}]: {} ({} chars)".format(i, str(value)[:50], len(str(value))))
                    else:
                        logger.info("  [{}]: {} ({})".format(i, value, type(value).__name__))
            
            # Try to find the serialized data column
            serialized_data = None
            data_column_index = None
            
            # Look for serialized data in each column
            for i, value in enumerate(record):
                if isinstance(value, (str, bytes)):
                    value_str = str(value)
                    # Check if this looks like PHP serialized data
                    if ('a:' in value_str and 's:' in value_str) or ('question_id' in value_str):
                        serialized_data = value
                        data_column_index = i
                        break
            
            if serialized_data is None:
                logger.error("No serialized data found in record. Record: {}".format(record[:3]))
                return False
            
            if data_column_index != 1:
                logger.info("Found serialized data in column {} (not column 1)".format(data_column_index))
            
            # Parse PHP data
            question_data = PHPDataParser.parse_php_data(serialized_data)
            if not question_data:
                logger.error("Failed to parse data from column {}".format(data_column_index))
                return False
            
            # Insert quiz
            quiz_table_id = self.insert_quiz(question_data.quiz_id, "Quiz {}".format(question_data.quiz_id))
            if not quiz_table_id:
                logger.error("Failed to insert quiz {}".format(question_data.quiz_id))
                return False
            
            # Insert question
            question_table_id = self.insert_question(question_data)
            if not question_table_id:
                logger.error("Failed to insert question {}".format(question_data.question_id))
                return False
            
            # Insert question options
            if not self.insert_question_options(question_table_id, question_data):
                logger.warning("Some options failed for question {}".format(question_data.question_id))
            
            # Insert quiz-question mapping
            self.insert_quiz_question_mapping(quiz_table_id, question_table_id)
            
            return True
            
        except Exception as e:
            logger.error("Error processing record: {}".format(e))
            return False
    
    def convert_data(self, source_table: str, batch_size: int = 100):
        """Main conversion method"""
        logger.info("Starting conversion from table: {}".format(source_table))
        
        # Get total count
        count_result = self.db.fetch_all("SELECT COUNT(*) FROM {}".format(source_table))
        total_records = count_result[0][0] if count_result else 0
        self.stats['total_records'] = total_records
        
        logger.info("Total records to process: {}".format(total_records))
        
        # Process in batches
        offset = 0
        while offset < total_records:
            logger.info("Processing batch: {} to {}".format(
                offset + 1, min(offset + batch_size, total_records)
            ))
            
            # Fetch batch - adjust column names based on your source table
            query = "SELECT * FROM {} LIMIT {} OFFSET {}".format(source_table, batch_size, offset)
            records = self.db.fetch_all(query)
            
            if not records:
                break
            
            # Process each record in the batch
            for record in records:
                if self.process_record(record):
                    self.stats['successful_conversions'] += 1
                else:
                    self.stats['failed_conversions'] += 1
            
            offset += batch_size
            
            # Log progress
            progress = (offset / total_records) * 100
            logger.info("Progress: {:.1f}% ({} successful, {} failed)".format(
                progress, self.stats['successful_conversions'], self.stats['failed_conversions']
            ))
        
        self.print_stats()
    
    def print_stats(self):
        """Print conversion statistics"""
        logger.info("=== Conversion Statistics ===")
        for key, value in self.stats.items():
            logger.info("{}: {}".format(key.replace('_', ' ').title(), value))

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Convert PHP serialized quiz data to relational schema')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--source-table', required=True, help='Source table name containing PHP serialized data')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for processing')
    parser.add_argument('--create-schema', action='store_true', help='Create target schema before conversion')
    
    args = parser.parse_args()
    
    # Initialize database manager
    db = DatabaseManager(args.host, args.user, args.password, args.database)
    
    if not db.connect():
        logger.error("Failed to connect to database")
        return 1
    
    try:
        # Initialize converter
        converter = QuizConverter(db)
        
        # Create schema if requested
        if args.create_schema:
            if not converter.create_schema():
                logger.error("Failed to create schema")
                return 1
        
        # Convert data
        converter.convert_data(args.source_table, args.batch_size)
        
        logger.info("Conversion completed successfully")
        return 0
        
    except Exception as e:
        logger.error("Conversion failed: {}".format(e))
        return 1
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    sys.exit(main())