import os
import string
from string import whitespace
import csv
from collections import defaultdict

def lexical_dictonary(fname):
	train = open(fname, "r")
	lex_dict = defaultdict(lambda: defaultdict(int))

	seen = set()

	tokens = []
	pos = []
	bio = []
	counter = 0



	for line in train:
		if counter % 3 == 0:
			tokens = line.split()

			for token in tokens:
				seen.add(token)

		if counter % 3 == 1:
			pos = line.split()
		if counter %3 == 2:
			bio = line.split()
			#at this point, tokens, pos, and bio all have the same length
			for tag in range(len(bio)):
				lex_dict[bio[tag]][tokens[tag]] += 1
		counter +=1

	return lex_dict, seen

def lexical_probabilities(lex_dict):
	lex_prob = lex_dict

	for key in lex_prob.keys(): #key is B-ORG
		total = sum(lex_prob[key].values())
		for k in lex_prob[key] : #key is a token
			lex_prob[key][k] /= float(total) 



	return lex_prob

# def main():
	
# 	lex_dict = lexical_dictonary("training.txt")
# 	lex_prob_dict = lexical_probabilities(lex_dict)


# main()