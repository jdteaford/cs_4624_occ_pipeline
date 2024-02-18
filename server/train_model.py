import numpy as np 
import pickle
import pandas as pd
import re
from gensim.models import KeyedVectors
from gensim import utils
import gensim.parsing.preprocessing as gsp
from tqdm import tqdm
from zipfile import ZipFile
from sklearn import svm
from sklearn.manifold import TSNE
from sklearn.neural_network import MLPRegressor
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error
import base64
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup

# Note that this wv.model is not included in the application due to size constraints and must be downloaded separately
wv = KeyedVectors.load('wv.model')

class DocSim:
    def __init__(self, stopwords=None):
        self.stopwords = stopwords if stopwords is not None else []

    def vectorize(self, doc):
        vectors = np.empty((doc.shape[0], 300))
        for idx, row in enumerate(doc['Text']):
            words = [w for w in row.split(" ") if w not in self.stopwords]
            word_vecs = []
            for word in words:
                try:
                    vec = wv[word]
                    word_vecs.append(vec)
                except KeyError:
                    pass
            vectors[idx] = np.mean(word_vecs, axis=0)
        return vectors

    def _cosine_sim(self, vecA, vecB):
        csim = np.dot(vecA, vecB) / (np.linalg.norm(vecA) * np.linalg.norm(vecB))
        if np.isnan(np.sum(csim)):
            return 0
        return csim

    def calculate_similarity(self, source_doc, target_docs=None, threshold=0):
        if not target_docs:
            return []

        if isinstance(target_docs, str):
            target_docs = [target_docs]

        source_vec = self.vectorize(source_doc)
        results = []
        for doc in target_docs:

            target_vec = self.vectorize(doc)
            sim_score = self._cosine_sim(source_vec, target_vec)
            if sim_score > threshold:
                results.append({"score": sim_score, "doc": doc})
            results.sort(key=lambda k: k["score"], reverse=True)

        return results

def process_url(url):
    session = HTMLSession()

    try:
        html = session.get(url, timeout=1.0)
    except requests.exceptions.ReadTimeout:
        print("Timed Out")
        session.close()
        return ""
    except requests.exceptions.ConnectionError:
        print("Connection Error")
        session.close()
        return ""
    html = html.text.lower()
    soup = BeautifulSoup(html, features='html.parser')
    session.close()
    return soup.get_text()

def clean_text(s, filters):
    s = s.lower()
    s = utils.to_unicode(s)
    for f in filters:
        s = f(s)
    return s

def preprocess_data(df):
    filters = [
           gsp.strip_tags, 
           gsp.strip_punctuation,
           gsp.strip_multiple_whitespaces,
           gsp.strip_numeric,
           gsp.remove_stopwords, 
           gsp.strip_short, 
           gsp.stem_text
          ]

    df['Text'] = df['Text'].map(lambda x: clean_text(x, filters))

    ds = DocSim()
    return ds.vectorize(df)

def train_autoencoder(df):
    df.to_csv("train_data.csv", index=False)
    train_vectors = preprocess_data(df)

    model = MLPRegressor(hidden_layer_sizes=(600, 50, 600))
    model.fit(train_vectors, train_vectors)

    s = pickle.dumps(model)
    s = base64.b64encode(s).decode("ascii")

    return (np.array(model.loss_curve_) * 100).tolist(), s

def inference_autoencoder(model, df, document_names):
    train_df = pd.read_csv("train_data.csv", index_col=False)
    train_vectors = preprocess_data(train_df)

    test_vectors = preprocess_data(df)
    test_output = model.predict(test_vectors)

#    mse = lambda doc_idx: mean_squared_error(test_vectors[doc_idx], test_output[doc_idx])
#    mse_vals = list(map(mse, range(test_output.shape[0])))

    similarities = cosine_similarity(train_vectors, test_vectors).mean(axis=0)

    return similarities.tolist(), document_names

