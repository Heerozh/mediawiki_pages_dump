#!/usr/bin/env python3
"""
MediaWiki Pages Dump Tool

Export pages directly from MediaWiki database to .text files.
Supports MediaWiki versions < 1.31

Database Schema:
- page table: page_id, page_title, page_latest (rev_id)
- revision table: rev_id, rev_text_id (old_id)  
- text table: old_id, old_text

Usage:
    python mediawiki_dump.py --host localhost --user wiki --password secret --database wikidb
"""

import argparse
import logging
import os
import re
import sys
from typing import Optional, Tuple

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("Error: mysql-connector-python is required. Install it with: pip install mysql-connector-python")
    sys.exit(1)


class MediaWikiDumper:
    """MediaWiki database dumper for exporting pages to text files."""
    
    def __init__(self, host: str, user: str, password: str, database: str, 
                 port: int = 3306, charset: str = 'utf8mb4'):
        """Initialize database connection parameters."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset
        self.connection = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Connect to the MediaWiki database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                use_unicode=True
            )
            
            if self.connection.is_connected():
                self.logger.info(f"Connected to MediaWiki database: {self.database}")
                return True
                
        except Error as e:
            self.logger.error(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def sanitize_filename(self, title: str) -> str:
        """Sanitize page title for use as filename."""
        # Replace invalid filename characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        # Limit length to avoid filesystem issues
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def get_page_content(self, page_id: int, page_title: str, rev_id: int) -> Optional[str]:
        """Get page content by following page -> revision -> text chain."""
        try:
            cursor = self.connection.cursor()
            
            # Get rev_text_id from revision table
            revision_query = """
                SELECT rev_text_id 
                FROM revision 
                WHERE rev_id = %s
            """
            cursor.execute(revision_query, (rev_id,))
            result = cursor.fetchone()
            
            if not result:
                self.logger.warning(f"No revision found for rev_id {rev_id} (page: {page_title})")
                return None
            
            text_id = result[0]
            
            # Get old_text from text table
            text_query = """
                SELECT old_text 
                FROM text 
                WHERE old_id = %s
            """
            cursor.execute(text_query, (text_id,))
            result = cursor.fetchone()
            
            if not result:
                self.logger.warning(f"No text found for old_id {text_id} (page: {page_title})")
                return None
            
            return result[0]
            
        except Error as e:
            self.logger.error(f"Error getting content for page {page_title}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def export_pages(self, output_dir: str = "pages", namespace: Optional[int] = None,
                    limit: Optional[int] = None) -> Tuple[int, int]:
        """
        Export all pages to .text files.
        
        Args:
            output_dir: Directory to save .text files
            namespace: Filter by namespace (None for all namespaces)
            limit: Maximum number of pages to export (None for all)
            
        Returns:
            Tuple of (successful_exports, total_pages)
        """
        if not self.connection or not self.connection.is_connected():
            self.logger.error("Not connected to database")
            return 0, 0
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"Created output directory: {output_dir}")
        
        try:
            cursor = self.connection.cursor()
            
            # Build query for pages
            base_query = """
                SELECT page_id, page_title, page_latest 
                FROM page 
                WHERE page_latest IS NOT NULL
            """
            params = []
            
            # Add namespace filter if specified
            if namespace is not None:
                base_query += " AND page_namespace = %s"
                params.append(namespace)
            
            # Add ordering and limit
            base_query += " ORDER BY page_id"
            if limit:
                base_query += " LIMIT %s"
                params.append(limit)
            
            cursor.execute(base_query, params)
            pages = cursor.fetchall()
            
            self.logger.info(f"Found {len(pages)} pages to export")
            
            successful_exports = 0
            
            for page_id, page_title, page_latest in pages:
                # Decode title if it's bytes
                if isinstance(page_title, bytes):
                    page_title = page_title.decode('utf-8', errors='replace')
                
                self.logger.info(f"Processing page: {page_title} (ID: {page_id})")
                
                # Get page content
                content = self.get_page_content(page_id, page_title, page_latest)
                
                if content is not None:
                    # Create filename
                    filename = self.sanitize_filename(page_title) + '.text'
                    filepath = os.path.join(output_dir, filename)
                    
                    try:
                        # Write content to file
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.logger.info(f"Exported: {filepath}")
                        successful_exports += 1
                        
                    except IOError as e:
                        self.logger.error(f"Error writing file {filepath}: {e}")
                else:
                    self.logger.warning(f"Skipping page {page_title} - no content found")
            
            return successful_exports, len(pages)
            
        except Error as e:
            self.logger.error(f"Error during export: {e}")
            return 0, 0
        finally:
            if cursor:
                cursor.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export MediaWiki pages directly from database to .text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --host localhost --user wiki --password secret --database wikidb
  %(prog)s --host localhost --user wiki --password secret --database wikidb --namespace 0 --limit 100
  %(prog)s --host localhost --user wiki --password secret --database wikidb --output-dir /tmp/wiki_pages
        """
    )
    
    # Database connection arguments
    parser.add_argument('--host', required=True, help='Database host')
    parser.add_argument('--port', type=int, default=3306, help='Database port (default: 3306)')
    parser.add_argument('--user', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', required=True, help='Database name')
    
    # Export options
    parser.add_argument('--output-dir', default='pages', 
                       help='Output directory for .text files (default: pages)')
    parser.add_argument('--namespace', type=int, 
                       help='Filter by namespace (e.g., 0 for main namespace)')
    parser.add_argument('--limit', type=int, 
                       help='Maximum number of pages to export')
    
    # Other options
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create dumper instance
    dumper = MediaWikiDumper(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    try:
        # Connect to database
        if not dumper.connect():
            sys.exit(1)
        
        # Export pages
        successful, total = dumper.export_pages(
            output_dir=args.output_dir,
            namespace=args.namespace,
            limit=args.limit
        )
        
        print(f"\nExport completed:")
        print(f"  Total pages processed: {total}")
        print(f"  Successfully exported: {successful}")
        print(f"  Failed: {total - successful}")
        print(f"  Output directory: {args.output_dir}")
        
        if successful == 0 and total > 0:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nExport interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        dumper.disconnect()


if __name__ == "__main__":
    main()