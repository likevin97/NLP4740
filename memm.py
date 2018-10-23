import nltk.classify.util
from nltk.classify import MaxentClassifier
from collections import defaultdict
import os
import string
from string import whitespace
import csv
from viterbi import *
from hmm import *
from lexicalDictonary import *
import operator
from wordToBio import *


TAGS = ["O", "B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC"]

B_TAG = ["B-PER", "B-LOC", "B-ORG", "B-MISC"]
I_TAG = ["I-PER", "I-LOC", "I-ORG", "I-MISC"]

NOUN = ["NN", "NNS", "NNP", "NNPS"]
ADJ = ["JJ", "JJR", "JJS"]
ADV = ["RB", "RBR", "RBS", "RP"]
VERB = ["MD", "VB", "VBD","VBG", "VBN", "VBP","VBZ"]
WH = ["WDT","WP", "WP$", "WRB"]
PUNC = [".", ",", ":", "(", ")", "\"", "\'"]


def initKaggleDict():
    dict = {}
    tags = ["PER", "ORG", "LOC", "MISC"]
    for t in tags:
        dict[t] = []
    return dict

def training_function(ftraining, w):

    train = open(ftraining, "r")
    pos = []
    all_pos = []
    counter = 0
    total_words = 0

    for line in train:
        if (counter % 3 == 1):
            pos = line.split()
            for p in pos:
                total_words +=1

                if p not in all_pos:
                    all_pos.append(p)
        counter += 1
    train.close()

    # print("total words = " + str(total_words))
    # print ("all pos" + "".join(all_pos))


    train = open(ftraining, "r")
    tokens = []
    BIOtag = []
    pos = []
    counter = 0

    #used for validation only
    correct = 0

    features = []

    for line in train:

        if (counter % 3 == 0):
            tokens = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            BIOtag = line.split()

            for i in range(len(tokens)):
                dict = {}
                #feature one = is this token captialized
                if tokens[i][0].isupper():
                    dict["caps"] = 1
                else:
                    dict["caps"] = 0

                #feature 2 = what pos is it (will be sparse, that's okay)
                dict["pos"] = pos[i]

                #feature 3 = what was the previous bio tag
                if i == 0:
                    dict["prevBIO"] = "<s>"
                else:
                    dict["prevBIO"] = BIOtag[i-1]

                #feature 4 = does prev word start in caps
                if i == 0:
                    dict["prevCaps"] = 0
                else:
                    if tokens[i-1][0].isupper():
                        dict["prevCaps"] = 1
                    else:
                        dict["prevCaps"] = 0

                #feature 5 = previous pos
                if i == 0:
                    dict["prevPOS"] = "<s>"
                else:
                    dict["prevPOS"] = pos[i-1]

                #feature 6 = previous word
                if i == 0:
                    dict["prevWord"] = "<s>"
                else:
                    dict["prevWord"] = tokens[i-1]

                #feature 7 = next word
                if i == len(tokens)-1:
                    dict["nextWord"] = "</s>"
                else:
                    dict["nextWord"] = tokens[i+1]

                #feature 8 = next word pos
                if i == len(tokens)-1:
                    dict["nextPOS"] = "</s>"
                else:
                    dict["nextPOS"] = pos[i+1]

                #feature 9 = does this word appear in training
                dict["training"] = "nan"
                #w[word] = tag
                if tokens[i] in w:
                    dict["training"] = w[tokens[i]]


                features.append((dict, BIOtag[i]))
        counter += 1
    train.close()
    return features, all_pos

