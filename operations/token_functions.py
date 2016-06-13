from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict
import time
import sys


def load_ngrams(ngram_file):
    """Loads n-grams from the given file"""

    ngrams = set()

    for line in ngram_file:
        if line.strip().count(" "):
            ngrams.add("_".join(line.split()))

    return ngrams


def parse_sentences(corpus):
    """Splits the text into sentences (lists of words)"""

    #stemmer = SnowballStemmer("english")
    sentences = sent_tokenize(corpus)

    print("[%s] corpus sentence-tokenized"%time.ctime(),
        file=sys.stderr)

    # parse sentences into lists of words, without punctuation
    ret = []
    for sentence in sentences:
        ret.append( [token for token in word_tokenize(sentence)
                            if token[0].isalnum()] )
    return ret


def find_prefixes(ngrams):
    """
    For ngrams that have other ngrams as prefixes, it finds them,
     and returns a dict in the form of:
        { ngram:[prefix_ngram1, prefix_ngram2, ... ] }
    """

    def is_prefix(prefix, word):
        # the extra space check is necessary
        #  for cases such as "to be" and "to become"
        return word.startswith(prefix+"_")
    
    # a weaker condition, so we don't miss short prefixes
    def loop_condition(prefix, word):
        p = prefix.split("_")
        w = word.split("_")
        return p[0] == w[0]

    prefix_table = {}
    ngrams = sorted(ngrams)

    for i in range(1, len(ngrams)):
        j = i-1
        prefixes = []
        while loop_condition(ngrams[j], ngrams[i]):
            if is_prefix(ngrams[j], ngrams[i]):
                prefixes.append( ngrams[j] )
            j -= 1
            if (j<0):
                break

        if prefixes:
            prefix_table[ ngrams[i] ] = prefixes
    
    return prefix_table


def make_inverse_prefix_table(prefix_table):
    """
    Turns an ngram prefix table into an inverse one, so instead of 
    looking up prefixes of ngrams, we look up the prefixed ngrams.
    I couldn't find a proper name for this. (It's not 'suffix'.)
    """
    inverse_prefix_table = defaultdict(lambda:[])

    for ngram in prefix_table.keys():
        for prefix in prefix_table[ngram]:
            inverse_prefix_table[prefix].append( ngram )

    return { x:inverse_prefix_table[x] for x in inverse_prefix_table }


def find_ngram(sentence, i, ngrams, inverse_prefix_table):
    """Detects the longest ngram in the sentence, starting with the i-th word.
    """
    s = sentence[i]
    j = i+1
    last_found = s
    while j<len(sentence):
        s += "_"+sentence[j]
        if s in ngrams:
            # if there's no ngram longer than this one
            if s not in inverse_prefix_table:
                return s
            # otherwise, continue building up
            else:
                last_found = s
        j += 1
    return last_found if (last_found in ngrams) else None


def substitute_ngrams(sentences, ngrams, prefix_table):
    """Substitutes the ngrams in the sentences with their _'d forms."""

    # for frequency counting, we'll need to substitute the longest one, 
    #  and then use the prefix table to increment the prefixes' counts too
    # for context vector building,
    #  we will have to use the inverse prefix table to trigger special processing

    # but first, we see which words can be used to start an ngram
    start_words = set([x.split("_")[0] for x in ngrams])

    # we then construct the inverse prefix table, so we can check
    #  whether there is a longer ngram
    inverse_prefix_table = make_inverse_prefix_table(prefix_table)

    # and we substitute the longest ngram we can find
    for sentence in sentences:
        i=0
        while i < len(sentence):
            if sentence[i] in start_words:
                # try to detect the ngram
                ngram = find_ngram(sentence, i, ngrams, inverse_prefix_table)
                # if there is one, do the substitution
                if ngram:
                    length = ngram.count("_")+1
                    sentence[i] = ngram
                    for j in range(1,length):
                        del sentence[i+1]
            i += 1 
    return sentences
