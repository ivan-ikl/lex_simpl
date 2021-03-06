from collections import Counter, defaultdict
import sys

def build_context_vectors(list_of_sentences, max_offset, cutoff=1):
    """Builds a context vector.
    Arguments:
        list_of_sentences -- a list of sentences to process,
                             each sentence being a list of word-tokens.
        max_offset -- the radius of the sliding window
        cutoff -- words with frequencies below cutoff will be
                  thrown out of the produced vectors

    Return value:
        the context vector returned is a defaultdict of word:context records,
        where context is a Counter
        So, for "fox" in "The quick brown fox jumps over the lazy dog", 
        with a window radius of 2, context_vectors["fox"] would be
        a Counter({'quick': 1, 'brown': 1, 'jumps': 1, 'over': 1}).
    """

    context_vectors = defaultdict(lambda: Counter())

    progress = 0

    print("generating context vectors", file=sys.stderr)
    for sentence in list_of_sentences:

        progress += 1
        if (progress%10000==0):
            print("%s out of %i sentences done"% \
                    (progress, len(list_of_sentences)), file=sys.stderr)

        # iteration through every word of the sentence
        for i in range(0, len(sentence)):

            word = sentence[i]

            # get this word's counter from the dictionary
            current_counter = context_vectors[word]

            # count the context words
            offset = max_offset
            to_add = sentence[max(0,i-offset) : i] + sentence[i+1 : i+offset+1]
            current_counter.update(to_add)

    # cut off low frequency words, i.e. remove hapax legomena
    if cutoff>1:
        filter_context_vectors(context_vectors, cutoff)

    return context_vectors


def filter_context_vectors(context_vectors, cutoff):
    """Filters out the context words with values strictly below cutoff."""
    for word in context_vectors.keys():
        cv = context_vectors[word]
        temp = Counter({ x:cv[x] for x in cv if cv[x]>=cutoff })
        context_vectors[word] = temp


def save_context_vectors(context_vectors, output_file):
    """Saves the list of context vectors into the given stream, 
        ignoring words that contain the delimiter"""

    # for each word in the corpus
    for word in sorted(context_vectors.keys()):
        line = word
        # context vector is a Counter() with word:frequency
        context_vector = context_vectors[word]

        # write out each recorded context word along with its frequency
        for cw in sorted(context_vector):
            line += " "+cw+" "+str(context_vector[cw])

        print(line, file=output_file)


def load_context_vectors(input_file):
    """Loads context vectors from the specified file"""

    context_vectors = defaultdict(lambda:Counter())
    for line in input_file:
        if line:
            words = line.split()
            head = words[0]
            tail = words[1:]
            # tail[0::2] are the words found in context
            # tail[1:.2] are their respective frequencies
            d = Counter(dict(zip( tail[::2], map(int, tail[1::2]) )))
            context_vectors[ head ] = d

    return context_vectors
