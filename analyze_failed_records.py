#!/usr/bin/env python3
"""
Script to analyze failed records and help with debugging
"""

import sys
import argparse
import pymysql

def analyze_failed_records(failed_log_file, host=None, user=None, password=None, database=None, source_table=None):
    """Analyze the failed_records.log file and optionally query the database for more details"""
    
    print("🔍 Analyzing Failed Records...")
    print("=" * 60)
    
    try:
        with open(failed_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("✅ No failed records found!")
            return
        
        print("📊 FAILURE SUMMARY:")
        print("Total Failed Records: {}".format(len(lines)))
        print()
        
        # Categorize failures by reason
        failure_reasons = {}
        failed_records = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("FAILED:"):
                parts = line.split(" | ")
                if len(parts) >= 2:
                    record_info = parts[0].replace("FAILED: ", "")
                    reason = parts[1].replace("Reason: ", "")
                    details = parts[2].replace("Details: ", "") if len(parts) > 2 else ""
                    
                    failed_records.append({
                        'record_info': record_info,
                        'reason': reason,
                        'details': details
                    })
                    
                    if reason not in failure_reasons:
                        failure_reasons[reason] = []
                    failure_reasons[reason].append(record_info)
        
        # Show failure breakdown
        print("📈 FAILURE BREAKDOWN:")
        for reason, records in failure_reasons.items():
            print("  {}: {} records".format(reason, len(records)))
            # Show first few examples
            for i, record in enumerate(records[:3]):
                print("    - {}".format(record))
            if len(records) > 3:
                print("    ... and {} more".format(len(records) - 3))
            print()
        
        print("=" * 60)
        print("📋 DETAILED FAILED RECORDS:")
        
        for i, record in enumerate(failed_records[:10]):  # Show first 10
            print("{}. {}".format(i + 1, record['record_info']))
            print("   Reason: {}".format(record['reason']))
            if record['details']:
                print("   Details: {}".format(record['details'][:100] + "..." if len(record['details']) > 100 else record['details']))
            print()
        
        if len(failed_records) > 10:
            print("... and {} more failed records".format(len(failed_records) - 10))
        
        # If database connection info provided, query specific records
        if all([host, user, password, database, source_table]):
            print("=" * 60)
            print("🔍 QUERYING DATABASE FOR FAILED RECORDS:")
            analyze_failed_in_database(failed_records[:5], host, user, password, database, source_table)
    
    except FileNotFoundError:
        print("❌ failed_records.log file not found!")
        print("   Make sure you've run the conversion script first.")
    except Exception as e:
        print("❌ Error analyzing failed records: {}".format(e))

def analyze_failed_in_database(failed_records, host, user, password, database, source_table):
    """Query the database for specific failed records to get more details"""
    
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        for record in failed_records:
            # Extract meta_id and post_id from record_info
            record_info = record['record_info']
            try:
                meta_id = record_info.split('meta_id=')[1].split(',')[0]
                post_id = record_info.split('post_id=')[1].split(',')[0] if 'post_id=' in record_info else None
                
                print("\n--- Analyzing {} ---".format(record_info))
                
                # Query the specific record
                if meta_id != "unknown":
                    cursor.execute("SELECT * FROM {} WHERE meta_id = %s".format(source_table), (meta_id,))
                    db_record = cursor.fetchone()
                    
                    if db_record:
                        print("✅ Record found in database")
                        print("   Data preview: {}".format(str(db_record)[:200] + "..." if len(str(db_record)) > 200 else str(db_record)))
                        
                        # Check if it looks like valid serialized data
                        for i, value in enumerate(db_record):
                            if isinstance(value, (str, bytes)):
                                value_str = str(value)
                                if 'a:' in value_str and 's:' in value_str:
                                    print("   Serialized data found in column {}: {}".format(i, value_str[:100] + "..."))
                                    break
                    else:
                        print("❌ Record not found in database")
                else:
                    print("❌ Cannot query - meta_id is unknown")
                    
            except Exception as e:
                print("❌ Error analyzing record {}: {}".format(record_info, e))
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print("❌ Database connection error: {}".format(e))

def main():
    parser = argparse.ArgumentParser(description='Analyze failed records from conversion')
    parser.add_argument('--failed-log', default='failed_records.log', help='Path to failed_records.log file')
    parser.add_argument('--host', help='Database host (optional, for detailed analysis)')
    parser.add_argument('--user', help='Database username (optional)')
    parser.add_argument('--password', help='Database password (optional)')
    parser.add_argument('--database', help='Database name (optional)')
    parser.add_argument('--source-table', help='Source table name (optional)')
    
    args = parser.parse_args()
    
    analyze_failed_records(
        args.failed_log,
        args.host,
        args.user, 
        args.password,
        args.database,
        args.source_table
    )

if __name__ == "__main__":
    main()