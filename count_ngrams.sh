#!/bin/bash
# counts the n-gram frequencies using standard UNIX tools

NGRAM_FILE="./data/ngrams.txt"
CORPUS_FILE="./data/simplewiki_corpus.txt"
TEMP_FILE=$(mktemp)

cat $CORPUS_FILE | tr "[:upper:]" "[:lower:]" >> $TEMP_FILE

cat $NGRAM_FILE | while read -r line
do
	printf "$line "
	cat $TEMP_FILE | grep -w -o "$line" | wc -l
done

rm $TEMP_FILE
