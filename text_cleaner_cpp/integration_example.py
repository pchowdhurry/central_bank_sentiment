#!/usr/bin/env python3
"""
Example integration of Cython Clean_Text wrapper with Python scrapers
"""

import sys
import os

# Add the parent directory to the path to import scrapers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scraper_py'))

def integrate_with_scrapers():
    """Example of how to use the Cython wrapper with scrapers"""
    
    try:
        # Import the Cython wrapper
        from speech_clean_wrapper import PyCleanText
        
        # Example: Process text from a scraper
        # This would typically come from your fed_scraper.py or collect_fed.py
        
        # Sample scraped text (replace with actual scraper output)
        scraped_text = """
        Federal Reserve Chair Jerome Powell delivered remarks today.
        The economy continues to show resilience despite challenges.
        Inflation remains a key concern for monetary policy.
        We will continue to monitor economic indicators closely.
        """
        
        # Create Clean_Text instance
        cleaner = PyCleanText(
            raw_text=scraped_text,
            file_name="fed_speech_cleaned.txt",
            min_chars=15  # Minimum characters per sentence
        )
        
        print("=== Integration Example ===")
        print("Processing scraped text...")
        
        # Clean the text
        cleaner.process_text()
        
        # Get results
        sentence_count = cleaner.get_sentence_count()
        sentences = cleaner.get_sentences()
        
        print(f"Found {sentence_count} valid sentences:")
        for i, sentence in enumerate(sentences, 1):
            print(f"  {i}. {sentence}")
        
        # Write to file
        if cleaner.write_to_file():
            print("Successfully saved cleaned text to file!")
        
        # Example database integration (uncomment if you have a database)
        # cleaner.add_to_db(
        #     db_name="speeches_db",
        #     user="your_user",
        #     password="your_password", 
        #     host="localhost",
        #     port=5432,
        #     table_name="cleaned_speeches"
        # )
        
        return True
        
    except ImportError as e:
        print(f"Error: Could not import speech_clean_wrapper. Make sure you've built it first.")
        print(f"Run: cd text_cleaner_cpp && ./build_cython.sh")
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error during integration: {e}")
        return False

def example_with_scraper_function():
    """Example showing how to integrate with an actual scraper function"""
    
    # This is how you would integrate with your existing scrapers
    # from fed_scraper import scrape_fed_speeches  # Your actual scraper
    
    # def process_scraped_speeches():
    #     # Get speeches from scraper
    #     speeches = scrape_fed_speeches()
    #     
    #     for speech in speeches:
    #         # Create cleaner for each speech
    #         cleaner = PyCleanText(
    #             raw_text=speech['text'],
    #             file_name=f"speech_{speech['date']}.txt",
    #             min_chars=20
    #         )
    #         
    #         # Process and save
    #         cleaner.process_text()
    #         cleaner.write_to_file()
    #         
    #         # Optionally save to database
    #         # cleaner.add_to_db(...)
    
    print("Example scraper integration function defined (commented out)")

if __name__ == "__main__":
    success = integrate_with_scrapers()
    if success:
        print("\nIntegration test completed successfully!")
    else:
        print("\nIntegration test failed. Please check the errors above.") 