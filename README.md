# MediaWiki Pages Dump

Export MediaWiki pages directly from database to .text files (MediaWiki < 1.31).

This tool extracts page content by following the MediaWiki database schema:
- `page` table: contains `page_id`, `page_title`, and `page_latest` (revision ID)
- `revision` table: contains `rev_id` and `rev_text_id` (text table old_id)
- `text` table: contains `old_id` and `old_text` (the actual page content)

## Installation

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python mediawiki_dump.py --host localhost --user wiki_user --password wiki_pass --database wikidb
```

### Advanced Usage

```bash
# Export only main namespace (namespace 0) pages
python mediawiki_dump.py --host localhost --user wiki_user --password wiki_pass --database wikidb --namespace 0

# Export only first 100 pages
python mediawiki_dump.py --host localhost --user wiki_user --password wiki_pass --database wikidb --limit 100

# Export to custom directory
python mediawiki_dump.py --host localhost --user wiki_user --password wiki_pass --database wikidb --output-dir /path/to/output

# Enable verbose logging
python mediawiki_dump.py --host localhost --user wiki_user --password wiki_pass --database wikidb --verbose
```

### Command Line Options

- `--host`: Database host (required)
- `--port`: Database port (default: 3306)
- `--user`: Database username (required)
- `--password`: Database password (required)
- `--database`: Database name (required)
- `--output-dir`: Output directory for .text files (default: 'pages')
- `--namespace`: Filter by namespace (e.g., 0 for main namespace)
- `--limit`: Maximum number of pages to export
- `--verbose`: Enable verbose logging

## Output

The tool creates `.text` files in the output directory, with each file named after the page title (sanitized for filesystem compatibility). Each file contains the raw MediaWiki content of the page.

## Database Schema Compatibility

This tool is designed for MediaWiki versions < 1.31 where the database schema uses:
- `page.page_latest` → `revision.rev_id`
- `revision.rev_text_id` → `text.old_id`
- `text.old_text` contains the page content

For newer MediaWiki versions (1.31+), the content storage may have changed to use the `content` and `slots` tables instead.

## Error Handling

The tool includes comprehensive error handling and logging:
- Database connection errors
- Missing revision or text records
- File system errors
- Invalid page titles

Failed exports are logged, and the tool continues processing remaining pages.

## License

This project is open source. Please check the repository for license details.
