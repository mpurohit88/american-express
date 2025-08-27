# PHP to MySQL Quiz Converter

This Python script converts PHP serialized quiz data from a WordPress/single table format to a normalized relational database schema.

## Features

- **Batch Processing**: Handles large datasets (40k+ records) efficiently with configurable batch sizes
- **Robust Parsing**: Properly handles PHP serialized data with error handling
- **Relational Schema**: Converts to normalized tables (quizzes, questions, question_options, quiz_questions)
- **Duplicate Prevention**: Prevents duplicate entries using IGNORE and UNIQUE constraints
- **Progress Tracking**: Real-time progress logging and statistics
- **Error Handling**: Comprehensive error handling with detailed logging

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your MySQL database is accessible and you have the necessary permissions.

**Note**: This script uses `pymysql` as the MySQL driver, which is a pure Python implementation and doesn't require additional system-level MySQL client libraries.

## Database Schema

The script creates the following tables:

### quizzes
- `id` (Primary Key)
- `quiz_id` (WordPress quiz ID)
- `slug` (Generated from title)
- `title` (Quiz title)
- `created_at`

### questions
- `id` (Primary Key)
- `question_id` (WordPress question ID)
- `text` (Question text)
- `explanation` (From extra_text field)
- `explanation_image`
- `tooltip`
- `featured_image`
- `created_at`

### question_options
- `id` (Primary Key)
- `question_id` (Foreign Key to questions.id)
- `option_text` (Answer text)
- `is_correct` (Boolean)
- `option_order` (Original order)

### quiz_questions
- `id` (Primary Key)
- `quiz_id` (Foreign Key to quizzes.id)
- `question_id` (Foreign Key to questions.id)
- `position` (Optional ordering)

## Usage

### Basic Usage

```bash
python php_to_mysql_converter.py \
    --user your_db_user \
    --password your_db_password \
    --database your_database_name \
    --source-table your_source_table_name \
    --create-schema
```

### Advanced Usage

```bash
python php_to_mysql_converter.py \
    --host localhost \
    --user root \
    --password mypassword \
    --database quiz_db \
    --source-table wp_quiz_data \
    --batch-size 500 \
    --create-schema
```

### Parameters

- `--host`: Database host (default: localhost)
- `--user`: Database username (required)
- `--password`: Database password (required)
- `--database`: Database name (required)
- `--source-table`: Source table containing PHP serialized data (required)
- `--batch-size`: Number of records to process in each batch (default: 100)
- `--create-schema`: Create the target schema before conversion

## Source Data Format

The script expects PHP serialized data in the following format:

```php
a:11:{
    s:11:"question_id";a:5:{...;s:5:"value";i:96;...}
    s:5:"title";a:5:{...;s:5:"value";s:41:"What is the question?";...}
    s:7:"quiz_id";a:5:{...;s:5:"value";i:1361;...}
    s:8:"selected";a:5:{...;s:5:"value";a:1:{i:0;i:1;}...}
    s:7:"answers";a:5:{...;s:5:"value";a:10:{...}...}
    s:10:"extra_text";a:5:{...;s:5:"value";s:1800:"Explanation text";...}
    ...
}
```

## Logging

The script creates a `conversion.log` file with detailed information about:
- Progress updates
- Error messages
- Conversion statistics
- Processing details

## Error Handling

- **Database Errors**: Automatically rolls back failed transactions
- **Parsing Errors**: Skips malformed records and continues processing
- **Duplicate Prevention**: Uses MySQL IGNORE to prevent duplicate entries
- **Memory Management**: Processes data in batches to handle large datasets

## Performance Considerations

- **Batch Size**: Adjust `--batch-size` based on your system memory and database performance
- **Indexing**: The script creates appropriate indexes for optimal query performance
- **Memory Usage**: Uses buffered cursors and batch processing to minimize memory usage

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify database credentials and network connectivity
2. **Permission Errors**: Ensure database user has CREATE, INSERT, SELECT privileges
3. **Encoding Issues**: The script handles UTF-8 encoding automatically
4. **Large Datasets**: Use smaller batch sizes for very large datasets

### Monitoring Progress

The script provides real-time progress updates:
```
2024-01-01 10:00:00 - INFO - Processing batch: 1 to 100
2024-01-01 10:00:05 - INFO - Progress: 25.0% (250 successful, 0 failed)
```

### Final Statistics

After completion, you'll see comprehensive statistics:
```
=== Conversion Statistics ===
Total Records: 40000
Successful Conversions: 39995
Failed Conversions: 5
Questions Created: 35000
Options Created: 140000
Quizzes Created: 500
Mappings Created: 40000
```

## Example Source Table Structure

Your source table should have at least these columns:
- `id` (or primary key)
- `serialized_data` (containing the PHP serialized string)

Adjust the `record[1]` index in the `process_record` method if your serialized data is in a different column position.

## Support

For issues or questions:
1. Check the `conversion.log` file for detailed error messages
2. Verify your source data format matches the expected PHP serialized structure
3. Test with a small batch first using `--batch-size 10`