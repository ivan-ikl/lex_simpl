#!/bin/bash
# corrects the SemEval xml input,
#  which doesn't parse in its original form

INPUT_FILE='contexts.xml'

if [ $1 ]; then
	INPUT_FILE=$1
fi

sed -r 's_(&#[[:digit:]]{4}) ;_\1;_g' $INPUT_FILE
