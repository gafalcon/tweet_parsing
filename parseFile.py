#./env/bin/python
# -*- coding: utf-8 -*-
import sys
import json
from dateutil import parser
import re
import string
from nltk.stem.snowball import FrenchStemmer, GermanStemmer, SpanishStemmer
from nltk.stem.porter import PorterStemmer


"""
palabras a buscar: paris, parís, ataque, attack, atentado, terrorist, siria, isis, pray, syria

"""
REGEX = r".*(terrorist|siria| isis |prayforparis|syria|atentado|(par[ií]s.*attack)|(attack.*par[ií]s)|(par[ií]s.*att?aque)|(att?aque.*par[ií]s)|(angriff.*par[ií]s)|(par[ií]s.*angriff)).*"

class TweetFiltering(object):

    def __init__(self):
        self.tweets = 0
        self.related_tweets = 0
        self.stopwords = {}
        self.stemmers = {}
        self.stemmers["es"] = SpanishStemmer()
        self.stemmers["en"] = PorterStemmer()
        self.stemmers["fr"] = FrenchStemmer()
        self.stemmers["de"] = GermanStemmer()
        self.stopwords["es"] = self.load_stopwords_file("spanish_stopwords.txt")
        self.stopwords["en"] = self.load_stopwords_file("english_stopwords.txt")
        self.stopwords["fr"] = self.load_stopwords_file("french_stopwords.txt")
        self.stopwords["ge"] = self.load_stopwords_file("german_stopwords.txt")
        self.output_file = open(sys.argv[2], 'a')

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
            text = self.process_text(text, tweet.get("lang", "en"))
            short_tweet = {
                "user_id": tweet.get('user').get('id'),
                "text": text,
                "coordinates": tweet["coordinates"]["coordinates"],
                "date": self.process_date(tweet.get("created_at"))
            }
            print short_tweet
            self.output_file.write("{}\n".format(json.dumps(short_tweet)))
            print "\n\n"

    def parseDate(self, str_date):
        """Parses a string date into a datetime object"""
        return parser.parse(str_date)

    def process_date(self, str_date):
        """ Removes the time from the date string """
        tweet_date = parser.parse(str_date)
        return tweet_date.strftime("%d-%m-%Y")



    def load_stopwords_file(self, filename):
        return [line.rstrip('\n') for line in open(filename)]

    def remove_stopwords(self, text, stopwords, stemmer=None):
        """Remove stopwords in text"""
        if stemmer:
            return ' '.join([stemmer.stem(word) for word in text.split() if word not in stopwords])
        return ' '.join([word for word in text.split() if word not in stopwords])

    def process_text(self, text, lang):
	#this function pre-process de text of a tweet
        text = text.lower() 
        emojiPattern = u'[\U0001f600-\U0001f64F]'
        symbolsPattern = u'[\U00002600-\U000026FF]'
        transportPattern = u'[\U0001f680-\U0001f6FF]'
        picPattern = u'[\U0001f300-\U0001f5fF]'
        dingbastPattern = u'[\U00002700-\U000027BF]'
        text = re.sub(emojiPattern, '', text)
        text = re.sub(symbolsPattern,'', text)
        text = re.sub(transportPattern, '', text)
        text = re.sub(picPattern, '', text)
        text = re.sub(dingbastPattern, '', text)
        text = re.sub("(?:\#+.[\w_]+[\w\'_\-]*[\w_]+)", '', text)
        text = re.sub('@[^\s]+', '', text)
        text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub('http', '', text)
        signsPattern = re.compile('[%s]' % re.escape(string.punctuation))
        text = re.sub(signsPattern, '', text)

        quoatesPattern = r'(\u201c.*?\u201d)|(".*?")|(\u2018.*?\u2019)|(\uff02.*?\uf\f02)|\s(\'.*?\')\s'
        text = re.sub(quoatesPattern, '', text)
        text = re.sub(r'[0-9]*', '', text)

        return self.remove_stopwords(text, self.stopwords.get(lang, "en"), self.stemmers.get(lang))



tweets_filter = TweetFiltering()
tweets_filter.read_file(sys.argv[1])

