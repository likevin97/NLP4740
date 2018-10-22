import nltk.classify.util
from nltk.classify import MaxentClassifier
from collections import defaultdict
import os
import string
from string import whitespace
import csv
from p2 import *


TAGS = ["O", "B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC"]

NOUN = ["NN", "NNS", "NNP", "NNPS"]
ADJ = ["JJ", "JJR", "JJS"]
ADV = ["RB", "RBR", "RBS", "RP"]
VERB = ["MD", "VB", "VBD","VBG", "VBN", "VBP","VBZ"]
WH = ["WDT","WP", "WP$", "WRB"]
PUNC = [".", ",", ":", "(", ")", "\"", "\'"]

#
# def baseline_train(filename):
#     hash = defaultdict(lambda: defaultdict(int))
#
#     train = open(filename, "r")
#     counter = 0
#     text = []
#     pos = []
#     bio = []
#     for line in train:
#         if (counter % 3 == 0):
#             text = line.split()
#         elif (counter % 3 == 1):
#             pos = line.split()
#         else:
#             bio = line.split()
#
#             for i in range(len(text)):
#                 hash[text[i]]["counter"] +=1
#                 hash[text[i]][bio[i]] += 1
#         counter += 1
#     #print (hash["American"])
#     return hash
# def testing(hash, test_file):
#     test = open(test_file, "r")
#     tokens = []
#     index = []
#     pos = []
#     counter = 0
#     # used for validation only
#     correct = 0
#     all_predictions = []
#
#     for line in test:
#         predictions = []
#
#         if (counter % 3 == 0):
#             tokens = line.split()
#             # print ("tokens: " + "".join(tokens))
#         elif (counter % 3 == 1):
#             pos = line.split()
#         else:
#             index = line.split()
#
#             for i in range(len(tokens)):
#                 print (tokens[i])
#                 if tokens[i] in hash:
#                     print ("in hash")
#                     maxcounter = 0
#                     maxtag = ""
#                     for key in hash[tokens[i]]:
#                         print ("key: " + key)

def training_function(ftraining):

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

                # if pos[i] == "NNP" or pos[i] == "NNPS":
                #     dict["NNP-NNPS"] = 1
                # else:
                #     dict["NNP-NNPS"] = 0

                dict["pos"] = pos[i]


                #feature 3 = what was the previous bio tag
                # for tag in TAGS:
                #     if i == 0:
                #         if tag == "O":
                #             dict["O"] = 0
                #         else:
                #             dict[tag[2:]] = 0
                #     else:
                #         if tag == BIOtag[-1]:
                #             if tag == "O":
                #                 dict["O"] = 1
                #             else:
                #                 dict[tag[2:]] = 1
                #         else:
                #             if tag == "O":
                #                 dict["O"] = 0
                #             else:
                #                 dict[tag[2:]] = 0
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
                # if pos[i-1] == "NNP":
                #     dict["prevNNP"] = 1
                # else:
                #     dict["prevNNP"] = 0
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


                features.append((dict, BIOtag[i]))
        counter += 1
    train.close()
    #print(features[0])
    return features, all_pos