def memm(classifier, test_file, all_pos, start, transition, w):

    test = open(test_file, "r")

    tokens = []
    index = []
    pos = []
    counter = 0
    #used for validation only
    correct = 0

    seen = set()
    greedy_predictions = []
    memm_predictions = []
    memm_lex = defaultdict(lambda: defaultdict(float))

    for line in test:
        predictions = []

        if (counter % 3 == 0):
            tokens = line.split()
            for t in tokens:
                seen.add(t)
            #print ("tokens: " + "".join(tokens))
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()
            for i in range(len(tokens)):
                dict = {}
                #feature one = is this token captialized
                #print ("word is " + tokens[i])
                if tokens[i][0].isupper():
                    #print ("upper")
                    dict["caps"] = 1
                else:
                    #print ("lower")
                    dict["caps"] = 0

                dict["pos"] = pos[i]

                if len(predictions)== 0:
                    dict["prevBIO"] = "<s>"
                else:
                    dict["prevBIO"] = predictions[-1]
                #feature 4 = does prev word start in caps
                if i == 0:
                    dict["prevCaps"] = 0
                else:
                    if tokens[i-1][0].isupper():
                        dict["prevCaps"] = 1
                    else:
                        dict["prevCaps"] = 0

                # feature 5 = previous pos
                # if pos[i - 1] == "NNP":
                #     dict["prevNNP"] = 1
                # else:
                #     dict["prevNNP"] = 0
                if i == 0:
                    dict["prevPOS"] = "<s>"
                else:
                    dict["prevPOS"] = pos[i-1]
                # feature 6 = previous word
                if i == 0:
                    dict["prevWord"] = "<s>"
                else:
                    dict["prevWord"] = tokens[i - 1]

                # feature 7 = next word
                if i == len(tokens) - 1:
                    dict["nextWord"] = "</s>"
                else:
                    dict["nextWord"] = tokens[i + 1]

                # feature 8 = next word pos
                if i == len(tokens) - 1:
                    dict["nextPOS"] = "</s>"
                else:
                    dict["nextPOS"] = pos[i + 1]

                # feature 9 = does this word appear in training
                dict["training"] = "nan"
                # w[word] = tag
                if tokens[i] in w:
                    dict["training"] = w[tokens[i]]

                #print (dict)
                probs = classifier.prob_classify(dict)

                #greedy predictions
                maxscore = 0
                best_tag = ""
                for tag in TAGS:
                    score = probs.prob(tag)
                    memm_lex[tag][tokens[i]] = score
                    if score > maxscore:
                        maxscore = score
                        best_tag = tag
                #print(best_tag)
                predictions.append(best_tag)

            memm_pre = viterbi(tokens, start, transition, memm_lex, seen)
            memm_predictions.append(memm_pre)
            greedy_predictions.append(predictions)
        counter += 1
    test.close()
    return greedy_predictions, memm_predictions



