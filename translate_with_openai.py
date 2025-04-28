import os
import time
import json
import re
from openai import OpenAI

def generate_mock_translation(text, identifier):
    """
    Generate a mock translation for debugging purposes.
    This simply adds a prefix to the original text.
    """
    return f"[DEBUG MOCK TRANSLATION] {text}"

def translate_with_openai(extracted_filepath, batch_size=1, api_key=None, debug_mode=False):
    """
    Translate the extracted text using OpenAI's API and save to a new file.
    
    Args:
        extracted_filepath: Path to the file with extracted text
        batch_size: Number of entries to batch in a single API request
        api_key: OpenAI API key (if None, will try to get from environment variable)
        debug_mode: If True, will print API requests without actually sending them
    """
    # Set up OpenAI client (only if not in debug mode)
    if not debug_mode:
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key is required. Either pass it as an argument or set OPENAI_API_KEY environment variable.")
        
        client = OpenAI(api_key=api_key)
    else:
        print("=== RUNNING IN DEBUG MODE - NO API CALLS WILL BE MADE ===")
        client = None
    
    # Read the extracted text
    with open(extracted_filepath, 'r', encoding='utf-8') as f:
        raw_content = f.read().strip()
    
    # Use regex to extract entries by TRANSLATE_ IDs directly
    pattern = r'(TRANSLATE_[a-zA-Z0-9]+)(?:\|\|\||[\s\n]+)([\s\S]*?)(?=TRANSLATE_[a-zA-Z0-9]+|$)'
    matches = re.findall(pattern, raw_content)
    
    # Process matches into valid entries
    valid_entries = []
    for identifier, text in matches:
        # Skip if text is empty
        if not text.strip():
            print(f"Skipping empty text for {identifier}")
            continue
            
        # Clean up text (remove extra whitespace at beginning/end)
        text = text.strip()
        valid_entries.append((identifier, text))
    
    translated_entries = []
    
    print(f"Found {len(valid_entries)} valid entries to translate")
    print(f"Using batch size: {batch_size}")
    
    # Process entries in batches
    for i in range(0, len(valid_entries), batch_size):
        batch = valid_entries[i:i+batch_size]
        batch_identifiers = [item[0] for item in batch]
        batch_texts = [item[1] for item in batch]
        
        print(f"\n===== BATCH {i//batch_size + 1} =====")
        print(f"Processing entries {i+1} to {min(i+batch_size, len(valid_entries))}")
        
        # Prepare system message
        system_message = "You are a professional translator specializing in academic and technical content. Translate from German to English, preserving all LaTeX commands and formatting exactly as they appear in the original text. Do not add any $ that were not there before. Also do not make the translation longer than the input."
        
        # Build the prompt - using the ID tags approach for all batch sizes
        prompt = "Translate each of the following German texts to English, preserving all LaTeX commands and formatting exactly as they appear in the original text. Escape all LaTeX special characters (e.g., #, %, _) where necessary, even in plain text environments. Do not add or remove any $ symbols under any circumstances—even if this results in incorrect or unusual LaTeX syntax. Check this carefully, especially around $ delimiters. Ensure all LaTeX commands, braces {}, brackets [], and parentheses () remain exactly as in the original text. Do not remove, add, or modify any structural characters. If a LaTeX environment or function is opened with {, it must be properly closed with }. Each text has a unique ID and must be returned with that exact same ID.\n\n"
        
        # Add each text to the prompt with its ID
        for j, (identifier, text) in enumerate(zip(batch_identifiers, batch_texts)):
            prompt += f"{identifier}\n{text}\n\n"
        
        # Add instructions for all batches
        prompt += "For each text above, provide the English translation with the exact same ID format:\n\n[ID]\n[Your English translation of the german text]\n\n"
        prompt += "Keep each ID exactly as provided. Make sure every original text has a corresponding translation."
        
        print(f"Sending batch to API with {len(batch_texts)} texts")
        
        if debug_mode:
            # In debug mode, print the request instead of sending it
            print("\n=== DEBUG: API REQUEST ===")
            print(f"Model: gpt-4o-mini")
            print(f"Temperature: 0.3")
            print(f"System message: {system_message}")
            
            print("\n--- FULL INPUT TEXTS TO TRANSLATOR ---")
            for j, (identifier, text) in enumerate(zip(batch_identifiers, batch_texts)):
                print(f"\nText {j+1}:")
                print(f"{identifier}")
                print(f"{text}")
                print("\n---")
            print("--- END FULL INPUT TEXTS ---\n")
            
            # Print prompt structure
            prompt_structure = re.sub(r'(TRANSLATE_[A-Za-z0-9]+\n).*?(\n\n|$)', r'\1[TEXT CONTENT]\2', prompt)
            print(f"User message structure:\n{prompt_structure}")
            print("=== END DEBUG API REQUEST ===\n")
            
            # Generate mock translations for each item in the batch
            print("--- DEBUG MOCK TRANSLATIONS (COMPLETE) ---")
            for j, (identifier, text) in enumerate(zip(batch_identifiers, batch_texts)):
                mock_translation = generate_mock_translation(text, identifier)
                translated_entries.append(f"{identifier}\n{mock_translation}")
                print(f"\nTranslation for text {j+1}:\n{identifier}\n{mock_translation}")
            print("--- END DEBUG MOCK TRANSLATIONS ---")
        else:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                
                translation_text = response.choices[0].message.content.strip()
                print("\n=== CHATGPT REPLY ===")
                print(translation_text)
                print("=== END REPLY ===\n")
                
                # Extract translations using a simpler approach
                translations = {}
                lines = translation_text.split('\n')
                
                current_id = None
                current_translation = []
                
                for line in lines:
                    # Check if this line contains an identifier
                    if "TRANSLATE_" in line:
                        # If we were already collecting a translation, save it
                        if current_id and current_translation:
                            translations[current_id] = '\n'.join(current_translation).strip()
                            print(f"Found translation for {current_id}")
                            current_translation = []
                        
                        # Extract the ID - just get the TRANSLATE_ part
                        id_parts = re.search(r'TRANSLATE_[a-zA-Z0-9]+', line)
                        if id_parts:
                            current_id = id_parts.group(0)
                            print(f"Found ID: {current_id}")
                            # Skip the line with the ID - don't add it to translation
                    else:
                        # Only add non-ID lines to the translation
                        if current_id:
                            current_translation.append(line)
                
                # Don't forget the last translation
                if current_id and current_translation:
                    translations[current_id] = '\n'.join(current_translation).strip()
                    print(f"Found translation for {current_id}")
                
                # Add translations to results, using original text as fallback
                for identifier, text in zip(batch_identifiers, batch_texts):
                    if identifier in translations:
                        translated_entries.append(f"{identifier}\n{translations[identifier]}")
                    else:
                        print(f"WARNING: Could not find translation for {identifier}, using original text")
                        translated_entries.append(f"{identifier}\n{text}")
                
            except Exception as e:
                print(f"Error processing batch: {e}")
                # Fallback: keep original texts
                for identifier, text in zip(batch_identifiers, batch_texts):
                    translated_entries.append(f"{identifier}\n{text}")
                time.sleep(1)
        
        # Sleep between batches to avoid rate limits (skip in debug mode)
        if not debug_mode:
            time.sleep(0.5)
    
    # Save translations to a new file
    output_filepath = extracted_filepath.rsplit('.', 1)[0] + '_translated.txt'
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(translated_entries))
    
    print(f"\nTranslations saved to: {output_filepath}")
    
    # Print analysis of all translations once at the end
    print("\n=== FINAL TRANSLATIONS ANALYSIS ===")
    
    # Create log file for lines with odd number of $ symbols
    log_filepath = extracted_filepath.rsplit('.', 1)[0] + '.log'
    with open(log_filepath, 'a', encoding='utf-8') as log_file:
        for entry in translated_entries:
            past_line = ""
            for line in entry.split('\n'):
                count = line.count('$')
                # Log lines with odd number of $ symbols
                if count % 2 != 0:
                    print(f" printing {line}\n")
                    log_file.write(f"{past_line}\n")
                    log_file.write(f"{count} $'s: {line}\n")
                past_line = line
            print("---")  # Separator between entries
    
    print(f"\nLog file with odd $ counts saved to: {log_filepath}")
    
    return output_filepath

# Usage example
if __name__ == "__main__":
    extracted_file = "slides/slides01_extracted.txt"
    batch_size = 100  # Adjust this to control how many entries are sent in each API request
    
    # To run in normal mode:
    # translate_with_openai(extracted_file, batch_size=batch_size)
    
    # To run in debug mode (no API calls):
    #translate_with_openai(extracted_file, batch_size=batch_size, debug_mode=True) 