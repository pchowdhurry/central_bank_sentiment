#ifndef TEXT_EXTRACT
#define TEXT_EXTRACT

#include <string>
#include <iostream>
#include <vector>
#include <map>
#include<regex>

class Doc {

private:
    std::string file_name ; 
    std::string file_text; 
    int num_pages ; 
    std::vector<std::string> sentences; 
    

public:
    Doc(const std::string& file_name); // constructor 
    int write_to_file () const; 
    void show_text() ; 
    void show_file () ; 
    void show_page () ; 
    void extract_text(const std::string& file_name); 
    
    // Fix these declarations to return values instead of void
    std::string get_text() const; 
    std::string get_filename() const; 
    int get_num_pages() const;
    std::vector<std::string> get_sentences() const;
};

#endif 