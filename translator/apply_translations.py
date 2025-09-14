"""
Apply Translations Script
Reads translations.json and recursively replaces Chinese strings with their English translations
"""

import os
import re
import json
from typing import Dict, Set
import shutil
from pathlib import Path

class TranslationApplicator:
    def __init__(self, translations_file: str = "translations.json"):
        self.translations_file = translations_file
        self.translations = {}
        self.backup_made = False
        self.files_modified = 0
        self.replacements_made = 0

    def load_translations(self) -> bool:
        """Load translations from JSON file"""
        try:
            with open(self.translations_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            print(f"Loaded {len(self.translations)} translations from {self.translations_file}")
            return True
        except FileNotFoundError:
            print(f"Error: {self.translations_file} not found!")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.translations_file}: {e}")
            return False
        except Exception as e:
            print(f"Error loading translations: {e}")
            return False

    def is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file that should be processed"""
        text_extensions = {
            '.py', '.js', '.html', '.htm', '.css', '.json', '.xml', '.txt', '.md',
            '.php', '.java', '.cpp', '.c', '.h', '.ts', '.tsx', '.jsx', '.vue',
            '.go', '.rs', '.rb', '.pl', '.sh', '.bat', '.yml', '.yaml', '.ini',
            '.cfg', '.conf', '.log', '.sql', '.csv', '.tsv'
        }

        # Skip certain files
        skip_files = {
            'translations.json', 'apply_translations.py', 'translate.py', 'translate_old.py', 'translate_local.py'
        }

        filename = os.path.basename(file_path)
        if filename in skip_files:
            return False

        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions

    def create_backup(self, directory: str):
        """Create a backup of the directory before making changes"""
        if self.backup_made:
            return

        directory_clean = directory.rstrip('/\\')
        backup_dir = f"{directory_clean}__backup"
        try:
            if os.path.exists(backup_dir):
                print(f"Backup directory {backup_dir} already exists, skipping backup creation")
            else:
                print(f"Creating backup at {backup_dir}...")
                shutil.copytree(directory, backup_dir,
                              ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__', 'venv', '.venv', 'env', '.env'))
                print("Backup created successfully!")
            self.backup_made = True
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            print("Continuing without backup...")
            self.backup_made = True

    def apply_translations_to_file(self, file_path: str) -> bool:
        """Apply translations to a single file"""
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
                print(f"Could not decode file: {file_path}")
                return False

            # Keep track of original content
            original_content = content
            file_replacements = 0

            # Sort translations by length (longest first) to avoid breaking up longer strings
            sorted_translations = sorted(self.translations.items(), key=lambda x: len(x[0]), reverse=True)

            # Apply each translation
            for chinese_text, english_translation in sorted_translations:
                # Skip translation errors or untranslated items
                if english_translation.startswith('[') and english_translation.endswith(']'):
                    continue

                # Count occurrences before replacement
                occurrences = content.count(chinese_text)
                if occurrences > 0:
                    # Escape quotation marks in the translation
                    escaped_translation = english_translation.replace('"', '\\"').replace("'", "\\'")

                    # Replace all occurrences
                    content = content.replace(chinese_text, escaped_translation)
                    file_replacements += occurrences
                    #print(f"  Replaced '{chinese_text}' -> '{escaped_translation}' ({occurrences} times)")

            # Only write file if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding=encoding_used) as f:
                    f.write(content)
                self.replacements_made += file_replacements
                return True

            return False

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return False

    def apply_translations_to_directory(self, directory: str, create_backup: bool = True):
        """Recursively apply translations to all files in directory"""
        if not self.translations:
            print("No translations loaded!")
            return

        print(f"Starting translation application in: {os.path.abspath(directory)}")

        if create_backup:
            self.create_backup(directory)

        for root, dirs, files in os.walk(directory):
            # Skip common non-text directories and backup directory
            dirs[:] = [d for d in dirs if d not in {
                '.git', '.svn', 'node_modules', '__pycache__', '.vscode',
                'venv', '.venv', 'env', '.env'
            } and not d.endswith('__backup')]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip hidden files and non-text files
                if file.startswith('.') or not self.is_text_file(file_path):
                    continue

                print(f"Processing: {file_path}")
                if self.apply_translations_to_file(file_path):
                    self.files_modified += 1

        print(f"\nTranslation application completed!")
        print(f"Files modified: {self.files_modified}")
        print(f"Total replacements made: {self.replacements_made}")

    def run(self, target: str = ".", create_backup: bool = True):
        """Main execution function"""
        if not self.load_translations():
            return

        # Filter out translation errors and untranslated items
        valid_translations = {k: v for k, v in self.translations.items()
                            if not (v.startswith('[') and v.endswith(']'))}

        print(f"Using {len(valid_translations)} valid translations out of {len(self.translations)} total")

        if not valid_translations:
            print("No valid translations found!")
            return

        self.translations = valid_translations

        # Check if target is a file or directory
        target_path = os.path.abspath(target)

        if os.path.isfile(target_path):
            # Single file processing
            if not self.is_text_file(target_path):
                print(f"Error: {target_path} is not a supported text file type")
                return

            print(f"\nReplacing Chinese text with English translations in: {target_path}")
            if create_backup:
                print("Creating backup before making changes...")

            if create_backup:
                # Create backup of just this file
                backup_path = f"{target_path}.backup"
                try:
                    shutil.copy2(target_path, backup_path)
                    print(f"Backup created: {backup_path}")
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")
                    print("Continuing without backup...")

            print(f"Processing: {target_path}")
            if self.apply_translations_to_file(target_path):
                self.files_modified = 1
                print(f"\nFile processing completed!")
                print(f"Total replacements made: {self.replacements_made}")
            else:
                print("No changes made to the file.")

        elif os.path.isdir(target_path):
            # Directory processing
            print(f"\nReplacing Chinese text with English translations in all text files under: {target_path}")
            if create_backup:
                print("Creating backup before making changes...")

            self.apply_translations_to_directory(target_path, create_backup)
        else:
            print(f"Error: {target_path} does not exist!")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Apply translations from translations.json to all files")
    parser.add_argument('target', nargs='?', default='.', help='File or directory to process (default: current directory)')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--translations', default='translations.json', help='Translations file to use (default: translations.json)')

    args = parser.parse_args()

    applicator = TranslationApplicator(args.translations)
    applicator.run(args.target, not args.no_backup)

if __name__ == "__main__":
    main()