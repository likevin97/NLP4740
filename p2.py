import os
import string
from string import whitespace
import csv

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


def common_class(fname):
    dict = initBIODict()

    counter = 0

    with open(fname) as trainingfile:
        for line in trainingfile:

            if (counter % 3 == 2):
                for tag in line.split():
                    dict[tag] += 1
            counter += 1
    return dict

def common_class_prediction(ftraining, ftesting):
    # predict most common class for everything in testing
    dict = common_class(ftraining)
    maxKey = max(dict, key=dict.get)

    validation = open(ftesting, "r")
    counter = 0
    correct = 0
    incorrect = 0
    for line in validation:
        if (counter % 3 == 2):
            for tag in line.split():
                if tag == maxKey:
                    correct += 1
                else:
                    incorrect += 1
        counter += 1

    print("Common Class Prediction")
    print ("Everything was predicted to be the class " + maxKey)
    if (correct > 0 or incorrect > 0):
        print ("Accuracy: " + str(float(correct) / (correct + incorrect)))

    '''
    f_read = open(ftesting, "r")
    last_line = f_read.readlines()[-1]
    x = last_line.split()
    last_word_index = x[-1]

    print ("Common Class Prediction")
    print ("Type,Prediction")
    print (maxKey + ",0-" + last_word_index)
    '''


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
    bio = []
    counter = 0
    kaggle = initKaggleDict()
    for line in test:
        if (counter % 3 == 0):
            text = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
        else:
            index = line.split()
            bio = []


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


            #at the end of this for loop (on a single line) the index of any variable, should correspond to that same index for any other variable

        print ("Tokens: " + str(text))

        print ("BIO: " + str(bio))
        print ("Indexes: " + str(index))

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

    for tag in kaggle:
        for index_ranges in kaggle[tag]:
            index = index_ranges.split()
            b_index = index[0]
            e_index = index[-1]
            if tag == "ORG":
                if b_index != e_index:
                    ORG += " "
                    ORG += str(b_index) + "-" + str(e_index)
                else:
                    ORG += " "
                    ORG += str(b_index)
            elif tag == "PER":
                if b_index != e_index:
                    PER += " "
                    PER += str(b_index) + "-" + str(e_index)
                else:
                    PER += " "
                    PER += str(b_index)
            elif tag == "LOC":
                if b_index != e_index:
                    LOC += " "
                    LOC += str(b_index) + "-" + str(e_index)
                else:
                    LOC += " "
                    LOC += str(b_index)
            elif tag == "MISC":
                if b_index != e_index:
                    MISC += " "
                    MISC += str(b_index) + "-" + str(e_index)
                else:
                    MISC += " "
                    MISC += str(b_index)

    print ("Type,Prediction")
    results = [PER,LOC,ORG,MISC]
    print ("PER," + PER)
    print("LOC, " + LOC)
    print("ORG," + ORG)
    print("MISC," + MISC)


    with open('baselineKaggle.csv', "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Type', 'Prediction'])
        val = 0
        temp = ["PER", "LOC", "ORG", "MISC"]
        while val < 4:
            writer.writerow((temp[val], results[val]))
            val += 1






def main():

    # if (os.path.isfile('/path/to/file')):
    #     preprocessing("train.txt")


    #common_class_prediction("training.txt", "validation.txt")
    #hash = baseline("sample.txt")
    baseline_prediction("train.txt", "test.txt")
    #print hash




main()
