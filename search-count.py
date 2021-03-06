#!/usr/bin/env python2
#-*- coding:utf-8 -*-
'''
Get number of search results for each idiom
'''

import sys
import httplib
import socket
import urllib
import urllib2
import re
import time
import random
import argparse
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

def search_baidu(word):
    ''' search word in baidu.com '''
    data = urllib.urlencode({'q2': word})
    request = urllib2.Request('http://www.baidu.com/s?' + data)

    retry_count = 0
    while True:
        try:
            response = urllib2.urlopen(request, timeout = 1)
            soup = BeautifulSoup(response.read(), "html.parser")
        except socket.timeout:
            # sys.stderr.write('Retry [' + word + ']: ' + str(retry_count) + '\n')
            time.sleep(8 + 2 * random.random())
            retry_count += 1
        except urllib2.HTTPError:
            return 'error'
        except httplib.IncompleteRead:
            # sys.stderr.write('Retry [' + word + ']: ' + str(retry_count) + '\n')
            time.sleep(3 + 2 * random.random())
            retry_count += 1
        else:
            break

    return re.findall('[0-9,]+',
                      soup.find('div', class_="nums").get_text())[0]

def search_bing(word, english=False):
    ''' search word in cn.bing.com '''
    if english:
        data = urllib.urlencode({'q': word, 'ensearch':1})
    else:
        data = urllib.urlencode({'q': word})

    request = urllib2.Request('http://cn.bing.com/search?' + data)

    retry_count = 0
    while True:
        try:
            response = urllib2.urlopen(request, timeout = 1)
            soup = BeautifulSoup(response.read(), "html.parser")
        except socket.timeout:
            time.sleep(8 + 2 * random.random())
            retry_count += 1
        except urllib2.HTTPError:
            return 'error'
        except httplib.IncompleteRead:
            time.sleep(3 + 2 * random.random())
            retry_count += 1
        else:
            break

    return re.findall('[0-9,]+',
                      soup.find('span', class_="sb_count").get_text())[0]

parser = argparse.ArgumentParser(description='Search & Count')
parser.add_argument('-i', '--input',
                    required=True,
                    help='input file')
parser.add_argument('-o', '--output',
                    help='output file',
                    default='-')
parser.add_argument('-s', '--source',
                    help='search engine',
                    type=str, choices=['baidu', 'bing'],
                    default='baidu')
parser.add_argument('-e', '--english',
                    help='English search',
                    action='store_true')
args = parser.parse_args()

word_file = args.input
word_out_file = args.output

with open(word_file, 'r') as word_file:
    while True:
        line = word_file.readline()
        if not line:
            break

        word = line.strip()
        if args.source == 'bing':
            if args.english:
                word_res = search_bing(word, english=True)
            else:
                word_res = search_bing(word)
        else:
            word_res = search_baidu(word)

        if word_out_file == '-':
            print word,word_res
        else:
            with open(word_out_file, 'a') as out_file:
                out_file.write(word + ' ' + word_res + '\n')

