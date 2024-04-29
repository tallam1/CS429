# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import pickle
import re

from itemadapter import ItemAdapter
from collections import defaultdict

class Cs429ProjectPipeline:

    

    def open_spider(self, spider):
        # Initialize lists to store seperate values
        self.review =[]
        self.url = []
        self.title = [] 
        self.score=[]
        self.title_url_mapping = {}
        


    def process_item(self, item, spider):
        #use items to keep track of text
        item_adap = ItemAdapter(item)
        print("text from process item:" , item_adap['review'])
        self.title.append(item_adap['title'])
        print('process item text', self.review)
        if 'review' in item_adap:
            preprocessed_text = preprocess(item_adap['review'])
            if preprocessed_text:  # Ensure there is content after preprocessing
                self.review.append(preprocessed_text)
                print('preprocessed_text', self.review)
                self.url.append(item_adap['url'])
                self.title_url_mapping[item_adap['title']] = item_adap['url']
            else:
                spider.logger.debug(f"Preprocessed text was empty for URL {item_adap['url']}")
        return item
    
    def close_spider(self,spider):
        print('closed spider text', self.review)
        #build vectors for tf-idf values for each term
        with open ('url_title.json', 'w') as f:
            json.dump({
                'url' : self.url,
                'title' : self.title
            },f, indent=4)
        with open ('reviews.json', 'w') as f:
            json.dump({
                'reviews' : self.review,
            },f, indent=4)
        self.vectors = TfidfVectorizer()
        tf_idf_vec = self.vectors.fit_transform(self.review)
        


        # building the inverted idx with tfidf values
        
        feature_names = self.vectors.get_feature_names_out()
        inverted_ind = {feature: [] for feature in feature_names}
        for i, doc_vector in enumerate(tf_idf_vec):
            row = doc_vector.toarray().flatten()
            for j, tfidf_score in enumerate(row):
                if tfidf_score > 0:
                    inverted_ind[feature_names[j]].append((self.url[i],tfidf_score))
        print("This is a inverted index shape" , len(inverted_ind))
       

        url_title_mapping = {url : title for url, title in zip(self.url, self.title)}
        with open('url_title_mapping.pkl', 'wb') as f:
            pickle.dump(url_title_mapping, f)
        

        with open('inverted_index.pkl', 'wb')as f:
            pickle.dump(inverted_ind, f)
        

        with open('vectorizer.pkl', 'wb') as f:
             pickle.dump(self.vectors, f)
        with open ('inverted_index.json', 'w') as f:
            json.dump({
                'tf-idf_values' : inverted_ind
            },f, indent=4)


stop_words = set(stopwords.words('english'))

def preprocess(strings_test):
        # remove new line special characters between the strings
    strings_m = strings_test.replace('\n', ' ')

        #remove any additional unicode characters between the strings
    strings_m = re.sub(r'[^\x00-\x7F]+', ' ', strings_m)

        #remove all stop words
    string_t = strings_m.split()
    string_t = [str_test for str_test in string_t if str_test.lower() not in stop_words]

    processed_text = ' '.join(string_t)
        #return the string for tf-idf vectors
    return processed_text