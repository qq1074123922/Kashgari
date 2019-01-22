# encoding: utf-8
"""
@author: BrikerMan
@contact: eliyar917@gmail.com
@blog: https://eliyar.biz

@version: 1.0
@license: Apache Licence
@file: embedding
@time: 2019-01-20

"""
import json
import logging
import os
from typing import Dict, Type

import keras
import keras_bert
import numpy as np
from gensim.models import KeyedVectors

from kashgari import k
from kashgari.utils import helper


EMBEDDINGS_PATH = os.path.join(k.DATA_PATH, 'embedding')


class EmbeddingModel(object):
    base_dict = {}

    special_tokens = {
        k.PAD: k.PAD,
        k.UNK: k.BOS,
        k.BOS: k.EOS,
        k.EOS: k.UNK,
    }

    def __init__(self,
                 name_or_path: str,
                 embedding_size: int = None,
                 **kwargs):
        self.name = name_or_path
        self.embedding_size = embedding_size
        self.model_path = ''

    def get_word2idx_dict(self):
        return self.base_dict


class Word2VecEmbedding(EmbeddingModel):
    base_dict = {
        k.PAD: 0,
        k.BOS: 1,
        k.EOS: 2,
        k.UNK: 3
    }

    pre_trained_models = {
        'sgns.weibo.bigram': 'embedding/word2vev/sgns.weibo.bigram.bz2'
    }

    def __init__(self,
                 name_or_path: str,
                 embedding_size: int = None,
                 **kwargs):
        super(Word2VecEmbedding, self).__init__(name_or_path, embedding_size, **kwargs)
        self.model_name = name_or_path
        self.model_path = helper.check_should_download(file=name_or_path,
                                                       download_url=self.pre_trained_models.get(name_or_path),
                                                       sub_folders=['embedding', 'w2v'])

        self.keyed_vector: KeyedVectors = KeyedVectors.load_word2vec_format(self.model_path, **kwargs)
        self.embedding_size = self.keyed_vector.vector_size
        logging.debug('------------------------------------------------')
        logging.debug('Loaded gensim word2vec model')
        logging.debug('model        : {}'.format(self.model_path))
        logging.debug('word count   : {}'.format(len(self.keyed_vector.index2entity)))
        logging.debug('Top 50 word  : {}'.format(self.keyed_vector.index2entity[:50]))
        logging.debug('------------------------------------------------')

    def get_embedding_matrix(self) -> np.array:
        base_matrix = []

        file = os.path.join(k.DATA_PATH, 'w2v_embedding_{}.json'.format(self.embedding_size))
        if os.path.exists(file):
            base_matrix = json.load(open(file, 'r', encoding='utf-8'))
            base_matrix = [np.array(matrix) for matrix in base_matrix]
        else:
            for index, key in enumerate(k.MARKED_KEYS):
                if index != 0:
                    vector = np.random.uniform(-0.5, 0.5, self.embedding_size)
                else:
                    vector = np.zeros(self.embedding_size)
                base_matrix.append(vector)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(json.dumps([list(item) for item in base_matrix]))

        matrix_list = base_matrix + list(self.keyed_vector.vectors)
        return np.array(matrix_list)

    def get_word2idx_dict(self):
        word2idx = self.base_dict.copy()
        for word in self.keyed_vector.index2entity:
            word2idx[word] = len(word2idx)
        return word2idx

    def __repr__(self):
        return 'word2vec:{}'.format(self.name)


