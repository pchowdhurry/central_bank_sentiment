import sys 
import os 
import time 
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.mixture import GaussianMixture
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np 
from typing import Dict, List, Any 
import re 

from pathlib import Path
sys.path.append(os.path.join(Path(__file__).parent, '..'))  # Go up to project root
from pdf_parser_cpp.cython_parser import PDF_Text
import pickle 
from tqdm import tqdm
# Check what's available
print("Current directory:", os.getcwd())
print("Available directories:", os.listdir('.'))

# Fix the path - go up one level to find data/
data_dir = '../data/bis_data'
pdf_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir)
              if file.endswith('.pdf')]

print(f"Found {len(pdf_files)} PDF files")

def show_file_text(file: str = None):
    if file is None: 
        raise ValueError("Must specify file")
    else: 
        object = PDF_Text(file)  # Now receives full path
        all_text = object.get_text()
        return all_text

# time test:
# time_start = time.time()
# time_log = []
# for name in pdf_files[0:1]:
#     # run function 
#     doc_text = show_file_text(name)
#     doc_time = time.time()
#     time_log.append(doc_time)
#     time_taken = doc_time - time_start if len(time_log) == 0 else doc_time - time_log[-1]
#     print(f"Processed {os.path.basename(name)} in {time_taken:.4f}s")

# end_time = time.time()
# total_time = end_time - time_start
# print(f"Total time: {total_time:.4f}s")
# print(doc_text)

def process_all_files(directory: str): 
    exists = True if os.path.isdir('../data/'+directory) else False 
    if not exists : 
        raise ValueError("Directory does not exist")
    
    elif exists : 
        file_list = [os.path.join(data_dir,file) for file in os.listdir('../data/'+directory)
                     if file.endswith('.pdf')]
        page_count = 0 
        text_values = {}
        for i in tqdm(range(len(file_list))):
            try:
                object = PDF_Text(file_list[i])
                text = object.get_text()
                pages = object.get_num_pages()
                file_name = object.get_filename()
                page_count += pages 
                print(f'Processed {page_count} pages')
                text_values[file_name] = text 
            except Exception as e:
                print(f"Error processing {file_list[i]}: {e}")
                continue
        
        print('transferring to pickle')
        with open('../data/processed.pkl', 'wb')as file :
            pickle.dump(text_values, file=file)

class Vectorize : 

    def __init__(self,
     model : str='sentence-transformers/all-MiniLM-L6-v2', max_tokens :int = 384): 
        self.model_name = model 
        self.model = SentenceTransformer(model)
        self.token_limit = max_tokens
    
    def __prepare_tokens(self, text: Dict[str,str]):
        max_len = self.token_limit
        for key, entry in text.items():
            interm_list = []
            sentence_list = sent_tokenize(entry)
            curr_sentence = ''
            counter = 0
            for sentence in sentence_list:
                word_count = len(word_tokenize(sentence))
                counter += word_count
                if counter <= max_len:
                    curr_sentence += sentence 

                elif counter > max_len : 
                    interm_list.append(curr_sentence)
                    curr_sentence = sentence
                    counter = word_count
            curr_date = self.__date_matcher(key)
            text[curr_date] = interm_list
        return text 
    
    def tfidf_vectorize(self, text_dict: Dict[str,str]):
        tokens = self.__prepare_tokens(text_dict)
        tf_vectorizer = TfidfVectorizer(
            max_features=self.token_limit,
            stop_words='english'
        )
        output = {}
        for key, sentences in tokens.items():
            interm = []
            for sentence in sentences: 
                X = tf_vectorizer.fit_transform(sentence)
                interm.append(X)
            match = self.__date_matcher(key)
            output[match] = interm 

        return output 
    
    def embedding_vectorize_chunk(self, text_dict: Dict[str,str]): 
        tokens = self.__prepare_tokens(text_dict)
        model = self.model 
        output = {}

        for key, sentences in tokens.items():
            interm_list = []
            for sent in sentences : 
                X = model.encode(sent)
                interm_list.append(X)
            output[key] = interm_list
        return output 

    def __date_matcher(self, title: str): 
        regex = r'\d{4}-\d{2}-\d{2}'
        curr_match = re.search(regex, title)

        if curr_match : 
            date = curr_match.group()
            return date 
        elif not curr_match:
            return title 
        
    def embedding_whole(self, text_dict:Dict[str,str]):
        tokens = self.__prepare_tokens(text_dict)
        model = self.model 
        output_dict = {}

        for key, values in tokens.items():
            date = self.__date_matcher(key)
            interm = []
            for words in values : 
                vector = model.encode(words)
                interm.append(vector)
            output_dict[date] = np.mean(np.array(interm), axis=1)
        return output_dict


class MixtureMode:

    def __init__(self, k:int, cov_type:str= 'full',random_state = 100, vector_size = 256 ):
        self.mixture = GaussianMixture(n_components=k, covariance_type=cov_type, random_state=random_state)
        self.dims = k 
        self.vec_size = vector_size
    
    def get_preds(self, text:Dict[str,List], hard:bool = True, soft:bool= True ):
        #aggregate all vectors 
        sum_list = sum([len(l1) for l1 in text.values()])
        size = self.vec_size
        arr = np.zeros(shape = (len(text)*sum_list, size))
        i = 0 
        for item in text.values : 
            for array in item : 
                arr[i] = array 
                i += 1 
        
        self.mixture.fit(arr)
        if hard and not soft  : 
            h_labels = self.mixture.predict(arr)
            return h_labels
        elif soft and not hard : 
            s_labels = self.mixture.predict_proba(arr)
            return s_labels
        
        elif soft and hard : 
            h_labels = self.mixture.predict(arr)
            s_labels = self.mixture.predict_proba(arr)
            return (s_labels, h_labels)


class PCAMatrix: 

    def __init__(self, num_components : int  = 100):
        self.components = num_components 
        self.model = PCA(n_components = self.components)
        self.applied_pca = False 

    def apply_pca(self, data):
        try : 
            output_matrix = self.model.fit_tranform(data)
           
            if output_matrix:
                if self.applied_pca == False : 
                    self.applied_pca = True 
                return output_matrix
            else : 
                return None 
        except Exception as e : 
            raise ValueError(f'Encountered the following error : {e}')
    
    def get_explained_variance(self):
        if self.applied_pca == False : 
            print(f' Must apply pca to a dataset to get explained variance')

        elif self.applied_pca == True : 
            explained_ratio = self.model.explained_variance_ratio_ # Ratio 
            explained_var = self.model.explained_variance_ 

            print(f'Explained variance by component :\n {explained_ratio}')
            return (explained_ratio, explained_var)
    
            
        


        
        
    
        
                

        




            

                






if __name__ == '__main__':
    process_all_files(directory = 'bis_data')