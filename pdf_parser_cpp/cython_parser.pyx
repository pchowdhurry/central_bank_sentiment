# cython: language_level=3
# distutils: language=c++

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool


cdef extern from "text_extract.hpp": 
    cdef cppclass Doc: 
        Doc(const string& file_path)
        int write_to_file() const 
        void show_text()
        void show_file()
        void show_page()
        void extract_text(const string& file_name)
        string get_text() const
        string get_filename() const
        int get_num_pages() const
        vector[string] get_sentences() const

# Wrapper class for pdf parser

cdef class PDF_Text: 
    cdef Doc* _pdf 
    
    def __cinit__(self, str file_name):
       
        cdef string cpp_file = file_name.encode('utf-8')
        self._pdf = new Doc(cpp_file)

    
    def __dealloc__(self):
        if self._pdf is not NULL:
            del self._pdf 
        
    def write_to_file(self):
        return self._pdf.write_to_file()

    def extract_text(self, str file_name):
        self._pdf.extract_text(file_name.encode('utf-8'))
    
    def show_text(self):
       self._pdf.show_text()

    def show_file(self):
        self._pdf.show_file()

    def show_page(self):
        self._pdf.show_page()

    def get_filename(self):
        cdef string text = self._pdf.get_filename()
        return text.decode('utf-8')

    def get_text(self):
        cdef string text = self._pdf.get_text()
        return text.decode('utf-8')
    
    def get_num_pages(self):
        return self._pdf.get_num_pages()

    def get_sentences(self):
        cdef vector[string] vector_sentence = self._pdf.get_sentences()
        cdef list sentences = []

        for sent in vector_sentence:
            sentences.append(sent.decode('utf-8'))
        return sentences 
    


    


        