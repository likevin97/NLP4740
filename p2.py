import os
import string
from string import whitespace
import csv
from hmm import *
from memm import *

B_TAG = ["B-PER", "B-LOC", "B-ORG", "B-MISC"]
I_TAG = ["I-PER", "I-LOC", "I-ORG", "I-MISC"]

def preprocessing(fname):
    counter = 0

    validation = open("validation.txt", "wr+")
    training = open("training.txt", "wr+")

    with open(fname) as f:
        for line in f:
            # validation
            if (counter >= 27):
                validation.write(line)
                if (counter == 29):
                    counter = -1
            else:
                training.write(line)
            counter += 1

def initBIODict():
    dict = {}
    tags = ["B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC", "O"]
    for t in tags:
        dict[t] = 0
    return dict

def initKaggleDict():
    dict = {}
    tags = ["PER", "ORG", "LOC", "MISC"]
    for t in tags:
        dict[t] = []
    return dict

def baseline(ftraining):
    training = open(ftraining, "r")
    text = ""
    pos = ""
    bio = ""
    counter = 0

    hash = {}
    for line in training:
        if (counter % 3 == 0):
            text = line.split()
            pos = ""
            bio = ""
        elif (counter % 3 == 1):
            pos = line.split()
            bio = ""
        else:
            bio = line.split()

            #do stuff bc now all three variables are initiated with the correct information

            for i in range(len(text)): #text, pos, and bio should all be of same length
                if bio[i] in B_TAG or bio[i] in I_TAG:
                    hash[text[i]] = bio[i]
        counter += 1
    return hash



