# -*- coding: utf8 -*-

import os
import json
import copy
import hashlib
import traceback

from flask import Flask
from flask import request
from flask import redirect
import psycopg2

from processor import Responder
import form_queries
import process_queries

'''
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('treebank')
nltk.download('stopwords')
'''

salt = b'\xdd\x8ed4\xd5\x8bG\xd2\xb7\x85\x06dWz\xc5\xa6\xfe-\x8f\x98\xb0k\xd94{<\x1b\xec\r-\x1e\xf1'
key = b'18Co\x18\xad\xa5\x98\x97\xd4\x04\xd4\xfe\x91\xb9\xed\xd5\xf84Y\xc1\x85\x94\xa6\xcdp0(\xa7\xb7-\x9a'

app = Flask(__name__)
resp_obj = Responder()


@app.route("/", methods=['GET', 'POST'])
def ping_test():
    return "API service for the Rehabilitation Knowledge Base is working"


@app.route("/medrehabbot/api/v1/ask/", methods=['GET', 'POST'])
def process():
    global key, resp_obj
    if request.method == 'POST':
        input_data = request.json
        print(input_data)
        new_key = hashlib.pbkdf2_hmac('sha256', input_data.get("password", "").encode('utf-8'), salt, 100000)
        print(new_key)
        if new_key == key:
            if isinstance(input_data.get("text"), str):
                try:
                    response = resp_obj.get_response(input_data.get("text").strip())
                    return json.dumps(response, ensure_ascii=False)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    message = {
                        "error": str(e),
                        "message": "an error occurred during the message handling"
                    }
                    return json.dumps(message, ensure_ascii=False)

            elif (isinstance(input_data.get("parameters"), list) and isinstance(input_data.get("query_type"), str) and
                  len(input_data.get("parameters")) > 0 and len(input_data.get("query_type").strip()) > 0):
                try:
                    saved_resp = query_from_db(input_data.get("query_type").strip(), input_data.get("parameters"))
                    if saved_resp is not None:
                        return json.dumps(saved_resp, ensure_ascii=False)
                    if "certain" in input_data.get("query_type") and len(input_data.get("parameters")) > 1:
                        qs = dict()
                        for parameter in input_data.get("parameters"):
                            new_query, outputs = resp_obj.qf.make_query(input_data.get("query_type"),
                                                                        parameter)
                            if input_data.get("query_type") not in qs:
                                qs[input_data.get("query_type")] = [{"query": new_query,
                                                                     "outputs": outputs,
                                                                     "input": parameter}]
                            else:
                                qs[input_data.get("query_type")].append({"query": new_query,
                                                                         "outputs": outputs,
                                                                         "input": parameter})
                    else:
                        new_query, outputs = resp_obj.qf.make_query(input_data.get("query_type"),
                                                                    input_data.get("parameters"))
                        qs = {input_data.get("query_type"): [{"query": new_query,
                                                              "outputs": outputs,
                                                              "input": input_data.get("parameters")}]}
                    try:
                        resp = resp_obj.query_exec.process_query_set(qs)
                        save_result_in_db(resp, input_data.get("query_type").strip(), input_data.get("parameters"))
                        return json.dumps(resp, ensure_ascii=False)
                    except Exception as e:
                        print(e)
                        print(traceback.format_exc())
                        message = {
                            "error": str(e),
                            "message": "an error occurred during the message handling"
                        }
                        return json.dumps(message, ensure_ascii=False)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    message = {
                        "error": str(e),
                        "message": "an error occurred during the message handling"
                    }
                    return json.dumps(message, ensure_ascii=False)
            else:
                return json.dumps({}, ensure_ascii=False)
        else:
            message = {
                "error": "wrong password",
                "message": "access denied"
            }
            return json.dumps(message, ensure_ascii=False)
    else:
        return "API service for the Rehabilitation Knowledge Base is working"


def query_from_db(query_type, parameters):
    conn = psycopg2.connect(dbname='rehab_technical', user='insamhlaithe',
                            password='rt27pq12mrs', host='192.168.133.3')
    cursor = conn.cursor()
    try:
        present_words_dump = json.dumps(sorted(list(copy.deepcopy(parameters))))
        select_query = "SELECT DISTINCT results FROM query_results WHERE sem_type = '" + str(query_type) + \
                       "' AND parameters = '" + present_words_dump + "';"
        cursor.execute(select_query)
        saved_result = cursor.fetchone()
        if saved_result is not None and len(saved_result) > 0:
            try:
                cursor.close()
                conn.close()
                return json.loads(saved_result[0])
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()
    return None


def save_result_in_db(resp, query_type, parameters):
    conn = psycopg2.connect(dbname='rehab_technical', user='insamhlaithe',
                            password='rt27pq12mrs', host='192.168.133.3')
    cursor = conn.cursor()
    if len(resp) > 0:
        try:
            present_words_dump = json.dumps(sorted(list(copy.deepcopy(parameters))))
            resp_dump = json.dumps(resp, sort_keys=True)
            record_query = "INSERT INTO query_results (sem_type, parameters, results) VALUES('" + \
                           str(query_type) + "', '" + present_words_dump + "', '" + resp_dump + \
                           "') ON CONFLICT DO NOTHING;"
            cursor.execute(record_query)
            conn.commit()
        except Exception as e:
            print(e)
    cursor.close()
    conn.close()


if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8100)))
