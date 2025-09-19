# MediaWiki Database Configuration Template
# Copy this file to config.py and fill in your database details

# Database connection settings
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "your_username"
DB_PASSWORD = "your_password"  
DB_NAME = "your_mediawiki_database"

# Export settings
OUTPUT_DIR = "pages"
NAMESPACE = None  # None for all namespaces, 0 for main namespace, etc.
LIMIT = None      # None for all pages, or specify maximum number