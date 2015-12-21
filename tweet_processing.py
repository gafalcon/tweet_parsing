#/usr/bin/python2
# -*- coding: utf-8 -*-
import json
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
import re
import string
from operator import itemgetter
from dateutil import parser

FREQUENCY_WORDS_DICT = {}
FREQUENCY_USERS_DICT = {}
FREQUENCY_DATES_DICT = {}

def writeFile(filename,dataList):
    fd = open(filename, 'w')
    for item in dataList:
        line = "%s\n"%(item)
        fd.write(line)#.encode('utf-8'))
    fd.close()

# def getFrequency(items):
#     freqs = {}
#     for word in items:
#         freqs[word] = freqs.get(word, 0) + 1 
#     listTuples = freqs.items()
#     listTuples.sort(key= itemgetter(1), reverse=True)

#     return listTuples #list ordered by frequency count

def update_word_freqs(tweet_text):
    for word in getWords(tweet_text):
        FREQUENCY_WORDS_DICT[word] = FREQUENCY_WORDS_DICT.get(word, 0) + 1

def update_freqs(label, freq_dict):
    freq_dict[label] = freq_dict.get(label, 0) + 1

def get_frequency_list(freq_dict):
    listTuples = list(freq_dict.items())
    listTuples.sort(key = itemgetter(1), reverse = True)
    return listTuples

def getWords(text):
    return [w for w in text.split(' ') if len(w) > 3]
    

def viewFrequencyWords(filename):
    listTuples = get_frequency_list(FREQUENCY_WORDS_DICT)
    size = len(listTuples)
    values = []
    words = []
    
    top = int(len(listTuples)*0.25)
    print ("{} words found, getting the first {}".format(size, top))

    dataList = []
    dataList.append("index,word,frequency,likelihood")
    i = 0 
    words, values = zip(*listTuples[:top])
    dataList += [ "{},{},{},{}".format(idx, word, value, 1.0*value/size) for idx, (word,value) in enumerate(listTuples[:top])]

    writeFile("wordsTweets.txt", words)
    writeFile(filename, dataList)

    index = np.arange(len(words))
    drawBarChart(index,words,values,'Words', "words_freqs.png")

def viewFrequency(filename, list_filename, freq_dict):
    listTuples = get_frequency_list(freq_dict)
    size = len(listTuples)
    values = []
    words = []
    
    dataList = []
    dataList.append("index,label,frequency")
    labels, values = zip(*listTuples)
    dataList += [ "{},{},{}".format(idx, label, value) for idx, (label,value) in enumerate(listTuples)]
    
    writeFile(list_filename,labels)
    writeFile(filename,dataList)
	
    index = np.arange(len(labels))
    drawBarChart(index,labels,
                 values,
                 list_filename.capitalize(),
                 list_filename  + "_freqs.png")



def processText(text):
	#this function pre-process de text of a tweet
    text = text.lower() 
    emojiPattern = u'[\U0001f600-\U0001f64F]'
    symbolsPattern = u'[\U00002600-\U000026FF]'
    transportPattern = u'[\U0001f680-\U0001f6FF]'
    picPattern = u'[\U0001f300-\U0001f5fF]'
    dingbastPattern = u'[\U00002700-\U000027BF]'
    text = re.sub(emojiPattern, '', text)
    text = re.sub(symbolsPattern,'',text)
    text = re.sub(transportPattern,'',text)
    text = re.sub(picPattern,'',text)
    text = re.sub(dingbastPattern,'',text)
    #text = re.sub("(?:\#+.[\w_]+[\w\'_\-]*[\w_]+)",'',text)
    text = re.sub('@[^\s]+','',text)
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',text)
    text = re.sub('http','',text)
    signsPattern = re.compile('[%s]' % re.escape(string.punctuation))
    text = re.sub(signsPattern,'', text)

    #quoatesPattern = r'(\u201c.*?\u201d)|(".*?")|(\u2018.*?\u2019)|(\uff02.*?\uf\f02)|\s(\'.*?\')\s'
    #text = re.sub(quoatesPattern,'',text)
    text = re.sub(r'[0-9]*','',text)
    return text

def drawBarChart(x,x_labels,y,title,filename, bar_width = 0.8):
    opacity = 0.4
    fig_size = plt.rcParams["figure.figsize"]# Get current size
    # Set figure width to 12 and height to 9
    fig_size[0] = 12
    fig_size[1] = 9
    plt.rcParams["figure.figsize"] = fig_size
    rects1 = plt.bar(x,y, 
                     bar_width,
                     alpha=opacity,
                     color='b')
    plt.ylabel('Scores')
    plt.title(title)
    #plt.xticks(x + 0.35,x_labels,rotation='vertical',fontsize='small')
    plt.legend()
    plt.savefig(filename)

def parseDate(str_date):
    """Parses a string date into a datetime object"""
    return parser.parse(str_date)

def process_date(str_date):
    date = parser.parse(str_date)
    return date.strftime("%d-%m-%Y")


def main(filename):
    #output_file = open(output_f, "w")
    with open(filename) as tweet_file:
        for line in tweet_file:
            tweet = json.loads(line)
            #tweet["text"] = processText(tweet.get("text"))
            #tweet["date"] = process_date(tweet.get("date"))
            update_word_freqs(tweet["text"])
            update_freqs(tweet["user_id"], FREQUENCY_USERS_DICT)
            update_freqs(tweet["date"], FREQUENCY_DATES_DICT)
            #output_file.write("{}\n".format(json.dumps(tweet)))

    viewFrequencyWords("word_frequency_results")
    viewFrequency("user_freq_results.csv", "user_ids", FREQUENCY_USERS_DICT)
    viewFrequency("dates_freq_results.csv", "dates", FREQUENCY_DATES_DICT)

main(sys.argv[1])
