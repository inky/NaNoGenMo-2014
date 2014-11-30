#!/usr/bin/env python
"""
Gricean Defier

"""
from __future__ import unicode_literals

import codecs
import json
import os
import re
import string
import sys
import time
import urllib
from random import choice, randint, random, shuffle

# http://www.clips.ua.ac.be/pages/pattern
from pattern import en

# http://docs.python-requests.org/en/latest/
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout


CACHE_DIR = '.disgrice-cache'

HEDGE_PHRASES = (
    'apparently',
    'basically',
    'in general',
    'in theory',
    'kind of',
    'like',
    'more or less',
    'perhaps',
    'presumably',
    'somewhat',
    'sort of',
    'supposedly',
    'uh',
    'um',
)
HEDGE_ADVERBS = (
    'slightly',
    'somewhat',
)
NUMBER_WORDS = (
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
)


def heads():
    return bool(randint(0, 1))

def get_pos(word):
    for token, pos in en.tag(word):
        if token[0].isalpha():
            return pos


class WordnikWizard:

    def __init__(self, api_key, cache_dir=CACHE_DIR):
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.cache_filename = os.path.join(cache_dir, 'wordnik.json')
        self.num_requests = 0

    def __enter__(self):
        # make the cache directory if it doesn't exist
        try:
            os.mkdir(self.cache_dir)
        except OSError:
            pass

        # read the cache file if it exists
        try:
            with codecs.open(self.cache_filename, encoding='utf-8') as fp:
                self.cache = json.load(fp)
        except IOError:
            self.cache = {}

        return self

    def __exit__(self, *args):
        with codecs.open(self.cache_filename, 'w', encoding='utf-8') as fp:
            json.dump(self.cache, fp)
        sys.stderr.write('Saved cache (%d items)\n' % len(self.cache))

    def get_json(self, url):
        try:
            req = requests.get(url, timeout=5)
            if req.status_code == 200:
                self.did_request()
                return json.loads(req.text)
            else:
                sys.stderr.write('Wordnik response code: %d\n' % req.status_code)
                return None
        except (ConnectTimeout, ReadTimeout):
            sys.stderr.write('Request timed out\n')
            return None

    def did_request(self):
        self.num_requests += 1
        if self.num_requests % 10 == 0:
            sys.stderr.write('Sleeping\n')
            time.sleep(3)
        else:
            time.sleep(random() * 0.5)

    def related_words(self, word, relationship='same-context'):
        cache_key = '%s/%s' % (word, relationship)
        if cache_key in self.cache:
            return self.cache[cache_key]

        base_url = ('http://api.wordnik.com:80/v4/word.json/%s/relatedWords'
                    % urllib.quote(word.encode('utf-8')))
        args = urllib.urlencode({
            'api_key': self.api_key,
            'useCanonical': 'false',
            'relationshipTypes': relationship,
            'limitPerRelationshipType': 10,
        })
        sys.stderr.write('Requesting: %s/%s\n' % (word, relationship))
        response = self.get_json('%s?%s' % (base_url, args))

        if not response:
            return None
        elif 'message' in response:
            sys.stderr.write('Wordnik %s response: %s\n'
                             % (response.get('type', ''),
                                response['message']))
            return []
        else:
            words = response[0].get('words', []) if response else []
            self.cache[cache_key] = words
            return words


class HarmlessHeading:
    HTML_TAG = 'h2'

    def __init__(self, text):
        self.text = text

class CuriousDecoration:
    HTML_TAG = 'hr'

    def __init__(self):
        self.text = ''

