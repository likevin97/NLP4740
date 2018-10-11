import os
import string
from string import whitespace
import csv
from collections import defaultdict

def lexical_probabilities(fname):
	train = open(fname, "r")
	lex_dict = defaultdict(lambda: defaultdict(int))

	tokens = []
	pos = []
	bio = []
	counter = 0

	for line in train:
		if counter % 3 == 0:
			tokens = line.split()
		if counter % 3 == 1:
			pos = line.split()
		if counter %3 == 2:
			bio = line.split()

			#at this point, tokens, pos, and bio all have the same length
			for tag in range(len(bio)):
				if bio[tag] != "O":
					#print (bio[tag][:2])
					lex_dict[bio[tag]][tokens[tag]] += 1
		counter +=1

	return lex_dict



def main():
	
	lex = lexical_probabilities("sample.txt")
	print (lex["B-ORG"])
	pass

main()