# -*- coding: utf-8 -*-

__author__ = 'Esther'
import wikipedia_config
import tweepy
import re
import urllib2
from wikiapi import WikiApi


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
    wiki = WikiApi()
    wiki = WikiApi({ 'locale' : 'en'}) # to specify your locale, 'en' is default

    first_sentence_pattern = re.compile("^(([^\.]+)(\s+is\s+|\s+are\s+|\s+was\s+|\s+were\s+)([^\.]+\.))\s+[A-Z]")
    bracket_pattern = re.compile("\s+(\(|\[)[^\)\]]+(\)|\])\s+")

    finished = False
    while not finished:
        seed_page = urllib2.urlopen('https://en.wikipedia.org/wiki/Special:Random')
        seed_title = seed_page.read().split("<title>")[1].split(" - Wikipedia, the free encyclopedia</title>")[0]
        if "(disambiguation)" not in seed_title and "List of" not in seed_title and "Category:" not in seed_title:
            results1 = wiki.find(seed_title)
            article1_content = wiki.get_article(results1[0]).content
            if article1_content.count(" ") > 2:
                first_sentence1 = article1_content.split("\n\n")[1]
                while re.search(bracket_pattern, first_sentence1):
                    first_sentence1 = re.sub(bracket_pattern, " ", first_sentence1)
                m = re.findall(first_sentence_pattern, first_sentence1)
                if m:
                    first_half = m[0][1]
                    connector = m[0][2]
                    output = first_half.strip() +" "+ connector.strip()
                    second_page_tries = 0
                    while not finished and second_page_tries < 15:
                        random_second_page = urllib2.urlopen('https://en.wikipedia.org/wiki/Special:Random')
                        random_second_page_title = random_second_page.read().split("<title>")[1].split(" - Wikipedia, the free encyclopedia</title>")[0]
                        second_page_tries += 1
                        if "(disambiguation)" not in random_second_page_title and "List of" not in random_second_page_title and "Category:" not in random_second_page_title:
                            results2 = wiki.find(random_second_page_title)
                            article2_content = wiki.get_article(results2[0]).content
                            if article2_content.count(" ") > 2:
                                first_sentence2 = article2_content.split("\n\n")[1].split(". ")[0]+"."
                                while re.search(bracket_pattern, first_sentence2):
                                    first_sentence2 = re.sub(bracket_pattern, " ", first_sentence2)
                                if connector in first_sentence2:
                                    output = output + " " + first_sentence2[first_sentence2.find(connector)+len(connector):]
                                    if len(output) < 141:
                                        finished = True


    while output.endswith(".."):
        output = output[:-1]
    return output

def tweet_something(debug):
    api = login()
    output = stick_together_output()
    if debug:
        print output
    else:
        api.update_status(status=output)
        print output

tweet_something(False)