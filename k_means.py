import glob as gl
from sklearn.cluster import KMeans as km
from sklearn.feature_extraction.text import TfidfVectorizer as tv
import spacy as sp
from nltk import PorterStemmer as ps

sp = sp.load("en_core_web_sm") #loads Spacy english
ps = ps() #loads Porter Stemmer
clusters = 8 #assigns k

class K_Means:

    def __init__(self, stop):
        self.representation = {} #declares instance variable representation
        self.dirty_texts = {} #declares instance variable dirty_texts
        self.read() #reads text and assigns dirty_texts
        processed_text = self.process(stop) #processes text
        vector = self.cluster(processed_text) #clusters text
        self.label(vector) #labels clusters
        self.represent() #categorizes labels
        
    def read(self):
        path = "flaskr/DirtyText/*.txt"
        filenames = gl.glob(path)
        for filename in filenames:
            dirty_text = open(filename, "r")
            self.dirty_texts.update({filename[17:] : dirty_text.read()})       

    def process(self, stop):
        processed_text = []
        for filename in list(self.dirty_texts):
            preprocessed_text = sp(self.dirty_texts[filename])
            for word in preprocessed_text:
                if word.is_stop == False and len(word.lemma_) > 4 and word.pos_ == "ADJ" and word.lemma_ not in stop:
                    processed_text.append(word.lemma_.lower())
        return processed_text

    def cluster(self, processed_text):
        vector = tv(use_idf = True)
        self.matrix = vector.fit_transform(processed_text)
        self.model = km(n_clusters = clusters, n_init = 1000)
        self.model.fit(self.matrix)
        self.model_pred = km(n_clusters = clusters, n_init = 1000)
        self.model_pred.fit_predict(self.matrix)
        return vector
        
    def label(self, vector):
        cluster_centers = self.model.cluster_centers_.argsort()[:,::-1]
        cluster_words = vector.get_feature_names()
        for i in range(clusters):
            topic = [cluster_words[j] for j in cluster_centers[i,:]][0]
            self.representation.update({topic : {"forms" : [], "count" : 0, "count_per" : [], "local" : 0, "global" : 0, "male" : 0, "female" : 0, "other" : 0, "gen_z" : 0, "gen_y" : 0, "gen_x" : 0, "baby_boomers" : 0}})
            
    def represent(self):
        for i in range(len(list(self.dirty_texts))):
            split_text = self.dirty_texts[list(self.dirty_texts)[i]].split()
            for topic in self.representation:
                stemmed_topic = ps.stem(topic)
                count = 0
                for word in split_text:
                    if (ps.stem(word) == stemmed_topic or ps.stem(word[:-1]) == stemmed_topic) and len(word) > 4:
                        self.representation[topic]["forms"].append(word)
                        self.representation[topic]["count"] = self.representation[topic]["count"] + 1
                        count += 1
                        if list(self.dirty_texts)[i][0:1] == "l":
                            self.representation[topic]["local"] = self.representation[topic]["local"] + 1
                        if list(self.dirty_texts)[i][0:1] == "g":
                            self.representation[topic]["global"] = self.representation[topic]["global"] + 1
                        if list(self.dirty_texts)[i][1:2] == "m": 
                            self.representation[topic]["male"] = self.representation[topic]["male"] + 1
                        if list(self.dirty_texts)[i][1:2] == "f": 
                            self.representation[topic]["female"] = self.representation[topic]["female"] + 1 
                        if list(self.dirty_texts)[i][1:2] == "o": 
                            self.representation[topic]["other"] = self.representation[topic]["other"] + 1 
                        if list(self.dirty_texts)[i][2:3] == "z": 
                            self.representation[topic]["gen_z"] = self.representation[topic]["gen_z"] + 1
                        if list(self.dirty_texts)[i][2:3] == "y": 
                            self.representation[topic]["gen_y"] = self.representation[topic]["gen_y"] + 1    
                        if list(self.dirty_texts)[i][2:3] == "x": 
                            self.representation[topic]["gen_x"] = self.representation[topic]["gen_x"] + 1    
                        if list(self.dirty_texts)[i][2:3] == "b": 
                            self.representation[topic]["baby_boomers"] = self.representation[topic]["baby_boomers"] + 1
                self.representation[topic]["count_per"].append(count)    
