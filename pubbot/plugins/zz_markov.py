"""
* Markov chatter plugin
*
* Originally based on http://www.eflorenzano.com/blog/post/writing-markov-chain-irc-bot-twisted-and-python/
"""

import pubbot.plugins as plugins

import os
from collections import defaultdict

import sqlite3
import random
import codecs

KEY_LENGTH = 2

def iter_sentence(sentence):
    words = ['\n'] + sentence.split() + ['\n']
    buf = words[:KEY_LENGTH+1]
    words = words[KEY_LENGTH+1:]
    yield buf
    for word in words:
        buf.append(word)
        del buf[0]
        yield buf


class ThinkingError(ValueError):
    pass


# This just tries to run a function multiple times...
def multiple_thinks(func, tries=5):
    def _(*args, **kwargs):
        retval = None
        for i in range(tries):
            try:
                retval = func(*args, **kwargs)
                break
            except ThinkingError:
                continue
        else:
            raise ThinkingError
        return retval
    return _


class Markov(object):

    def __init__(self, path):
        self.con = sqlite3.connect(path)
        cur = self.con.cursor()
        cur.execute("CREATE TABLE sets(k1, k2, k3)")

    def _get_x_words(self, words, x):
        if len(words) < x:
            y = x - len(words)
            for i in range(y):
                yield ''
            x -= y
        for i in range(x):
            yield words[i]

    def add_sentence(self, sentence):
        cur = self.con.cursor()
        for words in iter_sentence(sentence):
            cur.execute("INSERT INTO sets (k1, k2, k3) VALUES (?,?,?)", words)

    def get_all_starting_sets(self):
        cur = self.con.cursor()
        cur.execute("SELECT '\n' AS a, k2, k3 FROM sets WHERE sets.k1='\n'")
        return cur.fetchall()

    def get_possible_following_word(self, *words):
        word1, word2 = self._get_x_words(words, KEY_LENGTH)
        cur = self.con.cursor()
        if not word1:
            cur.execute("SELECT k3 FROM sets WHERE k2=?", (word1, ))
        else:
            cur.execute("SELECT k3 FROM sets WHERE k1=? AND k2=?", (word1, word2))
        return [word[0] for word in cur.fetchall()]

    @multiple_thinks
    def get_following_word(self, *words):
        possible_words = self.get_possible_following_word(*words)
        if not possible_words:
            raise ThinkingError()
        return random.choice(possible_words)

    def extend_words(self, *words):
        buffer = list(words[:])
        while buffer[-1:][0] != '\n':
            buffer.append(self.get_following_word(*buffer[-KEY_LENGTH:]))
        return " ".join(buffer[:-1])

    def extend_sentence(self, sentence):
        return self.extend_words(*sentence.split())

    def get_possible_preceeding_word(self, *words):
        word1, word2 = self._get_x_words(words, KEY_LENGTH)
        cur = self.con.cursor()
        if not word1:
            cur.execute("SELECT k1 FROM sets WHERE k2=?", (word1, ))
        else:
            cur.execute("SELECT k1 FROM sets WHERE k2=? AND k3=?", (word1, word2))
        return [word[0] for word in cur.fetchall()]

    @multiple_thinks
    def get_preceeding_word(self, *words):
        possible_words = self.get_possible_preceeding_word(*words)
        if not possible_words:
            raise ThinkingError()
        return random.choice(possible_words)

    def extend_words_backwards(self, *words):
        buffer = list(words[:])
        while buffer[0] != '\n':
            buffer.insert(0, self.get_preceeding_word(*buffer[:KEY_LENGTH]))
        return " ".join(buffer[1:])

    def extend_sentence_backwards(self, sentence):
        return self.extend_words_backwards(*sentence.split())


class MarkovPlugin(plugins.Plugin):

    name = "markov"

    def __init__(self, parent, config):
        super(MarkovPlugin, self).__init__(parent, config)
        self.markov = Markov(":memory:")
        self.chattiness = -1 # 0.05
        self.chain_length = 2
        self.max_words = 10000
        self.num_attempts = 5

        # load in my brain
        if os.path.exists('markov.brain'):
            f = codecs.open('markov.brain', 'r', 'utf-8')
            try:
                for line in f:
                    self._add_to_brain(line, False)
            except:
                pass
            f.close()

    def _add_to_brain(self, msg, write_to_disk=True):
        """ Append to brain """
        if write_to_disk:
            f = open('markov.brain', 'a')
            f.write(msg+'\n')
            f.close()

        self.markov.add_sentence(msg)

    def _generate_random_sentence(self):
        start = random.choice(self.markov.get_all_starting_sets())
        return self.markov.extend_words(*start).replace("\n", "").strip()

    def _generate_from_sentence(self, msg):
        buf = msg.split()
        if buf[0] in ('pubbot:', 'pubbot', 'pubbot,'):
            del buf[0]
        if buf[0][-1] in (":",):
            del buf[0]
        buf = buf[:KEY_LENGTH]
        for i in range(self.num_attempts):
            try:
                sentence = self.markov.extend_words(*buf)
                if sentence == msg:
                    continue
            except ThinkingError:
                continue
            return sentence
        return self._generate_random_sentence()

    def on_direct(self, source, msg):
        #try:
            sentence = self._generate_from_sentence(msg)
            if sentence:
                return source.msg(sentence)
        #except:
        #    return source.msg("Ow, it hurts, it hurts...")

    def on_message(self, source, user, msg):
        self._add_to_brain(msg)

        if "pubbot" in msg:
            sentence = self._generate_from_sentence(msg)
            if sentence:
                return source.msg(sentence)

