import nltk.classify.util
from nltk.classify import MaxentClassifier

TAGS = ["O", "B-PER", "B-LOC", "B-ORG", "B-MISC", "I-PER", "I-LOC", "I-ORG", "I-MISC"]

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
                for p in all_pos:
                    if pos[i] == p:
                        dict[p] = 1
                    else:
                        dict[p] = 0

                #feature 3 = what was the previous bio tag
                for tag in TAGS:
                    if i == 0:
                        dict[tag] = 0
                    else:
                        if tag == BIOtag[i-1]:
                            dict[tag] = 1
                        else:
                            dict[tag] = 0

                #feature 4 = does prev word start in caps
                if i == 0:
                    dict["prevCaps"] = 0
                else:
                    if tokens[i-1][0].isupper():
                        dict["prevCaps"] = 1
                    else:
                        dict["prevCaps"] = 0

                features.append((dict, BIOtag[i]))
        counter += 1
    print(features[0])
    return features

def main():
    features = training_function("sample.txt")
    classifier = nltk.classify.MaxentClassifier.train(features, max_iter=10)
    test1 = {'VB': 0, 'NN': 0, 'prevCaps': 0, 'I-LOC': 0, 'B-ORG': 0, 'O': 0, '.': 0, 'TO': 0, 'CD': 0, 'VBP': 0, 'B-PER': 0, 'I-PER': 0, 'I-MISC': 0, 'B-MISC': 0, 'caps': 1, ':': 0, 'I-ORG': 0, 'B-LOC': 0, 'NNP': 1}
    probs = classifier.prob_classify(test1)
    print(probs.prob("B-ORG"))
    print(probs.prob("I-ORG"))
    print(probs.prob("O"))

 	# pred = memm("training.txt", "sample.txt")
 	# print (pred)


main()
