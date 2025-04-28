import xml.etree.ElementTree as ET
import re

def merge_translations(ipe_filepath, translations_filepath):
    print(f"Opening files:\n{ipe_filepath}\n{translations_filepath}")
    
    # Read translations file
    translations = {}
    with open(translations_filepath, 'r', encoding='utf-8') as f:
        raw_content = f.read().strip()
        
        # Use regex to find translation entries - this handles multi-line translations better
        pattern = r'(TRANSLATE_[a-zA-Z0-9]+)\n([\s\S]*?)(?=TRANSLATE_[a-zA-Z0-9]+\n|$)'
        matches = re.findall(pattern, raw_content)
        
        for identifier, translation in matches:
            if translation.strip():
                translations[identifier] = translation.strip()
            else:
                print(f"WARNING: Empty translation for {identifier}")
    
    print(f"Loaded {len(translations)} translations")
    
    # Parse the .ipe file
    tree = ET.parse(ipe_filepath)
    root = tree.getroot()
    
    # Replace identifiers with translations
    replacements = 0
    not_found = set()
    for page in root.findall('.//page'):
        for elem in page.findall('.//text'):
            if elem.text and elem.text.strip():
                identifier = elem.text.strip()
                if identifier in translations:
                    elem.text = translations[identifier]
                    replacements += 1
                else:
                    not_found.add(identifier)
    
    if not_found:
        print("\nWARNING: Could not find translations for these identifiers:")
        for identifier in sorted(not_found):
            print(f"  - {identifier}")
    
    print(f"\nReplaced {replacements} text elements")
    
    # Save the merged file
    output_filepath = ipe_filepath.rsplit('.ipe', 1)[0] + '_merged.ipe'
    tree.write(output_filepath, encoding='unicode', xml_declaration=True)
    print(f"Merged file saved to: {output_filepath}")
    
    return output_filepath

# Usage
if __name__ == "__main__":
    ipe_filepath = "slides/slides07_en.ipe"  # The file with identifiers
    translations_filepath = "slides/slides07_extracted_translated.txt"  # The file with translations
    #print("Starting merge process...")
    #merge_translations(ipe_filepath, translations_filepath)
    #print("Merge complete!") 