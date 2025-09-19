# MediaWiki Pages Dump - Makefile

.PHONY: help install test clean example

help:
	@echo "MediaWiki Pages Dump - Available commands:"
	@echo ""
	@echo "  install    Install Python dependencies"
	@echo "  test       Run tests"
	@echo "  example    Show usage examples"
	@echo "  clean      Clean up generated files"
	@echo "  lint       Check code style (if pylint available)"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install"
	@echo "  make test"
	@echo "  python mediawiki_dump.py --help"

install:
	pip install -r requirements.txt

test:
	python test_dumper.py

example:
	python example_usage.py

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf pages/ exported_pages/

lint:
	@which pylint >/dev/null 2>&1 && pylint mediawiki_dump.py || echo "pylint not found, skipping lint check"

# Development helpers
check-syntax:
	python -m py_compile mediawiki_dump.py
	python -m py_compile example_usage.py
	python -m py_compile test_dumper.py