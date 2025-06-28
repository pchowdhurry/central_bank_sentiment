#!/usr/bin/env python3
"""
Test script for the Cython wrapper of Clean_Text class
"""

def test_cython_wrapper():
    """Test the Cython wrapper functionality"""
    
    # Sample text to clean
    sample_text = """
    This is a sample speech text. It contains multiple sentences!
    Some sentences have punctuation marks. Others don't.
    We want to clean this text and extract meaningful sentences.
    """
    
    # Create a Clean_Text instance using the Cython wrapper
    from speech_clean_wrapper import PyCleanText
    
    # Initialize with raw text, output file name, and minimum character threshold
    cleaner = PyCleanText(
        raw_text=sample_text,
        file_name="cleaned_speech.txt",
        min_chars=10
    )
    
    print("=== Testing Cython Clean_Text Wrapper ===")
    print(f"Raw text: {cleaner.get_raw_text()}")
    print(f"Output file: ", end="")
    cleaner.get_file()
    
    # Process the text
    print("\nProcessing text...")
    cleaner.process_text()
    
    # Get results
    print(f"Number of sentences: {cleaner.get_sentence_count()}")
    print(f"Cleaned sentences: {cleaner.get_sentences()}")
    
    # Write to file
    print("\nWriting to file...")
    result = cleaner.write_to_file()
    if result:
        print("Successfully wrote to file!")
    else:
        print("Failed to write to file!")
    
    # Test database connection (commented out to avoid errors if DB not available)
    # print("\nTesting database connection...")
    # cleaner.add_to_db(
    #     db_name="test_db",
    #     user="test_user", 
    #     password="test_pass",
    #     host="localhost",
    #     port=5432,
    #     table_name="test_speeches"
    # )

if __name__ == "__main__":
    test_cython_wrapper() 