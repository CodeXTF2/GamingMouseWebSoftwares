"""
Check for Chinese Characters
Simple script to check if a file contains any Chinese characters and count them
"""

import os
import re
import sys

def count_chinese_characters(file_path: str):
    """Count Chinese characters in a file"""
    # Expanded Chinese character ranges
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')

    try:
        # Try different encodings
        content = None
        encoding_used = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-16']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                encoding_used = encoding
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"Error: Could not decode file {file_path}")
            return

        # Find all Chinese characters
        chinese_chars = chinese_pattern.findall(content)

        # Find all Chinese strings (continuous sequences)
        chinese_strings = re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+', content)

        # Count total characters and unique characters
        total_chinese_chars = len(chinese_chars)
        unique_chinese_chars = len(set(chinese_chars))
        total_chinese_strings = len(chinese_strings)
        unique_chinese_strings = len(set(chinese_strings))

        print(f"File: {file_path}")
        print(f"Encoding: {encoding_used}")
        print(f"Total Chinese characters: {total_chinese_chars}")
        print(f"Unique Chinese characters: {unique_chinese_chars}")
        print(f"Total Chinese strings: {total_chinese_strings}")
        print(f"Unique Chinese strings: {unique_chinese_strings}")

        if total_chinese_chars > 0:
            print(f"\nHas Chinese characters: YES")

            # Show unique Chinese strings found
            if unique_chinese_strings > 0:
                print(f"\nChinese strings found:")
                for i, string in enumerate(sorted(set(chinese_strings)), 1):
                    print(f"  {i:3d}. {string}")
        else:
            print(f"\nHas Chinese characters: NO")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python check.py <filepath>")
        print("Example: python check.py ./static/index.js")
        sys.exit(1)

    file_path = sys.argv[1]

    # Convert to absolute path
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        sys.exit(1)

    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a file")
        sys.exit(1)

    count_chinese_characters(file_path)

if __name__ == "__main__":
    main()