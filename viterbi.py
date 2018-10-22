from hmm import *

TAGS = ["O", "B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC"]

def viterbi(tokens, start, transition, lexical):
	#for a single line
	#initalization
	score = [[0.0 for y in range(len(tokens))] for x in range(len(TAGS))]
	backpointer = [[0.0 for y in range(len(tokens))] for x in range(len(TAGS))]
	c = len(TAGS)
	for i in range(c):
		if lexical[TAGS[i]][tokens[0]] == 0:
			score[i][0] = 0
		else:
			# Try without the start prob
			score[i][0] = float(start[TAGS[i]]) * lexical[TAGS[i]][tokens[0]]
		backpointer[i][0] = 0

	#iteration
	for t in range(1, len(tokens)):
		for i in range(c):
			maxscore = 0
			maxindex = -1
			for j in range(c):
				s = score[j][t-1]*transition[TAGS[j]][TAGS[i]]
				print(s)
				if s > maxscore:
					maxscore = s
					maxindex = j
			x = lexical[TAGS[i]][tokens[t]]
			if (x != 0):
				score[i][t] = maxscore * lexical[TAGS[i]][tokens[t]]
			else:

				score [i][t] = maxscore
			backpointer[i][t] = maxindex
	#identify sequence
	max_array = []
	max_index = 0
	max_score = 0
	for i in range(len(TAGS)): #this is only for the last token (aka word n)
		s = score[i][len(tokens)-1]
		if s > max_score:
			max_score = s
			max_index = i

	max_array.insert(0,max_index)

	for i in range(len(tokens)-2, -1, -1): #this will do all the other words
		max_array.insert(0, backpointer[max_array[0]][i+1])

	return max_array



def main():
	start = startToTagDictionary("sample.txt")
	transition_dict = transition_counts("sample.txt")
	transition_probs = transition_probabilities(transition_dict)
	lex_dict = lexical_dictonary("sample.txt")
	lex_prob_dict = lexical_probabilities(lex_dict)

	test = open("sample.txt", "r")
	tokens = []
	pos = []
	index = [] #index for testing, or correct bio for validation

	total_predictions = []

	counter = 0
	for line in test:
		if counter % 3 == 0:
			tokens = line.split()
		if counter % 3 == 1:
			pos = line.split()
		if counter %3 == 2:
			index = line.split()
			predictions = viterbi(tokens, start, transition_probs, lex_prob_dict)
			total_predictions.append(predictions)
		counter += 1

	print (total_predictions)
	print (convertArrayToBIOTags(total_predictions))
main()