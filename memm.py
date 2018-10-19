import os
import string
from string import whitespace
import csv
from collections import defaultdict
import numpy as np
from hmm import *

TAGS = ["B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC" ,"O"]

def pos_tag_dict(fname):
	train = open(fname, "r")
	pos_tag_dict = defaultdict(lambda: defaultdict(int))

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
				pos_tag_dict[bio[tag]][pos[tag]] += 1
		counter +=1

	return pos_tag_dict

def pos_tag_probabilities(pos_tag_dict):
	pos_tag_prob = pos_tag_dict

	for key in pos_tag_prob.keys(): #key is B-ORG
		total = sum(pos_tag_prob[key].values())
		for k in pos_tag_prob[key] : #key is a token
			pos_tag_prob[key][k] /= float(total) 
	
	return pos_tag_prob

def pos_to_word_counts(fname):
    train = open(fname, "r")
    pos_to_word_dict = defaultdict(lambda: defaultdict(int))

    tokens = []
    pos = []
    bio = []
    counter = 0

    for line in train:
        if counter % 3 == 0:
            tokens = line.split()
        if counter % 3 == 1:
            pos = line.split()
        if counter % 3 == 2:
            bio = line.split()
            # at this point, tokens, pos, and bio all have the same length
            for pos_index in range(len(pos)):
                pos_to_word_dict[pos[pos_index]][tokens[pos_index]] += 1
        counter += 1

    return pos_to_word_dict


def pos_to_word_probabilities(pos_to_word_dict):
    pos_to_word_prob = pos_to_word_dict

    for key in pos_to_word_prob.keys():  # key is B-ORG
        total = sum(pos_to_word_prob[key].values())
        for k in pos_to_word_prob[key]:  # key is a token
            pos_to_word_prob[key][k] /= float(total)

    return pos_to_word_prob

def tag_probabilities(filename):
    train = open(filename, "r")
    tag_counts = defaultdict(int)
    counter = 0
    for line in train:
        # You are on the BIO tag line
        if counter % 3 == 2:
            line_array = line.split()
            for tag in line_array:
                tag_counts[tag] += 1
        counter += 1

    total = sum(tag_counts.values())

    for key in tag_counts.keys():  # key is B-ORG
        tag_counts[key] /= float(total)

    return tag_counts

def memm(training_file, test_file):
	pos_tag = pos_tag_dict(training_file)
 	pos_tag_prob = pos_tag_probabilities(pos_tag)
 	pos_word = pos_to_word_counts(training_file)
 	pos_word_prob = pos_to_word_probabilities(pos_word)
 	lex = lexical_dictonary(training_file)
	lex_prob = lexical_probabilities(lex)
	tag_prob = tag_probabilities(training_file)
	#need the probs(tag)
 	#how do we do start??

 	test = open(test_file, "r")
 	tokens = []
	pos = []
	index = [] #index for testing, or correct bio for validation
	predictions = []

	counter = 0

	for line in test:
		if counter % 3 == 0:
			tokens = line.split()
		if counter % 3 == 1:
			pos = line.split()
		if counter %3 == 2:
			index = line.split()

			max_array = []
			for j in range(len(index)): #word = index[j]
				prob_arr = [0 for i in range(len(TAGS))]
				for i in range(len(TAGS)): #tag want to compute for TAGS[i]
					y = pos_word_prob[pos[j]][tokens[j]]

					print (pos[j])
					print (index[j])
					print (y)



					if y != 0:
						l = lex_prob[TAGS[i]][tokens[j]]
						p_t = pos_tag_prob[TAGS[i]][pos[j]]
						t = tag_prob[TAGS[i]]
						prob_arr[i] =  l * p_t * t / y
				x = np.argmax(prob_arr) #x gives me the index of the best tag
				max_array.append(TAGS[x]) #max array will hold the best tag predictions for each word 

			predictions.append(max_array)

		counter +=1

	return predictions


def main():
 	

 	pred = memm("training.txt", "sample.txt")
 	print (pred)


main()
