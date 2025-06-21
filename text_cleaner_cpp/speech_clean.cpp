#include <string>
#include <vector>
#include <regex>
#include <fstream>
#include <iostream> 
#include <cctype> // for isascii 
#include "speech_clean.hpp"
#include <sstream>
#include <pqxx>
#include <ctime>
using namspace std ;
bool Clean_Text::is_ascii_only(const string& sentence){
    for (char c : sentence){
        if (! ::isascii(static_cast<unsigned char)(c)){
            return false ;
        }
    }
    return true ;
}

string new_line = "\n"; 

vector<string> split_punctuation(const& text){
    vector<string> results ; 
    string curr_sentence ; 
    for (char c: text){

        if (::ispunct(c)){
            if (!curr_sentence.empty()){
                results.push_back(curr_sentence);
                curr_sentence.clear();
            }
            else {
                current += c; 
            }   
        }
    }
    if (curr_sentence.empty() == false){
        results.push_back(curr_sentence);
    }
    return results;  
}

void Clean_Text::process_text(){
    vector<string> raw_text = split_punctuation(this->raw_text); 

    for (string sentence : raw_text){
        // cleaning additional space before and after sentence 
        sentence.erase(0, sentence.find_first_not_of(" \t\n\r"));
        sentence.erase(setence.find_last_not_of(" \t\n\r")+1); 
        
        if (is_ascii_only(sentence) && sentence.size() >= this->min_chars){
            this->sentences.push_back(sentence);
            this->cleaned_text += sentence ;
            this->num_sentences++;
        }

    }
    std::cout << "Number of lines processed: "<< this->num_sentences << std::endl;
}

int Clean_Text::write_to_file(){
    vector cleaned_sentences = this->sentences ; 

    string out_file_name = this->file_name; 
    ofstream file(file_name); 
    for (string clause : cleaned_sentences){

        try {
            file << clause << "\n"; 
        }
        catch (std::exception& e){
            std::err << "Encountered error when writing: " << e.what << std::endl ;
            return 0  
        }
    }
    file.close(); 
    return 1; 
}

void Clean_Text::get_clean_text(){
    if (this->sentences.size() <= 0){
        std::cout << "Nothing to print as no sentences have been parsed"<< std::endl ; 
    }
    else if (this->sentences.size > 0){
        std::cout << this->cleaned_text << std::endl ; 
    }
}
void Clean_Text::get_file(){
    std::cout << "File Name to add Cleaned Text:" << this->file_name << std::endl; 
}

std::vector Clean_Text::get_sentenes(){
    if (this->sentences.size() <=0) {
        std::cout << "Nothing to print as no sentences have been parsed"<< std::endl ; 
    }
    else if (this->sentences.size > 0){
        std::cout << this->sentences << std::endl ;
        return this->sentences; 
    }
}

std::string Clean_Text::get_raw_text(){
    std::cout << this->raw_text << std::endl ; 
    return this->raw_text; 
}

int Clean_Text::get_sentence_count(){
    std::cout << "Number of sentences in text: "<<this.num_sentences << std::endl; 
    return this.num_sentences; 
}

void Clean_Text::add_to_db(const std::string& db_name, 
  const std::string& user  ,
  const std::string& password, 
  const std::string& host , 
  const int& port, 
  const std::string& table_name = "speeches"){
    try {
        string connect = "dbname=" + db_name +
                               " user=" + user +
                               " password=" + password +
                               " host=" + host +
                               " port=" + std::to_string(port);
        pqxx::connection connection(connect); 
        pqxx::work cursor(connection); 
        // Creating table if it doesn't exsit 
        cursor.exec("CREATE TABLE IF NOT EXISTS " + table_name + R"(
            (
                id SERIAL PRIMARY KEY,
                date DATE, 
                text TEXT
            )
        )");

        cursor.exec_params(
            "INSERT INTO" + table_name + " (date, text) VALUES ($1, $2)",
                            this->date, this->cleaned_text);
                    
        }
  
    catch(std::exception& e){
        std::cerr << "Could not complete insertion into table  "<< e.what()<< std::endl;
    }
    std::cout << "Added number of sentences "<< this->num_sentences <<" to the database table " << table_name << std::endl;
    }
