# -*- coding: utf8 -*-

import os
import json
import copy
import time

import preprocess_input
import form_queries
import process_queries


class Responder:
    def __init__(self,  words_file="all_words.json", marker_words_file="marker_words.json",
                 templates_file="query_templates.json", ontology_settings_file="ontology_settings.json"):
        ontology_settings = json.loads(open(ontology_settings_file, "r", encoding="utf-8").read())
        self.preprocessor = preprocess_input.Preprocessor(words_file=words_file, marker_words_file=marker_words_file)
        self.qf = form_queries.QueryFormer(templates_file=templates_file)
        self.query_exec = process_queries.QueryExec(jena_endpoint=ontology_settings["jena_endpoint"],
                                                    user=ontology_settings["jena_user"],
                                                    password=ontology_settings["jena_password"],
                                                    ontologies=ontology_settings["ontologies"])

    def get_response(self, text):
        s_time = time.time()
        present_intents, present_words = self.preprocessor.get_intents(text)
        print("pre-processing: ", time.time() - s_time)
        s_time = time.time()
        qs = self.qf.form_query_set(present_intents, present_words)
        print("query set formation: ", time.time() - s_time)
        s_time = time.time()
        resp = self.query_exec.process_query_set(qs)
        print("ontology response obtainting: ", time.time() - s_time)
        return resp
