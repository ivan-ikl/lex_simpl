output_filename := test_output
gold_rankings_location := test-data
#gold_rankings_location := trial-dataset

test:
	python3 ./rank-scorer.py -i test_output -g $(gold_rankings_location)/substitutions.gold-rankings

verbose:
	python3 ./rank-scorer.py -v -i test_output -g $(gold_rankings_location)/substitutions.gold-rankings

create:
	python3 ./main.py test-data/contexts_rectified.xml $(gold_rankings_location)/substitutions > $(output_filename)

#optimize:
#	python3 ./optimize.py
