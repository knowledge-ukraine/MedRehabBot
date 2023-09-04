# -*- coding: utf8 -*-

import os
import json
import copy
from multiprocessing import Process
import time

from PyPDF2 import PdfReader
from tools.parser import parse_file


def load_settings(structure_file="structure.json", synonyms_keys_file="synonyms.json"):
    return json.load(open(structure_file, "r")), json.load(open(synonyms_keys_file, "r"))


def load_input_file(file_name=""):
    reader = PdfReader(file_name)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " \n \n"
    return text


def save_result(output, file_mane="", ensure_ascii=False):
    f = open(file_mane, 'w', encoding='utf8')
    f.write(json.dumps(output, ensure_ascii=ensure_ascii, indent=4))
    f.close()


def form_set_of_files(input_dir, threads_n):
    content = os.listdir(input_dir)
    input_data_set = list()
    new_set = list()
    for n, f in enumerate([i for i in content if i.split(".")[-1].lower().strip() == "pdf"]):
        new_set.append(f)
        if n % int(threads_n) == 0 and n > 0:
            input_data_set.append(copy.deepcopy(new_set))
            new_set = list()
    if len(new_set) > 0:
        input_data_set.append(copy.deepcopy(new_set))
    return input_data_set


def execute_file_parsing(input_file_name, out_dir, structure, synonyms_keys, add_text_list=False, ensure_ascii=False):
    file = load_input_file(file_name=input_file_name)
    output = parse_file(file, structure, synonyms_keys, add_text_list=add_text_list)
    out_name = ".".join(input_file_name.split("/")[-1].split(".")[:-1]) + ".json"
    save_result(output, out_dir + "/" + out_name, ensure_ascii)


def execute_package_parsing(input_dir, out_dir, threads_n=1, add_text_list=False, ensure_ascii=False):
    structure, synonyms_keys = load_settings()
    input_data = form_set_of_files(input_dir, threads_n)
    for file_set in input_data:
        thr_pool = list()
        for file_name in file_set:
            thr = Process(target=execute_file_parsing, name=".".join(file_name.split(".")[:-1]),
                          args=[input_dir + "/" + file_name, out_dir, structure, synonyms_keys],
                          kwargs={"add_text_list": add_text_list, "ensure_ascii": ensure_ascii})
            thr_pool.append(thr)
        # print("Parsing files")
        for thr in thr_pool:
            # print(thr.name)
            thr.start()
        for thr in thr_pool:
            thr.join()


if __name__ == "__main__":
    settings = json.load(open("settings.json", "r"))
    t_0 = time.time()
    execute_package_parsing(settings["input_files_dir"], settings["output_dir"], threads_n=settings["threads_n"],
                            add_text_list=settings.get("add_text_list", False),
                            ensure_ascii=settings.get("ensure_ascii", False))
    print("Parsing total time: ", time.time() - t_0)
