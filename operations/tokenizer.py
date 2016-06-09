from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.snowball import SnowballStemmer


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
        for i in text:
            words = word_tokenize(i)
            ngram = []

            printProgress(1000)

            for j in words:
                ngram.append(stemmer.stem(j).lower())

            longest_ngram = max(longest_ngram, len(ngram))
            ngrams.add("_".join(ngram))

    return ngrams


def parse_sentences(corpus):
    """Splits the text into sentence-wise groups of words
        (list of lists of words)"""

    stemmer = SnowballStemmer("english")
    sentences = sent_tokenize(corpus.read().lower())

    #list of lists of words paired with their stems
    corpusSentences = []
    resetProgress()

    for i in sentences:

        words = word_tokenize(i)
        corpusSentence = []

        for j in words:
            # Remove punctuation
            if (j not in [".", "!", "?", ",", ";", ":"]):
                corpusSentence.append((j, stemmer.stem(j)))

        corpusSentences.append(corpusSentence)
        printProgress(1000)

    return corpusSentences


def findNgram(sentece, index, ngrams):
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