def memm(classifier, test_file, all_pos):

    test = open(test_file, "r")

    tokens = []
    index = []
    pos = []
    counter = 0
    #used for validation only
    correct = 0
    all_predictions = []
    #memm_lex = {}

    for line in test:
        predictions = []

        if (counter % 3 == 0):
            tokens = line.split()
            #print ("tokens: " + "".join(tokens))
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()
            for i in range(len(tokens)):
                dict = {}
                #feature one = is this token captialized
                print ("word is " + tokens[i])
                if tokens[i][0].isupper():
                    #print ("upper")
                    dict["caps"] = 1
                else:
                    #print ("lower")
                    dict["caps"] = 0

                #feature 2 = what pos is it (will be sparse, that's okay)
                #print (pos[i])
                # for p in all_pos:
                #     if pos[i] == p:
                #         #print ("is " + p)
                #         dict[p] = 1
                #     else:
                #         #print ("is not " + p)
                #         dict[p] = 0



                # for p in all_pos:
                #     if p not in NOUN and p not in ADJ and p not in ADV and p not in VERB and p not in WH and p not in PUNC:
                #         dict[p] = 0
                #
                # if pos[i] in NOUN:
                #     dict["noun"] = 1
                # elif pos[i] in ADJ:
                #     dict["adj"] = 1
                # elif pos[i] in ADV:
                #     dict["adv"] = 1
                # elif pos[i] in VERB:
                #     dict["verb"] = 1
                # elif pos[i] in WH:
                #     dict["wh"] = 1
                # elif pos[i] in PUNC:
                #     dict["punc"] = 1
                # else:
                #     dict[pos[i]] = 1

                # if pos[i] == "NNP" or pos[i] == "NNPS": #not perfect, there are some VB and VBGs that are named entities
                #     dict["NNP-NNPS"] = 1
                # else:
                #     dict["NNP-NNPS"] = 0
                dict["pos"] = pos[i]
                #feature 3 = what was the previous bio tag
                # for tag in TAGS:
                #     if len(predictions) == 0:
                #         if tag == "O":
                #             dict["O"] = 0
                #         else:
                #             dict[tag[2:]] = 0
                #     else:
                #         if tag == predictions[-1]:
                #             if tag == "O":
                #                 dict["O"] = 1
                #             else:
                #                 dict[tag[2:]] = 1
                #         else:
                #             if tag == "O":
                #                 dict["O"] = 0
                #             else:
                #                 dict[tag[2:]] = 0
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

                print (dict)
                probs = classifier.prob_classify(dict)

                maxscore = 0
                best_tag = ""
                for tag in TAGS:
                    score = probs.prob(tag)
                    #memm_lex[tokens[i]][tag] = score
                    if score > maxscore:
                        maxscore = score
                        best_tag = tag
                print(best_tag)
                predictions.append(best_tag)
            all_predictions.append(predictions)
        counter += 1

    test.close()
    return all_predictions



def memm_prediction(training, testing):
    features, all_pos = training_function(training)
    classifier = nltk.classify.MaxentClassifier.train(features, max_iter=5)

    predictions = memm(classifier, testing, all_pos)

    test = open(testing, "r")

    kaggle = initKaggleDict()

    counter = 0

    for line in test:

        bio = predictions[counter / 3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()

            # everything has correct information

            for i in range(len(bio)):
                if bio[i] != "O":
                    if bio[i] in B_TAG:
                        kaggle[bio[i][2:]].append(index[i])
                    elif bio[i] in I_TAG:
                        kaggle[bio[i][2:]][-1] += " " + str(index[i])

        counter += 1

    # allpredicitons = [ [] [] [] ]

    ORG = ""
    PER = ""
    LOC = ""
    MISC = ""

    print "Kaggle Hash"

    print (kaggle)

    print "-------------"

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

    print ("PER," + PER)
    print("LOC, " + LOC)
    print("ORG," + ORG)
    print("MISC," + MISC)

    with open('memmKaggle.csv', "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Type', 'Prediction'])
        val = 0
        temp = ["PER", "LOC", "ORG", "MISC"]
        while val < 4:
            writer.writerow((temp[val], results[val]))
            val += 1


def main():
    # hash = baseline_train("sample.txt")
    # testing(hash, "sample.txt")

    #features, all_pos = training_function("sample.txt")
    #classifier = nltk.classify.MaxentClassifier.train(features, max_iter=10)
    # test1 = {'PRP$': 0, 'I-LOC': 0, 'I-MISC': 0, 'DT': 0, 'POS': 0, 'I-PER': 1, 'TO': 0, 'PRP': 0, 'B-PER': 0, 'CC': 0, 'PDT': 0, 'O': 0, 'caps': 1, 'IN': 0, 'prevCaps': 1, 'CD': 0, 'noun': 1, 'B-ORG': 0, 'UH': 0, 'B-MISC': 0, 'I-ORG': 0, 'B-LOC': 0}
    # probs = classifier.prob_classify(test1)
    # maxscore = 0
    # best_tag = ""
    # for tag in TAGS:
    #     score = probs.prob(tag)
    #     print (tag + ": " + str(score))
    #     if score > maxscore:
    #         maxscore = score
    #         best_tag = tag
    # print(best_tag)

    #predictions = memm(classifier, "becca_testing.txt", all_pos)
    #print(predictions)

    memm_prediction("sample.txt", "sample_test.txt")


 	# pred = memm("training.txt", "sample.txt")
 	# print (pred)


main()
