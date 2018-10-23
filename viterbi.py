from hmm import *

TAGS = ["O", "B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC"]

def viterbi(line, start, transition, lex, seen_words):
	#for a single line
	#initalization
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

	#iteration
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
	#identify sequence
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

	for i in range(len(tokens)-2, -1, -1): #this will do all the other words
		max_array.insert(0, backpointer[max_array[0]][i+1])

	return max_array



# def main():
# 	start = startToTagDictionary("sample.txt")
# 	transition_dict = transition_counts("sample.txt")
# 	transition_probs = transition_probabilities(transition_dict)
# 	lex_dict, seen_words = lexical_dictonary("sample.txt")
# 	lex_prob_dict = lexical_probabilities(lex_dict)
#
# 	test = open("sample.txt", "r")
# 	tokens = []
# 	pos = []
# 	index = [] #index for testing, or correct bio for validation
#
# 	total_predictions = []
#
# 	counter = 0
# 	for line in test:
# 		if counter % 3 == 0:
# 			tokens = line.split()
# 		if counter % 3 == 1:
# 			pos = line.split()
# 		if counter %3 == 2:
# 			index = line.split()
# 			predictions = viterbi(tokens, start, transition_probs, lex_prob_dict, seen_words)
# 			total_predictions.append(predictions)
# 		counter += 1
#
# 	print (total_predictions)
# 	print (convertArrayToBIOTags(total_predictions))
#main()