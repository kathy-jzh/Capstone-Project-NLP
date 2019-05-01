# coding: utf-8

from gensim.models.keyedvectors import KeyedVectors
from itertools import product
from collections import defaultdict
from scipy.spatial.distance import euclidean
import pulp
from nltk.corpus import stopwords
import nltk, string


class Similarity_score():
    def __init__(self, target_text, text_list, model_path):
        self.target_text = target_text
        self.text_list = text_list
        self.w2v_model = KeyedVectors.load(model_path)

    def result(self):
        """
        Using Word Mover's Distance algorithm and the pre-trained word vector to calculate similarity scores
        :return: the similarity score of target text and comparable texts in text list
        """

        def tokens_to_fracdict(tokens):
            """
            Decompose sentences to tokens
            :param tokens: a list of tokens to handle
            :return: a dictionary of {token: frequency of token}
            """
            cntdict = defaultdict(lambda: 0)
            for token in tokens:
                cntdict[token] += 1
            totalcnt = sum(cntdict.values())
            return {token: float(cnt) / totalcnt for token, cnt in cntdict.items()}


        def word_mover_distance_probspec(first_sent_tokens, second_sent_tokens, wvmodel, lpFile=None):
            """
            apply Word Mover's Distance algorithm
            :param first_sent_tokens: target text
            :param second_sent_tokens: comparable text (each text in the text list)
            :param wvmodel: the pre-trained word vector model
            :param lpFile: a file to store the result
            :return: a pulp LpProblem (will yield the result in the last part of <result> function)
            """
            all_tokens = list(set(first_sent_tokens + second_sent_tokens))
            wordvecs = {}
            for token in all_tokens:
                try:
                    wordvecs[token] = wvmodel[token]
                except:
                    wordvecs[token] = 0

            first_sent_buckets = tokens_to_fracdict(first_sent_tokens)
            second_sent_buckets = tokens_to_fracdict(second_sent_tokens)

            T = pulp.LpVariable.dicts('T_matrix', list(product(all_tokens, all_tokens)), lowBound=0)

            prob = pulp.LpProblem('WMD', sense=pulp.LpMinimize)
            prob += pulp.lpSum([T[token1, token2] * euclidean(wordvecs[token1], wordvecs[token2])
                                for token1, token2 in product(all_tokens, all_tokens)])
            for token2 in second_sent_buckets:
                prob += pulp.lpSum([T[token1, token2] for token1 in first_sent_buckets]) == second_sent_buckets[token2]
            for token1 in first_sent_buckets:
                prob += pulp.lpSum([T[token1, token2] for token2 in second_sent_buckets]) == first_sent_buckets[token1]

            if lpFile != None:
                prob.writeLP(lpFile)

            prob.solve()
            return prob


        def normalize(text):
            """
            remove punctuation, lowercase, stem
            :param text:
            :return: a list of normalized words
            """
            stop_words = set(stopwords.words('english')) - set(['no', 'not', 'nor'])  # drop 'no', 'not', and 'nor'
            remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
            res = nltk.word_tokenize(text.lower().translate(remove_punctuation_map))
            return [w for w in res if w not in stop_words]

        res = []
        for i in range(0, len(self.text_list)):
            prob = word_mover_distance_probspec(normalize(self.target_text),
                                                normalize(self.text_list[i]),
                                                self.w2v_model)
            res.append(1 - pulp.value(prob.objective) / 5)
        return res # the similarity score based on Word Mover's Distance algorithm
