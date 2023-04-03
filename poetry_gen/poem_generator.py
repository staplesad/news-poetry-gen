import random
import re
from collections import defaultdict
from itertools import chain
from functools import partial
from string import punctuation

import pronouncing


class PoemGenerator:
    def __init__(self, lines):
        self.lines = lines
        self.punc_table = str.maketrans({p: "" for p in punctuation})
        self.lines_wo_punc = []
        self.words = []
        self.rhyming_map = {}
        self.rhyming_count = {}
        if self.lines:
            self.analyse_lines()

        self.stopwords = ["to", "is", "and", "from", "for", "in", "of"]

    def analyse_lines(self):
        self.lines_wo_punc = [l.translate(self.punc_table) for l in self.lines]
        self.words = [l.split(" ") for l in self.lines_wo_punc]
        self.rhyming_map = self.get_rhyming_lines()
        counts = {l: len(v) for l, v in self.rhyming_map.items()}
        self.rhyming_count = defaultdict(list)
        for l, c in counts.items():
            self.rhyming_count[c].append(l)

    @staticmethod
    def count_syllables(words):
        phones = [pronouncing.phones_for_word(w) for w in words]
        counts = [pronouncing.syllable_count(p[0]) if p else 0 for p in phones]
        return counts

    def find_rhyming_scheme(self, scheme):
        """I'm not going to care about ensuring different rhymes right now."""
        unique_rhymes = set([c for c in scheme if c != " "])
        r_counts = {r: sum([1 if c == r else 0 for c in scheme]) for r in unique_rhymes}
        r_lines = {}
        most_rhyming = max(self.rhyming_count.keys())
        seen_lines = set()
        for r, count in sorted(r_counts.items(), key=lambda x: -x[1]):
            if count > most_rhyming:
                return []
            possible_lines = []
            search_order = random.sample(range(count, most_rhyming + 1), most_rhyming - count + 1)
            for i in search_order:
                possible_lines = self.rhyming_count.get(i, [])
                if possible_lines:
                    possible_lines = random.choice(possible_lines)
                    if possible_lines not in seen_lines:
                        seen_lines.add(possible_lines)
                        break
            if not possible_lines:
                return []
            r_lines[r] = random.sample(self.rhyming_map[possible_lines] + [possible_lines], count)
        lines = []
        for c in scheme:
            if c == " ":
                lines.append("")
            else:
                lines.append(r_lines[c].pop())
        return lines

    @staticmethod
    def partition_syllables(syllable_counts):
        split = [5, 7, 5]
        split_idxs = [0, 0, 0]
        cur = 0
        if sum(syllable_counts) != sum(split):
            return []
        for i, count in enumerate(split):
            total = 0
            while total < count:
                total += syllable_counts[cur]
                split_idxs[i] = cur
                cur += 1
            if total != count:
                return []
        return split_idxs

    def haiku(self):
        search_order = random.sample(range(len(self.lines)), len(self.lines))
        for i in search_order:
            syls = self.count_syllables(self.words[i])
            idxs = self.partition_syllables(syls)
            if idxs:
                lines = []
                s = 0
                for p in idxs:
                    lines.append(" ".join(self.words[i][s : p + 1]))
                    s = p + 1
                return lines
        return []

    def get_rhyming_lines(self):
        rhyming_map = {}
        for i, line in enumerate(self.lines):
            rhyming_map[line] = []
            w = self.words[i][-1].lower()
            r_words = pronouncing.rhymes(w)
            for j, l in enumerate(self.lines):
                if l == line:
                    continue
                final_word = self.words[j][-1].lower()
                if final_word in r_words and final_word not in self.stopwords:
                    rhyming_map[line].append(l)
        return rhyming_map

    def rhyming_couplet(self):
        search_order = random.sample(range(len(self.lines)), len(self.lines))
        for i in search_order:
            first_line = self.lines[i]
            if opts := self.rhyming_map[first_line]:
                return [first_line, random.choice(opts)]
        return []

    def rhyming_poem(self):
        search_order = random.sample(range(len(self.lines)), len(self.lines))
        for i in search_order:
            first_line = self.lines[i]
            next_lines = self.rhyming_map[first_line]
            if len(next_lines) > 2:
                n_lines = random.choice(range(3, len(next_lines) + 1))
                next_lines = random.sample(next_lines, n_lines)
                return [first_line] + next_lines
        return []

    def cutup(self, repetition=True):
        n_lines = random.choice(range(1, 4))
        n_words = random.choice(range(2, 6))
        lines = random.sample(self.lines, n_lines)
        words = list(chain(*[l.split(" ") for l in lines]))
        phrases = []
        for i in range(0, len(words), n_words):
            phrases.append(" ".join(words[i : i + n_words]))
            if repetition and random.choice(range(100)) < 3:
                phrases.append(" ".join(words[i : i + n_words]))
        phrases = random.sample(phrases, len(phrases))
        poem = []
        n_words = len(phrases) // (n_lines * 2)
        if n_words == 0:
            n_words = len(phrases) // (n_lines)
        for i in range(0, len(phrases), n_words):
            poem.append(" ".join(phrases[i : i + n_words]))
        if i + n_words < len(phrases):
            poem[-1] = " ".join([poem[-1]] + phrases[i + n_words :])
        return poem

    def get_poem(self):
        strategies = [
            self.rhyming_couplet,
            self.rhyming_poem,
            self.haiku,
            self.haiku,
            partial(self.find_rhyming_scheme, "ABCBBB"),
            partial(self.find_rhyming_scheme, "ABBA ABBA"),
            self.cutup,
            self.cutup,
        ]
        while True:
            poem = random.choice(strategies)()
            if poem:
                return poem
