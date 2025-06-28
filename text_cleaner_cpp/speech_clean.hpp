#ifndef CLEAN_TEXT 
#define CLEAN_TEXT 

#include <string>
#include <vector> 

class Clean_Text{

    /*
    Private methods and attributes 
    */
   private : 

   std::string raw_text ; 
   std::string file_name ; 
   std::string cleaned_text;
   std::vector<std::string> sentences ;
   int min_chars; 
   int num_sentences = 0; 
   std::string date ; 

   bool is_ascii_only(const std::string& sentence);

   public : 
   // Constructor for class 
   Clean_Text(const std::string &raw_text , const std::string &file_name, int min_chars);
   /* note 
   raw_text is the parsed text from the python scraper that will be cleaned and processed
   file_name is the file that will be created and will store the text 
   */

  // This will clean the text using a regex expression
  void process_text(); 

  // This will write the cleaned text to the file specified in the constructor 
  int write_to_file();

  // This function stores the cleaned text along with additional information into the postgres database specified in the specified table 
  void add_to_db(const std::string& db_name, 
  const std::string& user  ,
  const std::string& password, 
  const std::string& host , 
  const int port, 
  const std::string& table_name = "speeches");

  // Method that get information about the text and object 

  // This will print the raw text to the console
  std::string get_raw_text() const; 

  // This will print the file name to hte console 
  void get_file() const; 

  // This will show each sentence stored in the vector of sentences 
  std::vector<std::string> get_sentenes() const ; 

  // This will show the cleaned text 
  void get_clean_text() const;
  
  // This will print the count of sentences to the console 
  int get_sentence_count() const ;

};

#endif 

