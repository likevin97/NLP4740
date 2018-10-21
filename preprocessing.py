# import nltk.classify.util
# from nltk.classify import MaxentClassifier


def training_function(ftraining):

    train = open(ftraining, "r")
    tokens = []
    BIOtag = []
    pos = []
    counter = 0

    all_pos = []

    #used for validation only
    correct = 0

    features = []

    for line in train:

        if (counter % 3 == 0):
            tokens = line.split()
        elif (counter % 3 == 1):
            pos = line.split()
            for p in pos:
                if p not in all_pos:
                    all_pos.append(p)
        else:
            BIOtag = line.split()


        counter += 1
    return all_pos


def main():
    a = training_function("training.txt")
    print(a)

 	# pred = memm("training.txt", "sample.txt")
 	# print (pred)


main()
