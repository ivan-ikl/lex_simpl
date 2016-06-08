from collections import Counter


def build_context_vector(sentences, max_offset):
	"""Creates the context vector with max_offset words to the left and to the right counted"""

	vectors = {}

	resetProgress()
	
	for words in sentences:
			
		printProgress(1000)
		
		# iteration through every word of the sentence
		for word_index in range(0, len(words)):
			
			current_word = words[word_index][0]
			
			# if current_word hasn't appeared yet, initialize its counter
			if current_word not in vectors.keys():
				vectors[current_word] = Counter()

			# getting the current counter from the dictionary
			current_counter = vectors[current_word]

			for offset in range(1, max_offset + 1):
				
				# checking if the context word can be indexed
				if word_index-offset > 0:
					current_counter.update([words[word_index-offset]])

				if word_index+offset < len(words):
					current_counter.update([words[word_index+offset]])

	return vectors;


def save_context_vector(vectors, filename):
	"""Saves the list of context vectors into the specified file"""

	keys = vectors.keys()
	out = "";

	for key in keys:
		
		out+=key
		counter = vectors[key]
		
		for k in counter:
			out += " " + k + ":" + str(counter[k])

		out += "\n"

	with open(filename, "w") as output:
		output.write(out)


def load_context_vector(filename):
	"""Loads context vectors from the specified file"""
	
	vectors = {}
	
	with open(filename) as lines:
	
		for line in lines:
			if line != '':
	
				words = line.split()
				vectors[words[0]] = dict(map(lambda p: (p[0], p[1]), map(lambda w: w.split(':'), filter(lambda w: w.count(':') == 1, words))))
			
	return vectors
