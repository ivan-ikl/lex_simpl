import sys
import time
from operations import *
from collections import defaultdict, Counter
CORPUS_FILENAME =       "./input_data/simplewiki_corpus.txt"
NGRAM_FILENAME =        "./input_data/ngrams.txt"
UNIGRAM_FREQ_FILENAME = "./output_data/unigram_frequencies"
NGRAM_FREQ_FILENAME =   "./output_data/ngram_frequencies"
CV_FILENAME =           "./output_data/context_vectors"
NGRAM_CV_FILENAME =     "./output_data/ngram_context_vectors"

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
with open(NGRAM_FILENAME) as infile:
    ngrams = load_ngrams(infile)
prefix_table = find_prefixes(ngrams)
log("loaded n-grams, built prefix table")

# load the corpus and split it into sentences
with open(CORPUS_FILENAME) as infile:
    corpus = infile.read().lower()
corpus = parse_sentences(corpus)
# the corpus is now a list of sentences, each sentence being
#  a list of words/tokens (without punctuation)
log("parsed corpus into sentences")

# for each sentence, substitute the ngrams with their underscored forms
#  (longest possible ngram)
ngramized_sentences = substitute_ngrams(corpus, ngrams, prefix_table)
log("made n-gramized corpus sentences")

# now, count the unigram frequencies
c = Counter()
for sentence in corpus:
    c.update(sentence)
log("counted unigram frequencies")
with open(UNIGRAM_FREQ_FILENAME, "w") as fajl:
    for unigram in sorted(c):
        print(unigram+" "+str(c[unigram]), file=fajl)
log("wrote unigram frequencies to %s" % UNIGRAM_FREQ_FILENAME)

# and the ngram frequencies:
#  count the 'unigram' frequencies on the n-gramized corpus
nc = Counter()
for sentence in ngramized_sentences:
    nc.update(sentence)
#  filter out the real unigrams
nc = Counter(dict([(x,nc[x]) for x in nc if x in ngrams]))
#  and take care of the prefixes
for ngram in prefix_table:
    for prefix in prefix_table[ngram]:
        if nc[ngram]:
            nc[ prefix ] += nc[ngram]
log("counted n-gram frequencies")

with open(NGRAM_FREQ_FILENAME, "w") as fajl:
    #for ngram in sorted(nc):
    for ngram in sorted(ngrams):
        print(ngram+" "+str(nc[ngram]), file=fajl)
log("wrote n-gram frequencies to %s" % NGRAM_FREQ_FILENAME)

# generate the context vectors for the unigrams
context_vectors = build_context_vectors(corpus, 4)
log("built context vectors")
# and write them out
with open(CV_FILENAME, "w") as outfile:
    save_context_vectors(context_vectors, outfile)
log("wrote context vectors to "+CV_FILENAME)

# now, generate the context vectors for the n-grams
ngram_CVs = build_context_vectors(ngramized_sentences, 4)
# filter out  the unigram's CVs
ngram_CVs = defaultdict(
                lambda:Counter(),
                dict([(x, ngram_CVs[x]) for x in ngram_CVs if x in ngrams]))
# and take care of the prefixes
for ngram in prefix_table:
    for prefix in prefix_table[ngram]:
        diff = set(ngram.split("_")) - set(prefix.split("_"))
        for word in diff:
            ngram_CVs[prefix][word] += nc[ngram]
log("built n-gram context vectors")
        
with open(NGRAM_CV_FILENAME, "w") as outfile:
    save_context_vectors(ngram_CVs, outfile)
log("wrote n-gram context vectors to "+NGRAM_CV_FILENAME)
