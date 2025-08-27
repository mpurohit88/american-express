#!/usr/bin/env python3
"""
PHP Serialized Data to MySQL Relational Schema Converter

This script converts PHP serialized quiz data from a single table 
to a normalized relational schema with separate tables for:
- quizzes
- questions  
- question_options
- quiz_questions (mapping table)
"""

import mysql.connector
from mysql.connector import Error
import phpserialize
import logging
import sys
from typing import Dict, List, Any, Optional
import argparse
from dataclasses import dataclass
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

@dataclass
class QuestionData:
    """Data class to hold parsed question information"""
    question_id: int
    title: str
    quiz_id: int
    question_type: str
    answers: List[Dict[str, Any]]
    correct_answers: List[int]
    extra_text: str
    tooltip: str = ""
    featured_image: str = ""

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
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.connection.cursor(buffered=True)
            logger.info("Database connection established")
            return True
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
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
        except Error as e:
            logger.error(f"Error executing query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[tuple]:
        """Fetch all results from a query"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching data: {e}")
            return []

class PHPDataParser:
    """Handles parsing of PHP serialized data"""
    
    @staticmethod
    def parse_php_data(serialized_data: str) -> Optional[QuestionData]:
        """Parse PHP serialized data into QuestionData object"""
        try:
            # Handle potential encoding issues
            if isinstance(serialized_data, str):
                serialized_data = serialized_data.encode('utf-8')
            
            data = phpserialize.loads(serialized_data)
            
            # Extract basic information
            question_id = data.get('question_id', {}).get('value', 0)
            title = data.get('title', {}).get('value', '')
            quiz_id = data.get('quiz_id', {}).get('value', 0)
            question_type = data.get('question_type', {}).get('value', '')
            
            # Extract answers
            answers_data = data.get('answers', {}).get('value', {})
            answers = []
            for i, answer_data in answers_data.items():
                if isinstance(answer_data, dict) and answer_data.get('answer', '').strip():
                    answers.append({
                        'index': int(i),
                        'text': answer_data.get('answer', ''),
                        'image': answer_data.get('image', 0)
                    })
            
            # Extract correct answers
            selected_data = data.get('selected', {}).get('value', {})
            correct_answers = []
            if isinstance(selected_data, dict):
                for idx in selected_data.values():
                    if isinstance(idx, int):
                        correct_answers.append(idx)
            elif isinstance(selected_data, list):
                correct_answers = [int(x) for x in selected_data if str(x).isdigit()]
            
            # Extract additional fields
            extra_text = data.get('extra_text', {}).get('value', '')
            tooltip = data.get('tooltip', {}).get('value', '')
            featured_image = data.get('featured_image', {}).get('value', '')
            
            return QuestionData(
                question_id=int(question_id),
                title=title,
                quiz_id=int(quiz_id),
                question_type=question_type,
                answers=answers,
                correct_answers=correct_answers,
                extra_text=extra_text,
                tooltip=tooltip,
                featured_image=featured_image
            )
            
        except Exception as e:
            logger.error(f"Error parsing PHP data: {e}")
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
            # Assuming record structure: (id, serialized_data, ...)
            # Adjust index based on your source table structure
            serialized_data = record[1]  # Adjust this index as needed
            
            # Parse PHP data
            question_data = PHPDataParser.parse_php_data(serialized_data)
            if not question_data:
                return False
            
            # Insert quiz
            quiz_table_id = self.insert_quiz(question_data.quiz_id, f"Quiz {question_data.quiz_id}")
            if not quiz_table_id:
                logger.error(f"Failed to insert quiz {question_data.quiz_id}")
                return False
            
            # Insert question
            question_table_id = self.insert_question(question_data)
            if not question_table_id:
                logger.error(f"Failed to insert question {question_data.question_id}")
                return False
            
            # Insert question options
            if not self.insert_question_options(question_table_id, question_data):
                logger.warning(f"Some options failed for question {question_data.question_id}")
            
            # Insert quiz-question mapping
            self.insert_quiz_question_mapping(quiz_table_id, question_table_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing record: {e}")
            return False
    
    def convert_data(self, source_table: str, batch_size: int = 100):
        """Main conversion method"""
        logger.info(f"Starting conversion from table: {source_table}")
        
        # Get total count
        count_result = self.db.fetch_all(f"SELECT COUNT(*) FROM {source_table}")
        total_records = count_result[0][0] if count_result else 0
        self.stats['total_records'] = total_records
        
        logger.info(f"Total records to process: {total_records}")
        
        # Process in batches
        offset = 0
        while offset < total_records:
            logger.info(f"Processing batch: {offset + 1} to {min(offset + batch_size, total_records)}")
            
            # Fetch batch - adjust column names based on your source table
            query = f"SELECT * FROM {source_table} LIMIT {batch_size} OFFSET {offset}"
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
            logger.info(f"Progress: {progress:.1f}% ({self.stats['successful_conversions']} successful, {self.stats['failed_conversions']} failed)")
        
        self.print_stats()
    
    def print_stats(self):
        """Print conversion statistics"""
        logger.info("=== Conversion Statistics ===")
        for key, value in self.stats.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")

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
        logger.error(f"Conversion failed: {e}")
        return 1
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    sys.exit(main())