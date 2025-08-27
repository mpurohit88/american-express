# PHP Quiz Data to MySQL Converter

This Python script converts PHP-serialized quiz data from a single database table into multiple relational tables, providing a normalized database structure for quiz management.

## Features

- **PHP Serialized Data Parsing**: Handles complex PHP serialized data structures
- **Relational Database Design**: Converts to normalized tables (quizzes, questions, question_options, quiz_questions)
- **Batch Processing**: Efficiently processes large datasets (40,000+ records)
- **Transaction Support**: Ensures data integrity with database transactions
- **Duplicate Handling**: Avoids duplicate entries for questions and quizzes
- **Progress Tracking**: Real-time progress updates and statistics
- **Error Handling**: Comprehensive error handling and logging
- **Configurable**: Flexible configuration via files and environment variables

## Database Schema

The script creates and populates the following tables:

```sql
-- Quizzes table
CREATE TABLE quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    slug VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions table
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    text TEXT NOT NULL,
    explanation TEXT NULL,
    explanation_image VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question options table
CREATE TABLE question_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text VARCHAR(500) NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Quiz-Question mapping table
CREATE TABLE quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question_id INT NOT NULL,
    position INT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE KEY uq_quiz_question (quiz_id, question_id)
);
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**:
   - Copy `.env.example` to `.env`
   - Update database credentials in `.env` or `config.py`

3. **Update Configuration**:
   - Modify `config.py` to match your source table structure
   - Set the correct table name and column names

## Configuration

### Database Configuration (config.py)
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database',
    'port': 3306
}
```

### Source Table Configuration
```python
SOURCE_CONFIG = {
    'table_name': 'wp_postmeta',          # Your source table
    'data_column': 'meta_value',          # Column with PHP serialized data
    'id_column': 'meta_id',               # Primary key column
    'filter_condition': "meta_key = 'question_data'"  # Optional filter
}
```

## Usage

### Basic Usage
```bash
python enhanced_converter.py
```

### Test Data Parsing
Before running the full conversion, test with your sample data:
```bash
python test_data_parser.py
```

### Simple Version
For a basic conversion without advanced features:
```bash
python php_to_mysql_converter.py
```

## PHP Data Structure

The script expects PHP serialized data with the following structure:

```php
a:11:{
    s:11:"question_id";a:5:{...;s:5:"value";i:96;...}
    s:5:"title";a:5:{...;s:5:"value";s:41:"Question text here?";...}
    s:7:"quiz_id";a:5:{...;s:5:"value";i:1361;...}
    s:13:"question_type";a:5:{...;s:5:"value";s:20:"multiple_choice_text";...}
    s:8:"selected";a:5:{...;s:5:"value";a:1:{i:0;i:1;};...}
    s:7:"answers";a:5:{...;s:5:"value";a:10:{...};...}
    s:10:"extra_text";a:5:{...;s:5:"value";s:1800:"Explanation text...";...}
    ...
}
```

## Key Fields Extracted

- **question_id**: Unique identifier for the question
- **title**: The question text
- **quiz_id**: ID of the quiz this question belongs to
- **question_type**: Type of question (e.g., multiple_choice_text)
- **selected**: Array of correct answer indices
- **answers**: Array of answer options
- **extra_text**: Additional explanation or context
- **tooltip**: Optional tooltip text
- **featured_image**: Optional image URL

## Logging

The script provides detailed logging:
- Progress updates every 100 records
- Success/failure statistics
- Error details for debugging
- Final conversion summary

Log files are saved as `quiz_conversion.log`.

## Error Handling

The script handles various error scenarios:
- Invalid PHP serialized data
- Missing required fields
- Database connection failures
- Transaction rollbacks on errors
- Duplicate data detection

## Performance

- **Batch Processing**: Processes records in configurable batches (default: 500)
- **Memory Efficient**: Uses database cursors and generators
- **Transaction Optimization**: Configurable transaction handling
- **Duplicate Skip**: Avoids reprocessing existing data

## Customization

### Adding New Fields
To extract additional fields from PHP data:

1. Update the `QuizData` dataclass
2. Modify the `parse_php_data` method
3. Update the database insertion methods

### Custom Data Validation
Implement custom validation in the `QuizData.__post_init__` method.

### Different Source Formats
Modify the `_extract_field` method to handle different PHP data structures.

## Troubleshooting

### Common Issues

1. **PHP Parsing Errors**: Check that your PHP data is properly serialized
2. **Database Connection**: Verify credentials and database accessibility
3. **Missing Fields**: Update the field extraction logic for your data structure
4. **Memory Issues**: Reduce batch size for large datasets

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in configuration.

### Test with Sample Data
Always test with a small sample before processing large datasets:
```bash
python test_data_parser.py
```

## Sample Output

```
2024-01-15 10:30:00 - INFO - Total records to process: 40000
2024-01-15 10:30:05 - INFO - Processing batch: 1 to 500
2024-01-15 10:30:10 - INFO - Progress: 500/40000 (Success: 485, Failed: 15)
...
2024-01-15 11:45:30 - INFO - ==================================================
2024-01-15 11:45:30 - INFO - CONVERSION COMPLETED!
2024-01-15 11:45:30 - INFO - ==================================================
2024-01-15 11:45:30 - INFO - Total records processed: 39500
2024-01-15 11:45:30 - INFO - Failed records: 500
2024-01-15 11:45:30 - INFO - Quizzes created: 1250
2024-01-15 11:45:30 - INFO - Questions created: 35000
2024-01-15 11:45:30 - INFO - Options created: 140000
2024-01-15 11:45:30 - INFO - Quiz-Question mappings created: 39500
```

## License

This script is provided as-is for educational and conversion purposes. Modify as needed for your specific use case.