import os
import string
from string import whitespace
import csv
from collections import defaultdict
from tagToTag import *
from lexicalDictonary import *

TAGS = ["O", "B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC"]

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

def indexToBIOTag(backpointer):

	newBackpointer = [[0.0 for y in range(len(backpointer[0]))] for x in range(len(backpointer))]

	for outerIndex in range(len(backpointer)):
		for innerIndex in range(len(backpointer[0])):
			tagIndex = backpointer[outerIndex][innerIndex]
			if (tagIndex == -1):
				newBackpointer[outerIndex][innerIndex] = "Start"
			else:
				newBackpointer[outerIndex][innerIndex] = TAGS[tagIndex]

	return newBackpointer

def hmm_initialize(start, line, seen_words, lex):
	#LINE IS ALREADY SPLIT. IS AN ARRAY

	score = [[0.0 for y in range(len(line))] for x in range(len(TAGS))]
	backpointer = [[0 for y in range(len(line))] for x in range(len(TAGS))]
	for i in range(len(TAGS)):
		if line[0] not in seen_words:
			if (TAGS[i] == "O"):
				score[i][0] = 1
			else:
				score[i][0] = 0
		else:
			score[i][0] = float(start[TAGS[i]]) * float(lex[TAGS[i]][line[0]])
		#score[i][0] = float(lex[TAGS[i]][line[0]])
		backpointer[i][0] = 0
	return score, backpointer
	

def hmm_iteration(score, backpointer, line, transition, seen_words, lex):
	for token in range(1,len(line)): #index of 1 represents the 2nd word
		for i in range(len(TAGS)):
			max_score = 0.0
			max_index = 0
			for j in range(len(TAGS)):
				s = score[j][token-1] * transition[TAGS[j]][TAGS[i]]
				if s > max_score:
					max_score = s
					max_index = j
			if line[token] not in seen_words:
				if (TAGS[i] == "O"):
					score[i][token] = 1
				else:
					score[i][token] = 0
			else:
				score[i][token] = max_score
				score[i][token] = max_score * lex[TAGS[i]][line[token]]
			backpointer[i][token] = max_index
			#score[TAGS[i]][token] = max_score * transition[]

def hmm_identify_sequence(score, backpointer, line):
	max_array = []
	max_index = 0
	max_score = 0.0
	for i in range(len(TAGS)): #this is only for the last token (aka word n)
		s = score[i][len(line)-1]
		if s > max_score:
			max_score = s
			max_index = i

	max_array.insert(0,max_index)

	for i in range(len(line)-2, -1, -1): #this will do all the other words
		max_array.insert(0, backpointer[max_array[0]][i+1])

	return max_array


def hmm(trainingfile, testfile):
	transition_dict = transition_counts(trainingfile)
	transition_probs = transition_probabilities(transition_dict)
	lex_dict, seen_words = lexical_dictonary(trainingfile)
	lex_prob_dict = lexical_probabilities(lex_dict)

	start_prob = startToTagDictionary(trainingfile)

	test = open(testfile, "r")
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

			score, backpointer = hmm_initialize(start_prob, tokens, seen_words, lex_prob_dict)
			hmm_iteration(score, backpointer, tokens, transition_probs, seen_words, lex_prob_dict)
			max_array = hmm_identify_sequence(score, backpointer, tokens)

			predictions.append(max_array)

		counter +=1

	return predictions



def hmm_addk_initialize(start, line, seen_words, lex):
	# LINE IS ALREADY SPLIT. IS AN ARRAY

	score = [[0.0 for y in range(len(line))] for x in range(len(TAGS))]
	backpointer = [[0 for y in range(len(line))] for x in range(len(TAGS))]
	for i in range(len(TAGS)):
		if line[0] not in seen_words:
			score[i][0] = float(start[TAGS[i]]) * float(lex[TAGS[i]]["<UNK>"])
		else:
			score[i][0] = float(start[TAGS[i]]) * float(lex[TAGS[i]][line[0]])
		# score[i][0] = float(lex[TAGS[i]][line[0]])
		backpointer[i][0] = 0
	return score, backpointer


def hmm_addk_iteration(score, backpointer, line, transition, seen_words, lex):
	for token in range(1, len(line)):  # index of 1 represents the 2nd word
		for i in range(len(TAGS)):
			max_score = 0.0
			max_index = 0
			for j in range(len(TAGS)):
				s = score[j][token - 1] * transition[TAGS[j]][TAGS[i]]
				if s > max_score:
					max_score = s
					max_index = j
			if line[token] not in seen_words:
				score[i][token] = max_score * lex[TAGS[i]]["<UNK>"]
			else:
				score[i][token] = max_score * lex[TAGS[i]][line[token]]
			backpointer[i][token] = max_index
	# score[TAGS[i]][token] = max_score * transition[]



def hmm_addk_identify_sequence(score, backpointer, line):
	max_array = []
	max_index = 0
	max_score = 0.0
	for i in range(len(TAGS)):  # this is only for the last token (aka word n)
		s = score[i][len(line) - 1]
		if s > max_score:
			max_score = s
			max_index = i

	max_array.insert(0, max_index)

	for i in range(len(line) - 2, -1, -1):  # this will do all the other words
		max_array.insert(0, backpointer[max_array[0]][i + 1])

	return max_array


def hmm_addk(trainingfile, testfile, k):
	transition_dict = transition_counts(trainingfile)
	transition_probs = transition_probabilities(transition_dict)
	lex_dict, seen_words = lexical_dictonary(trainingfile)
	lex_addk_prob_dict = lexical_addk_probabilities(lex_dict, k)

	start_prob = startToTagDictionary(trainingfile)

	test = open(testfile, "r")
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

			score, backpointer = hmm_addk_initialize(start_prob, tokens, seen_words, lex_addk_prob_dict)
			hmm_addk_iteration(score, backpointer, tokens, transition_probs, seen_words, lex_addk_prob_dict)
			max_array = hmm_addk_identify_sequence(score, backpointer, tokens)

			predictions.append(max_array)

		counter +=1

	return predictions


def convertArrayToBIOTags(array):
	#new_array = [0 for i in range(len(array))]
	new_array=[]

	for i in range(len(array)):
		new_sub_array = []
		for j in range(len(array[i])):
			new_sub_array.append(TAGS[array[i][j]])
		new_array.append(new_sub_array)

	return new_array


# def main():
# # 	# transition_dict = transition_counts("training.txt")
# # 	# transition_probs = transition_probabilities(transition_dict)
# # 	# lex_dict = lexical_dictonary("training.txt")
# # 	# lex_prob_dict = lexical_probabilities(lex_dict)
# #
# # 	# start_prob = startToTagDictionary("training.txt")
# #
# #
# #
# # 	#score, backpointer = hmm_initialize(start_prob, line, lex_prob_dict)
# # 	#hmm_iteration(score, backpointer, line, transition_probs, lex_prob_dict)
# #
# # 	#backpointer_with_tags = indexToBIOTag(backpointer)
# # 	#print (backpointer_with_tags)
# #
# # 	#max_array = hmm_identify_sequence(score, backpointer, line)
# #
#
# 	max_array = hmm("training.txt","sample_test.txt")
#
# 	print ("HMM Predictions: ")
#
# 	print convertArrayToBIOTags(max_array)
# #
# # 	print ("--------")
# #
# main()