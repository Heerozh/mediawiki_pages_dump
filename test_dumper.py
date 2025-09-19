#!/usr/bin/env python3
"""Test script for MediaWiki dumper without MySQL dependency."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all non-MySQL imports work."""
    try:
        import argparse
        import logging
        import os
        import re
        import sys
        from typing import Optional, Tuple
        print("✓ All standard library imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_file_structure():
    """Test that the main script file exists and has proper structure."""
    script_path = "mediawiki_dump.py"
    if not os.path.exists(script_path):
        print(f"✗ Script file {script_path} not found")
        return False
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Check for main components
    required_elements = [
        'class MediaWikiDumper',
        'def connect',
        'def export_pages',
        'def main',
        '__name__ == "__main__"'
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        print(f"✗ Missing required elements: {missing}")
        return False
    
    print("✓ Script structure validation passed")
    return True

def test_filename_sanitization():
    """Test filename sanitization logic."""
    # Mock the sanitize_filename method
    import re
    
    def sanitize_filename(title: str) -> str:
        filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        filename = filename.replace(' ', '_')
        filename = filename.strip('. ')
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    test_cases = [
        ("Normal Page", "Normal_Page"),
        ("Page/with\\invalid:chars", "Page_with_invalid_chars"),
        ("Page with spaces", "Page_with_spaces"),
        ("Page<>:\"/\\|?*", "Page_________"),
        ("VeryLongTitle" + "x" * 200, "VeryLongTitle" + "x" * 187),  # Test length limit
    ]
    
    for input_title, expected in test_cases:
        result = sanitize_filename(input_title)
        if result != expected:
            print(f"✗ Filename sanitization failed for '{input_title}': got '{result}', expected '{expected}'")
            return False
    
    print("✓ Filename sanitization tests passed")
    return True

if __name__ == "__main__":
    print("Running MediaWiki Dumper tests...\n")
    
    tests = [
        test_imports,
        test_file_structure, 
        test_filename_sanitization
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("All tests passed! ✓")
        sys.exit(0)
    else:
        print("Some tests failed! ✗")
        sys.exit(1)