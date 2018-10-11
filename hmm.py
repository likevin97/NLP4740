import os
import string
from string import whitespace
import csv
from collections import defaultdict
from tagToTag import *
from lexicalDictonary import *

TAGS = ["B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC" ,"O"]

def startToTagDictionary(filename):
    train = open(filename, "r")
    start_counts = defaultdict(float)
    counter = 0

    for line in train:
        if counter % 3 == 2:
            line_array = line.split()
            first_tag = line_array[0]
            start_counts[first_tag] += 1.0
        counter += 1

    total_sentences = counter / 3

    for start_key in start_counts:
        start_counts[start_key] = start_counts[start_key] / total_sentences

    return start_counts

def hmm_initialize(start, line, lex):
	#LINE IS ALREADY SPLIT. IS AN ARRAY

	score = [[0.0 for y in range(len(line))] for x in range(len(TAGS))]
	backpointer = [[0.0 for y in range(len(line))] for x in range(len(TAGS))]
	for i in range(len(TAGS)):
		score[i][0] = float(start[TAGS[i]]) * float(lex[TAGS[i]][line[0]])
		backpointer[i][0] = 0
	return score, backpointer
	

def hmm_iteration(score, backpointer, line, transition, lex):
	for token in range(1,len(line)): #index of 1 represents the 2nd word
		for i in range(len(TAGS)):
			max_score = 0
			for j in range(len(TAGS)):
				s = score[j][token-1]
				if s > max_score:
					max_score = s
			#score[TAGS[i]][token] = max_score * transition[]

def hmm(fname,lex, transition, start):
	test = open(fname, "r")
	tokens = []
	pos = []
	index = [] #index for testing, or correct bio for validation

	counter = 0
	for line in test:
		if counter % 3 == 0:
			tokens = line.split()
		if counter % 3 == 1:
			pos = line.split()
		if counter %3 == 2:
			index = line.split()

			score,backpointer = hmm_initialize(start, tokens, lex)

		counter +=1


def main():
	transition_dict = transition_counts("training.txt")
	transition_probs = transition_probabilities(transition_dict)

	lex_dict = lexical_dictonary("training.txt")
	lex_prob_dict = lexical_probabilities(lex_dict)

	start_prob = startToTagDictionary("training.txt")

	line = "played on Monday"
	line = line.split()

	score, backpointer = hmm_initialize(start_prob, line, lex_prob_dict)

	#print (lex_prob_dict)
	#print ("======")

	print (start_prob)
	print ("========")

	print (score)
	print ("=======")
	print (backpointer)

	#hmm("sample.txt", lex_dict, transition_dict)

main()