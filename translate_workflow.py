import os
from split import extract_translations
from translate_with_openai import translate_with_openai
from merge import merge_translations

def translate_ipe_file(input_filepath, batch_size=3, max_elements=None, api_key=None, debug_mode=False):
    """
    Complete workflow to translate an IPE file from German to English.
    
    Args:
        input_filepath: Path to the input .ipe file
        batch_size: Number of entries to batch in a single API request
        max_elements: Maximum number of elements to translate (None for all)
        api_key: OpenAI API key (if None, will try to get from environment variable)
        debug_mode: If True, will print API requests without actually sending them
        
    Returns:
        Path to the final merged file
    """
    print(f"=== STARTING TRANSLATION WORKFLOW FOR {input_filepath} ===")
    print(f"Batch size: {batch_size}")
    print(f"Max elements: {max_elements if max_elements else 'All'}")
    print(f"Debug mode: {'Enabled' if debug_mode else 'Disabled'}")
    
    # Step 1: Extract text from IPE file
    print("\n=== STEP 1: EXTRACTING TEXT ===")
    if max_elements is None:
        # If max_elements is None, we want to extract all elements
        # The default in extract_translations is 10, so we set a very high number
        max_elements = 10000
    
    extracted_file = extract_translations(input_filepath, max_elements)
    
    # Step 2: Translate the extracted text
    print("\n=== STEP 2: TRANSLATING TEXT ===")
    translated_file = translate_with_openai(extracted_file, batch_size, api_key, debug_mode)
    
    # Step 3: Merge translations back into IPE file
    print("\n=== STEP 3: MERGING TRANSLATIONS ===")
    # The extract_translations function creates a file with _en.ipe suffix
    ipe_with_ids = input_filepath.rsplit('.', 1)[0] + '_en.ipe'
    merged_file = merge_translations(ipe_with_ids, translated_file)
    
    print(f"\n=== WORKFLOW COMPLETE ===")
    print(f"Original file: {input_filepath}")
    print(f"Extracted text: {extracted_file}")
    print(f"Translated text: {translated_file}")
    print(f"IPE with IDs: {ipe_with_ids}")
    print(f"Final merged file: {merged_file}")
    
    return merged_file

def translate_slides_range(start_slide, end_slide, batch_size=100, max_elements=1000000, api_key=None, debug_mode=False):
    """
    Translate a range of slides from start_slide to end_slide (inclusive).
    
    Args:
        start_slide: Starting slide number (e.g., 4 for slides04.ipe)
        end_slide: Ending slide number (inclusive)
        batch_size: Number of entries to batch in a single API request
        max_elements: Maximum number of elements to translate per slide
        api_key: OpenAI API key
        debug_mode: If True, will print API requests without actually sending them
    """
    print(f"\n=== STARTING BATCH TRANSLATION OF SLIDES {start_slide:02d} TO {end_slide:02d} ===")
    
    for slide_num in range(start_slide, end_slide + 1):
        input_file = f"slides/slides{slide_num:02d}.ipe"
        if not os.path.exists(input_file):
            print(f"\nWARNING: File {input_file} not found, skipping...")
            continue
            
        print(f"\n=== PROCESSING SLIDE {slide_num:02d} ===")
        try:
            translate_ipe_file(input_file, batch_size, max_elements, api_key, debug_mode)
            print(f"Successfully processed slide {slide_num:02d}")
        except Exception as e:
            print(f"Error processing slide {slide_num:02d}: {e}")
            print("Continuing with next slide...")
            continue
    
    print(f"\n=== COMPLETED BATCH TRANSLATION OF SLIDES {start_slide:02d} TO {end_slide:02d} ===")

# Usage
if __name__ == "__main__":
    # Example: Translate slides 4 through 23
    start_slide = 18
    end_slide = 23
    
    # Comment/uncomment as needed:
    
        # For single custom named slide:
    #translate_ipe_file("slides/Test.ipe", batch_size=100, max_elements=1000000, api_key='')
    #translate_ipe_file("slides/Test.ipe", batch_size=100, max_elements=1000000, debug_mode=True)
    
    # For normal operation:
    translate_slides_range(start_slide, end_slide, batch_size=100, max_elements=1000000, api_key='')
    
    # For debug mode (no API calls):
    #translate_slides_range(start_slide, end_slide, batch_size=50, max_elements=1000000, debug_mode=True) 
