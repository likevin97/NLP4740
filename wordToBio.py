from collections import defaultdict
import operator

def wordtoBIO(file):
    f = open(file,"r")
    d = defaultdict(lambda: defaultdict(int))
    words = []
    bio = []
    counter = 0
    for l in f:
        if counter % 3 == 0:
            words = l.split()
        if counter %3 == 2:
            bio = l.split()

            for i in range(len(words)):
                d[words[i]][bio[i]] += 1
        counter +=1

    w = {}
    for word in d.keys():
        t = 0
        for tag in d[word]:
            t += d[word][tag]
        for tag in d[word]:
            d[word][tag] /= float(t)
        x = max(d[word].iteritems(),key = operator.itemgetter(1))[0]
        w[word]=x
    return w

# def main():
#     w = wordtoBIO("sample.txt")
#     print(w)
#
# main()