# -*- coding: utf8 -*-

import json
import copy
import nltk

'''
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('treebank')
nltk.download('stopwords')
'''

from nltk.tokenize import sent_tokenize


def find_key(row_as_list, key_as_list, key, synonyms_keys, limit_score, synonyms):
    score = 0
    if len(row_as_list) > 0:
        for w in row_as_list:
            if w in key_as_list:
                score += 1
            elif synonyms is not None:
                synonyms_as_list = [[j for j in i.split()] for i in synonyms_keys.get(key)]
                for syn in synonyms_as_list:
                    if w in syn:
                        score += 1
                        break
        score = float(score) / (len(row_as_list))
    if score > limit_score and len(row_as_list) >= len(key_as_list):
        return key, True
    return key, False


def get_sent_list(text_struct, sentences):
    for key in text_struct:
        if key != "references":
            sentences += [s.capitalize() for s in sent_tokenize(str(key))]
            if isinstance(text_struct.get(key), dict):
                get_sent_list(text_struct.get(key), sentences)
            elif isinstance(text_struct.get(key), list):
                for item in text_struct[key]:
                    if isinstance(item, str):
                        sentences += [s for s in sent_tokenize(item) if len(s.strip()) > 3]
            elif isinstance(text_struct[key], str):
                sentences += [s for s in sent_tokenize(text_struct.get(key)) if len(s.strip()) > 3]


