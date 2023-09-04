# -*- coding: utf8 -*-

import os
import json
import re
import copy

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import numpy as np

'''
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('treebank')
nltk.download('stopwords')
'''


class Preprocessor:
    def __init__(self, words_file="all_words.json", marker_words_file="marker_words.json"):
        """
            Class for input text pre-processing
            :param words_file: file containing list of all the words appear in the database
            :param marker_words_file: file matches marker words lists to certain intents
        """
        # Class constants:
        self.stopWords = set(stopwords.words('english') + ["give", 'show', 'present', "could"])
        self.lemmatizer = WordNetLemmatizer()
        self.tmp = self.lemmatizer.lemmatize("cat")
        self.all_words = np.array(json.loads(open(words_file, "r", encoding="utf-8").read()))
        self.marker_words = json.loads(open(marker_words_file, "r", encoding="utf-8").read())
        self.allowed_symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '.',
                                'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a',
                                's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c',
                                'v', 'b', 'n', 'm', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U',
                                'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K',
                                'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ' ', '\t', '\n', '\r']

    @staticmethod
    def __match_conditions__(word):
        """
        Checks if the word meets conditions to appear a cpt, g-, or icd code
        :param word: str - word to be checked
        :return: srt - certain code key or False if no match was found
        """
        if word.isdigit() and len(word) == 5:
            return "certain cpt"
        if (re.fullmatch(r'[g]\d\d\d\d', word.lower()) and word.lower()[0] == "g" and len(word) == 5 and
                "." not in word):
            return "certain g-code"
        if (re.fullmatch(r'[e]\d\d\d\d', word.lower()) and word.lower()[0] == "e" and len(word) == 5 and
                "." not in word):
            return "certain hcpcs"
        if (re.fullmatch(r'[a-z]\d\d', word.lower()) or re.fullmatch(r'[a-z]\d\d[.-]\S', word.lower()) or
                re.fullmatch(r'[a-z]\d\d[.-]\S\S', word.lower()) or
                re.fullmatch(r'[a-z]\d\d[.-]\S{1,12}', word.lower())):
            return "certain icd 10"
        if re.fullmatch(r'\d\d\d', word.lower()) or re.fullmatch(r'\d\d\d\.\d{1,3}', word.lower()):
            return "certain icd 9"
        return False

    def __get_words_list_work__(self, input_text):
        """
        Initial pre-processing: makes cleaned list of words from the input text
        :param input_text: str - text to be processed
        :return: list of lemmatized words with stop words removed, each unique word appear once only
        """
        output = set()
        input_text = "".join([symbol for symbol in input_text if symbol in self.allowed_symbols])
        tokenized_text = np.array(nltk.pos_tag(nltk.tokenize.word_tokenize(input_text)))
        for word in tokenized_text:
            lemma_word = self.lemmatizer.lemmatize(word[0]).lower()
            if word[1] == "CD" or (lemma_word in self.all_words and lemma_word not in self.stopWords):
                output.add(lemma_word)
        return [w for w in output if w != '.' and w != '-']

    def __type_by_marker__(self, word_list):
        """
        Main working method aimed to find intents
        :param word_list: list of lemmatized words
        :return: intents as dictionary {"intent name": [[lists of marker words for each appearance]],
                 list of words which are not marker but meaningful and are to be used as query parameters
        """
        intents = dict()
        extra_words = [w.lower() for w in copy.deepcopy(word_list)]
        # Searching for intents according to the marker words
        for sem_type in self.marker_words:
            max_len = 0
            for w_set in self.marker_words[sem_type]:
                intent_present = True
                for marker_word in w_set:
                    if marker_word not in word_list:
                        intent_present = False
                        break
                if intent_present:
                    if max_len < len(w_set):
                        max_len = len(w_set)
                        if sem_type not in intents:
                            intents[sem_type] = [w_set]
                        elif w_set not in intents[sem_type]:
                            intents[sem_type].append([w_set])
                        extra_words = self.__remove_words__(w_set, extra_words)
        if "any_icd" in intents and "any_code" in intents:
            del intents["any_code"]
        if ("icd 9" in intents or "icd 10" in intents or "icd 11" in intents) and "any_icd" in intents:
            del intents["any_icd"]
        if ("icd 9" in intents or "icd 10" in intents or "icd 11" in intents or "g-code" in intents or
                                  "hcpcs" in intents or "cpt" in intents) and "any_code" in intents:
            del intents["any_code"]
        # Searching for the certain code values in the input
        certain_code_found = False
        for word in word_list:
            sem_type = self.__match_conditions__(word)
            if sem_type:
                w_set = [word.upper()]
                if "code" in word_list:
                    w_set.append("code")
                if sem_type not in intents:
                    intents[sem_type] = [w_set]
                else:
                    intents[sem_type].append(w_set)
                extra_words = self.__remove_words__(w_set, extra_words)
                certain_code_found = True
        if certain_code_found and "any_code" in intents:
            del intents["any_code"]

        if len(intents) == 0 and len(extra_words) > 0:
            intents["contexts"] = []
        return intents, extra_words

    @staticmethod
    def __remove_words__(w_set, words):
        """
        Removes words of "w_set" from the list "words"
        :param w_set: words to be deleted
        :param words: list from where the words are to me deleted
        :return: list "words" with the given words deleted
        """
        w_set_work = [w.lower() for w in copy.deepcopy(w_set)]
        for w in w_set_work:
            try:
                words.remove(w)
            except ValueError:
                pass
        return words

    def get_intents(self, text):
        """
        The executive method to find intents in the input text
        :param text: str -input natura language text - English only
        :return: intents as dictionary {"intent name": [[lists of marker words for each appearance]],
                 list of words which are not marker but meaningful and are to be used as query parameters
        """
        return self.__type_by_marker__(self.__get_words_list_work__(text))
