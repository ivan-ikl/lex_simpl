from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.snowball import SnowballStemmer
import time
import sys
import re


current_progress = 0
ngram_file = './data/ngrams.txt'
longest_ngram = 0

# Specifies wheather to print information about operation progress
verbose = True


def resetProgress():
    """Resets progress meter which is printed on the screen"""
    global current_progress
    current_progress = 0


def printProgress(printFrequency):
    """Prints the current progress every few turns"""
    global current_progress
    global verbose
    current_progress += progress
    if (verbose and current_progress % printFrequency) == 0:
        print(current_progress)


def load_ngrams():
    """Loads n-grams from the default file"""

    global longest_ngram
    longest_ngram = 0
    ngrams = set()
    resetProgress()

    with open(ngram_file) as text:
        for line in text:
            if line.strip().count(" "):
                ngrams.add("_".join(line.split()))
            """
            words = word_tokenize(line)
            ngram = []

            printProgress(1000)

            for j in words:
                ngram.append(stemmer.stem(j).lower())

            longest_ngram = max(longest_ngram, len(ngram))
            ngrams.add("_".join(ngram))
            """

    return ngrams


def parse_sentences(corpus):
    """Splits the text into sentence-wise groups of words
        (list of lists of words)"""

    #stemmer = SnowballStemmer("english")
    sentences = sent_tokenize(corpus)

    """
    #list of lists of words paired with their stems
    corpusSentences = []
    resetProgress()
    """
    print("[%s] corpus sentence-tokenized"%time.ctime(),
        file=sys.stderr)

    # parse sentences into lists of words, without punctuation
    ret = []
    for sentence in sentences:
        ret.append( [token for token in word_tokenize(sentence)
                            if token[0].isalnum()] )
    return ret

"""
    for sentence in sentences:

        words = word_tokenize(i)
        corpusSentence = []

        for j in words:
            # Remove punctuation
            if (j not in [".", "!", "?", ",", ";", ":"]):
                corpusSentence.append((j, stemmer.stem(j)))

        corpusSentences.append(corpusSentence)
        printProgress(1000)

    return corpusSentences
    """


def findNgram(sentence, index, ngrams):
    """Returns the length of the found n-gram
        or the individual word if none is found"""

    global longest_ngram

    # Find applicable n-gram
    for ngramlength in range(min(length - index, longest_ngram), 0, -1):

        #test each n-gram
        currentNgram = []
        for i in range(0, ngramlength):
            currentNgram.append(sentence[index + i][1])

        #Was an n-gram found?
        if ("_".join(currentNgram) in ngrams):
            #print(str(index) + " " + "_".join(currentNgram))
            return ngramlength

    #print ("- " + str(index) + " " + sentence[index + i][1])
    return 1


def ngrammizeSentences(corpusSentences):
    """Groups words inside the loaded sentence structure
        into ngrams using underscores"""

    resetProgress()

    for sentence in corpusSentences:

        length = len(sentence)
        ngrammized = []
        skipping = 0

        printProgress(1000)

        for index in range(0, length):
            if (index < skipping):
                continue

            foundNgram = findNgram(sentence, index, ngrams, longest)

            if (foundNgram == 1):
                ngrammized.append(sentence[index])
            else:
                currentWord = ""
                currentStem = ""

                for i in range(0, foundNgram):

                    if (currentWord != ""):
                        currentWord += "_"
                        currentStem += "_"

                    currentWord += sentence[index + i][0]
                    currentStem += sentence[index + i][1]

                skipping = index + foundNgram

                ngrammized.append((currentWord, currentStem))

        ngrammizedSentences.append(ngrammized)

    return ngrammizedSentences


# for ngrams that have other ngrams as prefixes, 
#  it finds them, and returns a dict in the form of 
#   { ngram:[prefix_ngram1, prefix_ngram2, ... ] }
def find_prefixes(ngrams):

    def is_prefix(prefix, word):
        # the extra space check is necessary
        #  for cases such as "to be" and "to become"
        return word.startswith(prefix+" ")
    
    # a weaker condition, so we don't miss short prefixes
    def loop_condition(prefix, word):
        p = prefix.split()
        w = word.split()
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


# Turns an ngram prefix table into an inverse one
#  so instead of looking up prefixes of ngrams, we look up 
#  the prefixed ngrams; I couldn't find a proper name for this.
def make_inverse_prefix_table(prefix_table):
    inverse_prefix_table = {}

    for ngram in prefix_table.keys():
        for prefix in prefix_table[ngram]:
            inverse_prefix_table[prefix] = ngram

    return inverse_prefix_table


"""
# creates regex match objects for the ngrams
def make_ngram_regexps(ngrams):
    regexps = {}
    for ngram in ngrams:
        s = ngram.replace("_"," ")
        regexps[ngram] = re.compile(s)
    return regexps
"""

# detects the longest ngram in the sentence, starting with the i-th word
def find_ngram(sentence, i, ngrams, inverse_prefix_table):
        s = sentence[i]
        j = i+1
        while j<len(sentence):
            s += sentence[j]
            if s in ngrams:
                # if there's no ngram longer than this one
                if s not in inverse_prefix_table:
                    return s
                # otherwise, it means we can look up the longest one
                else:
                    return max(inverse_prefix_table[s], key=len)
            j += 1

        return None


def substitute_ngrams(sentences, ngrams, prefix_table):

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
        for i in range(len(sentence)):
            if sentence[i] in start_words:
                # try to detect the ngram
                ngram = find_ngram(sentence, i, ngrams, inverse_prefix_table)
                # if there is one, do the substitution
                if ngram:
                    length = ngram.count("_")+1
                    sentence[i] = ngram
                    for j in range(1,length+1):
                        del sentence[j]
    return sentences