def parse_file(text, structure, synonyms_keys, add_text_list=False):
    text_list = text.split("\n")
    output = copy.deepcopy(structure)
    for key in structure:
        key_as_list = [i.lower() for i in key.split()]
        if key == "metadata":
            meta_key_fit = False
            new_code = ""
            new_code_set = ""
            new_sub_code = ""
            for key_m in structure["metadata"]:
                key_as_list = [i.lower() for i in key_m.split()]
                synonyms = synonyms_keys.get(key_m)
                for row in text_list:
                    if meta_key_fit and "›" in row:
                        meta_key_fit = False
                    row_as_list = [i.lower() for i in row.replace("/", " ").replace("›", "").replace("•", "").replace(
                        "–", "").replace("(", " ").replace(")", " ").split(":")[0].split()]
                    c_key, key_f = find_key(row_as_list, key_as_list, key_m, synonyms_keys, 0.7, synonyms)
                    if key_f and not meta_key_fit:
                        meta_key_fit = True
                        new_row = " ".join(row.split(":")[1:]).replace("›", "").replace("•", "")
                        if len(new_row.strip()) > 0:
                            if isinstance(output["metadata"][key_m], str):
                                output["metadata"][key_m] += new_row.strip()
                            elif isinstance(output["metadata"][key_m], list):
                                if key_m == "synonyms" or key_m == "area of specialty":
                                    if ";" in new_row:
                                        output["metadata"][key_m] += [i.lower().strip() for i in
                                                                      new_row.strip().split(";")]
                                    else:
                                        output["metadata"][key_m] += [i.lower().strip() for i in
                                                                      new_row.strip().split(",")]
                                else:
                                    output["metadata"][key_m].append(new_row.strip())
                            elif isinstance(output["metadata"][key_m], dict):
                                if "cpt" in key_m.lower() or "hcpcs" in key_m.lower():
                                    if ":" in row:
                                        output["metadata"][key_m]["code"] = row.split(":")[1].split("–")[0].strip(

                                        ).strip(",")
                                        if len(row.split(":", 1)) > 1 and len(row.split(":", 1)[1].split("–", 1)) > 1:
                                            output["metadata"][key_m]["description"] = row.split(":", 1)[1].split(
                                                "–", 1)[1].strip()
                                        else:
                                            output["metadata"][key_m]["description"] = ""
                    elif meta_key_fit:
                        if isinstance(output["metadata"][key_m], str):
                            output["metadata"][key_m] += " " + row
                        elif isinstance(output["metadata"][key_m], list):
                            if "•" in row:
                                if key_m == "synonyms" or key_m == "area of specialty":
                                    if ";" in row:
                                        output["metadata"][key_m] += [i.lower().strip() for i in
                                                                      row.replace("›", "").replace(
                                                                          "•", "").strip().split(";")]
                                    else:
                                        if row.strip().split(",")[0].lower().strip() != "":
                                            output["metadata"][key_m] += [i.lower().strip() for i in
                                                                          row.replace("›", "").replace(
                                                                              "•", "").strip().split(",")]
                                else:
                                    output["metadata"][key_m].append(row.replace("›", "").replace("•", "").strip())
                            else:
                                if key_m == "synonyms" or key_m == "area of specialty":
                                    if ";" in row:
                                        if row.strip().split(",")[0].lower().strip() != "" and len(output["metadata"][key_m]) > 0:
                                            output["metadata"][key_m][-1] += " " +\
                                                                             row.strip().split(";")[0].lower().strip()
                                        output["metadata"][key_m] += [i.lower().strip() for i in
                                                                      row.strip().split(";")[1:]]
                                    else:
                                        if row.strip().split(",")[0].lower().strip() != "" and len(output["metadata"][key_m]) > 0:
                                            output["metadata"][key_m][-1] += " " +\
                                                                             row.strip().split(",")[0].lower().strip()
                                        output["metadata"][key_m] += [i.lower().strip() for i in
                                                                      row.strip().split(",")[1:]]
                                elif len(output["metadata"][key_m]) > 0:
                                    output["metadata"][key_m][-1] += " " + row.strip()
                                else:
                                    output["metadata"][key_m].append(row.strip())
                        elif isinstance(output["metadata"][key_m], dict):
                            if "icd" in key_m.lower():
                                if "•" in row:
                                    new_code = row.split()[0].replace("›", "").replace("•", "").strip()
                                    if len(new_code) > 0:
                                        output["metadata"][key_m][new_code] = " ".join(row.split()[1:]).strip()
                                elif "–" in row:
                                    new_sub_code = row.split()[0].replace("–", "").replace("•", "").strip().strip("-")
                                    if len(new_sub_code) > 0 and key_m != "" and new_code != "":
                                        if isinstance(output["metadata"][key_m][new_code], str):
                                            output["metadata"][key_m][new_code] = {
                                                "base": output["metadata"][key_m][new_code],
                                                new_sub_code: " ".join(row.split()[1:]).strip().strip("-")
                                            }
                                        elif new_code in output["metadata"][key_m] and\
                                                new_sub_code in output["metadata"][key_m][new_code]:
                                            output["metadata"][key_m][new_code][new_sub_code] =\
                                                " ".join(row.split()[1:]).strip().strip("-")
                                        elif new_code in output["metadata"][key_m]:
                                            output["metadata"][key_m][new_code][new_sub_code] = " ".join(
                                                row.split()[1:]).strip().strip("-")
                                elif len(new_code) > 0 and "Note:" not in row and len(row.strip()) > 0:
                                    if new_code in output["metadata"][key_m] and\
                                            isinstance(output["metadata"][key_m][new_code], str):
                                        output["metadata"][key_m][new_code] += " " + row.strip()
                                    elif new_code in output["metadata"][key_m] and\
                                            isinstance(output["metadata"][key_m][new_code], dict):
                                        new_sub_code = row.split()[0].replace("–", "").replace(
                                            "•", "").strip().strip("-")
                                        if new_sub_code in output["metadata"][key_m][new_code]:
                                            output["metadata"][key_m][new_code][new_sub_code] +=\
                                                " " + row.strip().strip("-")
                                        else:
                                            output["metadata"][key_m][new_code][new_sub_code] = \
                                                " " + row.strip().strip("-")
                            elif "g-codes" in key_m.lower() and key_m != "":
                                if "•" in row:
                                    new_code_set = " ".join([i.strip() for i in
                                                             row.replace("›", "").replace("•", "").split()
                                                             if len(i.strip()) > 0])
                                    if len(new_code_set) > 0:
                                        output["metadata"][key_m][new_code_set] = dict()
                                if "–" in row and len(new_code_set) > 0:
                                    new_code = row.split(",")[0].replace("›", "").replace("•", "").replace(
                                        "–", "").strip().strip(".").strip()
                                    if len(new_code) > 0:
                                        output["metadata"][key_m][new_code_set][new_code] = ",".join(
                                            row.split(",")[1:]).strip().strip(".").strip()
                                elif len(new_code_set) > 0 and "G-code" not in row and new_code in output["metadata"][key_m][new_code_set] and\
                                        len(row.strip().strip(".").strip()) > 0:
                                    output["metadata"][key_m][new_code_set][new_code] += " " + row.strip(".").strip()
                                elif len(new_code_set) > 0 and len(new_code) > 0 and "G-code" in row and\
                                        new_code in output["metadata"][key_m][new_code_set] and len(row.strip()) > 0:
                                    new_code = ""
                            elif ("cpt" in key_m.lower() or "hcpcs" in key_m.lower()) and\
                                    "description" in output["metadata"][key_m]:
                                output["metadata"][key_m]["description"] += " " + row.strip()
                            elif "cpt" in key_m.lower() or "hcpcs" in key_m.lower():
                                if "•" in row:
                                    new_code = row.split()[0].replace("›", "").replace("•", "").strip().strip(",")
                                    if len(new_code) > 0:
                                        output["metadata"][key_m][new_code] = " ".join(row.split()[1:]).strip()
                                elif new_code in output["metadata"][key_m] and \
                                        isinstance(output["metadata"][key_m][new_code], str):
                                    output["metadata"][key_m][new_code] += " " + row.strip()

        else:
            current_key = ""
            current_key_m = ""
            current_key_m_2 = ""
            current_key_m_3 = ""
            current_key_m_4 = ""
            key_found = False
            is_other_point = False
            synonyms = synonyms_keys.get(key)
            new_point = False
            for row in text_list:
                row_as_list = [i.lower() for i in row.replace(",", "").replace(".", "").replace("/", " ").replace(
                    "(", " ").replace(")", " ").split()]
                c_key, key_f = find_key(row_as_list, key_as_list, key, synonyms_keys, 0.87, synonyms)
                if key_f:
                    current_key = c_key
                    key_found = key_f
                    continue
                # Проверка на остановку при обнаружении следующего ключа верхнего уровня
                if key_found:
                    new_key = False
                    for key_ctrl in structure:
                        key_ctrl_as_list = [i.lower() for i in key_ctrl.split()]
                        score = 0
                        if len(row_as_list) > 0:
                            for w in row_as_list:
                                if w in key_ctrl_as_list:
                                    score += 1
                                elif synonyms is not None:
                                    synonyms_as_list = [[j for j in i.split()] for i in synonyms_keys.get(key)]
                                    for syn in synonyms_as_list:
                                        if w in syn:
                                            score += 1
                                            break
                            score = float(score) / (len(row_as_list))
                        if score > 0.87 and "›" not in row and "•" not in row:
                            new_key = True
                            break
                    if new_key:  # Останоситься ели дошли до нового ключа
                        break

                # В сторке обнаружен искомый ключ
                if current_key != "" and current_key in output and isinstance(output[current_key], list):
                    # Если надо собрать список
                    if "›" in row:  # Новый пункт - новый элемент списка
                        output[current_key].append(row.replace("›", "").replace("•", "").strip())
                    elif current_key == "references":  # Списки литературы имеют особый формат
                        if len(row.split(".", 1)) > 0 and row.split(".", 1)[0].strip().isdigit():
                            output[current_key].append({
                                "number in article": int(row.split(".", 1)[0].strip()),
                                "reference": row.split(".", 1)[1]})
                        elif len(row_as_list) > 0 and len(output[current_key]) > 0 and\
                                isinstance(output[current_key], list) and isinstance(output[current_key][-1], dict) and\
                                "reference" in output[current_key][-1]:
                            output[current_key][-1]["reference"] += " " + row.strip()
                    elif len(output[current_key]) > 0:  # Иначе - "дорастить" последний элемент списка
                        output[current_key][-1] += " " + row.replace("›", "").replace("•", "").strip()
                elif current_key != "" and current_key in output and isinstance(output[current_key], dict):
                    if len(structure[current_key]) == 0:
                        # Если структура словаря не заданна, то имеющиеся пункты становятся ключами
                        if "›" in row:  # Новый пункт - новый элемент списка
                            current_key_m = row.replace("/", " ").replace("›", "").replace("•", "").replace(
                                "–", "").replace("(", " ").replace(")", " ").replace("0", "").replace("1", "").replace(
                                "2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace(
                                "7", "").replace("8", "").replace("9", "").strip().lower()
                            output[current_key][current_key_m] = list()
                            new_point = False
                        elif "•" in row and current_key_m != "" and current_key_m in output[current_key]:
                            output[current_key][current_key_m].append(row.replace("•", "").strip())
                            new_point = True
                        elif new_point and current_key_m != "" and current_key_m in output[current_key] and\
                                len(output[current_key][current_key_m]) > 0:
                            output[current_key][current_key_m][-1] += row.strip()
                        elif new_point and current_key_m != "" and current_key_m in output[current_key]:
                            output[current_key][current_key_m].append(row.strip())
                        elif current_key_m != "" and current_key_m in output[current_key]:
                            new_current_key_m = current_key_m + " " + row.replace("/", " ").replace("›", "").replace(
                                "•", "").replace("–", "").replace("(", " ").replace(")", " ").replace("0", "").replace(
                                "1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace(
                                "6", "").replace("7", "").replace("8", "").replace("9", "").strip().lower()
                            output[current_key][new_current_key_m] = copy.deepcopy(output[current_key][current_key_m])
                            del output[current_key][current_key_m]
                            new_point = False
                    else:
                        # Если словарь с заданной структурой, то слдует рассмотреть его ключи
                        row_as_list_m = [i.lower() for i in row.replace("/", " ").replace("›", "").replace(
                            "•", "").replace("–", "").replace("(", " ").replace(")", " ").replace("0", "").replace(
                            "1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace(
                            "6", "").replace("7", "").replace("8", "").replace("9", "").split(":")[0].split()]
                        for key_m in structure[current_key]:
                            key_m_as_list = [i.lower() for i in key_m.split()]
                            synonyms_key = synonyms_keys.get(key_m)
                            score = 0
                            if len(row_as_list_m) > 0:
                                for w in row_as_list_m:
                                    if w in key_m_as_list:
                                        score += 1
                                    elif synonyms_key is not None:
                                        synonyms_as_list = [[j for j in i.split()] for i in
                                                            synonyms_keys.get(key_m)]
                                        for syn in synonyms_as_list:
                                            if w in syn:
                                                score += 1
                                                break
                                score = float(score) / (len(row_as_list_m))
                            if score > 0.8:
                                current_key_m = key_m
                                break
                        if current_key_m != "":  # Если строка с ключём обнаружена
                            if isinstance(output[current_key][current_key_m], str):
                                if "•" in row or "›" in row:
                                    if ":" in row:
                                        output[current_key][current_key_m] += row.split(":")[1].strip()
                                    else:
                                        output[current_key][current_key_m] += " " + row.replace("•", "").replace(
                                            "›", "").strip()
                                else:
                                    output[current_key][current_key_m] += " " + row.replace("•", "").replace(
                                        "›", "").strip()
                            if isinstance(output[current_key][current_key_m], list):
                                if "•" in row and "›" not in row:
                                    output[current_key][current_key_m].append(row.replace("•", "").strip())
                                elif len(output[current_key][current_key_m]) > 0:
                                    output[current_key][current_key_m][-1] += " " + row.replace("•", "").strip()
                            elif isinstance(output[current_key][current_key_m], dict):
                                if len(row.split(":")) > 1 and "›" in row:
                                    output[current_key][current_key_m]["general"] = row.split(":", 1)[1].strip()
                                # Следующий уровень вложенности
                                row_as_list_m_2 = [i.lower() for i in
                                                   row.replace("/", " ").replace("›", "").replace("•", "").replace(
                                                     "–", "").replace("(", " ").replace(")", " ").split(":")[0].split()]

                                for key_m_2 in structure[current_key][current_key_m]:
                                    key_m_2_as_list = [i.lower() for i in key_m_2.split()]
                                    synonyms_key_m_2 = synonyms_keys.get(key_m_2)
                                    score = 0
                                    if len(row_as_list_m_2) > 0:
                                        for w in row_as_list_m_2:
                                            if w in key_m_2_as_list:
                                                score += 1
                                            elif synonyms_key_m_2 is not None:
                                                synonyms_as_list = [[j for j in i.split()] for i in
                                                                    synonyms_keys.get(key_m_2)]
                                                for syn in synonyms_as_list:
                                                    if w in syn:
                                                        score += 1
                                                        break
                                        score = float(score) / (len(row_as_list_m_2))
                                    if score > 0.8:
                                        current_key_m_2 = key_m_2
                                        break
                                if current_key_m_2 != "" and current_key_m_2 in output[current_key][current_key_m]:
                                    if isinstance(output[current_key][current_key_m][current_key_m_2], str):
                                        if ":" in row:
                                            output[current_key][current_key_m][current_key_m_2] += row.replace(
                                                "•", "").replace("›", "").split(":")[1].strip()
                                        else:
                                            output[current_key][current_key_m][current_key_m_2] += \
                                                " " + row.replace("•", "").replace("›", "").strip()
                                    elif isinstance(output[current_key][current_key_m][current_key_m_2], list):
                                        if "–" in row:
                                            output[current_key][current_key_m][current_key_m_2].append(
                                                row.replace("•", "").replace("–", "").strip())
                                            is_other_point = False
                                        elif "•" in row and "other" in output[current_key][current_key_m]:
                                            if "other" in output[current_key][current_key_m]:
                                                output[current_key][current_key_m]["other"].append(
                                                    row.replace("•", "").replace("–", "").strip())
                                            else:
                                                output[current_key][current_key_m]["other"] = [
                                                    row.replace("•", "").replace("–", "").strip()]
                                            is_other_point = True
                                        else:
                                            if is_other_point and "other" in output[current_key][current_key_m]:
                                                output[current_key][current_key_m]["other"][-1] += " " + row.strip()
                                            elif (not is_other_point and
                                                  len(output[current_key][current_key_m][current_key_m_2]) > 0):
                                                output[current_key][current_key_m][current_key_m_2][-1] += " " \
                                                                                                           + row.strip()
                                    elif isinstance(output[current_key][current_key_m][current_key_m_2], dict):
                                        # Следующий уровень вложенности
                                        row_as_list_m_3 = [i.lower() for i in
                                                           row.replace("/", " ").replace("–", "").replace(
                                                               "•", "").replace("–", "").replace("(", " ").replace(
                                                               ")", " ").split(":")[0].split()]
                                        for key_m_3 in structure[current_key][current_key_m][current_key_m_2]:
                                            key_m_3_as_list = [i.lower() for i in key_m_3.split()]
                                            synonyms_key_m_3 = synonyms_keys.get(key_m_3)
                                            score = 0
                                            if len(row_as_list_m_3) > 0:
                                                for w in row_as_list_m_3:
                                                    if w in key_m_3_as_list:
                                                        score += 1
                                                    elif synonyms_key_m_3 is not None:
                                                        synonyms_as_list = [[j for j in i.split()] for i in
                                                                            synonyms_keys.get(key_m_3)]
                                                        for syn in synonyms_as_list:
                                                            if w in syn:
                                                                score += 1
                                                                break
                                                score = float(score) / (len(row_as_list_m_3))
                                            if score > 0.8:
                                                current_key_m_3 = key_m_3
                                                break
                                        if current_key_m_3 != "" and current_key_m_3 in output[current_key][
                                                current_key_m][current_key_m_2]:
                                            if isinstance(output[current_key][current_key_m][current_key_m_2][
                                                              current_key_m_3], str):
                                                if ":" in row:
                                                    output[current_key][current_key_m][current_key_m_2][
                                                        current_key_m_3] += row.replace("•", "").replace(
                                                        "›", "").replace("–", "").split(":")[1].strip()
                                                else:
                                                    output[current_key][current_key_m][current_key_m_2][
                                                        current_key_m_3] += " " + row.replace("•", "").replace(
                                                        "›", "").replace("–", "").strip()
                                            elif isinstance(output[current_key][current_key_m][current_key_m_2][
                                                                current_key_m_3], dict):
                                                # Самый глубокий уровень вложенности
                                                row_as_list_m_4 = [i.lower() for i in
                                                                   row.replace("/", " ").replace("-", "").replace(
                                                                       "•", "").replace("–", "").replace(
                                                                       "(", " ").replace(")", " ").split(":")[
                                                                       0].split()]
                                                for key_m_4 in structure[current_key][current_key_m][current_key_m_2][
                                                        current_key_m_3]:
                                                    key_m_4_as_list = [i.lower() for i in key_m_4.split()]
                                                    synonyms_key_m_4 = synonyms_keys.get(key_m_4)
                                                    score = 0
                                                    if len(row_as_list_m_4) > 0:
                                                        for w in row_as_list_m_4:
                                                            if w in key_m_4_as_list:
                                                                score += 1
                                                            elif synonyms_key_m_4 is not None:
                                                                synonyms_as_list = [[j for j in i.split()] for i in
                                                                                    synonyms_keys.get(key_m_4)]
                                                                for syn in synonyms_as_list:
                                                                    if w in syn:
                                                                        score += 1
                                                                        break
                                                        score = float(score) / (len(row_as_list_m_3))
                                                    if score > 0.8:
                                                        current_key_m_4 = key_m_4
                                                        break
                                                if current_key_m_4 != "" and current_key_m_4 in output[current_key][
                                                        current_key_m][current_key_m_2][current_key_m_3]:
                                                    if isinstance(output[current_key][current_key_m][current_key_m_2][
                                                                      current_key_m_3][current_key_m_4], str):
                                                        if ":" in row:
                                                            output[current_key][current_key_m][current_key_m_2][
                                                                current_key_m_3][current_key_m_4] += row.replace(
                                                                "•", "").replace("-", "", 1).replace(
                                                                "–", "").split(":")[1].strip()
                                                        else:
                                                            output[current_key][current_key_m][current_key_m_2][
                                                                current_key_m_3][current_key_m_4] += " " + \
                                                                                    row.replace(
                                                                                        "•", "").replace(
                                                                                        "-", "", 1).replace(
                                                                                        "–", "").strip()
                                                    elif isinstance(output[current_key][current_key_m][current_key_m_2][
                                                                      current_key_m_3][current_key_m_4], list):
                                                        if "-" in row:
                                                            output[current_key][current_key_m][current_key_m_2][
                                                                      current_key_m_3][current_key_m_4].append(
                                                                row.replace("-", "", 1).replace("–", "", 1).strip())
                                                        elif len(output[current_key][current_key_m][current_key_m_2][
                                                                      current_key_m_3][current_key_m_4]) > 0:
                                                            output[current_key][current_key_m][current_key_m_2][
                                                                  current_key_m_3][current_key_m_4][-1] +=\
                                                                " " + row.strip()
                                elif "general" in output[current_key][current_key_m]:
                                    output[current_key][current_key_m]["general"] += " " + row.strip()
    if add_text_list:
        # sentences = list()
        # get_sent_list(output, sentences)
        output["sentences"] = [s.strip() for s in text_list if len(s.strip()) > 1]
    return output
