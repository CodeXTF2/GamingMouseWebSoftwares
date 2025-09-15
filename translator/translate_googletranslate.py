"""
Mass Translation Program - Hybrid Version v2
Uses Google Translate API for batch translation of strings >=5 characters
Uses argos-translate for individual translation of strings 3-4 characters
"""

import os
import re
import json
import argparse
from typing import Set, Dict, List
from pathlib import Path
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Note: tqdm not available. Install with: pip install tqdm for progress bars")

try:
    from google.cloud import translate_v2 as translate
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False
    print("Warning: google-cloud-translate not installed. Install with: pip install google-cloud-translate")

try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    print("Warning: argostranslate not installed. Install with: pip install argostranslate")

class LocalMassTranslator:
    def __init__(self, google_api_key=None, threshold=5):
        # Expanded Chinese character ranges to include all CJK characters
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+')
        self.google_translate_ready = False
        self.argos_translator_ready = False
        self.google_client = None
        self.google_api_key = google_api_key
        self.threshold = threshold
        self.setup_translators()

    def setup_translators(self):
        """Setup both Google Translate API and argos translators"""
        # Setup Google Translate API for strings >= threshold characters (unless threshold is -1)
        if GOOGLE_TRANSLATE_AVAILABLE and self.google_api_key and self.threshold != -1:
            try:
                print(f"Setting up Google Translate API for strings >= {self.threshold} characters...")
                # Use requests to make direct API calls with API key
                import requests

                # Test API key with a simple request
                test_url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
                test_data = {
                    'q': 'test',
                    'source': 'en',
                    'target': 'es',
                    'format': 'text'
                }

                response = requests.post(test_url, data=test_data)
                if response.status_code == 200:
                    self.google_translate_ready = True
                    print("Google Translate API ready for batch translation!")
                else:
                    print(f"API key validation failed. Status code: {response.status_code}")
                    print(f"Response: {response.text}")

            except Exception as e:
                print(f"Error setting up Google Translate API: {e}")
                import traceback
                traceback.print_exc()
        elif GOOGLE_TRANSLATE_AVAILABLE and not self.google_api_key:
            print("Google Translate API key not provided. Use --api-key argument.")
        elif not GOOGLE_TRANSLATE_AVAILABLE:
            print("google-cloud-translate not available. Install with: pip install google-cloud-translate")
        else:
            print("Google Translate API setup skipped due to threshold = -1")

        # Setup argos translator for strings < threshold characters (or all strings if threshold is -1)
        if self.threshold == 0:
            print("Argos Translate setup skipped (threshold = 0, all strings via cloud API)...")
        elif ARGOS_AVAILABLE:
            try:
                if self.threshold == -1:
                    print("Setting up Argos Translate for all strings (threshold = -1)...")
                else:
                    print(f"Setting up Argos Translate for strings < {self.threshold} characters...")
                # Update package index
                print("Updating Argos package index...")
                argostranslate.package.update_package_index()

                # Get available packages
                available_packages = argostranslate.package.get_available_packages()
                print(f"Found {len(available_packages)} available packages")

                # Find Chinese to English package
                zh_en_package = None
                for package in available_packages:
                    if package.from_code == "zh" and package.to_code == "en":
                        zh_en_package = package
                        print(f"Found Chinese->English package: {package}")
                        break

                if zh_en_package is None:
                    print("ERROR: Chinese to English translation package not found in available packages!")
                    print("Available language pairs:")
                    for pkg in available_packages[:10]:  # Show first 10 packages
                        print(f"  {pkg.from_code} -> {pkg.to_code}")
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

                # Verify installation worked
                installed_packages = argostranslate.package.get_installed_packages()
                zh_en_installed = any(
                    pkg.from_code == "zh" and pkg.to_code == "en"
                    for pkg in installed_packages
                )

                if zh_en_installed:
                    self.argos_translator_ready = True
                    print("Argos translator ready!")
                else:
                    print("ERROR: Chinese->English package installation failed!")

            except Exception as e:
                print(f"Error setting up Argos translator: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("argostranslate not available. Install with: pip install argostranslate")

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
                if cleaned and len(cleaned) >= 1 and re.search(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', cleaned):
                    chinese_strings.add(cleaned)

            # Debug: print found matches for this file
            if all_matches:
                print(f"  Found {len(all_matches)} Chinese strings in {file_path}")
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

    def translate_with_argos(self, chinese_text: str) -> str:
        """Translate Chinese text to English using Argos Translate"""
        if not self.argos_translator_ready:
            return f"[ARGOS_NOT_READY: {chinese_text}]"

        try:
            translation = argostranslate.translate.translate(chinese_text, "zh", "en")
            return translation.strip()
        except Exception as e:
            print(f"Error translating with Argos '{chinese_text}': {e}")
            return f"[ARGOS_ERROR: {chinese_text}]"


    def translate_batch_with_google_api(self, chinese_strings: List[str]) -> Dict[str, str]:
        """Translate Chinese strings using Google Translate API with true batching (max 128 per batch)"""
        if not self.google_translate_ready:
            print("Google Translate API not ready!")
            return {text: f"[GOOGLE_API_NOT_READY: {text}]" for text in chinese_strings}

        try:
            import requests
            translation_dict = {}
            batch_size = 128
            total_batches = (len(chinese_strings) + batch_size - 1) // batch_size

            print("Batch translating with Google Translate API...")

            # Process in batches of 128 with progress bar
            if TQDM_AVAILABLE:
                with tqdm(total=total_batches, desc="Google API Batches", unit="batch") as pbar:
                    for i in range(0, len(chinese_strings), batch_size):
                        batch = chinese_strings[i:i + batch_size]

                        # Use direct API calls with requests
                        url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
                        data = {
                            'q': batch,
                            'source': 'zh-CN',
                            'target': 'en',
                            'format': 'text'
                        }

                        response = requests.post(url, data=data)
                        if response.status_code == 200:
                            result_json = response.json()
                            translations = result_json['data']['translations']

                            # Map results back to original strings
                            for original, translation in zip(batch, translations):
                                translated_text = translation['translatedText'].strip()
                                translation_dict[original] = translated_text if translated_text else f"[GOOGLE_API_ERROR: {original}]"
                        else:
                            # Handle API error
                            for original in batch:
                                translation_dict[original] = f"[GOOGLE_API_ERROR: {original}]"

                        pbar.update(1)
            else:
                for i in range(0, len(chinese_strings), batch_size):
                    batch = chinese_strings[i:i + batch_size]
                    batch_num = (i // batch_size) + 1

                    print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} strings)...")

                    # Use direct API calls with requests
                    url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
                    data = {
                        'q': batch,
                        'source': 'zh-CN',
                        'target': 'en',
                        'format': 'text'
                    }

                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        result_json = response.json()
                        translations = result_json['data']['translations']

                        # Map results back to original strings
                        for original, translation in zip(batch, translations):
                            translated_text = translation['translatedText'].strip()
                            translation_dict[original] = translated_text if translated_text else f"[GOOGLE_API_ERROR: {original}]"
                    else:
                        # Handle API error
                        for original in batch:
                            translation_dict[original] = f"[GOOGLE_API_ERROR: {original}]"

            print(f"Successfully translated {len(translation_dict)} strings with Google Translate API!")
            return translation_dict

        except Exception as e:
            print(f"Error during Google API batch translation: {e}")
            # Fallback: return error messages for all strings
            return {text: f"[GOOGLE_API_ERROR: {text}]" for text in chinese_strings}

    def translate_all(self, chinese_strings: Set[str]) -> Dict[str, str]:
        """Translate all Chinese strings using hybrid approach or full Argos fallback"""
        strings_list = list(chinese_strings)

        # Handle special threshold cases
        if self.threshold == -1:
            # Everything done locally (Argos only)
            print(f"\n=== TRANSLATION BREAKDOWN ===")
            print(f"Total strings found: {len(strings_list)} (≥1 characters)")
            print(f"Google Translate API: 0 strings (threshold = -1, everything local)")
            print(f"Argos Translate (individual): {len(strings_list)} strings (all)")
            print(f"================================\n")

            all_translations = {}
            print("Translating all strings with Argos...")
            if TQDM_AVAILABLE:
                with tqdm(total=len(strings_list), desc="Argos Translation", unit="string") as pbar:
                    for chinese_text in strings_list:
                        translation = self.translate_with_argos(chinese_text)
                        all_translations[chinese_text] = translation
                        pbar.update(1)
            else:
                for i, chinese_text in enumerate(strings_list):
                    translation = self.translate_with_argos(chinese_text)
                    all_translations[chinese_text] = translation
                    if (i + 1) % 10 == 0:
                        print(f"Progress: {i + 1}/{len(strings_list)} strings translated")
            return all_translations

        elif self.threshold == 0 and self.google_translate_ready:
            # Everything done via cloud API (Google only)
            print(f"\n=== TRANSLATION BREAKDOWN ===")
            print(f"Total strings found: {len(strings_list)} (≥1 characters)")
            print(f"Google Translate API (batch): {len(strings_list)} strings (threshold = 0, everything cloud)")
            print(f"Argos Translate (individual): 0 strings")
            print(f"================================\n")

            return self.translate_batch_with_google_api(strings_list)

        # If Google API is available and threshold > 0, use hybrid approach
        elif self.google_translate_ready and self.threshold > 0:
            # Separate strings by configurable threshold
            long_strings = [s for s in strings_list if len(s) >= self.threshold]  # Use Google API batch
            short_strings = [s for s in strings_list if 3 <= len(s) < self.threshold]  # Use argos individual

            # Print breakdown summary
            print(f"\n=== TRANSLATION BREAKDOWN ===")
            print(f"Total strings found: {len(strings_list)} (≥1 characters)")
            print(f"Google Translate API (batch): {len(long_strings)} strings (≥{self.threshold} chars)")
            print(f"Argos Translate (individual): {len(short_strings)} strings (3-{self.threshold-1} chars)")
            print(f"================================\n")

            all_translations = {}

            # Batch translate long strings with Google API
            if long_strings:
                google_translations = self.translate_batch_with_google_api(long_strings)
                all_translations.update(google_translations)

            # Individual translate short strings with argos
            if short_strings:
                print("Translating short strings with Argos...")
                if TQDM_AVAILABLE:
                    with tqdm(total=len(short_strings), desc="Argos Translation", unit="string") as pbar:
                        for chinese_text in short_strings:
                            translation = self.translate_with_argos(chinese_text)
                            all_translations[chinese_text] = translation
                            pbar.update(1)
                else:
                    for i, chinese_text in enumerate(short_strings):
                        translation = self.translate_with_argos(chinese_text)
                        all_translations[chinese_text] = translation
                        if (i + 1) % 10 == 0:
                            print(f"Progress: {i + 1}/{len(short_strings)} short strings translated")

            return all_translations

        # Fallback: Use Argos for all strings (no Google API available)
        else:
            # Print breakdown summary
            print(f"\n=== TRANSLATION BREAKDOWN ===")
            print(f"Total strings found: {len(strings_list)} (≥1 characters)")
            print(f"Google Translate API: 0 strings (no API key provided)")
            print(f"Argos Translate (individual): {len(strings_list)} strings (all)")
            print(f"================================\n")

            all_translations = {}

            print("Translating all strings with Argos...")
            if TQDM_AVAILABLE:
                with tqdm(total=len(strings_list), desc="Argos Translation", unit="string") as pbar:
                    for chinese_text in strings_list:
                        translation = self.translate_with_argos(chinese_text)
                        all_translations[chinese_text] = translation
                        pbar.update(1)
            else:
                for i, chinese_text in enumerate(strings_list):
                    translation = self.translate_with_argos(chinese_text)
                    all_translations[chinese_text] = translation
                    if (i + 1) % 10 == 0:
                        print(f"Progress: {i + 1}/{len(strings_list)} strings translated")

            return all_translations

    def load_existing_translations(self, output_file: str) -> Dict[str, str]:
        """Load existing translations from JSON file"""
        try:
            abs_path = os.path.abspath(output_file)
            print(f"DEBUG: Checking for existing translations at: {abs_path}")
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)
                print(f"Loaded {len(existing_translations)} existing translations from {output_file}")
                return existing_translations
            else:
                print(f"No existing translation file found: {output_file}")
                return {}
        except Exception as e:
            print(f"Error loading existing translations: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def save_translations(self, translations: Dict[str, str], output_file: str = "translations.json"):
        """Save translations to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            print(f"Translations saved to {output_file}")
        except Exception as e:
            print(f"Error saving translations: {e}")

    def run(self, directory: str = ".", output_file: str = None):
        """Main execution function"""
        # Check if at least one translator is available
        if not GOOGLE_TRANSLATE_AVAILABLE and not ARGOS_AVAILABLE:
            print("Error: Neither google-cloud-translate nor argostranslate is installed.")
            print("Install with: pip install google-cloud-translate argostranslate")
            return

        if not self.google_translate_ready and not self.argos_translator_ready:
            print("Error: No translators ready. Check the setup process above.")
            print("Possible solutions:")
            if not ARGOS_AVAILABLE:
                print("  - Install Argos Translate: pip install argostranslate")
            if not GOOGLE_TRANSLATE_AVAILABLE:
                print("  - Install Google Cloud Translate: pip install google-cloud-translate")
            if not self.google_api_key and GOOGLE_TRANSLATE_AVAILABLE:
                print("  - Provide Google API key: --api-key YOUR_API_KEY")
            return

        if self.google_translate_ready:
            print("Starting hybrid mass translation process...")
            print(f"Scanning directory: {os.path.abspath(directory)}")
            if self.threshold == 0:
                print("Note: All strings use Google Translate API batch (threshold=0)")
            elif self.threshold == -1:
                print("Note: All strings use Argos Translate locally (threshold=-1)")
            else:
                print(f"Note: Strings >={self.threshold} chars use Google Translate API batch (128/batch), 3-{self.threshold-1} chars use Argos individual")
            if output_file is None:
                output_file = "translations_google_api_v2.json"
        else:
            print("Starting local mass translation process with Argos...")
            print(f"Scanning directory: {os.path.abspath(directory)}")
            print("Note: Using Argos Translate for all strings (no Google API key provided)")
            if output_file is None:
                output_file = "translations_argos_fallback.json"

        print(f"Output file: {output_file}")

        # Step 1: Load existing translations
        existing_translations = self.load_existing_translations(output_file)

        # Step 2: Scan for Chinese strings
        chinese_strings = self.scan_directory(directory)

        if not chinese_strings:
            print("No Chinese strings (≥1 characters) found!")
            return

        print(f"Found {len(chinese_strings)} unique Chinese strings (≥1 characters)")

        # Step 3: Filter out already translated strings
        already_translated = set(existing_translations.keys())
        new_strings_to_translate = chinese_strings - already_translated
        skipped_count = len(already_translated & chinese_strings)

        print(f"Loaded {len(existing_translations)} existing translations from {output_file}")
        print(f"Found {len(chinese_strings)} total Chinese strings")
        print(f"Already translated: {skipped_count} strings (skipping)")
        print(f"New strings to translate: {len(new_strings_to_translate)} strings")

        if not new_strings_to_translate:
            print("All strings already translated! No new translations needed.")
            return

        # Step 4: Translate only new strings (hybrid or full Argos)
        new_translations = self.translate_all(new_strings_to_translate)

        # Step 5: Merge with existing translations
        all_translations = existing_translations.copy()
        all_translations.update(new_translations)

        # Step 6: Save combined translations to JSON
        self.save_translations(all_translations, output_file)

        if self.google_translate_ready:
            print("Hybrid translation process completed!")
        else:
            print("Local translation process completed with Argos fallback!")

def main():
    """Main function with command-line argument support"""
    parser = argparse.ArgumentParser(
        description='Hybrid translation: Configurable threshold for Google Translate API batch vs argos individual translation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python translate_local_v2.py --api-key YOUR_API_KEY                        # Scan current directory (default threshold=5)
  python translate_local_v2.py --api-key YOUR_API_KEY -d /path/to/dir        # Scan specific directory
  python translate_local_v2.py --api-key YOUR_API_KEY -f file.txt            # Scan specific file
  python translate_local_v2.py --api-key YOUR_API_KEY -t 1                   # Only single chars locally, rest via cloud API
  python translate_local_v2.py --api-key YOUR_API_KEY -t 0                   # Everything via cloud API (Google only)
  python translate_local_v2.py -t -1                                         # Everything locally (Argos only, no API key needed)
        '''
    )

    parser.add_argument('--api-key',
                       required=False,
                       help='Google Translate API key string for Google Cloud Translation API')

    parser.add_argument('--threshold', '-t',
                       type=int,
                       default=5,
                       help='Character threshold for translation method selection. '
                            'Strings >= threshold use Google API (batch), strings < threshold use Argos (individual). '
                            'Use 1 for single chars only locally, 0 for everything via cloud API, -1 for everything locally (default: 5)')

    parser.add_argument('--output', '-o',
                       help='Output JSON filename. If file exists, will load existing translations and add new ones to it. '
                            'If not specified, uses default naming based on translation method.')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--directory',
                      default='.',
                      help='Directory to scan for Chinese strings (default: current directory)')
    group.add_argument('-f', '--file',
                      help='Single file to scan for Chinese strings')

    args = parser.parse_args()

    translator = LocalMassTranslator(google_api_key=args.api_key, threshold=args.threshold)

    if args.file:
        # Handle single file
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found!")
            return

        print(f"Scanning single file: {os.path.abspath(args.file)}")
        chinese_strings = translator.extract_chinese_strings_from_file(args.file)

        if not chinese_strings:
            print("No Chinese strings (≥1 characters) found in file!")
            return

        # Choose output filename based on user input or available translator
        if args.output:
            output_file = args.output
        elif translator.google_translate_ready:
            output_file = f"translations_google_api_{os.path.basename(args.file)}.json"
        else:
            output_file = f"translations_argos_{os.path.basename(args.file)}.json"

        # Load existing translations
        existing_translations = translator.load_existing_translations(output_file)

        print(f"Found {len(chinese_strings)} unique Chinese strings (≥1 characters)")

        # Filter out already translated strings
        already_translated = set(existing_translations.keys())
        new_strings_to_translate = chinese_strings - already_translated
        skipped_count = len(already_translated & chinese_strings)

        print(f"Loaded {len(existing_translations)} existing translations from {output_file}")
        print(f"Found {len(chinese_strings)} total Chinese strings")
        print(f"Already translated: {skipped_count} strings (skipping)")
        print(f"New strings to translate: {len(new_strings_to_translate)} strings")

        if not new_strings_to_translate:
            print("All strings already translated! No new translations needed.")
            return

        # Translate only new strings
        new_translations = translator.translate_all(new_strings_to_translate)

        # Merge with existing translations
        all_translations = existing_translations.copy()
        all_translations.update(new_translations)

        translator.save_translations(all_translations, output_file)
        print("Translation completed!")
    else:
        # Handle directory
        translator.run(args.directory, args.output)

if __name__ == "__main__":
    main()