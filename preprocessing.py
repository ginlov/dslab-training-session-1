import numpy as np
import os
import re

def gather_20newsgroups_data():
    path = 'dataset/'
    dirs = [path + dir_name + '/' 
            for dir_name in os.listdir(path)
            if not os.path.isfile(path+ dir_name)]
    train_dir, test_dir = (dirs[0], dirs[1]) if 'train' in dirs[0] else (dirs[1], dirs[0])
    list_newsgroups = [newsgroup for newsgroup in os.listdir(train_dir)]
    list_newsgroups.sort()

    with open('dataset/stop_words.txt') as f:
        stop_words = f.read().splitlines()
    from nltk.stem.porter import PorterStemmer
    stemmer = PorterStemmer()
    def collect_data_from(parent_dir, newsgroup_list):
        data = []
        for group_id, newsgroup in enumerate(newsgroup_list):
            label = group_id
            dir_path = parent_dir + '/' + newsgroup + '/'
            files = [(filename, dir_path + filename)
                    for filename in os.listdir(dir_path)
                    if os.path.isfile(dir_path + filename)]
            files.sort()
            for filename, filepath in files:
                print(filepath+ "\n")
                with open(filepath, encoding='latin1') as f:
                    text = f.read().lower()
                    words = [stemmer.stem(word)
                            for word in re.split('\W+', text)
                            if word not in stop_words]
                    content = ' '.join(words)
                    assert len(content.splitlines()) == 1
                    data.append(str(label) + '<fff>' +
                                filename + '<fff>' + content)
        return data

    train_data = collect_data_from(
        parent_dir=train_dir,
        newsgroup_list=list_newsgroups
    )
    test_data = collect_data_from(
        parent_dir=test_dir,
        newsgroup_list=list_newsgroups
    )
    full_data = train_data + test_data
    with open('dataset/20news-train-processed.txt', 'w') as f:
        f.write('\n'.join(train_data))
    with open('dataset/20news-test-processed.txt', 'w') as f:
        f.write('\n'.join(test_data))
    with open('dataset/20news-full-processed.txt', 'w') as f:
        f.write('\n'.join(full_data))

def generate_vocabulary(data_path):
    def compute_idf(df, corpus_size):
        assert df > 0
        return np.log10(corpus_size * 1. / df)
    with open(data_path) as f:
        lines = f.read().splitlines()
    doc_count = {}
    corpus_size = len(lines)

    for line in lines:
        features = line.split('<fff>')
        text = features[-1]
        words = list(set(text.split()))
        for word in words:
            if word in doc_count.keys():
                doc_count[word] += 1
            else:
                doc_count[word] = 1
    words_idfs = [(word, compute_idf(document_freq, corpus_size))
                    for word, document_freq in
                    zip(doc_count.keys(), doc_count.values())
                    if document_freq > 10 and not word.isdigit()]
    #words_idfs.sort(key=lambda(word, idf): -idf)
    print( 'Vocabulary size: {}'.format(len(words_idfs)))
    with open('./dataset/words_idfs.txt', 'w') as f:
        f.write('\n'.join([word + '<fff>' + str(idf) for word, idf in words_idfs]))

def get_tf_idf(data_path):
    with open('./dataset/words_idfs.txt') as f:
        words_idfs = [(line.split('<fff>')[0], float(line.split('<fff>')[1]))
                        for line in f.read().splitlines()]
        word_IDs = dict([(word, index)
                        for index, (word, idf) in enumerate(words_idfs)])
        idfs = dict(words_idfs)
    with open(data_path) as f:
        documents = [
            (int(line.split('<fff>')[0]),
            int(line.split('<fff>')[1]),
            line.split('<fff>')[2])
            for line in f.read().splitlines()]
    data_tf_idf = []
    for document in documents:
        label, doc_id, text = document
        words = [word for word in text.split() if word in idfs]
        word_set = list(set(words))
        max_term_freq = max([words.count(word)
                            for word in word_set])
        words_tfidfs = []
        sum_squares = 0.0
        for word in word_set:
            term_freq = words.count(word)
            tf_idf_value = term_freq * 1. / max_term_freq * idfs[word]
            words_tfidfs.append((word_IDs[word], tf_idf_value))
            sum_squares += tf_idf_value ** 2
        words_tfidfs_normalized = [str(index) + ':'
                                    + str(tf_idf_value / np.sqrt(sum_squares))
                                    for index, tf_idf_value in words_tfidfs]
        sparse_req = ' '.join(words_tfidfs_normalized)
        data_tf_idf.append((label, doc_id, sparse_req))
    with open('./dataset/tf_idf.txt', 'w') as f:
        for item in data_tf_idf:
            f.write(str(item[0]) + '<fff>' + str(item[1]) + '<fff>' + item[2] + '\n')
        
get_tf_idf('./dataset/20news-full-processed.txt')