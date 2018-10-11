from collections import defaultdict


def transition_counts(filename):
    train = open(filename, "r")
    trans_counts = defaultdict(lambda: defaultdict(int))
    counter = 0
    for line in train:
        # You are on the BIO tag line
        if counter % 3 == 2:
            line_array = line.split()
            for bioTagIndex in range(1, len(line_array)):
                prev_tag = line_array[bioTagIndex - 1]
                curr_tag = line_array[bioTagIndex]
                trans_counts[prev_tag][curr_tag] += 1
        counter += 1
    return trans_counts


def transition_probabilities(trans_counts):
    trans_probs = defaultdict(lambda: defaultdict(float))

    for prevTagKey in trans_counts.keys():
        prev_tag_dict = trans_counts[prevTagKey]
        prev_total = sum(prev_tag_dict.values())

        for currTagKey in prev_tag_dict.keys():
            trans_probs[prevTagKey][currTagKey] = float(trans_counts[prevTagKey][currTagKey]) / prev_total

    return trans_probs


# def main():

#     #print ("Dictionary Output: ")
#     transition_counts_output = transition_counts("sample.txt")

#     transition_prob_output = transition_probabilities(transition_counts_output)

#     #print ("End debug mode")


# main()