"""
Configuration file for PHP Quiz Data Converter
"""

# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database',
    'port': 3306
}

# Source Table Configuration
SOURCE_CONFIG = {
    'table_name': 'wp_postmeta',  # Change to your actual table name
    'data_column': 'meta_value',  # Column containing PHP serialized data
    'id_column': 'meta_id',       # Primary key column
    'filter_condition': "meta_key = 'question_data'"  # Optional: filter specific records
}

# Processing Configuration
PROCESSING_CONFIG = {
    'batch_size': 500,           # Number of records to process in each batch
    'log_level': 'INFO',         # Logging level: DEBUG, INFO, WARNING, ERROR
    'log_file': 'quiz_conversion.log',
    'enable_transaction': True,   # Use database transactions
    'skip_duplicates': True      # Skip already processed questions/quizzes
}

# Quiz Configuration
QUIZ_CONFIG = {
    'default_quiz_title': 'Imported Quiz',
    'max_title_length': 500,
    'max_slug_length': 255,
    'default_question_type': 'multiple_choice_text'
}