"""
Mass Translation Program - Local Version
Uses Argos Translate for local, offline translation of Chinese strings
"""

import os
import re
import json
from typing import Set, Dict
from pathlib import Path

try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    print("Warning: argostranslate not installed. Install with: pip install argostranslate")

class LocalMassTranslator:
    def __init__(self):
        # Expanded Chinese character ranges to include all CJK characters
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+')
        self.translator_ready = False
        self.setup_translator()

    def setup_translator(self):
        """Setup Argos Translate for Chinese to English translation"""
        if not ARGOS_AVAILABLE:
            print("Argos Translate not available. Please install with: pip install argostranslate")
            return

        try:
            # Update package index
            print("Updating Argos Translate package index...")
            argostranslate.package.update_package_index()

            # Get available packages
            available_packages = argostranslate.package.get_available_packages()

            # Find Chinese to English package
            zh_en_package = None
            for package in available_packages:
                if package.from_code == "zh" and package.to_code == "en":
                    zh_en_package = package
                    break

            if zh_en_package is None:
                print("Chinese to English translation package not found!")
                return

            # Install package if not already installed
            installed_packages = argostranslate.package.get_installed_packages()
            package_installed = any(
                pkg.from_code == "zh" and pkg.to_code == "en"
                for pkg in installed_packages
            )

            if not package_installed:
                print("Installing Chinese to English translation package...")
                argostranslate.package.install_from_path(zh_en_package.download())
                print("Package installed successfully!")
            else:
                print("Chinese to English package already installed.")

            self.translator_ready = True

        except Exception as e:
            print(f"Error setting up translator: {e}")

    def is_chinese_string(self, text: str) -> bool:
        """Check if string contains Chinese characters"""
        return bool(self.chinese_pattern.search(text))

    def extract_chinese_strings_from_file(self, file_path: str) -> Set[str]:
        """Extract Chinese strings from a single file"""
        chinese_strings = set()

        try:
            # Try different encodings
            for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-16']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"Could not decode file: {file_path}")
                return chinese_strings

            # Extract Chinese character sequences, including those separated by spaces/punctuation
            # But terminate at English letters to avoid mixed strings

            # Pattern 1: Chinese sequences with spaces and Chinese punctuation (but not English)
            pattern1 = r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff][\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\s，。、：；！？]*[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]|[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]'
            matches1 = re.findall(pattern1, content)

            # Pattern 2: All individual continuous Chinese sequences (this will catch parts like "传感器采样" from "传感器采样Rate")
            pattern2 = r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+'
            matches2 = re.findall(pattern2, content)

            # Combine and deduplicate
            all_matches = set(matches1 + matches2)

            # Clean up matches - strip whitespace and filter out empty strings
            for match in all_matches:
                cleaned = match.strip()
                if cleaned and re.search(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', cleaned):
                    chinese_strings.add(cleaned)

            # Debug: print found matches for this file
            if all_matches:
                print(f"  Found {len(all_matches)} Chinese strings in {file_path}")
                for match in sorted(all_matches):
                    if match.strip():
                        print(f"    {match.strip()}")
            else:
                print(f"  No Chinese strings found in {file_path}")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

        return chinese_strings

    def scan_directory(self, directory: str) -> Set[str]:
        """Recursively scan directory for Chinese strings"""
        all_chinese_strings = set()

        for root, dirs, files in os.walk(directory):
            # Skip common non-text directories
            dirs[:] = [d for d in dirs if d not in {'.git', '.svn', 'node_modules', '__pycache__', '.vscode', 'venv', '.venv', 'env', '.env'}]

            for file in files:
                file_path = os.path.join(root, file)

                # Only process text-based files
                if self.is_text_file(file_path):
                    print(f"Scanning: {file_path}")
                    chinese_strings = self.extract_chinese_strings_from_file(file_path)
                    all_chinese_strings.update(chinese_strings)

        return all_chinese_strings

    def is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            '.py', '.js', '.html', '.htm', '.css', '.xml', '.txt', '.md',
            '.php', '.java', '.cpp', '.c', '.h', '.ts', '.tsx', '.jsx', '.vue',
            '.go', '.rs', '.rb', '.pl', '.sh', '.bat', '.yml', '.yaml', '.ini',
            '.cfg', '.conf', '.log', '.sql', '.csv', '.tsv'
        }

        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions

    def translate_text(self, chinese_text: str) -> str:
        """Translate Chinese text to English using Argos Translate"""
        if not self.translator_ready:
            return f"[TRANSLATOR_NOT_READY: {chinese_text}]"

        try:
            translation = argostranslate.translate.translate(chinese_text, "zh", "en")
            return translation.strip()
        except Exception as e:
            print(f"Error translating '{chinese_text}': {e}")
            return f"[TRANSLATION_ERROR: {chinese_text}]"

    def translate_all(self, chinese_strings: Set[str]) -> Dict[str, str]:
        """Translate all Chinese strings individually"""
        strings_list = list(chinese_strings)
        all_translations = {}

        print(f"Found {len(strings_list)} unique Chinese strings")
        print("Translating strings one by one...")

        for i, chinese_text in enumerate(strings_list):
            print(f"Translating {i + 1}/{len(strings_list)}: {chinese_text}")
            translation = self.translate_text(chinese_text)
            all_translations[chinese_text] = translation

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{len(strings_list)} strings translated")

        return all_translations

    def save_translations(self, translations: Dict[str, str], output_file: str = "translations.json"):
        """Save translations to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            print(f"Translations saved to {output_file}")
        except Exception as e:
            print(f"Error saving translations: {e}")

    def run(self, directory: str = "."):
        """Main execution function"""
        if not ARGOS_AVAILABLE:
            print("Error: argostranslate is not installed. Please install with: pip install argostranslate")
            return

        if not self.translator_ready:
            print("Error: Translator not ready. Check the setup process above.")
            return

        print("Starting local mass translation process...")
        print(f"Scanning directory: {os.path.abspath(directory)}")

        # Step 1: Scan for Chinese strings
        chinese_strings = self.scan_directory(directory)

        if not chinese_strings:
            print("No Chinese strings found!")
            return

        print(f"Found {len(chinese_strings)} unique Chinese strings")

        # Step 2: Deduplicate and translate strings
        print(f"Deduplicating {len(chinese_strings)} strings...")
        unique_chinese_strings = set(chinese_strings)
        print(f"After deduplication: {len(unique_chinese_strings)} unique strings")

        translations = self.translate_all(unique_chinese_strings)

        # Step 3: Save to JSON
        self.save_translations(translations)

        print("Local translation process completed!")

def main():
    """Main function"""
    translator = LocalMassTranslator()
    translator.run()

if __name__ == "__main__":
    main()