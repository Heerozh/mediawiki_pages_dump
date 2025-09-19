#!/usr/bin/env python3
"""
Example usage of the MediaWiki Pages Dump tool.

This script shows how to use the MediaWikiDumper class programmatically.
For command-line usage, use mediawiki_dump.py directly.
"""

import os
import sys

# Add the current directory to path to import our module
sys.path.insert(0, os.path.dirname(__file__))

# Import with error handling for missing dependencies
try:
    from mediawiki_dump import MediaWikiDumper
except ImportError as e:
    print(f"Error importing MediaWikiDumper: {e}")
    print("Make sure to install dependencies: pip install -r requirements.txt")
    sys.exit(1)

def example_usage():
    """Example of programmatic usage."""
    
    # Database configuration (adjust these values)
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'wiki_user',
        'password': 'wiki_password',
        'database': 'mediawiki_db'
    }
    
    # Create dumper instance
    dumper = MediaWikiDumper(**config)
    
    try:
        # Connect to database
        print("Connecting to MediaWiki database...")
        if not dumper.connect():
            print("Failed to connect to database")
            return False
        
        print("Connected successfully!")
        
        # Export options
        export_options = {
            'output_dir': 'exported_pages',
            'namespace': 0,  # Main namespace only
            'limit': 10      # Export only first 10 pages for demo
        }
        
        print(f"Starting export with options: {export_options}")
        
        # Perform export
        successful, total = dumper.export_pages(**export_options)
        
        print(f"\nExport Results:")
        print(f"  Total pages: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total - successful}")
        
        return successful > 0
        
    except Exception as e:
        print(f"Error during export: {e}")
        return False
    finally:
        dumper.disconnect()

def show_usage_help():
    """Show usage examples."""
    print("MediaWiki Pages Dump - Usage Examples")
    print("=" * 40)
    print()
    print("1. Command Line Usage:")
    print("   python mediawiki_dump.py --host localhost --user wiki --password secret --database wikidb")
    print()
    print("2. Export specific namespace:")
    print("   python mediawiki_dump.py --host localhost --user wiki --password secret --database wikidb --namespace 0")
    print()
    print("3. Export with limit:")
    print("   python mediawiki_dump.py --host localhost --user wiki --password secret --database wikidb --limit 100")
    print()
    print("4. Custom output directory:")
    print("   python mediawiki_dump.py --host localhost --user wiki --password secret --database wikidb --output-dir /tmp/wiki")
    print()
    print("5. Programmatic usage:")
    print("   See the example_usage() function in this file")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo mode - actually try to run (will fail without real DB)
        print("Running demo (will fail without real database)...")
        example_usage()
    else:
        # Just show usage help
        show_usage_help()