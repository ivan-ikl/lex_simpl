import sys
import time
from operations import *
#import operations
from collections import Counter
from nltk.stem.snowball import SnowballStemmer
CORPUS_FILENAME = "./Bitno/simplewiki_corpus.txt"
UNIGRAM_FREQ_FILENAME = "unigram_frequencies"
NGRAM_FREQ_FILENAME = "ngram_frequencies"

start_time = time.time()

def log(message):
    now = "[%.4f] "%(time.time() - start_time)
    print(now + message, file=sys.stderr)


if len(sys.argv)>2:
    print("Usage: %s [corpus_file]"%sys.argv[0])
elif len(sys.argv)==2:
    CORPUS_FILENAME = sys.argv[1]

log("Starting processing, time is "+time.ctime())

#ps = SnowballStemmer("english")

# load ngrams and find which ones are prefixed by other ones
ngrams = load_ngrams()
prefix_table = find_prefixes(ngrams)
log("loaded n-grams, built prefix table")

# load the corpus and split it into sentences
with open(CORPUS_FILENAME) as infile:
    corpus = infile.read().lower()
corpus = parse_sentences(corpus)
# the corpus is now a list of sentences, each sentence being
#  a list of words/tokens (without punctuation)
log("parsed corpus into sentences")

#ngrammizedSentences = ngrammizeSentences(corpus)

# we ignore n-grams, for now
"""
# for each sentence, substitute the ngrams with their underscored forms
#  (longest possible ngram)
ngramized_sentences = substitute_ngrams(corpus, ngrams, prefix_table)
log("made n-gramized corpus sentences")
"""

# now, count the unigram frequencies
c = Counter()
for sentence in corpus:
    c.update(sentence)
log("counted unigram frequencies")
with open(UNIGRAM_FREQ_FILENAME, "w") as fajl:
    for unigram in sorted(c):
        print(unigram+" "+str(c[unigram]), file=fajl)
log("wrote unigram frequencies to %s" % UNIGRAM_FREQ_FILENAME)

# we ignore n-grams, for now
"""
# and the ngram frequencies
nc = Counter()
for sentence in ngramized_sentences:
    nc.update(sentence)
nc = Counter(dict([(x,nc[x]) for x in nc if x in ngrams]))
log("counted n-gram frequencies")
with open(NGRAM_FREQ_FILENAME, "w") as fajl:
    for ngram in sorted(nc):
        print(ngram+" "+str(nc[unigram]), file=fajl)
log("wrote n-gram frequencies to %s" % NGRAM_FREQ_FILENAME)

print(nc)

# Fill out the output files for the next stage
outwords = []

# Output the source corpus sentence list
with open("data/outSentences.txt", "w") as sourceSentences:

    for sentence in corpus:
        sourceSentences.write(" ".join(map(lambda j: j[0], sentence)) + "\n")
        outwords += sentence


# Output the ngrammized sentence list
with open("data/outNgrammized.txt", "w") as ngrSentences:

    for sentence in ngrammizedSentences:
        ngrSentences.write(" ".join(map(lambda j: j[0], sentence)) + "\n")
        outwords += filter(lambda w: "_" in w[0], sentence)


# Output counters
with open("data/outCounters.txt", "w") as counters:

    wordcount = Counter(outwords)

    for c in wordcount:
        counters.write(c[0] + " " + c[1] + " " + str(wordcount[c]) + "\n")


print('Generating context vectors...')

vectors = build_context_vector(corpus, 4)
save_context_vector(vectors, 'data/outSentences.txt')

ngramVectors = build_context_vector(ngrammizedSentences, 4)
save_context_vector(ngramVectors, 'data/vectorNgrammized.txt')
"""