class DisgricefulParagraph:
    HTML_TAG = 'p'

    def __init__(self, text, wordnik):
        output = []
        words_seen, pos_seen = [''], ['']
        for word in text.split():
            # get the part of speech, and hold onto the original string for
            # later comparison
            pos = get_pos(word) or ''
            result = word

            #
            # Make random changes to the text here
            #

            if pos.startswith('JJ'):  # adjective

                if pos_seen[-1] not in ('RB', ) and heads():
                    # green -> NOT GREEN
                    result = 'NOT %s' % word.upper()

            elif pos.startswith('VB'):  # verb

                if pos == 'VBG' and output and output[-1].lower() == 'was' and heads():
                    # was eating -> WAS NOT EATING
                    output.append(output.pop().upper())
                    result = 'NOT %s' % word.upper()

                elif pos_seen[-1] == 'PRP' and heads():
                    # it verbed -> it, SUPPOSEDLY, verbed
                    hedge = choice(HEDGE_PHRASES)
                    if output[-1][-1].isalpha():
                        output.append(output.pop() + ',')
                        result = '%s, %s' % (hedge, word)

            elif pos == 'NN':  # singular noun

                if word.isalpha() and heads() and heads():
                    # whale -> whale (or fish)
                    related = wordnik.related_words(word.lower())
                    if related:
                        aka_word = choice(related)
                        result = '%s (or %s)' % (word, aka_word)

            elif pos.startswith('TO') and word == 'to':

                if (pos_seen[-1].startswith('VB') and len(pos_seen) > 1
                    and pos_seen[-2] == 'PRP' and words_seen[-2].lower() != 'it'
                    and heads()):
                    # she tried to -> she tried NOT to
                    result = 'NOT %s' % word

            elif pos == 'CD' and heads():  # number

                number = choice(NUMBER_WORDS) #.upper()
                if word.lower() != number.lower():
                    result = '%s or %s' % (word, number)

            elif word.lower() == 'very' and heads():

                result = choice(HEDGE_ADVERBS).upper()

            elif word.lower() == 'all':

                if pos_seen[-1].startswith('RB') and output[-1].isalpha():
                    # almost all men -> not all men
                    output.pop()
                    output.append('NOT')

            elif words_seen[-1] == 'is' and heads():

                if word.lower() == 'the':
                    # is -> is (OR IS NOT)
                    result = '(OR IS NOT) %s' % word
                elif word.lower() in ('it', 'this'):
                    result = '%s (OR IS %s NOT)' % (word, word.upper())

            elif word == 'his' and heads() and heads():

                result = 'his or her'

            elif word == 'him' and heads() and heads():

                result = 'him or her'

            elif word in ('he', 'she') and heads() and heads():

                result = 'he or she'

            output.append(result)
            words_seen.append(word)
            pos_seen.append(pos)

        # put it all together
        self.text = ' '.join(output)


def disgriceful_novel(text, wordnik):
    # regex to detect headings and separators in the text
    re_heading = re.compile(r'^(CHAPTER [0-9IVXLCDM]+(\.|$)|THE END$)', re.IGNORECASE)
    re_sep = re.compile(r'^[*\s]+$')

    # convert the text into a series of headings and paragraphs without
    # linebreaks, then transform each paragraph individually
    novel = []
    word_count = 0
    for block in '\n'.join(text.splitlines()).split('\n\n'):
        block = ' '.join(block.strip().split('\n'))
        if not block:
            continue
        elif re_sep.match(block):
            if not (novel and isinstance(novel[-1], CuriousDecoration)):
                novel.append(CuriousDecoration())
        elif re_heading.match(block) or block == block.upper():
            novel.append(HarmlessHeading(block))
        else:
            novel.append(DisgricefulParagraph(block, wordnik))
            word_count += len(novel[-1].text.split())
            sys.stderr.write('Word count: %d\n' % word_count)

    return novel


def format_html(blocks):
    escape = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    output = []
    for block in blocks:
        text, tag = block.text, block.HTML_TAG
        if text:
            escaped_text = escape(block.text)
            output.append('<%s>%s</%s>' % (tag, escaped_text, tag))
        else:
            output.append('<%s>' % block.HTML_TAG)
    return '\n\n'.join(output)


def main():
    wordnik_api_key = os.environ.get('WORDNIK_API_KEY', '')
    if not wordnik_api_key:
        sys.stderr.write('Error: Please set the WORDNIK_API_KEY environment '
                         'variable.\n')
        return

    novel = ''
    try:
        text = sys.stdin.read().decode('utf-8').lstrip(u'\ufeff')
        with WordnikWizard(wordnik_api_key) as wordnik:
            novel = disgriceful_novel(text, wordnik)
    except KeyboardInterrupt:
        sys.stderr.write('\n')
        return 1

    if novel:
        print format_html(novel).encode('utf-8')
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
