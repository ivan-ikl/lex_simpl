output_filename := test_output
which_dataset := trial-dataset
#which_dataset := test-data

test:
	python3 ./rank-scorer.py -i test_output -g $(which_dataset)/substitutions.gold-rankings

verbose:
	python3 ./rank-scorer.py -v -i test_output -g $(which_dataset)/substitutions.gold-rankings

create:
	python3 ./main.py $(which_dataset)/contexts_rectified.xml $(which_dataset)/substitutions > $(output_filename)

process:
	python3 ./processCorpus.py

#optimize:
#	python3 ./optimize.py
