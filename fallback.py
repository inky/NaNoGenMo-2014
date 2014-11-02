"""
50,000 words through the eyes of @everyword.

"""
from random import choice, random, shuffle
from textwrap import wrap

DICTIONARY = set()
with open('/usr/share/dict/web2') as fp:
    for word in fp:
        DICTIONARY.add(word.rstrip())

PATTERNS = (
    'Oh {}.',
    'Oh {}, what a word.',
    'Hmm, {}.',
    'Hmm, {}, how interesting.',
    '{}, indeed.',
    '{}, splendid!',
    '{}, could it be?',
    'My oh my, {}.',
)

STORY_TEMPLATE = """
Chapter 99
@everyword
----------

{}

THE END
"""

def generate_sentences():
    words = list(DICTIONARY)
    shuffle(words)

    sentences, word_count = [], 0
    while word_count < 50000:
        word = words.pop()
        pattern = choice(PATTERNS)
        if pattern.startswith('{'):
            word = word.capitalize()

        sentence = pattern.format(word)
        sentences.append(sentence)
        word_count += len(sentence.split())

        if random() < 0.1:
            sentences.append('')

    return sentences

def format_story(sentences):
    text, paragraph = [], []
    for sentence in sentences:
        if sentence:
            paragraph.append(sentence)
        elif paragraph:
            text.append(' '.join(paragraph))
            paragraph = []

    if paragraph:
        text.append(' '.join(paragraph))

    text = '\n\n'.join('\n'.join(wrap(p)) for p in text)
    return STORY_TEMPLATE.format(text).strip()

print format_story(generate_sentences())
