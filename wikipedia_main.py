#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Esther'
import wikipedia_config
import tweepy
import re
import urllib2

import sys
import time


def login():
    # for info on the tweepy module, see http://tweepy.readthedocs.org/en/

    # Authentication is taken from wikipedia_config.py
    consumer_key = wikipedia_config.consumer_key
    consumer_secret = wikipedia_config.consumer_secret
    access_token = wikipedia_config.access_token
    access_token_secret = wikipedia_config.access_token_secret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api

def stick_together_output():

    first_sentence_pattern = re.compile("^(([^\.]+)(\s+is\s+|\s+are\s+|\s+was\s+|\s+were\s+)([^\.]+\.))\s+")
    round_bracket_pattern = re.compile("\s+(\()[^\)\]]+(\))\s+")
    square_bracket_pattern = re.compile("\s+(\[)[^\)\]]+(\])\s+")

    finished = False
    while not finished:
        seed_page = urllib2.urlopen('https://en.wikipedia.org/wiki/Special:Random')
        seed_content = seed_page.read()
        seed_title = seed_content.split("<title>")[1].split(" - Wikipedia, the free encyclopedia</title>")[0]
        if "(disambiguation)" not in seed_title and "List of" not in seed_title and "Category:" not in seed_title:

            seed_text = seed_content.split("<p>")[1].split("</p>")[0]
            seed_text = re.sub("<[^>]+>", "", seed_text)

            first_sentence1 = re.split("[^\s].\.\s", seed_text, 1)[0]+". "

            while re.search(round_bracket_pattern, first_sentence1):
                first_sentence1 = re.sub(round_bracket_pattern, " ", first_sentence1)
            while re.search(square_bracket_pattern, first_sentence1):
                first_sentence1 = re.sub(square_bracket_pattern, " ", first_sentence1)
            m = re.findall(first_sentence_pattern, first_sentence1)
            if m:
                first_half = m[0][1]
                connector = m[0][2]
                output = first_half.strip() +" "+ connector.strip()
                second_page_tries = 0
                while not finished and second_page_tries < 15:
                    random_second_page = urllib2.urlopen('https://en.wikipedia.org/wiki/Special:Random')
                    random_second_page_content = random_second_page.read()
                    random_second_page_title = random_second_page_content.split("<title>")[1].split(" - Wikipedia, the free encyclopedia</title>")[0]
                    second_page_tries += 1
                    if "(disambiguation)" not in random_second_page_title and "List of" not in random_second_page_title and "Category:" not in random_second_page_title:

                        random_second_page_text = random_second_page_content.split("<p>")[1].split("</p>")[0]
                        random_second_page_text = re.sub("<[^>]+>", "", random_second_page_text)
                        first_sentence2 = re.split("(?<=[^\s].)\.\s", random_second_page_text, 1)[0]

                        while re.search(round_bracket_pattern, first_sentence2):
                            first_sentence2 = re.sub(round_bracket_pattern, " ", first_sentence2)
                        while re.search(square_bracket_pattern, first_sentence2):
                            first_sentence2 = re.sub(square_bracket_pattern, " ", first_sentence2)

                        if connector in first_sentence2:
                            output = output + " " + first_sentence2[first_sentence2.find(connector)+len(connector):]
                            if len(output) < 141:
                                finished = True


    output = output.strip(". :")+"."
    return output

def tweet_something(debug):
    api = login()
    try:
        output = stick_together_output()
        if debug:
            print output
        else:
            api.update_status(status=output)
            print output
    except:
        api.send_direct_message(screen_name = "ojahnn", text = str(sys.exc_info())[:130] + " " + time.strftime("%H:%M:%S"))

tweet_something(False)