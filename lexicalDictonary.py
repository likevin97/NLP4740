import os
import string
from string import whitespace
import csv
from collections import defaultdict

def lexical_dictonary(fname):
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

def lexical_probabilities(lex_dict):
	lex_prob = defaultdict(lambda: defaultdict(int))

	for key in lex_dict.keys(): #key is B-ORG
		total = sum(lex_dict[key].values())
		for k in lex_dict[key] : #key is a token
			lex_dict[key][k] /= float(total) 
			print (lex_dict[key])
			print (lex_dict[key][k])
def main():
	
	lex_dict = lexical_dictonary("sample.txt")
	lexical_probabilities(lex_dict)
	#print (lex["B-ORG"])
	pass

main()