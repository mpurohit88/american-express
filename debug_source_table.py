#!/usr/bin/env python3
"""
Debug script to examine the source table structure and data
"""

import pymysql
import sys
import argparse

def debug_table_structure(host, user, password, database, source_table):
    """Debug the source table to understand its structure"""
    
    try:
        # Connect to database
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        print("🔍 Debugging source table structure...")
        print("=" * 60)
        
        # 1. Show table structure
        print("📋 TABLE STRUCTURE:")
        cursor.execute("DESCRIBE {}".format(source_table))
        columns = cursor.fetchall()
        
        for i, col in enumerate(columns):
            print("  Column {}: {} ({})".format(i, col[0], col[1]))
        
        print("\n" + "=" * 60)
        
        # 2. Show sample data from first few rows
        print("📊 SAMPLE DATA (First 3 rows):")
        cursor.execute("SELECT * FROM {} LIMIT 3".format(source_table))
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ No data found in table!")
            return
        
        for row_num, row in enumerate(rows):
            print("\n--- ROW {} ---".format(row_num + 1))
            for col_num, value in enumerate(row):
                col_name = columns[col_num][0] if col_num < len(columns) else "col_{}".format(col_num)
                value_type = type(value).__name__
                
                if isinstance(value, (str, bytes)) and len(str(value)) > 100:
                    display_value = "{}... ({} chars)".format(str(value)[:100], len(str(value)))
                else:
                    display_value = str(value)
                
                print("  [{}] {}: {} ({})".format(col_num, col_name, display_value, value_type))
        
        print("\n" + "=" * 60)
        
        # 3. Try to identify which column contains serialized data
        print("🔍 LOOKING FOR SERIALIZED DATA:")
        
        first_row = rows[0]
        for col_num, value in enumerate(first_row):
            col_name = columns[col_num][0] if col_num < len(columns) else "col_{}".format(col_num)
            
            if isinstance(value, (str, bytes)):
                value_str = str(value)
                if 'a:' in value_str and 's:' in value_str:
                    print("  ✅ Column {} ({}): Looks like PHP serialized data".format(col_num, col_name))
                    print("     Preview: {}...".format(value_str[:150]))
                elif 'question_id' in value_str or 'quiz_id' in value_str:
                    print("  ✅ Column {} ({}): Contains question/quiz data".format(col_num, col_name))
                    print("     Preview: {}...".format(value_str[:150]))
                else:
                    print("  ❓ Column {} ({}): Text data, but doesn't look like serialized".format(col_num, col_name))
            else:
                print("  ❌ Column {} ({}): {} (not text data)".format(col_num, col_name, type(value).__name__))
        
        print("\n" + "=" * 60)
        print("💡 RECOMMENDATIONS:")
        print("1. Look for columns marked with ✅ above")
        print("2. The serialized data column should contain 'a:11:' or similar at the start")
        print("3. Update the script to use the correct column index")
        print("4. Current script uses record[1] - you may need to change this")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print("❌ Error: {}".format(e))
        import traceback
        print("Traceback: {}".format(traceback.format_exc()))

def main():
    parser = argparse.ArgumentParser(description='Debug source table structure')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--source-table', required=True, help='Source table name')
    
    args = parser.parse_args()
    
    debug_table_structure(args.host, args.user, args.password, args.database, args.source_table)

if __name__ == "__main__":
    main()