def baseline_prediction(training, testing):
    hash = baseline(training)
    test = open(testing, "r")
    text = []
    pos = []
    index = []
    counter = 0
    kaggle = initKaggleDict()

    #used for validation only
    correct = 0

    for line in test:

        bio = []

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()

            #everything has correct information

            for i in range(len(text)):
                if text[i] in hash:
                    if hash[text[i]] in B_TAG:
                        bio.append(hash[text[i]])
                    elif hash[text[i]] in I_TAG:
                        if len(bio) == 0 or bio[-1] == "O":
                            bio.append("O")
                        elif bio[-1][2:] == hash[text[i]][2:] and i > 0: #if previous word is part of the entity
                            bio.append(hash[text[i]])
                        else:
                            bio.append("O")
                else:
                    bio.append("O")

        for i in range(len(bio)):
            if bio[i] != "O":
                if bio[i] in B_TAG:
                    kaggle[bio[i][2:]].append(index[i])
                elif bio[i] in I_TAG:
                    kaggle[bio[i][2:]][-1] += " " + str(index[i])

        counter += 1

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

    # print ("Type,Prediction")

    results = [PER,LOC,ORG,MISC]

    # print ("PER," + PER)
    # print("LOC, " + LOC)
    # print("ORG," + ORG)
    # print("MISC," + MISC)


    with open('baselineKaggle.csv', "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Type', 'Prediction'])
        val = 0
        temp = ["PER", "LOC", "ORG", "MISC"]
        while val < 4:
            writer.writerow((temp[val], results[val]))
            val += 1

        # at the end of this for loop (on a single line) the index of any variable, should correspond to that same index for any other variable


def hmm_hash(ftraining):
    training = open(ftraining, "r")
    max_array = hmm("training.txt", "sample.txt")
    text = ""
    pos = ""
    bio = ""
    counter = 0

    hash = {}
    for line in training:
        if (counter % 3 == 0):
            text = line.split()
            pos = ""
            bio = ""
        elif (counter % 3 == 1):
            pos = line.split()
            bio = ""
        else:
            bio = line.split()

            #do stuff bc now all three variables are initiated with the correct information

            for i in range(len(text)): #text, pos, and bio should all be of same length
                if bio[i] in B_TAG or bio[i] in I_TAG:
                    hash[text[i]] = bio[i]

            # prediction_line = max_array[counter]
            #
            # for i in range(len(text)):
            #     if prediction_line[i]
            #     hash[text[i]] = prediction_line[i]

        counter += 1
    return hash


def hmm_unsmoothed_prediction(training, testing):

    bio_arr_test = convertArrayToBIOTags(hmm(training, testing))

    test = open(testing, "r")
    text = []
    index = []
    counter = 0

    kaggle = initKaggleDict()

    for line in test:

        bio = bio_arr_test[counter/3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()

            #everything has correct information


            for i in range(len(bio)):
                if bio[i] != "O":
                    if bio[i] in B_TAG:
                        kaggle[bio[i][2:]].append(index[i])
                    elif bio[i] in I_TAG:
                        kaggle[bio[i][2:]][-1] += " " + str(index[i])

        counter += 1


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

    results = [PER,LOC,ORG,MISC]

    print ("PER," + PER)
    print("LOC, " + LOC)
    print("ORG," + ORG)
    print("MISC," + MISC)


    with open('hmmUnsmoothedKaggle.csv', "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Type', 'Prediction'])
        val = 0
        temp = ["PER", "LOC", "ORG", "MISC"]
        while val < 4:
            writer.writerow((temp[val], results[val]))
            val += 1

        # at the end of this for loop (on a single line) the index of any variable, should correspond to that same index for any other variable


def hmm_addk_prediction(training, testing, k):

    bio_arr_test = convertArrayToBIOTags(hmm_addk(training, testing, k))

    test = open(testing, "r")
    text = []
    index = []
    counter = 0

    kaggle = initKaggleDict()

    for line in test:

        bio = bio_arr_test[counter/3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()

            #everything has correct information


            for i in range(len(bio)):
                if bio[i] != "O":
                    if bio[i] in B_TAG:
                        kaggle[bio[i][2:]].append(index[i])
                    elif bio[i] in I_TAG:
                        kaggle[bio[i][2:]][-1] += " " + str(index[i])

        counter += 1


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

    results = [PER,LOC,ORG,MISC]

    print ("PER," + PER)
    print("LOC, " + LOC)
    print("ORG," + ORG)
    print("MISC," + MISC)


    with open('hmmAddKKaggle.csv', "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Type', 'Prediction'])
        val = 0
        temp = ["PER", "LOC", "ORG", "MISC"]
        while val < 4:
            writer.writerow((temp[val], results[val]))
            val += 1

        # at the end of this for loop (on a single line) the index of any variable, should correspond to that same index for any other variable


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


def baseline_precision_recall(training, validation):
    hash = baseline(training)
    valid = open(validation, "r")
    text = []
    pos = []
    index = []
    counter = 0
    kaggle = initKaggleDict()

    precision = 0
    recall = 0
    pcorrect = 0
    rcorrect = 0

    # used for validation only
    correct = 0

    for line in valid:

        bio = []

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            answer_bio = line.split()

            #everything has correct information

            for i in range(len(text)):
                if text[i] in hash:
                    if hash[text[i]] in B_TAG:
                        bio.append(hash[text[i]])
                    elif hash[text[i]] in I_TAG:
                        if len(bio) == 0 or bio[-1] == "O":
                            bio.append("O")
                        elif bio[-1][2:] == hash[text[i]][2:] and i > 0: #if previous word is part of the entity
                            bio.append(hash[text[i]])
                        else:
                            bio.append("O")
                else:
                    bio.append("O")

            for i in range(len(bio)):
                if bio[i] != "O":
                    if bio[i] != "O":
                        if kaggle[bio[i][2:]] == []:
                            kaggle[bio[i][2:]].append(answer_bio[i])
                        else:
                            kaggle[bio[i][2:]][-1] += " " + str(answer_bio[i])

            for i in range(len(bio)):
                if (bio[i] != "O"):
                    precision += 1
                    if bio[i] == answer_bio[i]:
                        pcorrect += 1
            for i in range(len(answer_bio)):
                if (answer_bio[i] != "O"):
                    recall += 1

        counter += 1

    # Precision/recall
    print "Baseline Precision/Recall: "
    precision_answ = float(pcorrect) / precision
    print ("precision " + str(precision_answ))
    recall_answ = float(pcorrect) / recall
    print ("recall " + str(recall_answ))
    print ("f-score " + str((2 * precision_answ * recall_answ)/ (precision_answ + recall_answ) ))
    print "----------------------"


def hmm_precision_recall(training, validation):
    bio_arr_test = convertArrayToBIOTags(hmm(training, validation))

    valid = open(validation, "r")
    text = []
    answer_bio = []
    counter = 0

    kaggle = initKaggleDict()

    precision = 0
    recall = 0
    pcorrect = 0
    rcorrect = 0

    # used for validation only
    correct = 0

    for line in valid:

        bio = bio_arr_test[counter / 3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            answer_bio = line.split()

            # everything has correct information

            for i in range(len(bio)):
                if bio[i] != "O":
                    if kaggle[bio[i][2:]] == []:
                        kaggle[bio[i][2:]].append(answer_bio[i])
                    else:
                        kaggle[bio[i][2:]][-1] += " " + str(answer_bio[i])

            for i in range(len(bio)):
                if (bio[i] != "O"):
                    precision += 1
                    if bio[i] == answer_bio[i]:
                        pcorrect += 1
            for i in range(len(answer_bio)):
                if (answer_bio[i] != "O"):
                    recall += 1

        counter += 1

    # Precision/recall

    print "HMM Precision/Recall: "
    precision_answ = float(pcorrect) / precision
    print ("precision " + str(precision_answ))
    recall_answ = float(pcorrect) / recall
    print ("recall " + str(recall_answ))
    print ("f-score " + str((2 * precision_answ * recall_answ)/ (precision_answ + recall_answ) ))
    print "----------------------"


def hmm_addk_precision_recall(training, validation, k):
    bio_arr_test = convertArrayToBIOTags(hmm_addk(training, validation, k))

    valid = open(validation, "r")
    text = []
    answer_bio = []
    counter = 0

    kaggle = initKaggleDict()

    precision = 0
    recall = 0
    pcorrect = 0
    rcorrect = 0

    # used for validation only
    correct = 0

    for line in valid:

        bio = bio_arr_test[counter / 3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            answer_bio = line.split()

            # everything has correct information

            for i in range(len(bio)):
                if bio[i] != "O":
                    if kaggle[bio[i][2:]] == []:
                        kaggle[bio[i][2:]].append(answer_bio[i])
                    else:
                        kaggle[bio[i][2:]][-1] += " " + str(answer_bio[i])

            for i in range(len(bio)):
                if (bio[i] != "O"):
                    precision += 1
                    if bio[i] == answer_bio[i]:
                        pcorrect += 1
            for i in range(len(answer_bio)):
                if (answer_bio[i] != "O"):
                    recall += 1

        counter += 1

    # Precision/recall

    print "HMM Add-K Precision/Recall: "
    precision_answ = float(pcorrect) / precision
    print ("precision " + str(precision_answ))
    recall_answ = float(pcorrect) / recall
    print ("recall " + str(recall_answ))
    print ("f-score " + str((2 * precision_answ * recall_answ)/ (precision_answ + recall_answ) ))
    print "----------------------"


def memm_precision_recall(training, validation):
    w = wordtoBIO(training)

    features, all_pos = training_function(training, w)

    classifier = nltk.classify.MaxentClassifier.train(features, max_iter=5)

    start_prob = startToTagDictionary(training)

    transition_dict = transition_counts(training)
    transition_probs = transition_probabilities(transition_dict)

    bio_arr_predictions, viterbi_test = memm(classifier, validation, all_pos, start_prob, transition_probs, w)

    bio_arr_test = convertArrayToBIOTags(bio_arr_predictions)

    valid = open(validation, "r")
    text = []
    answer_bio = []
    counter = 0

    kaggle = initKaggleDict()

    precision = 0
    recall = 0
    pcorrect = 0
    rcorrect = 0

    # used for validation only
    correct = 0

    for line in valid:

        bio = bio_arr_test[counter / 3]

        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            answer_bio = line.split()

            # everything has correct information

            for i in range(len(bio)):
                if bio[i] != "O":
                    if kaggle[bio[i][2:]] == []:
                        kaggle[bio[i][2:]].append(answer_bio[i])
                    else:
                        kaggle[bio[i][2:]][-1] += " " + str(answer_bio[i])

            for i in range(len(bio)):
                if (bio[i] != "O"):
                    precision += 1
                    if bio[i] == answer_bio[i]:
                        pcorrect += 1
            for i in range(len(answer_bio)):
                if (answer_bio[i] != "O"):
                    recall += 1

        counter += 1

    # Precision/recall

    print "MEMM Precision/Recall: "
    precision_answ = float(pcorrect) / precision
    print ("precision " + str(precision_answ))
    recall_answ = float(pcorrect) / recall
    print ("recall " + str(recall_answ))
    print ("f-score " + str((2 * precision_answ * recall_answ)/ (precision_answ + recall_answ) ))
    print "----------------------"


def main():

    # if (os.path.isfile('/path/to/file')):
    #     preprocessing("train.txt")

    # baseline_prediction("training.txt", "test.txt")
    # hmm_unsmoothed_prediction("training.txt", "test.txt")


    # print ("Kaggle Hash")
    #
    # print ("--------------")
    #
    # max_array = hmm("training.txt", "test.txt")
    # print convertArrayToBIOTags(max_array)

    baseline_precision_recall("training.txt", "validation.txt")
    hmm_precision_recall("training.txt", "validation.txt")
    hmm_addk_precision_recall("training.txt", "validation.txt", 0.86)

    baseline_prediction("training.txt", "test.txt")
    hmm_unsmoothed_prediction("training.txt", "test.txt")
    hmm_addk_prediction("training.txt", "test.txt", 0.5)
    memm_prediction("sample.txt", "sample_test.txt")


main()
