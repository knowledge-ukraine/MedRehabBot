# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import hashlib
import json
from multiprocessing import Process
import copy


class CreatorConstants:
    __instance = None

    def __init__(self):
        if not CreatorConstants.__instance:
            self.owl = ""
            self.rdf = ""
            self.rdfs = ""
            self.xsd = ""
            self.base = ""
            self.xmlns = ""
            self.name = ""
            self.language = ""
        else:
            print("Instance already created:", self.get_instance())

    @classmethod
    def get_instance(cls, config_file="creator_config.xml"):
        if not cls.__instance:
            cls.__instance = CreatorConstants()
            cls.__instance.config_file = config_file
            tree = Et.parse(config_file)
            root = tree.getroot()
            for i in root:
                if i.tag == "owl":
                    cls.__instance.owl = i.text.strip()
                if i.tag == "rdf":
                    cls.__instance.rdf = i.text.strip()
                if i.tag == "rdfs":
                    cls.__instance.rdfs = i.text.strip()
                if i.tag == "xsd":
                    cls.__instance.xsd = i.text.strip()
                if i.tag == "base":
                    cls.__instance.base = i.text.strip()
                if i.tag == "xmlns":
                    cls.__instance.xmlns = i.text.strip()
                if i.tag == "name":
                    cls.__instance.name = i.text.strip()
                if i.tag == "language":
                    cls.__instance.language = i.text.strip()
        return cls.__instance


