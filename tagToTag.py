from collections import defaultdict

TAGS = ["B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC", "O"]


def transition_probabilities(fname):
    train = open(fname, "r")
    trans_dict = defaultdict(lambda: defaultdict(int))
    counter = 0
    for line in train:
        # You are on the BIO tag line
        if counter%3 == 2:
            line_array = line.split()
            for bioTagIndex in range(1, len(line_array)):
                prevTag = line_array[bioTagIndex - 1]
                currTag = line_array[bioTagIndex]
                trans_dict[prevTag][currTag] += 1
        counter += 1
    return trans_dict

def main():

    print ("Dictionary Output: ")
    transitionProbabilities =  (transition_probabilities("training.txt"))
    print ("End debug mode")


main()