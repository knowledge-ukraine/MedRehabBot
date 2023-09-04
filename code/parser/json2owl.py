# -*- coding: utf8 -*-

import os
import json
import time

import nltk
from nltk.stem import WordNetLemmatizer
from tools.ontology_components import *
'''
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('treebank')
nltk.download('stopwords')
'''
lemmatizer = WordNetLemmatizer()


def get_uncertain_dicts(structure, p_key, out):
    for key in structure:
        if isinstance(structure[key], dict):
            if len(structure[key]) > 0:
                get_uncertain_dicts(structure[key], key, out)
            elif p_key != "metadata":
                out.add(key)


def get_classes(p_dict, p_key, output, title, uncertain, counter):
    def make_individual(item, title, key, output, counter):
        if key == "title" and len(item.lower().strip().strip(",").strip().strip(":").strip(":").strip()) == 0:
            new_name = ' '.join(title.strip().split())
        else:
            new_name = ' '.join(item.strip().split())
        new_entity_id = replace_symbols_1(del_unknown_symbols(new_name.lower().strip().strip(
            ",").strip().strip(":").strip(":").strip()))
        if len(new_entity_id) > 0:
            title_id = replace_symbols_1(del_unknown_symbols(title.lower().strip().strip(
                ",").strip().strip(":").strip(":").strip()))
            parent_class_id = replace_symbols_1(del_unknown_symbols(key.lower().strip().strip(
                ",").strip().strip(":").strip()))
            if new_entity_id not in output["entities"]:
                new_individual = OntoEntity(id="n_ind"+str(counter),  # new_entity_id,
                                            of_classes="cl_"+parent_class_id if parent_class_id is not None else None,
                                            comment=new_name.replace(" & ", " and ").replace("& ", "and ").replace(
                                                        " &", " and").replace("&", "and").replace(
                                                        "<", "less than").replace(">", "more than"),
                                            label=" ".join(new_name.split()[:7]).replace(" & ", " and ").replace(
                                                           "& ", "and ").replace(" &", " and").replace(
                                                           "&", "and").replace("<", "less than").replace(
                                                           ">", "more than"),
                                            language="en",
                                            assertions={"relate_to_article": [title_id]})
                output["entities"][new_entity_id] = new_individual
            elif "relate_to_article" in output["entities"][new_entity_id].assertions:
                if title_id not in output["entities"][new_entity_id].assertions["relate_to_article"]:
                    output["entities"][new_entity_id].assertions["relate_to_article"].append(title_id)
            if "cl_"+parent_class_id not in output["entities"][new_entity_id].of_classes:
                output["entities"][new_entity_id].of_classes.append("cl_"+parent_class_id)

    if title not in output["classes"]:
        new_title_entity_id = replace_symbols_1(del_unknown_symbols(' '.join(title.strip().split(
                                                )).lower().strip().strip(",").strip(":").strip()))
        new_title_individual = OntoEntity(id="n_ind"+new_title_entity_id, of_classes="articles_names",
                                          assertions={"relate_to_article": [new_title_entity_id]},
                                          label=del_unknown_symbols(" ".join(title.split()[:7])).replace(
                                              " & ", " and ").replace("& ", "and ").replace(" &", " and").replace(
                                              "&", "and").replace("<", " less than ").replace(">", " more than "),
                                          language="en")
        output["entities"][new_title_entity_id] = new_title_individual
    if p_key is not None:
        parent_class_id = replace_symbols_1(del_unknown_symbols(p_key.lower().strip().strip(",").strip()))
    else:
        parent_class_id = None
    for key in p_dict:
        if not (p_key in uncertain and len([j for j in p_dict[key] if
                                            j.strip().strip(",").strip().strip(":").strip() != ""]) == 0):
            new_class_id = replace_symbols_1(del_unknown_symbols(key.lower().strip().strip(",").strip(
                ).strip(":").strip()))
            if new_class_id not in output["classes"]:
                new_class = OntoClass(id="cl_"+new_class_id,
                                      parent_class_id="cl_"+parent_class_id if parent_class_id is not None else None,
                                      label=' '.join(key.strip().split()[:7]).replace(" & ", " and ").replace(
                                          "& ", "and ").replace(
                                        " &", " and").replace("&", "and").replace("<", "less than").replace(
                                        ">", "more than"), language="en")
                output["classes"][new_class_id] = new_class
        if isinstance(p_dict[key], dict):
            counter += 1
            get_classes(p_dict[key], key, output, title, uncertain, counter)  # Рекурсивный вызов для перехода ниже по иерархии
        elif isinstance(p_dict[key], str):
            make_individual(p_dict[key], title, key, output, counter)
        elif isinstance(p_dict[key], list) and len(p_dict[key]) > 0:
            for item in p_dict[key]:
                if isinstance(item, str):
                    make_individual(item, title, key, output, counter)
                elif isinstance(item, dict) and len(item) > 0:
                    if key == "references":
                        make_individual(item["reference"], title, key, output, counter)
        elif isinstance(p_dict[key], list) and p_key in uncertain:
            if ":" not in key:
                make_individual(key, title, p_key, output, counter)
            else:
                new_class_id = replace_symbols_1(del_unknown_symbols(key.split(":")[0].lower().strip().strip(",").strip(
                    ).strip(":").strip()))
                if new_class_id not in output["classes"]:
                    new_class = OntoClass(id="cl_"+new_class_id,
                                          parent_class_id="cl_"+parent_class_id if parent_class_id is not None else None,
                                          label=' '.join(key.strip().split()[:7]).replace(" & ", " and ").replace(
                                              "& ", "and ").replace(" &", " and").replace("&", "and").replace(
                                              "<", "less than").replace(">", "more than"),
                                          language="en")
                    output["classes"][new_class_id] = new_class
                if len(key.split(":")[1:]) > 0:
                    make_individual(":".join(key.split(":")[1:]), title, key.split(":")[0], output, counter)