def memm_prediction(training, testing):
    w = wordtoBIO(training)

    features, all_pos = training_function(training, w)

    classifier = nltk.classify.MaxentClassifier.train(features, max_iter=5)

    start_prob = startToTagDictionary(training)

    transition_dict = transition_counts(training)
    transition_probs = transition_probabilities(transition_dict)


    greedy_predictions, memm_predictions = memm(classifier, testing, all_pos, start_prob, transition_probs, w)

    test = open(testing, "r")

    kaggle = initKaggleDict()

    counter = 0

    for line in test:

        #greedy_bio = greedy_predictions[counter / 3]

        memm_bio = memm_predictions[counter / 3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()

            # everything has correct information

            for i in range(len(memm_bio)):
                if memm_bio[i] != "O":
                    if memm_bio[i] in B_TAG:
                        kaggle[memm_bio[i][2:]].append(index[i])
                    elif memm_bio[i] in I_TAG:
                        if kaggle[memm_bio[i][2:]] == []:
                            kaggle[memm_bio[i][2:]].append(index[i])
                        else:
                            kaggle[memm_bio[i][2:]][-1] += " " + str(index[i])

        counter += 1

    # allpredicitons = [ [] [] [] ]

    ORG = ""
    PER = ""
    LOC = ""
    MISC = ""

    # print "Kaggle Hash"
    #
    # print (kaggle)
    #
    # print "-------------"

    for tag in kaggle:
        for index_ranges in kaggle[tag]:
            index = index_ranges.split()
            b_index = index[0]
            e_index = index[-1]
            if tag == "ORG":
                ORG += " "
                ORG += str(b_index) + "-" + str(e_index)
            elif tag == "PER":
                PER += " "
                PER += str(b_index) + "-" + str(e_index)
            elif tag == "LOC":
                LOC += " "
                LOC += str(b_index) + "-" + str(e_index)
            elif tag == "MISC":
                MISC += " "
                MISC += str(b_index) + "-" + str(e_index)

    print ("Type,Prediction")

    results = [PER, LOC, ORG, MISC]

    # print ("PER," + PER)
    # print("LOC, " + LOC)
    # print("ORG," + ORG)
    # print("MISC," + MISC)

    with open('memmViterbiKaggle.csv', "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Type', 'Prediction'])
        val = 0
        temp = ["PER", "LOC", "ORG", "MISC"]
        while val < 4:
            writer.writerow((temp[val], results[val]))
            val += 1


# def main():
#     # hash = baseline_train("sample.txt")
#     # # testing(hash, "sample.txt")
#     # transition_dict = transition_counts("training.txt")
#     # transition_probs = transition_probabilities(transition_dict)
#     # #lex_dict, a = lexical_dictonary("sample.txt")
#     # w = wordtoBIO("training.txt")
#     # #print (lex_dict)
#     # #print (lex_dict['I-LOC']['Albans'])
#     # #print (lex_dict.keys())
#     #
#     # start_prob = startToTagDictionary("training.txt")
#
#     #features, all_pos = training_function("training.txt", w)
#     #classifier = nltk.classify.MaxentClassifier.train(features, max_iter=5)
#     # test1 = {'PRP$': 0, 'I-LOC': 0, 'I-MISC': 0, 'DT': 0, 'POS': 0, 'I-PER': 1, 'TO': 0, 'PRP': 0, 'B-PER': 0, 'CC': 0, 'PDT': 0, 'O': 0, 'caps': 1, 'IN': 0, 'prevCaps': 1, 'CD': 0, 'noun': 1, 'B-ORG': 0, 'UH': 0, 'B-MISC': 0, 'I-ORG': 0, 'B-LOC': 0}
#     # probs = classifier.prob_classify(test1)
#     # maxscore = 0
#     # best_tag = ""
#     # for tag in TAGS:
#     #     score = probs.prob(tag)
#     #     print (tag + ": " + str(score))
#     #     if score > maxscore:
#     #         maxscore = score
#     #         best_tag = tag
#     # print(best_tag)
#
#     # greedy_predictions, memm_predictions = memm(classifier, "validation.txt", all_pos, start_prob, transition_probs, w)
#     # print(greedy_predictions)
#     # print ("========")
#     # print (convertArrayToBIOTags(memm_predictions))
#
#
#     memm_prediction("training.txt", "test.txt")
#
#
#     #
#     # v = open('validation.txt', "r")
#     # counter = 0
#     # correct = []
#     # c_tags = []
#     # for l in v:
#     #     if counter %3 == 2:
#     #         c_tags = l.split()
#     #         correct.append(c_tags)
#     #     counter +=1
#     #
#     # recall = 0
#     # rc = 0
#     # rwrong = 0
#     # for i in range(len(correct)):
#     #     for j in range(len(correct[i])):
#     #         if (correct[i][j] != "0"):
#     #             recall += 1
#     #             if (correct[i][j] == greedy_predictions[i][j]):
#     #                 rc += 1
#     #             else:
#     #                 rwrong += 1
#     #
#     # precision = 0
#     # pc = 0
#     # pwrong = 0
#     # for i in range(len(greedy_predictions)):
#     #     for j in range(len(greedy_predictions[i])):
#     #         if (greedy_predictions[i][j] != "0"):
#     #             precision += 1
#     #             if (correct[i][j] == greedy_predictions[i][j]):
#     #                 pc += 1
#     #             else:
#     #                 pwrong += 1
#     # print ("")
#     # print ("")
#     # print ("")
#     # print ("Correct Recall: " + str(float(rc) / recall))
#     # print ("Incorrect Recall: " + str(float(rwrong) / recall))
#     # print ("Correct Precision: " + str(float(pc) / precision))
#     # print ("Incorrect Precision: " + str(float(pwrong) / precision))
#
#
# main()
