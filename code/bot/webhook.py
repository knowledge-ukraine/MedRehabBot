# -*- coding: utf8 -*-

import os
import json
import copy
import time
import traceback
import signal
import multiprocessing
import threading
from random import shuffle

import telebot

from processor import Responder

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

articles_dir = "https://cdn.e-rehab.pp.ua/u/"


bot_token = '6636808315:AAGT97GtpiwuHKhCaQ54G4lIfvHSK8wJCSw'

bot = telebot.TeleBot(bot_token)
is_connected = False
current_cookies = None
is_running = True
resp_obj = Responder()
verbose_sem_types = None

current_resp_count = dict()

responding_pool = dict()


def respond(message, verbose_sem, articles_path, resp_count):
    global current_cookies, is_connected, articles_dir, current_resp_count

    def unfold_response(structure, out):
        if structure is not None:
            for field in structure:
                if field not in ["value", "verbose", "rel", "rel_field"] and isinstance(structure[field], list):
                    for item in structure[field]:
                        if "value" in item:
                            current_message = item["value"].strip()
                            if field == "article_name":
                                current_message = '<i><a href="' + \
                                                  articles_path + current_message.replace(' ', '%20') + \
                                                  '.pdf' + '">' + current_message + '</a></i>\n'
                            if field in ["chapter", "topic", "scope", "set", "code_type"]:
                                current_message = '<i><b>' + current_message + '</b></i>\n'
                            if len(current_message) > 0:
                                if "verbose" in item and len(item["verbose"]) > 0:
                                    current_message = "<b>" + item["verbose"] + "</b> " + current_message
                                    if len(item["verbose"]) > 3:
                                        current_message = "\n" + current_message
                                    out['out'] += current_message
                                else:
                                    out['out'] += current_message
                                if len(out['out']) > 0 and out['out'][-1] != "\n":
                                    out['out'] += "\n"
                            unfold_response(item, out)
                        if "values" in item:
                            if "verbose" in item and len(str(item["verbose"]).strip()) > 0:
                                out['out'] += "<b>" + item["verbose"] + "</b> \n"
                            items_counter = 0
                            if isinstance(item["values"], dict):
                                for key in item["values"]:
                                    if len(item["values"][key]) > 0:
                                        out['out'] += "<i>" + key + ':' + "</i>\n "
                                        unfold_response(item["values"][key], out)
                                    else:
                                        if field == "article_name":
                                            current_message = '<i><a href="' + articles_path + \
                                                              key.replace(' ', '%20') + '.pdf' + '">' + key +\
                                                              '</a></i>\n'
                                            out['out'] += current_message
                                            items_counter += 1
                                        else:
                                            out['out'] += key + "\n"
                                            items_counter += 1
                                    if items_counter >= 3:
                                        out['out'] += "And others. \n"
                                        break
                            if isinstance(item["values"], list):
                                current_message = ""
                                shuffle(item["values"])
                                for name in item["values"]:
                                    if field == "article_name":
                                        current_message += '<i><a href="' + articles_path + name.replace(' ', '%20') +\
                                                           '.pdf' + '">' + name + '</a></i>\n '
                                    else:
                                        current_message += name + "\n"
                                    items_counter += 1
                                    if items_counter >= 3:
                                        current_message += " And others.\n"
                                        break
                                out['out'] += current_message + "\n"

    if len(message.text.strip().split()) > 30:
        bot.reply_to(message, "Your massage is too long. Try to use less than 30 words in your query.")
    elif len(message.text.strip()) > 0:
        response = resp_obj.get_response(message.text.strip())
        if isinstance(response, dict) and len(response) > 0:
            for sem_type in response:
                for block in response[sem_type]:
                    response_structure = block.get("response")
                    input_entities = block.get("input")
                    if len(response_structure) == 0 and len(input_entities) > 0:
                        verbose_sem_type = "Sorry, but I don't know about "
                        verbose_sem_type += verbose_sem.get(sem_type, "").lower()
                        if isinstance(input_entities, str):
                            verbose_sem_type += " " + input_entities + ". "
                        elif isinstance(input_entities, list):
                            verbose_sem_type += " " + " ".join(input_entities) + ". "
                        bot.reply_to(message, verbose_sem_type)
                    elif len(response_structure) == 0 and len(input_entities) == 0:
                        bot.reply_to(message, "Unfortunately, I don't have any relevant information on this question.")
                    else:
                        verbose_sem_type = verbose_sem.get(sem_type, "")
                        if isinstance(input_entities, str):
                            verbose_sem_type += " " + input_entities + ": "
                        elif isinstance(input_entities, list):
                            verbose_sem_type += " " + " ".join(input_entities) + ": "
                        bot.reply_to(message, verbose_sem_type)
                        if response_structure is not None:
                            str_for_out = {"out": ""}
                            unfold_response(response_structure, str_for_out)
                            if len(str_for_out["out"].strip()) > 0:
                                send_message(message, str_for_out["out"])
                                if block.get("too_long"):
                                    send_message(message,
                                                 "Your question is quite spacious. Try to specify if it is possible.")
                            else:
                                send_message(message, "No answer, nothing to display.")
        else:
            bot.reply_to(message, "Sorry, but I haven't understood your message.")
            send_message(message, "It was either not in English or far from the scope.")
            send_message(message, "The scope of the bot is Rehabilitation Medicine and it can understand English only.")

        resp_count[message.from_user.id] = 0