def label_autoencoder(model, related_df, unrelated_df, related_document_names, unrelated_document_names):
    train_df = pd.read_csv("train_data.csv", index_col=False)
    train_vectors = preprocess_data(train_df)

    test_related_vectors = preprocess_data(related_df)
    test_related_output = model.predict(test_related_vectors)

    test_unrelated_vectors = preprocess_data(unrelated_df)
    test_unrelated_output = model.predict(test_unrelated_vectors)

    test_vectors = np.concatenate([test_related_vectors, test_unrelated_vectors])
    test_output = np.concatenate([test_related_output, test_unrelated_output])

    vis = TSNE(n_components=2, learning_rate='auto', perplexity=3).fit_transform(test_output)
    vis = [{'x': str(round(vis[i, 0], 2)), 'y': str(round(vis[i, 1], 2))} for i in range(vis.shape[0])]

    related_similarities = cosine_similarity(train_vectors, test_related_vectors).mean(axis=0)
    unrelated_similarities = cosine_similarity(train_vectors, test_unrelated_vectors).mean(axis=0)


#    labels = ['Related'] * len(related_document_names) + ['Unrelated'] * len(unrelated_document_names)
    return related_similarities.tolist(), unrelated_similarities.tolist(), vis, related_document_names, unrelated_document_names

def train_model(model_type, data_type):
    df = pd.DataFrame(columns=['Text'])
    with ZipFile('data') as zipfile:
        for filename in tqdm(zipfile.infolist()):
            with zipfile.open(filename) as file:
                if re.match('url_.*.txt', file.name) is not None:
                    f = pd.DataFrame([file.read()], columns=['Text'])
                    df = pd.concat([df, f])

    if model_type == "ae":
        return train_autoencoder(df)

def process_file(file, df, filename, document_names, data_type):
    if data_type == "txt":
        if re.match('url_.*.txt', file.name) is not None:
            f = pd.DataFrame([file.read()], columns=['Text'])
            df = pd.concat([df, f])
            document_names.append(filename.filename)
            return df, document_names

    elif data_type == "urls":
        if re.match('urls.txt', file.name) is not None:
            f = pd.DataFrame(file.readlines(), columns=['Urls'])
            for url in f['Urls']:
                url = url.decode().strip()
                url_df = pd.DataFrame([process_url(url)], columns=['Text'])
                df = pd.concat([df, url_df])
                document_names.append(url)

    return df, document_names

def model_inference(model_type, data_type):
    with open('model', 'r') as f:
        pickle_string = f.read()
        pickle_bytes = base64.b64decode(pickle_string)
        model = pickle.loads(pickle_bytes)

    df = pd.DataFrame(columns=['Text'])
    document_names = []

    with ZipFile('data') as zipfile:
        for filename in tqdm(zipfile.infolist()):
            with zipfile.open(filename) as file:
                df, document_names = process_file(file, df, filename, document_names, data_type)

    if model_type == "ae":
        return inference_autoencoder(model, df, document_names)

def model_label(model_type, data_type):
    with open('model', 'r') as f:
        pickle_string = f.read()
        pickle_bytes = base64.b64decode(pickle_string)
        model = pickle.loads(pickle_bytes)

    related_df = pd.DataFrame(columns=['Text'])
    related_document_names = []

    with ZipFile('related_data') as zipfile:
        for filename in tqdm(zipfile.infolist()):
            with zipfile.open(filename) as file:
                related_df, related_document_names = process_file(file, related_df, filename, related_document_names, data_type)

    unrelated_df = pd.DataFrame(columns=['Text'])
    unrelated_document_names = []

    with ZipFile('unrelated_data') as zipfile:
        for filename in tqdm(zipfile.infolist()):
            with zipfile.open(filename) as file:
                unrelated_df, unrelated_document_names = process_file(file, unrelated_df, filename, unrelated_document_names, data_type)

    if model_type == "ae":
        return label_autoencoder(model, related_df, unrelated_df, related_document_names, unrelated_document_names)
