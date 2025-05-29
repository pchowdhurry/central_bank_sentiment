#include "text_extract.hpp"
#include <string>
#include <iostream>

int main(){
    std::string file = "test.pdf";

    Doc curr(file); 

    curr.show_text(); 
    curr.write_to_file();
    return 1; 
}