def get_verbose_sem_types(file="query_templates.json"):
    out = dict()
    templates = json.loads(open(file, "r", encoding="utf-8").read())
    for sem_type in templates:
        out[sem_type] = templates[sem_type].get("verbose")
    return out


def make_keyboard(string_list):
    markup = telebot.types.InlineKeyboardMarkup()
    try:
        for key, value in string_list.items():
            markup.add(telebot.types.InlineKeyboardButton(text=key,
                                                          callback_data=key))
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())
    return markup


def service_shutdown(signum, frame):
    global is_running, clean_thr
    print(frame)
    is_running = False
    for id in responding_pool:
        for job in responding_pool[id]:
            job.terminate()
    clean_thr.stop()
    print('Caught signal %d' % signum)
    raise ServerExit


class ServerExit(Exception):
    pass


def connect():
    global bot, is_connected, resp_obj, verbose_sem_types
    if bot is None:
        bot = telebot.TeleBot(bot_token)
    if bot is not None:
        is_connected = True
        verbose_sem_types = get_verbose_sem_types()
    else:
        is_connected = False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(chat_id=message.chat.id,
                         text="<b>This is a reference system for Rehabilitation Medicine.</b>",
                         parse_mode='HTML')
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())
        bot.send_message(chat_id=call.message.chat.id,
                         text="Sorry, but an error occurred...")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global current_cookies, is_connected, articles_dir, current_resp_count, responding_pool, resp_obj
    try:
        if (message.text.strip().lower() in ["halt", 'enough', "stop"]
                and responding_pool.get(message.from_user.id) is not None
                and len(responding_pool.get(message.from_user.id)) > 0):
            for job in responding_pool.get(message.from_user.id):
                job.terminate()
            del responding_pool[message.from_user.id]
        elif len(message.text.strip()) > 0:
            job = multiprocessing.Process(target=respond, args=[message, verbose_sem_types, articles_dir,
                                                                current_resp_count],
                                          name=message.text.strip(), daemon=True)
            if message.from_user.id not in responding_pool:
                responding_pool[message.from_user.id] = [job]
            else:
                responding_pool[message.from_user.id].append(job)
            job.start()
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text="Sorry, but an error occurred...")


def make_send_message(message, text):
    try:
        bot.send_message(message.from_user.id, str(text), parse_mode='HTML')
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        try:
            bot.send_message(message.from_user.id, str(text))
        except Exception as e:
            print(e)
            print(traceback.format_exc())


