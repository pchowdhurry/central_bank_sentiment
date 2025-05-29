#include <poppler-document.h>
#include <poppler-page.h>
#include <iostream>
#include <vector> 
#include "text_extract.hpp"
#include <memory>
#include<regex>
#include<stdexcept>
#include<fstream> 
#include <cctype>  // for isascii

bool is_ascii_only(const std::string& sentence) {
    for (char c : sentence) {
        if (!::isascii(static_cast<unsigned char>(c)))
            return false;
    }
    return true;
}

using namespace std ; 
string new_line = "\n";

void Doc::extract_text(const std::string& file){
    std::regex sentence_regex(R"(([^.!?]+[.!?]))"); // Match full sentences
    
    std::unique_ptr<poppler::document> curr_doc(poppler::document::load_from_file(file)); 

    if(!curr_doc){
        cerr << "Failed to load PDF file, error in name" << endl ; 
        return;
    }

    // string to hold the result full text 
    string text ; 

    for (int i =0; i < curr_doc->pages(); i ++){
        std::unique_ptr<poppler::page> page(curr_doc->create_page(i)); 

        if(!page) {
            continue ; 
        }
        auto bytes = page->text().to_utf8(); 
        if (bytes.empty()){
            continue; 
        }
        auto latin_bytes = page->text().to_latin1();  // store the result
        std::string raw(latin_bytes.begin(), latin_bytes.end());  // now safe

        sregex_iterator it(raw.begin(), raw.end(), sentence_regex); 
        std::sregex_iterator end ; 

        for (; it!= end; it++){
            string curr = it->str(); 
            // cleanup extra spaces 
            string sentence = std::regex_replace(curr, std::regex("^\\s+|\\s+$"), "");

            if (!is_ascii_only(sentence)){
                continue ; 
            }
            if (sentence.length() < 30){
                continue; 
            }
            if (sentence.find('(') != std::string::npos || sentence.find(')') != std::string::npos) {
    continue;  // skip sentences with parentheses
}
            if(sentence.empty() == false){
                size_t pos  = sentence.find(new_line);
                if (pos != std::string::npos){
                    sentence.erase(pos, new_line.length());
                }
                text += sentence; 
                text += " "; 
                this->sentences.push_back(sentence); 
            }
        }
    }
    // filling out the fields of the class
    this->file_name = file; 
    this->file_text = text ; 
    this->num_pages = curr_doc->pages(); 
}

Doc::Doc(const string& file_name){
    try {
        extract_text(file_name);
    }
    catch (const std::exception& e ){
        cerr << "Encountered exception when calling constructor" << endl ; 
    }
}

int Doc::write_to_file() const {
    std::regex sentence_regex(R"(([^.!?\n]+[.!?]))"); // Match full sentences
    string total_text = this->file_text; 
    string out_name = "Text for " + this->file_name+".txt"; 
    
    ofstream output(out_name); 


    for(std::string words : this->sentences){
        output << words << "\n"; 
    }
    output.close(); 
    return 1; 

}

void Doc::show_text(){
    std::cout << this->file_text << std::endl ; 
}
void Doc::show_file(){
    std::cout << this->file_name << std::endl ; 
}
void Doc::show_page(){
    std::cout << this->num_pages << std::endl ; 
}
