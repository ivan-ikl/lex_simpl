from collections import Counter, defaultdict
#from tokenizer import *


def build_context_vector(list_of_sentences, max_offset):
    """Creates the context vector
        with max_offset words to the left
        and to the right counted"""

    context_vectors = defaultdict(lambda: Counter())

    resetProgress()

    for sentence in list_of_sentences:

        printProgress(1000)

        # iteration through every word of the sentence
        for i in range(0, len(sentence)):

            word = sentence[i][0]

            # get this word's counter from the dictionary
            current_counter = context_vectors[word]

            # count the context words
            for offset in range(1, max_offset + 1):

                # check if the context word can be indexed
                if i-offset > 0:
                    current_counter.update([sentence[i-offset]])

                if i+offset < len(sentence):
                    current_counter.update([sentence[i+offset]])

    return context_vectors


def save_context_vector(vectors, filename):
    """Saves the list of context vectors into the specified file"""

    with open(filename, "w") as output:

        # for each word in the corpus
        for word in vectors.keys():
            line = word
            freq_counter = vectors[key]
    
            # write out each recorded context word along with its frequency
            for cw in freq_counter:
                line += " "+cw+":"+str(freq_counter[cw])
            
            print(line, file=output)


def load_context_vector(filename):
    """Loads context vectors from the specified file"""

    vectors = {}
    with open(filename) as lines:
        for line in lines:
            if line:
                head = words[0]
                d = { w.split(":")[0]: w.split(":")[1] for w in words[1:]}
                vectors[ head ] = d

    return vectors