def extract_terms(owl_entities):
    words_entities = dict()
    word_classes = dict()
    for entity in owl_entities:
        name_str = str(owl_entities[entity].comment).strip()
        if len(name_str) > 0:
            tokenized_text = nltk.pos_tag(nltk.tokenize.word_tokenize(name_str))
            for word in tokenized_text:
                if len(word) > 1 and (word[1] == "NN" or word[1] == "NNS" or word[1] == 'VBG' or
                                      word[1] == 'VBP' or word[1] == 'JJ' or word[1] == "JJR" or
                                      word[1] == "JJS" or word[1] == 'NNP' or word[1] == "NNPS" or
                                      word[1] == "PDT" or word[1] == "VB" or word[1] == "VBD" or word[1] == "VBN"):
                    lemma_word = lemmatizer.lemmatize(word[0])
                    no_djts = True
                    for s in lemma_word:
                        if s in ["/", "\\", "%", "$", "#", "@", "_", "+", "=", "*", "(", ")", "[", "]", "{", "}", "!",
                                 ">", "<", ",", ".", "?", "–"]:
                            no_djts = False
                            break
                        if s.isdigit():
                            no_djts = False
                            break
                    if no_djts:
                        if word[1] not in word_classes:
                            new_class = OntoClass(id=word[1], parent_class_id="words", label=word[1],
                                                  language="en")
                            word_classes[word[1]] = new_class
                        new_entity_id = replace_symbols_1(del_unknown_symbols(lemma_word.lower().strip(
                                                          ).strip(",").strip().strip(":").strip("-").strip()))
                        if new_entity_id not in words_entities:
                            new_individual = OntoEntity(id=new_entity_id,
                                                        of_classes=word[1],
                                                        comment=lemma_word.replace("&", "and").replace(
                                                            "<", " less than ").replace(">", "more than").strip(
                                                            "-").strip(",").lower(),
                                                        label=lemma_word.replace("&", "and").replace(
                                                            "<", " less than ").replace(">", "more than").strip(
                                                            "-").strip(",").lower(),
                                                        language="en",
                                                        assertions={"relate_to_context": [owl_entities[entity].id]})
                            words_entities[new_entity_id] = new_individual
                        if owl_entities[entity].id not in words_entities[new_entity_id].assertions["relate_to_context"]:
                            words_entities[new_entity_id].assertions["relate_to_context"].append(owl_entities[entity].id)
                        if word[1] not in words_entities[new_entity_id].of_classes:
                            words_entities[new_entity_id].of_classes.append(word[1])
    return words_entities, word_classes


if __name__ == "__main__":
    uncertain_dicts = set()
    print("Loading input JSONs")
    tau_0 = time.time()
    settings = json.load(open("settings.json", "r"))
    get_uncertain_dicts(json.load(open("structure.json", "r")), None, uncertain_dicts)
    input_files_names = [i for i in os.listdir("parse_results") if i.split(".")[-1].lower().strip() == "json"]
    print(time.time() - tau_0, " sec")
    print("Creating ontology objects")
    tau_0 = time.time()
    onto_objects = {
        "classes": {
            "articles_names": OntoClass(id="articles_names", label="Articles names", language="en"),
            "words": OntoClass(id="words", label="words", language="en")
        },
        "entities": {},
        "properties": {
            "relate_to_article": OntoProperty(id="relate_to_article", range_id="articles_names",
                                              label="Relate to article",
                                              language="en"),
            "relate_to_context": OntoProperty(id="relate_to_context", range_id="words",
                                              label="Relate to context",
                                              language="en")
        }
    }
    c = 1
    for file_name in input_files_names:
        data = json.load(open("parse_results/" + file_name, "r"))
        name = file_name.split(".")[0]
        get_classes(data, None, onto_objects, name, uncertain_dicts, c)
        c += 1

    print(time.time() - tau_0, " sec")
    print("Extracting named entities from the contexts")
    tau_0 = time.time()
    terms, pos_tags = extract_terms(onto_objects["entities"])
    onto_objects["entities"].update(terms)
    onto_objects["classes"].update(pos_tags)
    print(time.time() - tau_0, " sec")
    print("Forming and serializing OWL ontology")
    tau_0 = time.time()
    owl_text = make_owl(onto_objects, path="Context Ontology", threads_n=settings["threads_n"])
    print(time.time() - tau_0, " sec")
    print("Saving OWL file")
    tau_0 = time.time()
    save_owl("ContextOntology_new_2.owl", text_owl=owl_text)
    print(time.time() - tau_0, " sec")
    print("Process id complete")
