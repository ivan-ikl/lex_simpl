#!/usr/bin/python3
import sys
import lxml
import time
import math
from lxml import etree
from nltk import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from collections import defaultdict

CONTEXTS_FILENAME = "./test-data/contexts_rectified.xml"
CANDIDATES_FILENAME = "./test-data/substitutions"
SIMPLEWIKI_FREQS_FILENAME = "./input_data/unigram_frequencies"
NGRAM_FREQ_FILENAME =   "./input_data/ngram_frequencies"
unigram_frequencies = defaultdict(lambda:0)
ngram_frequencies = defaultdict(lambda:0)

# here to preserve state when running multiple times
candidates = None
contexts = None
already_loaded = False

start_time = time.time()

def log(message):
    now = "[%.4f] "%(time.time() - start_time)
    print(now + message, file=sys.stderr)

def get_index(context):
    """Returns the index of the word to replace, given the XML context node"""
    if not context.text:
        return 0
    tokens = word_tokenize( context.text )
    return len([x for x in tokens if x[0].isalnum() ])


def get_text(context):
    """Reconstructs the original sentence from the given XML context node"""
    child = context.getchildren()[0]
    s = context.text if context.text else ""
    s += child.text
    s += child.tail if child.tail else ""
    return s


def get_wordnet_score(word):
    """Returns the number of WordNet meanings of the given word"""
    lemmatizer = WordNetLemmatizer()
    lemma = lemmatizer.lemmatize(word)
    return len(wordnet.synsets(lemma))


def get_simplewiki_score(word):
    global unigram_frequencies, ngram_frequencies

    if word in ngram_frequencies:
        return ngram_frequencies[word]
    else:
        return unigram_frequencies[word]


def check_for_ties(ranked_words):
    """
    Joins the words with tied scores.
    Expects a sorted list of (word, score) tuples as input.
     Returns a sorted list of words,
      with (word, word, ... ) tuples in case of tied words.
    """

    last_candidate = ranked_words[0]
    ret = [ last_candidate[0] ]
    last_score = last_candidate[1]

    for candidate in ranked_words[1:]:
        if candidate[1]==last_score:
            last = ret.pop()
            if type(last)==tuple:
                ret.append( last + (candidate[0],) )
            else:
                ret.append( (last, candidate[0]) )
        else:
            last_score = candidate[1]
            ret.append(candidate[0])
    return ret


def get_CV_similarity_score(cvector1, cvector2):
    """Returns the cosine between the two context vectors."""
    ret = Counter()
    for word in cvector1:
        if word in cvector2:
            Counter[word] = cvector1[word] * cvector2[word]

    cv1_sum = sum([cv[w]**2 for w in cvector1])
    cv2_sum = sum([cv[w]**2 for w in cvector2])
    ret /= math.sqrt(cv1_sum * cv2_sum)

    return ret


def extract_context_vector(sentence, index, max_offset):
    """Extracts the local context vector from the given sentence."""
    cvector = Counter()
    to_add = sentence[max(0,i-max_offset) : i] + sentence[i+1 :i+max_offset+1]
    cvector.update( to_add )
    return cvector

def rank(context, candidates, weights=[1.0,1.0,1.0]):
    """Ranks the candidate words."""

    index = get_index(context)
    scores = []
    for word in candidates:
        _word = word.replace(" ","_") # the underscored form, in case of ngram

        score = 1.0/len(word) * weights[0]                  # ilen_weight
        score += get_wordnet_score(word) * weights[1]       # wnet_weight
        score += get_simplewiki_score(_word) * weights[2]   # swiki_weight
        scores.append( score )

    z = sorted(list(zip(candidates, scores)),
                key=lambda x:x[1], reverse=True)

    return check_for_ties(z)

def load_the_files(opt=False):
    """Loads the necessary files, if it hasn't been done yet."""
    global CONTEXTS_FILENAME, CANDIDATES_FILENAME, already_loaded
    global candidates, contexts, unigram_frequencies

    if not already_loaded:

        # load in the sentence contexts
        with open(CONTEXTS_FILENAME) as infile:
            xml_source = infile.read()
        root = etree.fromstring( bytes(xml_source, "utf-8") )
        contexts = root.xpath("//lexelt//context")
        if not opt:
            log("loaded the contexts")
        
        # load the candidates
        with open(CANDIDATES_FILENAME) as infile:
            candidates = infile.readlines()
        candidates = [ line.strip().split(";")[:-1] for line in candidates ]
        if not opt:
            log("loaded the candidates")
        
        assert len(contexts)==len(candidates), \
                "Mismatched number of contexts/candidate sets!"
        
        # load the simplewiki/unigram frequencies
        with open(SIMPLEWIKI_FREQS_FILENAME) as infile:
            lines = [l.strip() for l in infile.readlines()]
        unigram_frequencies.update(
                {l.split()[0] : int(l.split()[1]) for l in lines} )
        if not opt:
            log("loaded the unigram freqs")

        # and the simplewiki/ngram frequencies
        with open(NGRAM_FREQ_FILENAME) as infile:
            lines = [l.strip() for l in infile.readlines()]
        ngram_frequencies.update(
                {l.split()[0] : int(l.split()[1]) for l in lines} )
        if not opt:
            log("loaded the n-gram freqs")

        already_loaded = True


def main(weights=[1.0, 1.0, 1.0], output_stream=sys.stdout, opt=False):
     
    global CONTEXTS_FILENAME, CANDIDATES_FILENAME, already_loaded
    global candidates, contexts, unigram_frequencies
    if not opt:
        if (len(sys.argv) == 3):
            CONTEXTS_FILENAME = sys.argv[1]
            CANDIDATES_FILENAME = sys.argv[2]
        else:
            print("Usage: ./%s contexts.xml substitutions.txt" % sys.argv[0])
            sys.exit(-1)

    # load the files if necessary
    if not already_loaded:
        load_the_files(opt)
    
    # rank the candidates
    for i in range(len(contexts)):
        ranked_words = rank(contexts[i], candidates[i], weights)
        s = "Sentence "+str(i+1)+" rankings:"
        for word in ranked_words:
            if type(word)==tuple:   # in case of ties
                word = ", ".join(word)
            s += " {"+word+"}"
        print(s, file=output_stream)
    if not opt:
        log("done.")

if __name__=="__main__":
    main()
