#include <array>
#include <string>
#include <vector>
#include <regex>
#include <fstream>
#include <iostream> 
#include <cctype> // for isascii 
#include <array>
#include "speech_clean.hpp"
#include <sstream>
#include <pqxx/pqxx>
#include <ctime>

using namespace std;

// Constructor implementation
Clean_Text::Clean_Text(const std::string &raw_text, const std::string &file_name, int min_chars) 
    : raw_text(raw_text), file_name(file_name), min_chars(min_chars), num_sentences(0) {
    // Initialize date to current date
    time_t now = time(0);
    struct tm* ltm = localtime(&now);
    char date_str[11];
    sprintf(date_str, "%04d-%02d-%02d", 1900 + ltm->tm_year, 1 + ltm->tm_mon, ltm->tm_mday);
    this->date = std::string(date_str);
}

bool Clean_Text::is_ascii_only(const std::string& sentence){
    for (char c : sentence){
        if (! ::isascii(static_cast<unsigned char>(c))){
            return false ;
        }
    }
    return true ;
}

std::string new_line = "\n";

std::vector<std::string> split_punctuation(const std::string& text){
    std::vector<std::string> results ; 
    std::string curr_sentence ; 
    for (char c: text){
        // Add the character to current sentence
        curr_sentence += c;
        
        // If we hit sentence-ending punctuation, split here
        if (c == '.' || c == '!' || c == '?'){
            if (!curr_sentence.empty()){
                results.push_back(curr_sentence);
                curr_sentence.clear();
            }
        }
    }
    // Add any remaining text
    if (!curr_sentence.empty()){
        results.push_back(curr_sentence);
    }
    return results;  
}

void Clean_Text::process_text(){
    std::vector<std::string> raw_text = split_punctuation(this->raw_text); 

    for (std::string sentence : raw_text){
        // cleaning additional space before and after sentence 
        sentence.erase(0, sentence.find_first_not_of(" \t\n\r"));
        sentence.erase(sentence.find_last_not_of(" \t\n\r")+1);
        
        if (is_ascii_only(sentence) && sentence.size() >= this->min_chars){
            this->sentences.push_back(sentence);
            this->cleaned_text += sentence ;
            this->num_sentences++;
        }

    }
    std::cout << "Number of lines processed: "<< this->num_sentences << std::endl;
}

int Clean_Text::write_to_file(){
    std::vector<std::string> cleaned_sentences = this->sentences ; 

    std::string out_file_name = this->file_name;
    std::ofstream file(out_file_name);
    for (std::string clause : cleaned_sentences){

        try {
            file << clause << "\n"; 
        }
        catch (std::exception& e){
            std::cerr << "Encountered error when writing: " << e.what() << std::endl ;
            return 0;
        }
    }
    file.close(); 
    return 1; 
}

void Clean_Text::get_clean_text() const{
    if (this->sentences.size() <= 0){
        std::cout << "Nothing to print as no sentences have been parsed"<< std::endl ; 
    }
    else if (this->sentences.size() > 0){
        std::cout << this->cleaned_text << std::endl ; 
    }
}

void Clean_Text::get_file() const{
    std::cout << "File Name to add Cleaned Text:" << this->file_name << std::endl; 
}

std::vector<std::string> Clean_Text::get_sentenes() const{
    if (this->sentences.size() <=0) {
        std::cout << "Nothing to print as no sentences have been parsed"<< std::endl ; 
    }
    else if (this->sentences.size() > 0){
        std::cout << "Number of sentences: " << this->sentences.size() << std::endl ;
        return this->sentences; 
    }
    return std::vector<std::string>();
}

std::string Clean_Text::get_raw_text() const{
    std::cout << this->raw_text << std::endl ; 
    return this->raw_text; 
}

int Clean_Text::get_sentence_count() const{
    std::cout << "Number of sentences in text: "<< this->num_sentences << std::endl;
    return this->num_sentences; 
}

void Clean_Text::add_to_db(const std::string& db_name, 
  const std::string& user  ,
  const std::string& password, 
  const std::string& host , 
  const int port,
  const std::string& table_name){
    try {
        std::string connect = "dbname=" + db_name +
                               " user=" + user +
                               " password=" + password +
                               " host=" + host +
                               " port=" + std::to_string(port);
        pqxx::connection connection(connect); 
        pqxx::work cursor(connection); 
        // Creating table if it doesn't exist 
        cursor.exec("CREATE TABLE IF NOT EXISTS " + table_name + R"(
            (
                id SERIAL PRIMARY KEY,
                date DATE, 
                text TEXT
            )
        )");

        cursor.exec_params(
            "INSERT INTO " + table_name + " (date, text) VALUES ($1, $2)",
                            this->date, this->cleaned_text);
                    
        }
  
    catch(std::exception& e){
        std::cerr << "Could not complete insertion into table  "<< e.what()<< std::endl;
    }
    std::cout << "Added number of sentences "<< this->num_sentences <<" to the database table " << table_name << std::endl;
    }