class OntoClass:

    def __init__(self, id="Thing", parent_class_id="", interactions=None, union=None, label="", language="uk",
                 comment="", equality=None, disjoint_with=None,
                 deprecated=None,
                 version_info=None,
                 prior_version=None,
                 incompatible_with=None,
                 see_also=None,
                 is_defined_by=None,
                 backward_compatible_with=None,
                 additional_fields=None,
                 other_types_of_links=None,
                 properties_interactions=None,
                 properties_union=None):
        """
        Програмное представление именованной класа для OWL

        :param id: имя класа, строка, не начинать с цифры або символа, не должна содержать символов, кроме '_'
        :param parent_class_id: имя родительского класа, строка, список строк, словарь вида {"text": "class_name",
                                                                                              "attr_1": "value",
                                                                                              "attr_2": "value",
                                                                                              ...}
                                або список словарей такого вида
        :param interactions: список имён классов, входящих в коллекцию пересечения, возожен вариант списка словарей
                             вида: {"text": "class_name",
                                    "attr_1": "value",
                                    "attr_2": "value",
                                    ...}
        :param union: список имён классов, входящих в коллекцию объединения, возожен вариант списка словарей вида:
                      {"text": "class_name",
                       "attr_1": "value",
                       "attr_2": "value",
                       ...}
        :param properties_interactions: список имён свойств, входящих в коллекцию пересечения, возожен вариант списка словарей
                             вида: {"text": "class_name",
                                    "attr_1": "value",
                                    "attr_2": "value",
                                    ...}
        :param properties_union: список имён свойств, входящих в коллекцию объединения, возожен вариант списка словарей вида:
                      {"text": "class_name",
                       "attr_1": "value",
                       "attr_2": "value",
                       ...}
        :param label: название класа, строка або словарь с указанием атрибутов языка і типа, возможна передача списка
                      вида {"text": "label text",
                             "lang": "en",
                             "type": "string",
                             ...}
        :param language: маркер основного языка, строка типа "en", "ru", "uk", "de" і т.п.
        :param comment: пояснение к класу, строка або словарь с указанием атрибутов языка і типа,
                        возможна передача списка
        :param equality: имя эквивалентного класа, стока, список строк, словарь вида {"text": "class_name",
                                                                                       "attr_1": "value",
                                                                                       "attr_2": "value",
                                                                                       ...}
                         або список таких словарей
        :param disjoint_with: имя класа, для которого указано явное различие с данным,
                              стока, список строк, словарь вида {"text": "class_name",
                                                                 "attr_1": "value",
                                                                 "attr_2": "value",
                                                                 ...}
                              або список таких словарей
        :param deprecated: указание deprecated, строка або список строк
        :param version_info: указание version_info, строка або список строк
        :param prior_version: указание prior_version, строка або список строк
        :param incompatible_with: имя несопоставимого класа, строка або список строк
        :param see_also: указание see_also, строка або список строк
        :param is_defined_by: указание is_defined_by, строка або список строк
        :param backward_compatible_with: указание backward_compatible_with, строка або список строк
        :param additional_fields: дополнительные нестандартные поля, предаются в виде словаря вида:
                                  {"имя_поля_1": "значение поля 1",
                                   "имя_поля_2": "значение поля 2",
                                   ...}
        :param other_types_of_links: дополнительные нестандартные связи с другими объектами,
                                     предаются в виде словаря вида:
                                     {"link_name": "название связи",
                                      "object": "ID объекта, на который ссылается данная связь",
                                      "attr_1": "value",
                                      "attr_2": "value",
                                      ...}
                                    або списка таких словарей
        """
        self.owl_text = ""
        if union is None:
            union = []
        if interactions is None:
            interactions = []
        if properties_union is None:
            properties_union = []
        if properties_interactions is None:
            properties_interactions = []
        self.id = replace_symbols_1(id).replace("&", "_and_")
        if isinstance(parent_class_id, list) or isinstance(parent_class_id, set):
            self.parent_class_ids = [i.replace("&", "_and_") for i in parent_class_id
                                     if i is not None and i.strip() != ""]
        elif isinstance(parent_class_id, str) or isinstance(parent_class_id, dict):
            self.parent_class_ids = [parent_class_id.replace("&", "_and_").strip()]
        else:
            self.parent_class_ids = list()
        self.interactions = interactions
        self.union = union
        self.properties_interactions = properties_interactions
        self.properties_union = properties_union
        if isinstance(label, list) or isinstance(label, set):
            self.label = label
        elif isinstance(label, str) or isinstance(label, dict):
            self.label = [label.strip()]

        self.language = language.strip()

        if isinstance(equality, list) or isinstance(equality, set):
            self.equality = equality
        elif isinstance(equality, str) or isinstance(equality, dict):
            self.equality = [equality]
        else:
            self.equality = []

        if isinstance(disjoint_with, list) or isinstance(disjoint_with, set):
            self.disjoint_with = disjoint_with
        elif isinstance(disjoint_with, str) or isinstance(disjoint_with, dict):
            self.disjoint_with = [disjoint_with]
        else:
            self.disjoint_with = []

        if isinstance(comment, list) or isinstance(comment, set):
            self.comment = comment
        elif isinstance(comment, str) or isinstance(comment, dict):
            self.comment = [comment.strip()]

        if isinstance(deprecated, list) or isinstance(deprecated, set):
            self.deprecated = deprecated
        elif isinstance(deprecated, str) or isinstance(deprecated, dict):
            self.deprecated = [deprecated]
        else:
            self.deprecated = []

        if isinstance(version_info, list) or isinstance(version_info, set):
            self.version_info = version_info
        elif isinstance(version_info, str) or isinstance(version_info, dict):
            self.version_info = [version_info]
        else:
            self.version_info = []

        if isinstance(prior_version, list) or isinstance(prior_version, set):
            self.prior_version = prior_version
        elif isinstance(prior_version, str) or isinstance(prior_version, dict):
            self.prior_version = [prior_version]
        else:
            self.prior_version = []

        if isinstance(incompatible_with, list) or isinstance(incompatible_with, set):
            self.incompatible_with = incompatible_with
        elif isinstance(incompatible_with, str) or isinstance(incompatible_with, dict):
            self.incompatible_with = [incompatible_with]
        else:
            self.incompatible_with = []

        if isinstance(see_also, list) or isinstance(see_also, set):
            self.see_also = see_also
        elif isinstance(see_also, str) or isinstance(see_also, dict):
            self.see_also = [see_also]
        else:
            self.see_also = []

        if isinstance(is_defined_by, list) or isinstance(is_defined_by, set):
            self.is_defined_by = is_defined_by
        elif isinstance(is_defined_by, str) or isinstance(is_defined_by, dict):
            self.is_defined_by = [is_defined_by]
        else:
            self.is_defined_by = []

        if isinstance(backward_compatible_with, list) or isinstance(backward_compatible_with, set):
            self.backward_compatible_with = backward_compatible_with
        elif isinstance(backward_compatible_with, str) or isinstance(backward_compatible_with, dict):
            self.backward_compatible_with = [backward_compatible_with]
        else:
            self.backward_compatible_with = []

        if isinstance(additional_fields, dict):
            self.additional_fields = additional_fields
        else:
            self.additional_fields = dict()

        if isinstance(other_types_of_links, list) or isinstance(other_types_of_links, set):
            self.other_types_of_links = list(other_types_of_links)
        elif isinstance(other_types_of_links, dict):
            self.other_types_of_links = [other_types_of_links]
        elif isinstance(other_types_of_links, str):
            self.other_types_of_links = [{"link_name": other_types_of_links}]
        else:
            self.other_types_of_links = list()


    def __eq__(self, other):
        if isinstance(other, OntoClass):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, OntoClass):
            return self.id != other.id
        else:
            return False

    def __hash__(self):
        return int(hashlib.md5(self.id.encode()).hexdigest(), 16)

    def __str__(self):
        return str(self.id.strip())

    def serialize(self):
        for parent_class_id in self.parent_class_ids:
            if isinstance(parent_class_id, str):
                if parent_class_id.strip() == "" and len(self.interactions) == 0 and\
                        len(self.union) == 0 and len(self.label) == 0 and self.language.strip() == "":
                    return '\t<owl:Class rdf:ID="' + self.id.strip().strip('"').strip("'") + '" />\n'
            elif isinstance(parent_class_id, dict):
                if (len(parent_class_id) == 0 or parent_class_id.get("text") is None) \
                        and len(self.interactions) == 0 and len(self.union) == 0 and len(self.label) == 0\
                        and self.language.strip() == "":
                    return '\t<owl:Class rdf:ID="' + self.id.strip().strip('"').strip("'") + '" />\n'

        owl_text = '\t<owl:Class rdf:ID="' + self.id.strip().strip('"').strip("'") + '" >\n'

        # Родительские класи
        if isinstance(self.parent_class_ids, list) or isinstance(self.parent_class_ids, set):
            for parent_class_id in self.parent_class_ids:
                if isinstance(parent_class_id, str) and parent_class_id.strip() != "":
                    owl_text += '\t\t<rdfs:subClassOf rdf:resource="#' + parent_class_id.strip() + '" />\n'
                elif isinstance(parent_class_id, dict) and len(parent_class_id) > 0:
                    main_data = parent_class_id.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t<rdfs:subClassOf'
                        for attr in parent_class_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(parent_class_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.parent_class_ids, dict) and len(self.parent_class_ids) > 0:
            main_data = self.parent_class_ids.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<rdfs:subClassOf'
                for attr in self.parent_class_ids:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.parent_class_ids.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.parent_class_ids, str) and self.parent_class_ids.strip() != "":
            owl_text += '\t\t<rdfs:subClassOf rdf:resource="#' + self.parent_class_ids.strip() + '" />\n'

        # Пересечения
        if len(self.interactions) > 0:
            owl_text += '\t\t<owl:intersectionOf rdf:parseType="Collection" >\n'
            for item in self.interactions:
                if isinstance(item, str):
                    owl_text += '\t\t\t<owl:Class rdf:about="#' + item.strip() + '" />\n'
                elif isinstance(item, dict):
                    main_data = item.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t\t<owl:Class'
                        for attr in item:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(item.get(attr)).strip() + '"'
                        owl_text += ' rdf:about="#' + main_data.strip() + '" />\n'
            owl_text += '\t\t</owl:intersectionOf>\n'

        # Пересечения свойств
        if len(self.properties_interactions) > 0:
            owl_text += '\t\t<owl:intersectionOf rdf:parseType="Collection" >\n'
            for item in self.properties_interactions:
                if isinstance(item, str):
                    owl_text += '\t\t\t<owl:ObjectProperty rdf:about="#' + item.strip() + '" />\n'
                elif isinstance(item, dict):
                    main_data = item.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t\t<owl:ObjectProperty'
                        for attr in item:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(item.get(attr)).strip() + '"'
                        owl_text += ' rdf:about="#' + main_data.strip() + '" />\n'
            owl_text += '\t\t</owl:intersectionOf>\n'

        # Объединения
        if len(self.union) > 0:
            owl_text += '\t\t<owl:unionOf rdf:parseType="Collection" >\n'
            for item in self.union:
                if isinstance(item, str):
                    owl_text += '\t\t\t<owl:Class rdf:about="#' + item.strip() + '" />\n'
                elif isinstance(item, dict):
                    main_data = item.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t\t<owl:Class'
                        for attr in item:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(item.get(attr)).strip() + '"'
                        owl_text += ' rdf:about="#' + main_data.strip() + '" />\n'
            owl_text += '\t\t</owl:unionOf>\n'

        # Объединения свойств
        if len(self.properties_union) > 0:
            owl_text += '\t\t<owl:unionOf rdf:parseType="Collection" >\n'
            for item in self.properties_union:
                if isinstance(item, str):
                    owl_text += '\t\t\t<owl:ObjectProperty rdf:about="#' + item.strip() + '" />\n'
                elif isinstance(item, dict):
                    main_data = item.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t\t<owl:ObjectProperty'
                        for attr in item:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(item.get(attr)).strip() + '"'
                        owl_text += ' rdf:about="#' + main_data.strip() + '" />\n'
            owl_text += '\t\t</owl:unionOf>\n'

        # Label
        full_name = recover_symbols(recover_digits(self.id))

        try:
             if len(self.label) == 0:
                    self.label = {"text": full_name,
                                  "lang": self.language.strip(),
                                  "type": "string"}

        except Ecxeption as e:
             print(e)

        # if self.id == "b_five__four__five__zero__Водний_баланс":
        #    print("self.label", self.label)
        #    print("full_name", full_name)


        if isinstance(self.label, list) or isinstance(self.label, set):
            main_label_exist = False
            if len(self.label) > 0:
                for text in self.label:
                    if isinstance(text, str) and text.strip() != "":
                        owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + text.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
                        if text.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") == full_name:
                            main_label_exist = True
                    elif isinstance(text, dict) and len(text) > 0:
                        main_data = text.get("text")
                        lang = text.get("lang")
                        if not isinstance(lang, str) or lang.strip() == "":
                            lang = self.language.strip()
                        type = text.get("type")
                        if isinstance(main_data, str) and main_data.strip() != "":
                            owl_text += '\t\t<rdfs:label'
                            if isinstance(lang, str):
                                owl_text += ' xml:lang="' + lang.strip() + '"'
                            if isinstance(type, str) and type.strip() != "":
                                owl_text += ' rdf:datatype="' + type.strip() + '"'
                            for attr in text:
                                if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                    owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                            owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
                            if main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") == full_name:
                                main_label_exist = True
            else:
                owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + full_name + '</rdfs:label>\n'
                main_label_exist = True
        elif isinstance(self.label, str) and self.label.strip() != "":
            owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.label.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'

            if (self.label.strip().lower().replace("&", "and").replace("<", "_less_").replace(">", "_more_") ==
                     full_name):
                owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + full_name + '</rdfs:label>\n'
                main_label_exist = True

        elif isinstance(self.label, dict) and len(self.label) > 0:
            main_data = self.label.get("text")
            lang = self.label.get("lang")
            type = self.label.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:label'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.label:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.label.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
                if main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") != full_name:
                    owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + full_name + '</rdfs:label>\n'
                    main_label_exist = True
        else:
            owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + full_name + '</rdfs:label>\n'
            main_label_exist = True
        # if not main_label_exist:
        #     owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + full_name + '</rdfs:label>\n'



        # Comment
        if isinstance(self.comment, list) or isinstance(self.comment, set):
            for text in self.comment:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:comment xml:lang="' + self.language.strip() + '">' + text.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:comment'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'
        elif isinstance(self.comment, str) and self.comment.strip() != "":
            owl_text += '\t\t<rdfs:comment xml:lang="' + self.language.strip() + '">' + self.comment.strip() + '</rdfs:comment>\n'
        elif isinstance(self.comment, dict) and len(self.comment) > 0:
            main_data = self.comment.get("text")
            lang = self.comment.get("lang")
            type = self.comment.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:comment'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.comment:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.comment.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'

        # Эквивалентность
        if isinstance(self.equality, list) or isinstance(self.equality, set):
            for class_id in self.equality:
                if isinstance(class_id, str) and class_id.strip() != "":
                    owl_text += '\t\t<owl:equivalentClass rdf:resource="#' + class_id.strip() + '" />\n'
                elif isinstance(class_id, dict):
                    main_data = class_id.get("text")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:equivalentClass'
                        for attr in class_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(class_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.equality, str):
            if self.equality.strip() != "":
                owl_text += '\t\t<owl:equivalentClass rdf:resource="#' + self.equality.strip() + '" />\n'
        elif isinstance(self.equality, dict):
            main_data = self.equality.get("text")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:equivalentClass'
                for attr in self.equality:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.equality.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'

        # Явно заданное различие
        if isinstance(self.disjoint_with, list) or isinstance(self.disjoint_with, set):
            for class_id in self.disjoint_with:
                if isinstance(class_id, str) and class_id.strip() != "":
                    owl_text += '\t\t<owl:disjointWith rdf:resource="#' + class_id.strip() + '" />\n'
                elif isinstance(class_id, dict):
                    main_data = class_id.get("text")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:disjointWith'
                        for attr in class_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(class_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.disjoint_with, str) and self.disjoint_with.strip() != "":
            owl_text += '\t\t<owl:disjointWith rdf:resource="#' + self.disjoint_with.strip() + '" />\n'
        elif isinstance(self.disjoint_with, dict):
            main_data = self.disjoint_with.get("text")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:disjointWith'
                for attr in self.disjoint_with:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.disjoint_with.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'

        # Связи нестандартного типа
        if isinstance(self.other_types_of_links, list) or isinstance(self.other_types_of_links, set):
            for link in self.other_types_of_links:
                if isinstance(link, str) and link.strip() != "":
                    owl_text += '\t\t<rdfs:' + link + ' rdf:resource="#" />\n'
                elif isinstance(link, dict):
                    link_name = link.get("link_name")
                    link_object = link.get("object")
                    if (isinstance(link_name, str) and link_name.strip() != "" and
                        isinstance(link_object, str) and link_object.strip() != ""):
                        owl_text += '\t\t<rdfs:' + link_name
                        for attr in link:
                            if attr.strip() != "link_name" and attr.strip() != "object":
                                owl_text += ' xml:' + attr + '="' + str(
                                    link.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'
        elif isinstance(self.other_types_of_links, str) and self.other_types_of_links.strip() != "":
            owl_text += '\t\t<owl:' + replace_symbols_1(self.other_types_of_links) + ' rdf:resource="#" />\n'
        elif isinstance(self.self.other_types_of_links, dict):
            link_name = self.self.other_types_of_links.get("link_name")
            link_object = self.self.other_types_of_links.get("object")
            if (isinstance(link_name, str) and link_name.strip() != "" and
                    isinstance(link_object, str) and link_object.strip() != ""):
                owl_text += '\t\t<rdfs:' + replace_symbols_1(link_name)
                for attr in self.self.other_types_of_links:
                    if attr.strip() != "link_name" and attr.strip() != "object":
                        owl_text += ' xml:' + replace_symbols_1(replace_digits(attr)) + '="' + str(
                            self.self.other_types_of_links.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'

        # Параметр deprecated
        if isinstance(self.deprecated, list) or isinstance(self.deprecated, set):
            for text in self.deprecated:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:deprecated>' + text.replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'
                elif isinstance(text, dict):
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:deprecated'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'
        elif isinstance(self.deprecated, str) and self.deprecated.strip() != "":
            owl_text += '\t\t<owl:deprecated>' + self.deprecated + '</owl:deprecated>\n'
        elif isinstance(self.deprecated, dict) and len(self.deprecated) > 0:
            main_data = self.deprecated.get("text")
            lang = self.deprecated.get("lang")
            type = self.deprecated.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:deprecated'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.deprecated:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.deprecated.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'

        # Параметр versionInfo
        if isinstance(self.version_info, list) or isinstance(self.version_info, set):
            for text in self.version_info:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:versionInfo>' + text + '</owl:versionInfo>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:versionInfo'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:versionInfo>\n'
        elif isinstance(self.version_info, str) and self.version_info.strip() != "":
            owl_text += '\t\t<owl:versionInfo>' + self.version_info.strip() + '</owl:versionInfo>\n'
        elif isinstance(self.version_info, dict) and len(self.version_info) > 0:
            main_data = self.version_info.get("text")
            lang = self.version_info.get("lang")
            type = self.version_info.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:versionInfo'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.version_info:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.version_info.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:versionInfo>\n'

        # Параметр priorVersion
        if isinstance(self.prior_version, list) or isinstance(self.prior_version, set):
            for text in self.prior_version:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:priorVersion>' + text + '</owl:priorVersion>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:priorVersion'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:priorVersion>\n'
        elif isinstance(self.prior_version, str) and self.prior_version.strip() != "":
            owl_text += '\t\t<owl:priorVersion>' + self.prior_version.strip() + '</owl:priorVersion>\n'
        elif isinstance(self.prior_version, dict) and len(self.prior_version) > 0:
            main_data = self.prior_version.get("text")
            lang = self.prior_version.get("lang")
            type = self.prior_version.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:priorVersion'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.prior_version:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.prior_version.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:priorVersion>\n'

        # Параметр incompatibleWith
        if isinstance(self.incompatible_with, list) or isinstance(self.incompatible_with, set):
            for text in self.incompatible_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:incompatibleWith>' + text + '</owl:incompatibleWith>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:incompatibleWith'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:incompatibleWith>\n'
        elif isinstance(self.incompatible_with, str) and self.incompatible_with.strip() != "":
            owl_text += '\t\t<owl:incompatibleWith>' + self.incompatible_with.strip() + '</owl:incompatibleWith>\n'
        elif isinstance(self.incompatible_with, dict) and len(self.incompatible_with) > 0:
            main_data = self.incompatible_with.get("text")
            lang = self.incompatible_with.get("lang")
            type = self.incompatible_with.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:incompatibleWith'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.incompatible_with:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.incompatible_with.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:incompatibleWith>\n'

        # Параметр seeAlso
        if isinstance(self.see_also, list) or isinstance(self.see_also, set):
            for text in self.see_also:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:seeAlso>' + text + '</rdfs:seeAlso>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:seeAlso'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:seeAlso>\n'
        elif isinstance(self.see_also, str) and self.see_also.strip() != "":
            owl_text += '\t\t<rdfs:seeAlso>' + self.see_also.strip() + '</rdfs:seeAlso>\n'
        elif isinstance(self.see_also, dict) and len(self.see_also) > 0:
            main_data = self.see_also.get("text")
            lang = self.see_also.get("lang")
            type = self.see_also.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:seeAlso'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.see_also:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.see_also.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:seeAlso>\n'

        # Параметр isDefinedBy
        if isinstance(self.is_defined_by, list) or isinstance(self.is_defined_by, set):
            for text in self.is_defined_by:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:isDefinedBy>' + text + '</rdfs:isDefinedBy>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:isDefinedBy'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:isDefinedBy>\n'
        elif isinstance(self.is_defined_by, str) and self.is_defined_by.strip() != "":
            owl_text += '\t\t<rdfs:isDefinedBy>' + self.is_defined_by.strip() + '</rdfs:isDefinedBy>\n'
        elif isinstance(self.is_defined_by, dict) and len(self.is_defined_by) > 0:
            main_data = self.is_defined_by.get("text")
            lang = self.is_defined_by.get("lang")
            type = self.is_defined_by.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:isDefinedBy'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.is_defined_by:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.is_defined_by.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:isDefinedBy>\n'

        # Параметр backwardCompatibleWith
        if isinstance(self.backward_compatible_with, list) or isinstance(self.backward_compatible_with, set):
            for text in self.backward_compatible_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:backwardCompatibleWith>' + text + '</owl:backwardCompatibleWith>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:backwardCompatibleWith'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:backwardCompatibleWith>\n'
        elif isinstance(self.backward_compatible_with, str) and self.backward_compatible_with.strip() != "":
            owl_text += '\t\t<owl:backwardCompatibleWith>' + self.backward_compatible_with.strip() + '</owl:backwardCompatibleWith>\n'
        elif isinstance(self.backward_compatible_with, dict) and len(self.backward_compatible_with) > 0:
            main_data = self.backward_compatible_with.get("text")
            lang = self.backward_compatible_with.get("lang")
            type = self.backward_compatible_with.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:backwardCompatibleWith'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.backward_compatible_with:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.backward_compatible_with.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:backwardCompatibleWith>\n'

        for field in self.additional_fields:
            if isinstance(self.additional_fields.get(field), str):
                owl_text += '\t\t<rdfs:' + replace_digits(str(field)) + ' xml:' + replace_digits(str(field)) + '="' + self.additional_fields.get(field) + '">' \
                            + self.additional_fields.get(field) + '</rdfs:' + replace_digits(str(field)) + '>\n'
            elif isinstance(self.additional_fields.get(field), dict):
                main_data = self.additional_fields.get(field).get("text")
                lang = self.additional_fields.get(field).get("lang")
                type = self.additional_fields.get(field).get("type")
                if isinstance(main_data, str):
                    owl_text += '\t\t<rdfs:' + replace_digits(replace_symbols_1(str(field)))
                    if isinstance(lang, str):
                        owl_text += ' xml:lang="' + lang.strip() + '"'
                    if isinstance(type, str) and type.strip() != "":
                        owl_text += ' rdf:datatype="' + type.strip() + '"'
                    for attr in self.additional_fields.get(field):
                        if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                            owl_text += ' xml:' + attr.strip() + '="' +\
                                        replace_symbols_2(str(self.additional_fields.get(field).get(attr))) + '"'

                    owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:' \
                                + replace_digits(replace_symbols_1(str(field))) + '>\n'

            elif isinstance(self.additional_fields.get(field), list):
                for data_item in self.additional_fields.get(field):
                    main_data = data_item.get("text")
                    lang = data_item.get("lang")
                    type = data_item.get("type")
                    if isinstance(main_data, str):
                        owl_text += '\t\t<rdfs:' + replace_digits(replace_symbols_1(str(field)))
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in data_item:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + replace_digits(attr.strip()) + '="' + \
                                            replace_symbols_2(str(data_item.get(attr))) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_").replace('°', "_degree_").replace('%', "_percent_") + '</rdfs:' \
                                    + replace_digits(replace_symbols_1(str(field))) + '>\n'

        owl_text += '\t</owl:Class>\n'
        self.owl_text = owl_text
        return owl_text


class OntoProperty:
    def __init__(self, id="", domain_id="", range_id="", parent_id=None, label="", language="uk",
                 comment="",  equality=None,
                 asymmetric=False,
                 functional=False,
                 inverse_functional=False,
                 irreflexive=False,
                 reflexive=False,
                 symmetric=False,
                 transitive=False,
                 deprecated=None,
                 version_info=None,
                 prior_version=None,
                 incompatible_with=None,
                 see_also=None,
                 is_defined_by=None,
                 inverse_of=None,
                 disjoint_with=None,
                 backward_compatible_with=None,
                 additional_fields=None,
                 other_types_of_links=None):
        """
        Програмное представление именованной властивості для OWL

        :param id: имя властивості, строка, не начинать с цифры або символа, не должна содержать символов, кроме '_'
        :param domain_id: имя класа, входящего в domain данного властивості, строка, список строк, словарь вида
                          {"text": "class_name",
                           "attr_1": "value",
                           "attr_2": "value",
                           ...}
                           або список таких словарей
        :param range_id: имя класа, входящего в range данного властивості, строка, список строк, словарь вида
                          {"text": "class_name",
                           "attr_1": "value",
                           "attr_2": "value",
                           ...}
                           або список таких словарей
        :param parent_id: имя родительского властивості, строка, список строк, словарь вида {"text": "class_name",
                                                                                          "attr_1": "value",
                                                                                          "attr_2": "value",
                                                                                           ...}
                          або список словарей такого вида
        :param label: название властивості, строка або словарь с указанием атрибутов языка і типа, возможна передача списка
                      вида {"text": "label text",
                             "lang": "en",
                             "type": "string",
                             ...}
        :param language: маркер основного языка, строка типа "en", "ru", "uk", "de" і т.п.
        :param comment: пояснение к свойству, строка або словарь с указанием атрибутов языка і типа,
                        возможна передача списка
                        словарь вида {"text": "label text",
                                      "lang": "en",
                                      "type": "string",
                                       ...}
        :param equality: список эквивалентных свойств, строка, список строк, словарь або список словарей вида
                         {"text": "class_name",
                          "attr_1": "value",
                          "attr_2": "value",
                           ...}
        :param asymmetric: указание asymmetric, True/False
        :param functional: указание functional, True/False
        :param inverse_functional: указание inverse_functional, True/False
        :param irreflexive: указание irreflexive, True/False
        :param reflexive: указание reflexive, True/False
        :param symmetric: указание symmetric, True/False
        :param transitive: указание transitive, True/False
        :param deprecated: указание deprecated, строка або список строк
        :param version_info: указание version_info, строка або список строк
        :param prior_version: указание prior_version, строка або список строк
        :param incompatible_with: указание имён несовместимых свойств, строка або список строк
        :param see_also: указание see_also, строка або список строк
        :param is_defined_by: указание is_defined_by, строка або список строк
        :param inverse_of: указание inverse_of, строка або список строк
        :param disjoint_with: свойство або список свойств, с которыми указано явное различие
        :param additional_fields: дополнительные нестандартные поля, , предаются в виде словаря вида:
                                  {"имя_поля_1": "значение поля 1",
                                   "имя_поля_2": "значение поля 2",
                                   ...}
        :param other_types_of_links: дополнительные нестандартные связи с другими объектами,
                                     предаются в виде словаря вида:
                                     {"link_name": "название связи",
                                      "object": "ID объекта, на который ссылается данная связь",
                                      "attr_1": "value",
                                      "attr_2": "value",
                                      ...}
                                    або списка таких словарей
        """
        self.id = replace_symbols_1(id).replace("&", "_and_")
        self.owl_text = ""

        if isinstance(domain_id, list) or isinstance(domain_id, set):
            self.domain_id = domain_id
        elif isinstance(domain_id, str) or isinstance(domain_id, dict):
            self.domain_id = [domain_id]
        else:
            self.domain_id = []

        if isinstance(range_id, list) or isinstance(range_id, set):
            self.range_id = range_id
        elif isinstance(range_id, str) or isinstance(range_id, dict):
            self.range_id = [range_id]
        else:
            self.range_id = []

        if isinstance(parent_id, list) or isinstance(parent_id, set):
            self.parent_ids = parent_id
        elif isinstance(parent_id, str) or isinstance(parent_id, dict):
            self.parent_ids = [parent_id]
        else:
            self.parent_ids = []

        self.label = label
        self.language = language
        self.comment = comment

        self.asymmetric = asymmetric
        self.functional = functional
        self.inverse_functional = inverse_functional
        self.irreflexive = irreflexive
        self.reflexive = reflexive
        self.symmetric = symmetric
        self.transitive = transitive

        if isinstance(deprecated, list) or isinstance(deprecated, set):
            self.deprecated = deprecated
        elif isinstance(deprecated, str) or isinstance(deprecated, dict):
            self.deprecated = [deprecated]
        else:
            self.deprecated = []

        if isinstance(version_info, list) or isinstance(version_info, set):
            self.version_info = version_info
        elif isinstance(version_info, str) or isinstance(version_info, dict):
            self.version_info = [version_info]
        else:
            self.version_info = []

        if isinstance(prior_version, list) or isinstance(prior_version, set):
            self.prior_version = prior_version
        elif isinstance(prior_version, str) or isinstance(prior_version, dict):
            self.prior_version = [prior_version]
        else:
            self.prior_version = []

        if isinstance(incompatible_with, list) or isinstance(incompatible_with, set):
            self.incompatible_with = incompatible_with
        elif isinstance(incompatible_with, str) or isinstance(incompatible_with, dict):
            self.incompatible_with = [incompatible_with]
        else:
            self.incompatible_with = []

        if isinstance(see_also, list) or isinstance(see_also, set):
            self.see_also = see_also
        elif isinstance(see_also, str) or isinstance(see_also, dict):
            self.see_also = [see_also]
        else:
            self.see_also = []

        if isinstance(is_defined_by, list) or isinstance(is_defined_by, set):
            self.is_defined_by = is_defined_by
        elif isinstance(is_defined_by, str) or isinstance(is_defined_by, dict):
            self.is_defined_by = [is_defined_by]
        else:
            self.is_defined_by = []

        if isinstance(inverse_of, list) or isinstance(inverse_of, set):
            self.inverse_of = inverse_of
        elif isinstance(inverse_of, str) or isinstance(inverse_of, dict):
            self.inverse_of = [inverse_of]
        else:
            self.inverse_of = []

        if isinstance(backward_compatible_with, list) or isinstance(backward_compatible_with, set):
            self.backward_compatible_with = backward_compatible_with
        elif isinstance(backward_compatible_with, str) or isinstance(backward_compatible_with, dict):
            self.backward_compatible_with = [backward_compatible_with]
        else:
            self.backward_compatible_with = []

        if isinstance(disjoint_with, list) or isinstance(disjoint_with, set):
            self.disjoint_with = disjoint_with
        elif isinstance(disjoint_with, str) or isinstance(disjoint_with, dict):
            self.disjoint_with = [disjoint_with]
        else:
            self.disjoint_with = []

        if isinstance(equality, list) or isinstance(equality, set):
            self.equality = equality
        elif isinstance(equality, str) or isinstance(equality, dict):
            self.equality = [equality]
        else:
            self.equality = []

        if isinstance(additional_fields, dict):
            self.additional_fields = additional_fields
        else:
            self.additional_fields = dict()

        if isinstance(other_types_of_links, list) or isinstance(other_types_of_links, set):
            self.other_types_of_links = list(other_types_of_links)
        elif isinstance(other_types_of_links, dict):
            self.other_types_of_links = [other_types_of_links]
        elif isinstance(other_types_of_links, str):
            self.other_types_of_links = [{"link_name": other_types_of_links}]
        else:
            self.other_types_of_links = list()

    def __eq__(self, other):
        if isinstance(other, OntoProperty):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, OntoProperty):
            return self.id != other.id
        else:
            return False

    def __hash__(self):
        return int(hashlib.md5(self.id.encode()).hexdigest(), 16)

    def serialize(self):
        global warnings_list
        owl_text = '\t<owl:ObjectProperty rdf:ID="' + self.id.strip() + '">\n'

        if isinstance(self.parent_ids, str) and self.parent_ids.strip() != "":
            owl_text += '\t\t<rdfs:subPropertyOf rdf:resource="#' + self.parent_ids.strip() + '"/>\n'
        elif isinstance(self.parent_ids, dict) and len(self.parent_ids) > 0:
            main_data = self.parent_ids.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<rdfs:subPropertyOf'
                for attr in self.parent_ids:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.parent_ids.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'
        elif isinstance(self.parent_ids, list) or isinstance(self.parent_ids, set):
            for parent_id in self.parent_ids:
                if isinstance(parent_id, str) and parent_id.strip() != "":
                    owl_text += '\t\t<rdfs:subPropertyOf rdf:resource="#' + parent_id.strip() + '"/>\n'
                elif isinstance(parent_id, dict) and len(parent_id) > 0:
                    main_data = parent_id.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t<rdfs:subPropertyOf'
                        for attr in parent_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(parent_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'

        if isinstance(self.domain_id, list) or isinstance(self.domain_id, set):
            for i in self.domain_id:
                try:
                    if isinstance(i, str) and str(i) != "":
                        owl_text += '\t\t<rdfs:domain rdf:resource="#' + str(i).strip() + '"/>\n'
                    elif isinstance(i, dict) and len(i) > 0:
                        main_data = i.get("text")
                        if isinstance(main_data, str):
                            owl_text += '\t\t<rdfs:domain'
                            for attr in i:
                                if attr != "text":
                                    owl_text += ' xml:' + attr + '="' + str(i.get(attr)).strip() + '"'
                            owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'
                except Exception as e:
                    print(e)
                    warnings_list.append(str(e))
        elif isinstance(self.domain_id, str):
            try:
                if self.domain_id.strip() != "":
                    owl_text += '\t\t<rdfs:domain rdf:resource="#' + self.domain_id.strip() + '"/>\n'
            except Exception as e:
                print(e)
                warnings_list.append(str(e))
        elif isinstance(self.domain_id, dict) and len(self.domain_id) > 0:
            main_data = self.domain_id.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<rdfs:domain'
                for attr in self.domain_id:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.domain_id.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'

        if isinstance(self.range_id, list) or isinstance(self.range_id, set):
            for i in self.range_id:
                try:
                    if isinstance(i, str) and str(i) != "":
                        owl_text += '\t\t<rdfs:range rdf:resource="#' + str(i).strip() + '"/>\n'
                    elif isinstance(i, dict) and len(i) > 0:
                        main_data = i.get("text")
                        if isinstance(main_data, str):
                            owl_text += '\t\t<rdfs:range'
                            for attr in i:
                                if attr != "text":
                                    owl_text += ' xml:' + attr + '="' + str(i.get(attr)).strip() + '"'
                            owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'
                except Exception as e:
                    print(e)
                    warnings_list.append(str(e))
        elif isinstance(self.range_id, str):
            try:
                if self.range_id.strip() != "":
                    owl_text += '\t\t<rdfs:range rdf:resource="#' + self.range_id.strip() + '"/>\n'
            except Exception as e:
                print(e)
                warnings_list.append(str(e))
        elif isinstance(self.range_id, dict) and len(self.range_id) > 0:
            main_data = self.range_id.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<rdfs:range'
                for attr in self.range_id:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.range_id.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'

        # owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.id.strip() + '</rdfs:label>\n'
        if isinstance(self.label, list) or isinstance(self.label, set):
            for text in self.label:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + text.strip() + '</rdfs:label>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:label'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
        elif isinstance(self.label, str) and self.label.strip() != "":
            owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.label.strip() + '</rdfs:label>\n'
        elif isinstance(self.label, dict) and len(self.label) > 0:
            main_data = self.label.get("text")
            lang = self.label.get("lang")
            type = self.label.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:label'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.label:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + replace_digits(attr.strip()) + '="' + str(self.label.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
        else:
             owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.id.strip() + '</rdfs:label>\n'

        if isinstance(self.comment, list) or isinstance(self.comment, set):
            for text in self.comment:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:comment xml:lang="' + self.language.strip() + '">' + text.strip() + '</rdfs:comment>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:comment'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'
        elif isinstance(self.comment, str) and self.comment.strip() != "":
            owl_text += '\t\t<rdfs:comment xml:lang="' + self.language.strip() + '">' + self.comment.strip() + '</rdfs:comment>\n'
        elif isinstance(self.comment, dict) and len(self.comment) > 0:
            main_data = self.comment.get("text")
            lang = self.comment.get("lang")
            type = self.comment.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:comment'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.comment:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.comment.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'

        if isinstance(self.equality, list) or isinstance(self.equality, set):
            for prop_id in self.equality:
                if isinstance(prop_id, str) and prop_id.strip() != "":
                    owl_text += '\t\t<owl:equivalentProperty rdf:resource="#' + prop_id.strip() + '" />\n'
                elif isinstance(prop_id, dict) and len(prop_id) > 0:
                    main_data = prop_id.get("text")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:equivalentProperty'
                        for attr in prop_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(prop_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'
        elif isinstance(self.equality, str):
            owl_text += '\t\t<owl:equivalentProperty rdf:resource="#' + prop_self.equality.strip() + '" />\n'
        elif isinstance(self.equality, dict) and len(self.equality) > 0:
            main_data = self.equality.get("text")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:equivalentProperty'
                for attr in self.equality:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.equality.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'

        if self.asymmetric:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;AsymmetricProperty"/>\n'
        if self.functional:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;FunctionalProperty"/>\n'
        if self.inverse_functional:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;InverseFunctionalProperty"/>\n'
        if self.irreflexive:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;IrreflexiveProperty"/>\n'
        if self.reflexive:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;ReflexiveProperty"/>\n'
        if self.symmetric:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;SymmetricProperty"/>\n'
        if self.transitive:
            owl_text += '\t\t<rdf:type rdf:resource="&owl;TransitiveProperty"/>\n'

        # Параметр deprecated
        if isinstance(self.deprecated, list) or isinstance(self.deprecated, set):
            for text in self.deprecated:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:deprecated>' + text + '</owl:deprecated>\n'
                elif isinstance(text, dict):
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:deprecated'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'
        elif isinstance(self.deprecated, str) and self.deprecated.strip() != "":
            owl_text += '\t\t<owl:deprecated>' + self.deprecated + '</owl:deprecated>\n'
        elif isinstance(self.deprecated, dict) and len(self.deprecated) > 0:
            main_data = self.deprecated.get("text")
            lang = self.deprecated.get("lang")
            type = self.deprecated.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:deprecated'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.deprecated:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.deprecated.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'

        # Параметр versionInfo
        if isinstance(self.version_info, list) or isinstance(self.version_info, set):
            for text in self.version_info:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:versionInfo>' + text + '</owl:versionInfo>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:versionInfo'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:versionInfo>\n'
        elif isinstance(self.version_info, str) and self.version_info.strip() != "":
            owl_text += '\t\t<owl:versionInfo>' + self.version_info.strip() + '</owl:versionInfo>\n'
        elif isinstance(self.version_info, dict) and len(self.version_info) > 0:
            main_data = self.version_info.get("text")
            lang = self.version_info.get("lang")
            type = self.version_info.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:versionInfo'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.version_info:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.version_info.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:versionInfo>\n'

        # Параметр priorVersion
        if isinstance(self.prior_version, list) or isinstance(self.prior_version, set):
            for text in self.prior_version:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:priorVersion>' + text + '</owl:priorVersion>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:priorVersion'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:priorVersion>\n'
        elif isinstance(self.prior_version, str) and self.prior_version.strip() != "":
            owl_text += '\t\t<owl:priorVersion>' + self.prior_version.strip() + '</owl:priorVersion>\n'
        elif isinstance(self.prior_version, dict) and len(self.prior_version) > 0:
            main_data = self.prior_version.get("text")
            lang = self.prior_version.get("lang")
            type = self.prior_version.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:priorVersion'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.prior_version:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.prior_version.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:priorVersion>\n'

        # Параметр incompatibleWith
        if isinstance(self.incompatible_with, list) or isinstance(self.incompatible_with, set):
            for text in self.incompatible_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:incompatibleWith>' + text + '</owl:incompatibleWith>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:incompatibleWith'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:incompatibleWith>\n'
        elif isinstance(self.incompatible_with, str) and self.incompatible_with.strip() != "":
            owl_text += '\t\t<owl:incompatibleWith>' + self.incompatible_with.strip() + '</owl:incompatibleWith>\n'
        elif isinstance(self.incompatible_with, dict) and len(self.incompatible_with) > 0:
            main_data = self.incompatible_with.get("text")
            lang = self.incompatible_with.get("lang")
            type = self.incompatible_with.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:incompatibleWith'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.incompatible_with:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.incompatible_with.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:incompatibleWith>\n'

        # Параметр seeAlso
        if isinstance(self.see_also, list) or isinstance(self.see_also, set):
            for text in self.see_also:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:seeAlso>' + text + '</rdfs:seeAlso>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:seeAlso'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:seeAlso>\n'
        elif isinstance(self.see_also, str) and self.see_also.strip() != "":
            owl_text += '\t\t<rdfs:seeAlso>' + self.see_also.strip() + '</rdfs:seeAlso>\n'
        elif isinstance(self.see_also, dict) and len(self.see_also) > 0:
            main_data = self.see_also.get("text")
            lang = self.see_also.get("lang")
            type = self.see_also.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:seeAlso'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.see_also:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.see_also.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:seeAlso>\n'

        # Параметр isDefinedBy
        if isinstance(self.is_defined_by, list) or isinstance(self.is_defined_by, set):
            for text in self.is_defined_by:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:isDefinedBy>' + text + '</rdfs:isDefinedBy>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:isDefinedBy'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:isDefinedBy>\n'
        elif isinstance(self.is_defined_by, str) and self.is_defined_by.strip() != "":
            owl_text += '\t\t<rdfs:isDefinedBy>' + self.is_defined_by.strip() + '</rdfs:isDefinedBy>\n'
        elif isinstance(self.is_defined_by, dict) and len(self.is_defined_by) > 0:
            main_data = self.is_defined_by.get("text")
            lang = self.is_defined_by.get("lang")
            type = self.is_defined_by.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:isDefinedBy'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.is_defined_by:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.is_defined_by.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:isDefinedBy>\n'

        # Параметр backwardCompatibleWith
        if isinstance(self.backward_compatible_with, list) or isinstance(self.backward_compatible_with, set):
            for text in self.backward_compatible_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:backwardCompatibleWith>' + text + '</owl:backwardCompatibleWith>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:backwardCompatibleWith'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:backwardCompatibleWith>\n'
        elif isinstance(self.backward_compatible_with, str) and self.backward_compatible_with.strip() != "":
            owl_text += '\t\t<owl:backwardCompatibleWith>' + self.backward_compatible_with.strip() + '</owl:backwardCompatibleWith>\n'
        elif isinstance(self.backward_compatible_with, dict) and len(self.backward_compatible_with) > 0:
            main_data = self.backward_compatible_with.get("text")
            lang = self.backward_compatible_with.get("lang")
            type = self.backward_compatible_with.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:backwardCompatibleWith'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.backward_compatible_with:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(
                            self.backward_compatible_with.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:backwardCompatibleWith>\n'

        if isinstance(self.inverse_of, list) or isinstance(self.inverse_of, set):
            for text in self.inverse_of:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:inverseOf rdf:resource="#' + text + '"/>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:inverseOf'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:inverseOf>\n'
        elif isinstance(self.inverse_of, str) and self.inverse_of.strip() != "":
            owl_text += '\t\t<owl:inverseOf rdf:resource="#' + self.inverse_of.strip() + '"/>\n'
        elif isinstance(self.inverse_of, dict) and len(self.inverse_of) > 0:
            main_data = self.inverse_of.get("text")
            lang = self.inverse_of.get("lang")
            type = self.inverse_of.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:inverseOf'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.inverse_of:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.inverse_of.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:inverseOf>\n'

        if isinstance(self.disjoint_with, list) or isinstance(self.disjoint_with, set):
            for text in self.disjoint_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:propertyDisjointWith rdf:resource="#' + text.strip() + '"/>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t<owl:propertyDisjointWith'
                        for attr in text:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(text.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'
        elif isinstance(self.disjoint_with, str) and self.disjoint_with.strip() != "":
            owl_text += '\t\t<owl:propertyDisjointWith rdf:resource="#' + self.disjoint_with.strip() + '"/>\n'
        elif isinstance(self.disjoint_with, dict) and len(self.disjoint_with) > 0:
            main_data = self.disjoint_with.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<owl:propertyDisjointWith'
                for attr in self.disjoint_with:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.disjoint_with.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '"/>\n'

        # Связи нестандартного типа
        if isinstance(self.other_types_of_links, list) or isinstance(self.other_types_of_links, set):
            for link in self.other_types_of_links:
                if isinstance(link, str) and link.strip() != "":
                    owl_text += '\t\t<rdfs:' + replace_digits(link) + ' rdf:resource="#" />\n'
                elif isinstance(link, dict):
                    link_name = link.get("link_name")
                    link_object = link.get("object")
                    if (isinstance(link_name, str) and link_name.strip() != "" and
                            isinstance(link_object, str) and link_object.strip() != ""):
                        owl_text += '\t\t<rdfs:' + replace_digits(link_name)
                        for attr in link:
                            if attr.strip() != "link_name" and attr.strip() != "object":
                                owl_text += ' xml:' + attr + '="' + str(
                                    link.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'
        elif isinstance(self.other_types_of_links, str) and self.other_types_of_links.strip() != "":
            owl_text += '\t\t<owl:' + replace_symbols_1(replace_digits(self.other_types_of_links)) + ' rdf:resource="#" />\n'
        elif isinstance(self.self.other_types_of_links, dict):
            link_name = self.self.other_types_of_links.get("link_name")
            link_object = self.self.other_types_of_links.get("object")
            if (isinstance(link_name, str) and link_name.strip() != "" and
                    isinstance(link_object, str) and link_object.strip() != ""):
                owl_text += '\t\t<rdfs:' + replace_digits(replace_symbols_1(link_name))
                for attr in self.self.other_types_of_links:
                    if attr.strip() != "link_name" and attr.strip() != "object":
                        owl_text += ' xml:' + replace_symbols_1(replace_digits(attr)) + '="' + str(
                            self.self.other_types_of_links.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'

        for field in self.additional_fields:
            if isinstance(self.additional_fields.get(field), str):
                owl_text += '\t\t<rdfs:' + replace_digits(str(field)) + ' xml:' + replace_digits(str(field)) + '="' + self.additional_fields.get(
                    field) + '">' \
                            + self.additional_fields.get(field) + '</rdfs:' + replace_digits(str(field)) + '>\n'
            elif isinstance(self.additional_fields.get(field), dict):
                main_data = self.additional_fields.get(field).get("text")
                lang = self.additional_fields.get(field).get("lang")
                type = self.additional_fields.get(field).get("type")
                if isinstance(main_data, str) and main_data.strip() != "":
                    owl_text += '\t\t<owl:' + replace_symbols_1(replace_digits(str(field)))
                    if isinstance(lang, str):
                        owl_text += ' xml:lang="' + lang.strip() + '"'
                    if isinstance(type, str) and type.strip() != "":
                        owl_text += ' rdf:datatype="' + type.strip() + '"'
                    for attr in self.additional_fields.get(field):
                        if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                            owl_text += ' xml:' + attr.strip() + '="' + \
                                        str(self.additional_fields.get(field).get(attr)) + '"'
                    owl_text += '>' + main_data.strip().replace("&", "and") + '</owl:' + replace_symbols_1(main_data) + '>\n'

        owl_text +=  '\t</owl:ObjectProperty>\n'
        self.owl_text = owl_text
        return owl_text


class OntoEntity:
    def __init__(self, id="ThingEntity", of_classes=None, label=None, language="uk", equality=None,
                 comment=None,
                 assertions=None,
                 deprecated=None,
                 version_info=None,
                 prior_version=None,
                 incompatible_with=None,
                 see_also=None,
                 is_defined_by=None,
                 backward_compatible_with=None,
                 additional_fields=None,
                 other_types_of_links=None):
        """
        Програмное представление именованной сутності (NamedIndividual) для OWL
        :param id: имя сутності, строка
        :param of_classes: имя класа, к которому принадлежит данная сутність, строка, список строк, словарь
                           с обязательным полем "text", в котором указано имя класа, а также заначениями
                           дополнительных атрибутов
        :param label: название сутності, строка, список строк, словарь с указанием полей "lang" и/или "type"
                      або список таких словарей
        :param language: маркер основного языка, строка
        :param equality: эквивалентные сутності, строка, список строк, словарь
                         с обязательным полем "text", в котором указано имя класа, а также заначениями
                         дополнительных атрибутов
        :param comment: поясление к сутності, строка, список строк, словарь с указанием полей "lang" и/или "type"
                        або список таких словарей
        :param assertions: привязка к свойствам, может задаваться в виде словаря типа {имя_свойства: [значеня_свойства]}
                           или списка пар значений [[имя_свойства, значене_свойства_1, значене_свойства_2...]]
                           при хранении приводится к словарю указанного вида
        :param deprecated: указание deprecated, строка або список строк
        :param version_info: указание version_info, строка або список строк
        :param prior_version: указание prior_version, строка або список строк
        :param incompatible_with: указание incompatible_with, строка або список строк
        :param see_also: указание see_also, строка або список строк
        :param is_defined_by: указание is_defined_by, строка або список строк
        :param backward_compatible_with: указание backward_compatible_with, строка або список строк
        :param additional_fields: дополнительные нестандартные поля, предаются в виде словаря вида:
                                  {"имя_поля_1": "значение поля 1",
                                   "имя_поля_2": "значение поля 2",
                                   ...}
        :param other_types_of_links: дополнительные нестандартные связи с другими объектами,
                                     предаются в виде словаря вида:
                                     {"link_name": "название связи",
                                      "object": "ID объекта, на который ссылается данная связь",
                                      "attr_1": "value",
                                      "attr_2": "value",
                                      ...}
                                    або списка таких словарей
        """

        self.id = replace_symbols_1(id).replace("&", "_and_")
        self.owl_text = ""

        if isinstance(of_classes, list) or isinstance(of_classes, set):
            self.of_classes = of_classes
        elif of_classes is None:
            self.of_classes = []
        else:
            self.of_classes = [of_classes]

        if isinstance(equality, list) or isinstance(equality, set):
            self.equality = equality
        elif isinstance(equality, str) or isinstance(equality, dict):
            self.equality = [equality]
        else:
            self.equality = []

        self.label = label
        self.language = language.strip()

        self.comment = comment

        self.assertions = dict()
        if isinstance(assertions, list) or isinstance(assertions, set):
            for sublist in assertions:
                if len(sublist) > 0 and isinstance(sublist, list) or isinstance(sublist, set):
                    self.assertions[sublist[0]] = sublist[1:]
        elif isinstance(assertions, dict):
            self.assertions = assertions

        if isinstance(deprecated, list) or isinstance(deprecated, set):
            self.deprecated = list(deprecated)
        elif isinstance(deprecated, str) or isinstance(deprecated, dict):
            self.deprecated = [deprecated]
        else:
            self.deprecated = []

        if isinstance(version_info, list) or isinstance(version_info, set):
            self.version_info = list(version_info)
        elif isinstance(version_info, str) or isinstance(version_info, dict):
            self.version_info = [version_info]
        else:
            self.version_info = []

        if isinstance(prior_version, list) or isinstance(prior_version, set):
            self.prior_version = list(prior_version)
        elif isinstance(prior_version, str) or isinstance(prior_version, dict):
            self.prior_version = [prior_version]
        else:
            self.prior_version = []

        if isinstance(incompatible_with, list) or isinstance(incompatible_with, set):
            self.incompatible_with = list(incompatible_with)
        elif isinstance(incompatible_with, str) or isinstance(incompatible_with, dict):
            self.incompatible_with = [incompatible_with]
        else:
            self.incompatible_with = []

        if isinstance(see_also, list) or isinstance(see_also, set):
            self.see_also = list(see_also)
        elif isinstance(see_also, str) or isinstance(see_also, dict):
            self.see_also = [see_also]
        else:
            self.see_also = []

        if isinstance(is_defined_by, list) or isinstance(is_defined_by, set):
            self.is_defined_by = list(is_defined_by)
        elif isinstance(is_defined_by, str) or isinstance(is_defined_by, dict):
            self.is_defined_by = [is_defined_by]
        else:
            self.is_defined_by = []

        if isinstance(backward_compatible_with, list) or isinstance(backward_compatible_with, set):
            self.backward_compatible_with = list(backward_compatible_with)
        elif isinstance(backward_compatible_with, str)  or isinstance(backward_compatible_with, dict):
            self.backward_compatible_with = [backward_compatible_with]
        else:
            self.backward_compatible_with = []

        if isinstance(additional_fields, dict):
            self.additional_fields = additional_fields
        else:
            self.additional_fields = dict()

        if isinstance(other_types_of_links, list) or isinstance(other_types_of_links, set):
            self.other_types_of_links = list(other_types_of_links)
        elif isinstance(other_types_of_links, dict):
            self.other_types_of_links = [other_types_of_links]
        elif isinstance(other_types_of_links, str):
            self.other_types_of_links = [{"link_name": other_types_of_links}]
        else:
            self.other_types_of_links = list()

    def __eq__(self, other):
        if isinstance(other, OntoClass):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, OntoClass):
            return self.id != other.id
        else:
            return False

    def __hash__(self):
        return int(hashlib.md5(self.id.encode()).hexdigest(), 16)

    def serialize(self):
        if isinstance(self.of_classes, list) or isinstance(self.of_classes, dict):
            for of_class in self.of_classes:
                if isinstance(of_class, str) and of_class.strip() == ""\
                        and len(self.label) == 0 and self.language.strip() == "":
                    return '\t<owl:NamedIndividual rdf:about="' + self.id.strip().strip('"').strip("'") + '" />\n'
                elif isinstance(of_class, dict) and len(of_class) == 0 and len(self.label) == 0\
                        and self.language.strip() == "":
                    return '\t<owl:NamedIndividual rdf:about="' + self.id.strip().strip('"').strip("'") + '" />\n'

        owl_text = '\t<owl:NamedIndividual rdf:about="' + self.id.strip().strip('"').strip("'") + '" >\n'

        if isinstance(self.of_classes, list) or isinstance(self.of_classes, set):
            for class_id in self.of_classes:
                if isinstance(class_id, str) and class_id.strip() != "":
                    owl_text += '\t\t<rdf:type rdf:resource="#' + class_id.strip() + '" />\n'
                elif isinstance(class_id, dict) and len(class_id) > 0:
                    main_data = class_id.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t<rdf:type'
                        for attr in class_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(class_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.of_classes, dict) and len(self.of_classes) > 0:
            main_data = self.of_classes.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<rdf:type'
                for attr in self.of_classes:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.of_classes.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.of_classes, str):
            owl_text += '\t\t<rdf:type rdf:resource="#' + self.of_classes.strip() + '" />\n'

        # owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.id.strip() + '</rdfs:label>\n'
        if isinstance(self.label, list) or isinstance(self.label, set):
            for text in self.label:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + text.strip() + '</rdfs:label>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:label'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
        elif isinstance(self.label, str) and self.label.strip() != "":
            owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.label.strip() + '</rdfs:label>\n'
        elif isinstance(self.label, dict) and len(self.label) > 0:
            main_data = self.label.get("text")
            lang = self.label.get("lang")
            type = self.label.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:label'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.label:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.label.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:label>\n'
        else:
             owl_text += '\t\t<rdfs:label xml:lang="' + self.language.strip() + '">' + self.id.strip() + '</rdfs:label>\n'

        if isinstance(self.comment, list) or isinstance(self.comment, set):
            for text in self.comment:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:comment xml:lang="' + self.language.strip() + '">' + text.strip() + '</rdfs:comment>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:comment'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + replace_digits(attr.strip()) + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'
        elif isinstance(self.comment, str) and self.comment.strip() != "":
            owl_text += '\t\t<rdfs:comment xml:lang="' + self.language.strip() + '">' + self.comment.strip() + '</rdfs:comment>\n'
        elif isinstance(self.comment, dict) and len(self.comment) > 0:
            main_data = self.comment.get("text")
            lang = self.comment.get("lang")
            type = self.comment.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:comment'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.comment:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.comment.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:comment>\n'

        if isinstance(self.equality, list) or isinstance(self.equality, set):
            for entity_id in self.equality:
                if isinstance(entity_id, str) and entity_id.strip() != "":
                    owl_text += '\t\t<owl:sameAs rdf:resource="#' + entity_id.strip() + '" />\n'
                elif isinstance(entity_id, dict) and len(entity_id) > 0:
                    main_data = entity_id.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t<owl:sameAs'
                        for attr in entity_id:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(entity_id.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.equality, dict) and len(self.equality) > 0:
            main_data = self.equality.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t<owl:sameAs'
                for attr in self.equality:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.equality.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + main_data.strip() + '" />\n'
        elif isinstance(self.equality, str) and self.equality.strip() != "":
            owl_text += '\t\t<owl:sameAs rdf:resource="#' + self.equality.strip() + '" />\n'

        # Связи нестандартного типа
        if isinstance(self.other_types_of_links, list) or isinstance(self.other_types_of_links, set):
            for link in self.other_types_of_links:
                if isinstance(link, str) and link.strip() != "":
                    owl_text += '\t\t<rdfs:' + replace_digits(link) + ' rdf:resource="#" />\n'
                elif isinstance(link, dict):
                    link_name = link.get("link_name")
                    link_object = link.get("object")
                    if (isinstance(link_name, str) and link_name.strip() != "" and
                            isinstance(link_object, str) and link_object.strip() != ""):
                        owl_text += '\t\t<rdfs:' + replace_digits(link_name)
                        for attr in link:
                            if attr.strip() != "link_name" and attr.strip() != "object":
                                owl_text += ' xml:' + attr + '="' + str(
                                    link.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'
        elif isinstance(self.other_types_of_links, str) and self.other_types_of_links.strip() != "":
            owl_text += '\t\t<owl:' + replace_digits(replace_symbols_1(self.other_types_of_links)) + ' rdf:resource="#" />\n'
        elif isinstance(self.self.other_types_of_links, dict):
            link_name = self.self.other_types_of_links.get("link_name")
            link_object = self.self.other_types_of_links.get("object")
            if (isinstance(link_name, str) and link_name.strip() != "" and
                    isinstance(link_object, str) and link_object.strip() != ""):
                owl_text += '\t\t<rdfs:' + replace_digits(replace_symbols_1(link_name))
                for attr in self.self.other_types_of_links:
                    if attr.strip() != "link_name" and attr.strip() != "object":
                        owl_text += ' xml:' + replace_symbols_2(attr) + '="' + str(
                            self.self.other_types_of_links.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'

        # Параметр deprecated
        if isinstance(self.deprecated, list) or isinstance(self.deprecated, set):
            for text in self.deprecated:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:deprecated>' + text + '</owl:deprecated>\n'
                elif isinstance(text, dict):
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:deprecated'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'
        elif isinstance(self.deprecated, str) and self.deprecated.strip() != "":
            owl_text += '\t\t<owl:deprecated>' + self.deprecated + '</owl:deprecated>\n'
        elif isinstance(self.deprecated, dict) and len(self.deprecated) > 0:
            main_data = self.deprecated.get("text")
            lang = self.deprecated.get("lang")
            type = self.deprecated.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:deprecated'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.deprecated:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.deprecated.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:deprecated>\n'

        # Параметр versionInfo
        if isinstance(self.version_info, list) or isinstance(self.version_info, set):
            for text in self.version_info:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:versionInfo>' + text + '</owl:versionInfo>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:versionInfo'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:versionInfo>\n'
        elif isinstance(self.version_info, str) and self.version_info.strip() != "":
            owl_text += '\t\t<owl:versionInfo>' + self.version_info.strip() + '</owl:versionInfo>\n'
        elif isinstance(self.version_info, dict) and len(self.version_info) > 0:
            main_data = self.version_info.get("text")
            lang = self.version_info.get("lang")
            type = self.version_info.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:versionInfo'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.version_info:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.version_info.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:versionInfo>\n'

        # Параметр priorVersion
        if isinstance(self.prior_version, list) or isinstance(self.prior_version, set):
            for text in self.prior_version:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:priorVersion>' + text + '</owl:priorVersion>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:priorVersion'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:priorVersion>\n'
        elif isinstance(self.prior_version, str) and self.prior_version.strip() != "":
            owl_text += '\t\t<owl:priorVersion>' + self.prior_version.strip() + '</owl:priorVersion>\n'
        elif isinstance(self.prior_version, dict) and len(self.prior_version) > 0:
            main_data = self.prior_version.get("text")
            lang = self.prior_version.get("lang")
            type = self.prior_version.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:priorVersion'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.prior_version:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.prior_version.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:priorVersion>\n'

        # Параметр incompatibleWith
        if isinstance(self.incompatible_with, list) or isinstance(self.incompatible_with, set):
            for text in self.incompatible_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:incompatibleWith>' + text + '</owl:incompatibleWith>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:incompatibleWith'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:incompatibleWith>\n'
        elif isinstance(self.incompatible_with, str) and self.incompatible_with.strip() != "":
            owl_text += '\t\t<owl:incompatibleWith>' + self.incompatible_with.strip() + '</owl:incompatibleWith>\n'
        elif isinstance(self.incompatible_with, dict) and len(self.incompatible_with) > 0:
            main_data = self.incompatible_with.get("text")
            lang = self.incompatible_with.get("lang")
            type = self.incompatible_with.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:incompatibleWith'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.incompatible_with:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.incompatible_with.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:incompatibleWith>\n'

        # Параметр seeAlso
        if isinstance(self.see_also, list) or isinstance(self.see_also, set):
            for text in self.see_also:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:seeAlso>' + text + '</rdfs:seeAlso>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:seeAlso'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:seeAlso>\n'
        elif isinstance(self.see_also, str) and self.see_also.strip() != "":
            owl_text += '\t\t<rdfs:seeAlso>' + self.see_also.strip() + '</rdfs:seeAlso>\n'
        elif isinstance(self.see_also, dict) and len(self.see_also) > 0:
            main_data = self.see_also.get("text")
            lang = self.see_also.get("lang")
            type = self.see_also.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:seeAlso'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.see_also:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + replace_digits(attr.strip()) + '="' + str(self.see_also.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:seeAlso>\n'

        # Параметр isDefinedBy
        if isinstance(self.is_defined_by, list) or isinstance(self.is_defined_by, set):
            for text in self.is_defined_by:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<rdfs:isDefinedBy>' + text + '</rdfs:isDefinedBy>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<rdfs:isDefinedBy'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + replace_digits(attr.strip()) + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:isDefinedBy>\n'
        elif isinstance(self.is_defined_by, str) and self.is_defined_by.strip() != "":
            owl_text += '\t\t<rdfs:isDefinedBy>' + self.is_defined_by.strip() + '</rdfs:isDefinedBy>\n'
        elif isinstance(self.is_defined_by, dict) and len(self.is_defined_by) > 0:
            main_data = self.is_defined_by.get("text")
            lang = self.is_defined_by.get("lang")
            type = self.is_defined_by.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<rdfs:isDefinedBy'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.is_defined_by:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(self.is_defined_by.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</rdfs:isDefinedBy>\n'

        # Параметр backwardCompatibleWith
        if isinstance(self.backward_compatible_with, list) or isinstance(self.backward_compatible_with, set):
            for text in self.backward_compatible_with:
                if isinstance(text, str) and text.strip() != "":
                    owl_text += '\t\t<owl:backwardCompatibleWith>' + text + '</owl:backwardCompatibleWith>\n'
                elif isinstance(text, dict) and len(text) > 0:
                    main_data = text.get("text")
                    lang = text.get("lang")
                    if not isinstance(lang, str) or lang.strip() == "":
                        lang = self.language.strip()
                    type = text.get("type")
                    if isinstance(main_data, str) and main_data.strip() != "":
                        owl_text += '\t\t<owl:backwardCompatibleWith'
                        if isinstance(lang, str):
                            owl_text += ' xml:lang="' + lang.strip() + '"'
                        if isinstance(type, str) and type.strip() != "":
                            owl_text += ' rdf:datatype="' + type.strip() + '"'
                        for attr in text:
                            if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                                owl_text += ' xml:' + attr.strip() + '="' + str(text.get(attr)) + '"'
                        owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:backwardCompatibleWith>\n'
        elif isinstance(self.backward_compatible_with, str) and self.backward_compatible_with.strip() != "":
            owl_text += '\t\t<owl:backwardCompatibleWith>' + self.backward_compatible_with.strip() + '</owl:backwardCompatibleWith>\n'
        elif isinstance(self.backward_compatible_with, dict) and len(self.backward_compatible_with) > 0:
            main_data = self.backward_compatible_with.get("text")
            lang = self.backward_compatible_with.get("lang")
            type = self.backward_compatible_with.get("type")
            if isinstance(main_data, str) and main_data.strip() != "":
                owl_text += '\t\t<owl:backwardCompatibleWith'
                if isinstance(lang, str):
                    owl_text += ' xml:lang="' + lang.strip() + '"'
                if isinstance(type, str) and type.strip() != "":
                    owl_text += ' rdf:datatype="' + type.strip() + '"'
                for attr in self.backward_compatible_with:
                    if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                        owl_text += ' xml:' + attr.strip() + '="' + str(
                            self.backward_compatible_with.get(attr)) + '"'
                owl_text += '>' + main_data.strip().replace("&", "and").replace("<", "_less_").replace(">", "_more_") + '</owl:backwardCompatibleWith>\n'

        # Привязка свойств
        if len(self.assertions) > 0:
            for assertion in self.assertions:
                if len(self.assertions[assertion]) > 0:
                    for val in self.assertions[assertion]:
                        owl_text += '\t\t<' + assertion + ' rdf:resource="' + val + '"/>\n'
                else:
                    owl_text += '\t\t<' + assertion + '/>\n'

        # Связи нестандартного типа
        if isinstance(self.other_types_of_links, list) or isinstance(self.other_types_of_links, set):
            for link in self.other_types_of_links:
                if isinstance(link, str) and link.strip() != "":
                    owl_text += '\t\t<rdfs:' + replace_digits(link) + ' rdf:resource="#" />\n'
                elif isinstance(link, dict):
                    link_name = link.get("link_name")
                    link_object = link.get("object")
                    if (isinstance(link_name, str) and link_name.strip() != "" and
                            isinstance(link_object, str) and link_object.strip() != ""):
                        owl_text += '\t\t<rdfs:' + replace_digits(link_name)
                        for attr in link:
                            if attr.strip() != "link_name" and attr.strip() != "object":
                                owl_text += ' xml:' + attr + '="' + str(
                                    link.get(attr)).strip() + '"'
                        owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'
        elif isinstance(self.other_types_of_links, str) and self.other_types_of_links.strip() != "":
            owl_text += '\t\t<owl:' + replace_digits(replace_symbols_1(self.other_types_of_links)) + ' rdf:resource="#" />\n'
        elif isinstance(self.self.other_types_of_links, dict):
            link_name = self.self.other_types_of_links.get("link_name")
            link_object = self.self.other_types_of_links.get("object")
            if (isinstance(link_name, str) and link_name.strip() != "" and
                    isinstance(link_object, str) and link_object.strip() != ""):
                owl_text += '\t\t<rdfs:' + replace_digits(replace_symbols_1(link_name))
                for attr in self.self.other_types_of_links:
                    if attr.strip() != "link_name" and attr.strip() != "object":
                        owl_text += ' xml:' + replace_digits(attr) + '="' + str(
                            self.self.other_types_of_links.get(attr)).strip() + '"'
                owl_text += ' rdf:resource="#' + link_object.strip() + '" />\n'

        for field in self.additional_fields:
            if isinstance(self.additional_fields.get(field), str):
                owl_text += '\t\t<rdfs:' + replace_digits(str(field)) + ' xml:' + replace_digits(str(field)) + '="' + self.additional_fields.get(
                    field) + '">' \
                            + self.additional_fields.get(field) + '</rdfs:' + replace_digits(str(field)) + '>\n'
            elif isinstance(self.additional_fields.get(field), dict):
                main_data = self.additional_fields.get(field).get("text")
                lang = self.additional_fields.get(field).get("lang")
                type = self.additional_fields.get(field).get("type")
                if isinstance(main_data, str) and main_data.strip() != "":
                    owl_text += '\t\t<owl:' + replace_digits(replace_symbols_1(str(field)))
                    if isinstance(lang, str):
                        owl_text += ' xml:lang="' + lang.strip() + '"'
                    if isinstance(type, str) and type.strip() != "":
                        owl_text += ' rdf:datatype="' + type.strip() + '"'
                    for attr in self.additional_fields.get(field):
                        if attr.lower().strip() not in ["text", "lang", "language", "type"]:
                            owl_text += ' xml:' + replace_digits(attr.strip()) + '="' + \
                                        str(self.additional_fields.get(field).get(attr)) + '"'
                    owl_text += '>' + main_data.strip().replace("&", "and") + '</owl:' + replace_digits(replace_symbols_1(str(field))) + '>\n'

        owl_text += '\t</owl:NamedIndividual>\n'
        self.owl_text = owl_text
        return owl_text


class EntityDifferenceDescription:
    def __init__(self, names=None):
        """
        Класс для представления явно заданных различий сущностей
        :param names: список имён сущностей, для которых задано явное различие, список строк або словарей
        """
        if isinstance(names, list) or isinstance(names, set):
            self.names = names
        elif isinstance(names, str) or isinstance(names, dict):
            self.names = [names]
        else:
            self.names = []
        self.owl_text = ""

    def __eq__(self, other):
        if isinstance(other, EntityDifferenceDescription):
            for name in self.names:
                if name not in other.names:
                    return False
            return True
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, EntityDifferenceDescription):
            for name in self.names:
                if name not in other.names:
                    return True
            return False
        else:
            return False

    def __hash__(self):
        id = ""
        if (isinstance(self.names, list) or isinstance(self.names, set)) and len(self.names) > 0:
            for name in self.names:
                if isinstance(name, str):
                    id += name
                elif isinstance(name, dict):
                    for attr in name:
                        if isinstance(attr, str):
                            id += attr
                        value = name.get(attr)
                        if isinstance(value, str):
                            id += value
        elif isinstance(self.names, str):
            id = self.names
        return int(hashlib.md5(id.encode()).hexdigest(), 16)

    def serialize(self):
        owl_text = '\t<rdf:Description>\n'
        owl_text += '\t\t<rdf:type rdf:resource="&owl;AllDifferent"/>\n'
        owl_text += '\t\t<owl:distinctMembers rdf:parseType="Collection">\n'
        if isinstance(self.names, str):
            owl_text += '\t\t\t<rdf:Description rdf:about="' + self.names + '"/>'
        elif isinstance(self.names, list) or isinstance(self.names, set):
            for name in self.names:
                if isinstance(name, str):
                    owl_text += '\t\t\t<rdf:Description rdf:about="' + name + '"/>'
                elif isinstance(name, dict):
                    main_data = name.get("text")
                    if isinstance(main_data, str):
                        owl_text += '\t\t\t<rdf:Description'
                        for attr in name:
                            if attr != "text":
                                owl_text += ' xml:' + attr + '="' + str(name.get(attr)).strip() + '"'
                        owl_text += ' rdf:about="' + main_data.strip() + '"/>'
        elif isinstance(self.names, dict):
            main_data = self.names.get("text")
            if isinstance(main_data, str):
                owl_text += '\t\t\t<rdf:Description'
                for attr in self.names:
                    if attr != "text":
                        owl_text += ' xml:' + attr + '="' + str(self.names.get(attr)).strip() + '"'
                owl_text += ' rdf:about="' + main_data.strip() + '"/>\n'
        owl_text += '\t\t</owl:distinctMembers>\n'
        owl_text += '\t</rdf:Description>\n\n'
        self.owl_text = owl_text
        return owl_text


class ConstantOWLPart:

    def __init__(self, input_file="semantic_hierarchy.xml"):
        out_file = open(input_file, mode='r', encoding='utf-8')
        self.owl_text = out_file.read()
        out_file.close()


class SemanticCategoriesRelations:

    def __init__(self, input_file="relations.xml"):
        self.rel_dict = dict()
        tree = Et.ElementTree(Et.fromstring(open(input_file, mode='r', encoding='utf-8').read()))  # Et.parse(input_file)

        root = tree.getroot()
        for i in root:
            name_block = i.find("name")
            if name_block is not None:
                parent_props = set()
                for j in i:
                    if j.tag == "parent_name":
                        parent_props.add(j.text.strip())
                if len(parent_props) == 1:
                    self.rel_dict[name_block.text.strip()] = list(parent_props)[0]
                elif len(parent_props) > 1:
                    self.rel_dict[name_block.text.strip()] = list(parent_props)


class RelationReplacer:

    def __init__(self, input_file="substitutes.xml", default_parent_type="WordsLink",
                 default_parent_type_verbose="Зв'язки між окремими поняттями"):
        self.rel_dict = dict()
        self.rel_dict_verbose = dict()
        tree =  Et.ElementTree(Et.fromstring(open(input_file, mode='r', encoding='utf-8').read()))  # Et.parse(input_file)
        root = tree.getroot()
        for i in root:
            goal_type = i.find("goal_type")
            if goal_type is not None:
                goal_name = goal_type.find("name")
                goal_verbose_name = goal_type.find("verbose_name")
                if goal_name is not None:
                    goal_name = goal_name.text.strip()
                if goal_verbose_name is not None:
                    goal_verbose_name = goal_verbose_name.text.strip()
                if goal_name is not None or goal_verbose_name is not None:
                    replace_options = dict()
                    for item in i:
                        if i.tag == "item":
                            name = item.find("name")
                            verbose_name = item.find("verbose_name")
                            parent_type = item.find("parent_type")
                            parent_type_verbose = item.find("parent_type_verbose")
                            eliminate = item.find("eliminate")
                            find_new_link = item.find("find_new_link")
                            if name is None:
                                continue
                            else:
                                name = name.text.strip()
                            if verbose_name is None:
                                verbose_name = name
                            else:
                                verbose_name = verbose_name.text.strip()
                            if eliminate is None:
                                eliminate = False
                            else:
                                if eliminate.text.strip() == "true":
                                    eliminate = True
                                else:
                                    eliminate = False
                            if find_new_link is None:
                                find_new_link = False
                            else:
                                if find_new_link.text.strip() == "true":
                                    find_new_link = True
                                else:
                                    find_new_link = False
                            if parent_type is None:
                                parent_type = default_parent_type
                            else:
                                parent_type = parent_type.text.strip()
                            if parent_type_verbose is None:
                                parent_type_verbose = default_parent_type_verbose
                            else:
                                parent_type_verbose = parent_type_verbose.text.strip()
                            marker_words = item.find("marker_words")
                            if marker_words is not None:
                                for word in marker_words:
                                    if word.text.strip() in replace_options:
                                        replace_options[word.text.strip()].append({
                                            "name": name,
                                            "verbose_name": verbose_name,
                                            "parent_type": parent_type,
                                            "parent_type_verbose": parent_type_verbose,
                                            "eliminate": eliminate,
                                            "find_new_link": find_new_link
                                        })
                                    else:
                                        replace_options[word.text.strip()] = [{
                                            "name": name,
                                            "verbose_name": verbose_name,
                                            "parent_type": parent_type,
                                            "parent_type_verbose": parent_type_verbose,
                                            "eliminate": eliminate,
                                            "find_new_link": find_new_link
                                        }]
                    self.rel_dict[goal_name] = replace_options
                    self.rel_dict_verbose[goal_verbose_name] = replace_options


def del_unknown_symbols(input_str=""):
    allowed_symbols = {'q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n',
                       'm','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C','V','B',
                       'N','M','1','2','3','4','5','6','7','8','9','0','!','@','#','$','%','^','&','*','(',')','-','_','=',
                       '+',',','.','?','<','>','{','}','[',']',':',';','|','\\','/','№','\n', '\r', '\t', "й","ц","у","к",
                       "е","н","г","ш","щ","з","х","ъ","ф","ы","в","а","п","р","о", "д", "л","ж","э","я","ч","с","м","и","т","ь",
                       "б","ю","Й","Ц","У","К","Е","Н","Г","Ш","Щ","З","Х","Ъ","Ф","Ы","В","А","П","Р","О","Л","Д","Ж","Э",
                       "Я","Ч","С","М","И","Т","Ь","Б","Ю","Ё","І","ё","і","ї","Ї","є","Є"," ", "—", "å", "é", "ø", "Ø",
                       "Å", "æ", "É", "Æ"}
    out_str = ""
    input_str = ' '.join(input_str.strip().split())
    for i in input_str:
        if i in allowed_symbols:
            out_str += i
    return out_str


def make_owl(owl_objects, path="", threads_n=1,
             owl_config=None, owl_config_file="tools/creator_config.xml"):

    if owl_config is None:
        owl_config = CreatorConstants().get_instance(config_file=owl_config_file)
    else:
        owl_config = owl_config.get_instance(config_file=owl_config_file)
    owl_text = '<?xml version = "1.0"?>\n\n'

    owl_text += '''
        <!DOCTYPE rdf:RDF [
            <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
            <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
            <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
            <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#"> 
            <!ENTITY comma ","> 
            <!ENTITY apostrof "_apr_">
            <!ENTITY squote "\'"> 
            <!ENTITY dquote '"'>
            <!ENTITY dot "."> 
            <!ENTITY lquote "«"> 
            <!ENTITY rquote "»"> 
            <!ENTITY colon ":"> 
            <!ENTITY dash "–"> 
            <!ENTITY interrogative "?"> 
        ]>
        '''

    owl_text += '<rdf:RDF xmlns:owl ="' + owl_config.owl + '"\n'
    owl_text += 'xmlns:rdfs="' + owl_config.rdfs + '"\n'
    owl_text += 'xmlns:xsd ="' + owl_config.xsd + '"\n'
    owl_text += 'xml:base = "' + owl_config.base + owl_config.name + '"\n'
    owl_text += 'xmlns:rdf = "' + owl_config.rdf + '"\n'

    if "ontology" in owl_objects and owl_objects["ontology"] is not None:
        if ('nodeName' in owl_objects["ontology"]['attributes'] and
                owl_objects["ontology"]['attributes']['nodeName'].strip() != ""):
            owl_text += 'xml:affiliation = "' + owl_objects["ontology"]['attributes']['nodeName'].strip() + '"\n'
            owl_text += 'xmlns = "' + owl_config.xmlns + owl_objects["ontology"]['attributes']['nodeName'].strip() + '#">\n'
            owl_text += '\t<owl:Ontology rdf:about="' + owl_objects["ontology"]['attributes']['nodeName'].strip() + '">\n'
        else:
            owl_text += 'xml:affiliation = "' + owl_config.name + '"\n'
            owl_text += 'xmlns = "' + owl_config.xmlns + owl_config.name + '#">\n'
            owl_text += '\t<owl:Ontology rdf:about="' + owl_config.name + '">\n'
        for d_item in owl_objects["ontology"]['data']:
            if d_item['attributes']['tclass'].strip().lower() == 'comment':
                if d_item['text'].strip() != "":
                    owl_text += '\t\t<rdfs:comment>' + d_item['text'].strip().replace("&", "&amp;") + '</rdfs:comment>\n'
                else:
                    owl_text += '\t\t<rdfs:comment>Text ontology for ' + path.split('/')[-1].replace("&", "&amp;") + '</rdfs:comment>\n'
            if d_item['attributes']['tclass'].strip().lower() == 'label':
                if d_item['text'].strip() != "":
                    owl_text += '\t\t<rdfs:label>' + d_item['text'].strip().replace("&", "&amp;") + ' </rdfs:label>\n'
                else:
                    owl_text += '\t\t<rdfs:label>' + path.split('/')[-1].replace("&", "&amp;") + ' ontology</rdfs:label>\n'
    else:
        owl_text += 'xml:affiliation = "' + owl_config.name + '"\n'
        owl_text += 'xmlns = "' + owl_config.xmlns + owl_config.name + '#">\n'
        owl_text += '\t<owl:Ontology rdf:about="' + owl_config.name + '">\n'
        owl_text += '\t\t<rdfs:comment>Text ontology for ' + path.split('/')[-1].replace("&", "&amp;") + '</rdfs:comment>\n'
        owl_text += '\t\t<rdfs:label>' + path.split('/')[-1].replace("&", "&amp;") + ' ontology</rdfs:label>\n'
    owl_text += '\t</owl:Ontology>\n\n'

    if "ontology" in owl_objects:
        del owl_objects["ontology"]

    try:
        owl_text += ConstantOWLPart().owl_text + '\n'
    except Exception as e:
        pass
        # print("Warning: ", e)

    for part in owl_objects:
        print("dealing with: ", part)
        if isinstance(owl_objects[part], list) or isinstance(owl_objects[part], set):
            cleaned_part = set(owl_objects[part])
            part_len = len(cleaned_part)
            div_data = list()
            new_set = list()
            for n, item in enumerate(cleaned_part):
                new_set.append(item)
                if n % int(threads_n) == 0 and n > 0:
                    div_data.append(copy.deepcopy(new_set))
                    new_set = list()
            counter = 0
            for group in div_data:
                thr_pool = list()
                for obj in group:
                    thr = Process(target=obj.serialize, name=obj.id)
                    thr_pool.append(thr)
                for thr in thr_pool:
                    # print(thr.name)
                    thr.start()
                for thr in thr_pool:
                    thr.join()
                    counter += 1
                    if part_len > 50 and counter % 10 == 0 or counter == part_len:
                        completion = counter / float(part_len)
                        print(f'Completion of the part:   {completion}', end='\r')
            print()
            owl_text += "".join([i.owl_text + '\n' for i in cleaned_part])
        elif isinstance(owl_objects[part], dict):
            cleaned_part = set([owl_objects[part][i] for i in owl_objects[part]])
            part_len = len(cleaned_part)
            for n, item in enumerate(cleaned_part):
                item.serialize()
                if part_len > 50 and n % 10 == 0 or n == part_len:
                    completion = n / float(part_len)
                    print(f'Completion of the part:   {completion}', end='\r')
            print()
            owl_text += "".join([i.owl_text + '\n' for i in cleaned_part])
        owl_text += '\n'
    owl_text += '\n'

    owl_text += '</rdf:RDF>\n'

    return owl_text


def save_owl(file_name="ontology.owl", text_owl=""):
    out_file = open(file_name, mode='w', encoding='utf-8')
    out_file.write(text_owl)
    out_file.close()



def replace_symbols_1(input_text):
    return input_text.strip().replace(" ", "_").replace('\n', "_").replace('\r', "_").replace("-", "__").replace(
            ",", "_comma_").replace(
            "`", "_apostrof_").replace("'", "_squote_").replace('"', "_dquote_").replace('.', "_dot_").replace(
            ';', "_semicolon_").replace(
            '«', "_lquote_").replace('»', "_rquote_").replace(':', "_colon_").replace('–', "_dash_").replace(
            '(', "_lbraket_").replace(')', "_rbraket_").replace('/', "_slash_").replace(':', "_colon_").replace(
            '<', "_less_").replace(
            '>', "_more_").replace('’', "_apostrof_").replace('°', "_degree_").replace('%', "_percent_").replace(
            ';', "_semicolon_").replace('—', "_dash_").replace('+', "_plus_").replace('“', "_lquote_").replace(
            '”', "_rquote_").replace('¹', "_upone_").replace('№', "_number_").replace('?', "_interrogative_").replace(
            '!', "_exclem_").replace('#', "_sharp_").replace('[', "_lsqbraket_").replace(']', "_rsqbraket_").replace(
            "&", "_and_").replace('|', "_pipe_")


def replace_symbols_2(input_text):
    return input_text.strip().replace(",", "_comma_").replace("`", "_apostrof_").replace(
                               "'", "_squote_").replace('"', "_dquote_").replace('«', "_lquote_").replace(
                               '»', "_rquote_").replace('<', "_less_").replace('>', "_more_").replace(
                               '’', "_apostrof_").replace('°', "_degree_").replace('+', "_plus_").replace(
                               '“', "_lquote_").replace('”', "_rquote_").replace('¹', "_upone_").replace(
                               '?', "_interrogative_").replace('!', "_exclem_").replace('#', "_sharp_")


def replace_digits(input_text):
    return input_text.replace("1", "_one_").replace("2", "_two_").replace("3", "_thre_").replace(
        "4", "_four_").replace("5", "_five_").replace("6", "_six_").replace("7", "_seven_").replace(
        "8", "_eight_").replace("9", "_nine_").replace("0", "_zero_")


def recover_symbols(input_text):
    return input_text.strip().replace("_comma_", ",").replace("_apostrof_", "`").replace(
        "_squote_", "'").replace("_dquote_", '"').replace("_dot_", '.').replace("_lquote_", '«').replace(
        "_rquote_", '»').replace("_colon_", ':').replace("_dash_", '–').replace("_lbraket_", '(').replace(
        "_rbraket_", ')').replace("_slash_", '/').replace(
        "_apostrof_", '’').replace("_semicolon_", ';').replace("_degree_", '°').replace("_plus_", '+').replace(
        "_upone_", '¹').replace("_number_", '№').replace("_interrogative_", '?').replace("_exclem_", '!').replace(
        "_sharp_", '#').replace(
        "__", "-").replace("_", " ").replace("_pipe_", '|').replace("_lsqbraket_", '[').replace("_rsqbraket_", ']')


def recover_digits(input_text):
    return input_text.replace("_one_", "1").replace("_two_", "2").replace("_thre_", "3").replace(
        "_four_", "4").replace("_five_", "5").replace("_six_", "6").replace("_seven_", "7").replace(
        "_eight_", "8").replace("_nine_", "9").replace("_zero_", "0")