def make_pause_for_long_inference(message):
    global current_resp_count
    if message.from_user.id not in current_resp_count:
        current_resp_count[message.from_user.id] = 1
    else:
        current_resp_count[message.from_user.id] += 1
    if current_resp_count[message.from_user.id] > 50:
        bot.send_message(message.from_user.id, "Too much information to provide, please wait for about 15 seconds...")
        t = "<i>...or, if you would like to stop the inference, press the button</i> <b>\"STOP\"</b> <i>below.</i>"
        bot.send_message(message.from_user.id,
                         text={t},
                         reply_markup=make_keyboard({"STOP": "stop"}),
                         parse_mode='HTML')
        time.sleep(15)
        current_resp_count[message.from_user.id] = 0


def send_message(message, text):
    global current_resp_count
    if len(str(text)) < 4096:
        make_send_message(message, text)
        make_pause_for_long_inference(message)
    else:
        cutternt_token_phrase = ""
        delim = '\n'
        spl_text = str(text).strip().split(delim)
        for word in spl_text:
            cutternt_token_phrase += word + delim
            if 3100 <= len(cutternt_token_phrase) < 4095:
                make_send_message(message, cutternt_token_phrase)
                cutternt_token_phrase = ""
                make_pause_for_long_inference(message)
            elif len(cutternt_token_phrase) >= 4095:
                cutternt_token_phrase_2 = ""
                for symbol in cutternt_token_phrase.replace("<b>", " ").replace("</b>", " ").replace(
                        "b>", " ").replace("<b", " ").replace("/b>", " ").replace("</b", " ").replace(
                        "<i>", " ").replace("</i>", " ").replace("i>", " ").replace("<i", " ").replace(
                        "/i>", " ").replace("</i", " "):
                    cutternt_token_phrase_2 += symbol
                    if len(cutternt_token_phrase_2) >= 4095:
                        make_send_message(message, cutternt_token_phrase_2)
                        cutternt_token_phrase_2 = ""
                        make_pause_for_long_inference(message)
                if len(cutternt_token_phrase_2.strip().strip(delim).strip()) > 0:
                    make_send_message(message, cutternt_token_phrase_2)
                    make_pause_for_long_inference(message)
                cutternt_token_phrase = ""
        if len(cutternt_token_phrase.strip().strip(delim).strip()) > 0:
            make_send_message(message, cutternt_token_phrase)
            make_pause_for_long_inference(message)


def clean_pool():
    global responding_pool
    while is_running:
        for id in responding_pool:
            jobs_to_del = list()
            for job in responding_pool[id]:
                if not job.is_alive():
                    if job not in jobs_to_del:
                        jobs_to_del.append(job)
            for job in jobs_to_del:
                try:
                    responding_pool[id].remove(job)
                except Exception as e:
                    print(e)
        time.sleep(20)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global responding_pool
    try:
        if isinstance(call.data, str):
            if (call.data.strip().lower() == "stop" and responding_pool.get(call.message.chat.id) is not None
                    and len(responding_pool.get(call.message.chat.id)) > 0):
                for job in responding_pool.get(call.message.chat.id):
                    job.terminate()
                del responding_pool[call.message.chat.id]
                bot.send_message(chat_id=call.message.chat.id,
                                 text="<b>The inference has been stopped.</b>",
                                 parse_mode='HTML')
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())
        bot.send_message(chat_id=call.message.chat.id,
                         text="Sorry, but an error occurred during call-bak handling...")


if __name__ == "__main__":
    connect()
    print("init")
    clean_thr = threading.Thread(target=clean_pool, name="cleaning", daemon=True)
    clean_thr.start()
    print("clean_thr started")
    while is_running:
        try:
            if is_connected and bot is not None:
                print("polling")
                bot.infinity_polling()
        except Exception as exc:
            try:
                connect()
            except Exception as exc:
                print(traceback.format_exc())
                print(exc)
            print(traceback.format_exc())
            print(exc)
        time.sleep(10)
