# cython: language_level=3
# distutils: language=c++

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool

# Declare the C++ class
cdef extern from "speech_clean.hpp":
    cdef cppclass Clean_Text:
        Clean_Text(const string& raw_text, const string& file_name, int min_chars)
        void process_text()
        int write_to_file()
        void add_to_db(const string& db_name, const string& user, const string& password, 
                      const string& host, int port, const string& table_name)
        string get_raw_text()
        void get_file()
        vector[string] get_sentenes()
        void get_clean_text()
        int get_sentence_count()

# Python wrapper class
cdef class PyCleanText:
    cdef Clean_Text* _clean_text
    
    def __cinit__(self, str raw_text, str file_name, int min_chars):
        self._clean_text = new Clean_Text(
            raw_text.encode('utf-8'),
            file_name.encode('utf-8'),
            min_chars
        )
    
    def __dealloc__(self):
        if self._clean_text is not NULL:
            del self._clean_text
    
    def process_text(self):
        """Clean the text using regex expressions"""
        self._clean_text.process_text()
    
    def write_to_file(self):
        """Write the cleaned text to the specified file"""
        return self._clean_text.write_to_file()
    
    def add_to_db(self, str db_name, str user, str password, str host, int port, str table_name="speeches"):
        """Add cleaned text to PostgreSQL database"""
        self._clean_text.add_to_db(
            db_name.encode('utf-8'),
            user.encode('utf-8'),
            password.encode('utf-8'),
            host.encode('utf-8'),
            port,
            table_name.encode('utf-8')
        )
    
    def get_raw_text(self):
        """Get the raw text"""
        return self._clean_text.get_raw_text().decode('utf-8')
    
    def get_file(self):
        """Get the file name"""
        self._clean_text.get_file()
    
    def get_sentences(self):
        """Get the list of cleaned sentences"""
        cdef vector[string] sentences = self._clean_text.get_sentenes()
        return [s.decode('utf-8') for s in sentences]
    
    def get_clean_text(self):
        """Get the cleaned text"""
        self._clean_text.get_clean_text()
    
    def get_sentence_count(self):
        """Get the number of sentences"""
        return self._clean_text.get_sentence_count() 