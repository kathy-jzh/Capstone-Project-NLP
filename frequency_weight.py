#!/usr/bin/env python
# coding: utf-8

def word_freq_dict (text):
    import re
    import nltk

    # Preprocessing the data
    text = re.sub(r'\[[0-9]*\]',' ',text)
    text = re.sub(r'\s+',' ',text)
    clean_text = text.lower()
    clean_text = re.sub(r'\W',' ',clean_text)
    clean_text = re.sub(r'\d',' ',clean_text)
    clean_text = re.sub(r'\s+',' ',clean_text)

    # Tokenize sentences
    sentences = nltk.sent_tokenize(text)

    # Stopword list
    stop_words = nltk.corpus.stopwords.words('english')

    # Word counts 
    word2count = {}
    for word in nltk.word_tokenize(clean_text):
        if word not in stop_words:
            if word not in word2count.keys():
                word2count[word] = 1
            else:
                word2count[word] += 1

    # Converting counts to weights
    max_count = max(word2count.values())
    for key in word2count.keys():
        word2count[key] = word2count[key]/max_count
    return word2count


def sent_score(word2count,text):
    import re
    import nltk
    
    # Tokenize sentences
    sentences = nltk.sent_tokenize(text)

    
    sent2score = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word2count.keys():
                if sentence not in sent2score.keys():
                    sent2score[sentence] = word2count[word]
                else:
                    sent2score[sentence] += word2count[word]
    return sent2score


def sql_freq (term,text):
    import sqlite3
    sqlite_file = 'database.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    
    query = """SELECT definition
    FROM DEFINITION
    WHERE term = '""" + term +"'"
    c.execute(query)
    
    a = c.fetchall()
    t = str()
    for i in a:
        t += i[0]
    word_dict = word_freq_dict(str(t))
    return(sent_score(word_dict,text))

def indenture_names(x):
    return x.split('.')[0]

def get_sent_score(search_term, all_text):
    # Get sentence and sentence score for every term in every indenture
    sent_list = []
    sent_score_list = []
    for comp_text in all_text:
        sql_result = sql_freq(search_term, comp_text)
        temp = [x[1] for x in sql_freq(search_term, comp_text).items()]
        sent_list.append('##'.join([x[0] for x in sql_result.items()]))
        sent_score_list.append('##'.join([str(ele/max(temp))[:4] for ele in temp]))
    return sent_list, sent_score_list

def color_df(row):
    def color_range(num_color):
        from colour import Color
        import numpy as np
        red = Color("red")
        colors = list(red.range_to(Color("green"),num_color))
        score_range=np.linspace(0,1,num_color+1)
        return colors, score_range
    
    colors, score_range=color_range(3)
    color=''
    num=row.index.get_level_values(0)=='Sent_Score'
    text=row.index.get_level_values(0)=='Text'
    for j in range(len(score_range)-1):
        if score_range[j] <= row[num][0] <= score_range[j+1]:
            color = colors[j].hex
    return ['color: %s' % color if x else '' for x in text]