class BERTEmbedding(EmbeddingModel):
    base_dict = {}
    special_tokens = {
        k.PAD: '[PAD]',
        k.UNK: '[UNK]',
        k.BOS: '[CLS]',
        k.EOS: '[SEP]',
    }
    
    pre_trained_models = {
        # BERT-Base, Uncased: 12-layer, 768-hidden, 12-heads, 110M parameters
        'uncased_L-12_H-768_A-12': 'https://storage.googleapis.com/bert_models/2018_10_18/'
                                   'uncased_L-12_H-768_A-12.zip',
        # BERT-Large, Uncased
        # 24-layer, 1024-hidden, 16-heads, 340M parameters
        'uncased_L-24_H-1024_A-16': 'https://storage.googleapis.com/bert_models/2018_10_18/'
                                    'uncased_L-24_H-1024_A-16.zip',
        # BERT-Base, Cased
        # 12-layer, 768-hidden, 12-heads , 110M parameters
        'cased_L-12_H-768_A-12': 'https://storage.googleapis.com/bert_models/2018_10_18/'
                                 'cased_L-12_H-768_A-12.zip',
        # BERT-Large, Cased
        # 24-layer, 1024-hidden, 16-heads, 340M parameters
        'cased_L-24_H-1024_A-16': 'https://storage.googleapis.com/bert_models/2018_10_18/'
                                  'cased_L-24_H-1024_A-16.zip',
        # BERT-Base, Multilingual Cased (New, recommended)
        # 104 languages, 12-layer, 768-hidden, 12-heads, 110M parameters
        'multi_cased_L-12_H-768_A-12': 'https://storage.googleapis.com/bert_models/2018_11_23/'
                                       'multi_cased_L-12_H-768_A-12.zip',
        # BERT-Base, Multilingual Uncased (Orig, not recommended)
        # 12-layer, 768-hidden, 12-heads, 110M parameters
        'multilingual_L-12_H-768_A-12': 'https://storage.googleapis.com/bert_models/2018_11_03/'
                                        'multilingual_L-12_H-768_A-12.zip',
        # BERT-Base, Chinese
        # Chinese Simplified and Traditional, 12-layer, 768-hidden, 12-heads, 110M
        'chinese_L-12_H-768_A-12': 'https://storage.googleapis.com/bert_models/2018_11_03/'
                                   'chinese_L-12_H-768_A-12.zip',
    }

    def __init__(self,
                 name_or_path: str,
                 embedding_size: int = None,
                 **kwargs):
        super(BERTEmbedding, self).__init__(name_or_path, embedding_size, **kwargs)
        self.model_name = name_or_path
        self.model_path = helper.check_should_download(file=name_or_path,
                                                       download_url=self.pre_trained_models.get(name_or_path),
                                                       sub_folders=['embedding', 'bert'])

    def get_word2idx_dict(self):
        dict_path = os.path.join(self.model_path, 'vocab.txt')
        word2idx = {}
        with open(dict_path, 'r', encoding='utf-8') as f:
            words = f.read().splitlines()
            for word in words:
                word2idx[word] = len(word2idx)
        for key, value in self.special_tokens.items():
            word2idx[key] = word2idx[value]
        return word2idx

    def get_base_model(self, seq_len: int) -> keras.models.Model:
        """get base bert model for fine tune
        
        Arguments:
            seq_len {int} -- [length of the input sequence]

        Returns:
            keras.models.Model -- [keras base model]
        """
        config_path = os.path.join(self.model_path, 'bert_config.json')
        check_point_path = os.path.join(self.model_path, 'bert_model.ckpt')
        model: keras.models.Model = keras_bert.load_trained_model_from_checkpoint(config_path,
                                                                                  check_point_path,
                                                                                  seq_len=seq_len)
        return model

    def __repr__(self):
        return 'bert:{}'.format(self.name)


class CustomEmbedding(EmbeddingModel):
    base_dict = {
        k.PAD: 0,
        k.BOS: 1,
        k.EOS: 2,
        k.UNK: 3
    }

    def __init__(self,
                 name_or_path: str = 'custom',
                 embedding_size: int = None,
                 **kwargs):
        super(CustomEmbedding, self).__init__(name_or_path, embedding_size, **kwargs)

    def __repr__(self):
        return 'custom_embedding:{}_embedding_size:{}'.format(self.name,
                                                              self.embedding_size)


def get_embedding_by_conf(name: str, **kwargs) -> EmbeddingModel:
    embedding_class: Dict[str, Type[EmbeddingModel]] = {
        'word2vec': Word2VecEmbedding,
        'bert': BERTEmbedding,
        'custom': CustomEmbedding
    }
    return embedding_class[name](**kwargs)


if __name__ == '__main__':
    bert_embedding = BERTEmbedding('cased_L-24_H-1024_A-16')
    print(bert_embedding.get_word2idx_dict())
    print(bert_embedding.model_path)


