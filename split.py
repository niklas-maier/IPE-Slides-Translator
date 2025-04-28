import xml.etree.ElementTree as ET
import uuid
import copy

def extract_translations(input_filepath, max_elements=10):
    print(f"Opening file: {input_filepath}")
    print(f"Will extract up to {max_elements} elements")
    
    # Parse the .ipe file as XML
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(input_filepath, parser=parser)
    root = tree.getroot()
    
    # Create a copy of the tree for the modified version
    modified_tree = copy.deepcopy(tree)
    modified_root = modified_tree.getroot()
    
    text_count = 0
    extracted_texts = []
    
    # Find all text elements in the XML
    for page_idx, page in enumerate(root.findall('.//page')):
        modified_page = modified_root.findall('.//page')[page_idx]
        
        for elem_idx, elem in enumerate(page.findall('.//text')):
            modified_elem = modified_page.findall('.//text')[elem_idx]
            
            if elem.text and elem.text.strip():  # Check if it's a text element
                text_count += 1
                if text_count > max_elements:  # Skip if we've reached our limit
                    print(f"\nReached maximum of {max_elements} elements. Stopping.")
                    break
                    
                print(f"\nProcessing text element {text_count}:")
                try:
                    # Generate identifier
                    identifier = f"TRANSLATE_{str(uuid.uuid4())[:8]}"
                    
                    # Store the original text with its identifier using a special separator
                    # Use "|||" as a separator instead of newline
                    extracted_texts.append(f"{identifier}|||{elem.text}")
                    
                    # Replace text with identifier in the modified XML
                    modified_elem.text = identifier
                    
                except Exception as e:
                    print(f"Error processing text element: {e}")
                    continue
    
    # Save modified .ipe file with exact same format
    output_ipe = input_filepath.rsplit('.', 1)[0] + '_en.ipe'
    modified_tree.write(output_ipe, encoding='unicode', xml_declaration=True)
    print(f"Modified IPE file saved to: {output_ipe}")
    
    # Save extracted texts to a file
    extracted_filepath = input_filepath.rsplit('.', 1)[0] + '_extracted.txt'
    with open(extracted_filepath, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(extracted_texts))
    print(f"Extracted texts saved to: {extracted_filepath}")
    
    return extracted_filepath

# Usage
#filepath = "slides/test.ipe"
#max_elements = 1000000  # Specify how many elements to extract
#print("Starting extraction process...")
#extract_translations(filepath, max_elements)
#print("Extraction complete!")