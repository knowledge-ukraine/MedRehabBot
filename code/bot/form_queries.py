# -*- coding: utf8 -*-

import os
import json
import copy
import traceback


class QueryFormer:

    def __init__(self, templates_file="query_templates.json"):
        self.query_templates = json.loads(open(templates_file, "r", encoding="utf-8").read())

    def make_query(self, sem_type, input_parameters):
        """
        Method to make a SPARQL query by the given template name with certain input parameters
        :param sem_type: str - name of the SPARQL query template
        :param input_parameters: list or str (depending on the query template type) corresponding to the input
        :return: SPARQL as a string and list of the names of output fields for the query
                 with the appropriate output form description
        """
        template = self.query_templates.get(sem_type)
        out_query = ""
        outputs = None
        if sem_type is not None and template is not None:
            template_parts = template.get("parts")
            outputs = template.get("outputs")
            if template_parts is not None:
                template_parts.sort(key=lambda x: x.get("n", -1))
                for part in template_parts:
                    part_type = part.get("type", "constant")
                    part_body = part.get("body", [])
                    if part_type == "constant":
                        out_query += " \n".join(part_body) + " \n"
                    elif part_type == "listed input":
                        temp_part = " \n".join(part_body) + " \n"
                        if ((isinstance(input_parameters, list) or
                                isinstance(input_parameters, set) or
                                isinstance(input_parameters, tuple)) and len(input_parameters) > 0):
                            for n, var in enumerate(input_parameters):
                                out_query += copy.deepcopy(temp_part).replace(">_order_<", str(n+1)).replace(
                                    ">_input_<", '"' + str(var) + '"')
                        elif isinstance(input_parameters, str):
                            out_query += copy.deepcopy(temp_part).replace(">_order_<", "1").replace(
                                    ">_input_<", '"' + input_parameters + '"')
                        else:
                            return "", outputs
                    elif part_type == "single input":
                        if isinstance(input_parameters, str):
                            temp_part = " \n".join(part_body) + " \n"
                            out_query += copy.deepcopy(temp_part).replace(">_input_<", '"' + input_parameters + '"')
                        elif ((isinstance(input_parameters, list) or
                                isinstance(input_parameters, set) or
                                isinstance(input_parameters, tuple)) and len(input_parameters) > 0):
                            temp_part = " \n".join(part_body) + " \n"
                            out_query += copy.deepcopy(temp_part).replace(">_input_<",
                                                                          '"' + str(input_parameters[0]) + '"')
                        else:
                            return "", outputs
        return out_query, outputs

    def form_query_set(self, intents, entities):
        """
        Method to make SPARQL queries set from a given primary semantic parse results
        :param intents: dict - semantic intents (as the query templates names) found in the input text previously
        :param entities: list - named entities found in the input text presiously
        :return: dictionary with the appropriate SPARQL queries in the following form:
                {
                    "sem_type":
                        [
                            {"query": SPARQL query text,
                            "outputs": list names of the query output fields,
                            "input": input entities as a string or list of strings}
                            ...
                        ]
                }
        """
        query_set = dict()
        if isinstance(intents, dict):
            for sem_type in intents:
                if "certain" in sem_type:
                    for point in intents[sem_type]:
                        for item in point:
                            if item != "code":
                                new_query, outputs = self.make_query(sem_type, str(item))
                                if new_query != "":
                                    if sem_type not in query_set:
                                        query_set[sem_type] = [{"query": new_query,
                                                               "outputs": outputs,
                                                               "input": str(item)}]
                                    else:
                                        query_set[sem_type].append({"query": new_query,
                                                                    "outputs": outputs,
                                                                    "input": str(item)})
                else:
                    new_query, outputs = self.make_query(sem_type, list(entities))
                    if new_query != "":
                        if sem_type not in query_set:
                            query_set[sem_type] = [{"query": new_query,
                                                   "outputs": outputs,
                                                   "input": entities}]
                        else:
                            query_set[sem_type].append({"query": new_query,
                                                        "outputs": outputs,
                                                        "input": entities})
        return query_set
