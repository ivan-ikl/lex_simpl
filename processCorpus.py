from operations import *
from collections import Counter

ps = SnowballStemmer("english")

ngrams = load_ngrams()
corpusSentences = parse_sentences(open("./Bitno/simplewiki_corpus.txt"))
ngrammizedSentences = ngrammizeSentences(corpusSentences)


# Fill out the output files for the next stage
outwords = []


# Output the source corpus sentence list
with open("data/outSentences.txt", "w") as sourceSentences:

    for sentence in corpusSentences:
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

vectors = build_context_vector(corpusSentences, 4)
save_context_vector(vectors, 'data/outSentences.txt')

ngramVectors = build_context_vector(ngrammizedSentences, 4)
save_context_vector(ngramVectors, 'data/vectorNgrammized.txt')
