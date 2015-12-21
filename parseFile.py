# -*- coding: utf-8 -*-
import sys
import json
from dateutil import parser
import re

"""
palabras a buscar: paris, parís, ataque, attack, atentado, terrorist, siria, isis, pray, syria

"""
REGEX = r".*(terrorist|siria|isis|prayforparis|syria|atentado|(par[ií]s.*attack)|(attack.*par[ií]s)|(par[ií]s.*att?aque)|(att?aque.*par[ií]s)|(angriff.*par[ií]s)|(par[ií]s.*angriff)).*"

class TweetFiltering(object):

    def __init__(self):
        self.tweets = 0
        self.related_tweets = 0
        self.spanish_stopwords = self.load_stopwords_file("spanish_stopwords.txt")
        self.english_stopwords = self.load_stopwords_file("english_stopwords.txt")
        self.german_stopwords = self.load_stopwords_file("german_stopwords.txt")
        self.french_stopwords = self.load_stopwords_file("french_stopwords.txt")
        self.stopwords_full = self.english_stopwords + self.german_stopwords
        self.output_file = open('filtered_tweets_berlin', 'a')

    def read_file(self, filename):
        """Read json file a extracts each object as a json tweet"""
        with open(filename) as json_file:
            json_string = ""
            reading_object = False
            line_number = 0
            for line in json_file:
                line_number += 1
                if line == '{\n':
                    reading_object = True
                if reading_object:
                    if line == "},\n":
                        json_string += "}"
                        reading_object = False
                        try:
                            json_object = json.loads(json_string)
                        except ValueError as e:
                            print e
                            print "ERROR in line : ", line_number
                            break
                        self.process_tweet(json_object)
                        json_string = ""
                    else:
                        json_string += line
        print "Total number of tweets parsed: ", self.tweets
        print "Total number of related tweets: ", self.related_tweets

    def process_tweet(self, tweet):
        """ Process the tweet """
        self.tweets += 1
        text = tweet.get("text")
        if re.match(REGEX, text, re.I):
            self.related_tweets += 1
            #print tweet
            print "Tweet number : ", self.related_tweets
            #print self.parseDate(tweet.get("created_at"))
            text = self.remove_stopwords(text, self.stopwords_full)
            short_tweet = {
                "user_id": tweet.get('user').get('id'),
                "text": text,
                "coordinates": tweet["coordinates"]["coordinates"],
                "date": tweet.get("created_at")
            }
            print short_tweet
            self.output_file.write("{}\n".format(json.dumps(short_tweet)))
            print "\n\n"

    def parseDate(self, str_date):
        """Parses a string date into a datetime object"""
        return parser.parse(str_date)

    def load_stopwords_file(self, filename):
        return [line.rstrip('\n') for line in open(filename)]

    def remove_stopwords(self, text, stopwords):
        """Remove stopwords in text"""
        return ' '.join([word for word in text.split() if word not in stopwords])



tweets_filter = TweetFiltering()
tweets_filter.read_file(sys.argv[1])

