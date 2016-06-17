#!/usr/bin/env python
# encoding: utf-8

"""
Adapted from scorer.py (originally by Sujay Kumar Jauhar on 2011-11-27)
"""
import sys
import re
import itertools
import io
import time
from collections import Counter
import main
from main import log, get_wordnet_score, unigram_frequencies
GOLD_RANKINGS_FILENAME = "./test-data/substitutions.gold-rankings"
NORMALIZE = True

check_range = None
norm_coefficients = None
gold_rankings = None

#function to read system produced ranking file
def getSystemRankings(file):
    #pattern to recognize rankings in output file
    pattern = re.compile('.*?\{(.*?)\}(.*)')
    
    #extract rankings
    allContextRankings = []
    for line in file:
        rest = line
        currentContextRanking = {}
        counter = 0
        while rest:
            match = pattern.search(rest)
            currentRank = match.group(1)
            individualWords = currentRank.split(', ')
            for word in individualWords:
                word = re.sub('\s$','',word)
                currentContextRanking[word] = counter
            rest = match.group(2)
            counter += 1
        
        allContextRankings.append(currentContextRanking)
        
    return allContextRankings

#comparator function
def compare(val1, val2):
    if (val1 < val2):
        return -1
    elif (val1 > val2):
        return 1
    else:
        return 0

#function to score system with reference to gold
#function is based on kappa with rank correlation
def getScore(system, gold):
    
    #intialize vars
    totalPairCount = 0
    agree = 0
    equalAgree = 0
    
    #go through contexts parallely
    for (sysContext, goldContext) in zip(system, gold):

        #go through each combination of substitutions
        for pair in itertools.permutations(list(sysContext.keys()), 2):
            totalPairCount += 1
            #find ranking order given by system and gold for current pair
            sysCompareVal = compare(sysContext[pair[0]],sysContext[pair[1]])
            goldCompareVal = compare(goldContext[pair[0]],goldContext[pair[1]])
            
            #system and gold agree
            #add appropriate counts to agree count
            if (sysCompareVal) == (goldCompareVal):
                agree += 1
                    
            #add count if at least one of them tied candidate pair
            if sysCompareVal == 0:
                    equalAgree += 1
            if goldCompareVal == 0:
                    equalAgree += 1
    
    equalAgreeProb = float(equalAgree)/float(totalPairCount*2)
    
    #P(A) and P(E) values    
    absoluteAgreement = float(agree)/float(totalPairCount)
    chanceAgreement = (3*pow(equalAgreeProb,2)-2*equalAgreeProb+1.0)/2.0
    
    #return kappa score
    return (absoluteAgreement - chanceAgreement)/(1.0 - chanceAgreement)
    

def get_neighbors(visited, position):
    ret = []
    # enumerate the neighbors
    for dim in range(len(position)):
        pos = list(position)
        ret.append( pos[0:dim] + [pos[dim]+1] + pos[dim+1:] )
        ret.append( pos[0:dim] + [pos[dim]-1] + pos[dim+1:] )

    # eliminate the impossible ones
    ret = [pos for pos in ret if not any(map(lambda x:x<0, pos))]
    ret = [pos for pos in ret if not any(map(lambda x:x>=7, pos))]

    # eliminate the visited ones
    ret = [x for x in ret if tuple(x) not in visited]
    ret = list(map(tuple, ret))
    return ret


def evaluate_solution(position):
    global check_range, norm_coefficients

    # generate weights
    weights = [check_range[position[i]] for i in range(4)]
    for i in range(len(weights)):
        weights[i] /= norm_coefficients[i]

    # evaluate them
    stream = io.StringIO()
    main.main( weights=weights, output_stream=stream, opt=True )
    stream.seek(0)
    system_rankings = getSystemRankings(stream)
    score = getScore(system_rankings, gold_rankings)
    return score


def hill_climbing_search():

    log("Started at %s"%time.ctime())
    # get gold rankings and store in structure
    with open(GOLD_RANKINGS_FILENAME) as goldFile:
        global gold_rankings
        gold_rankings = getSystemRankings(goldFile)

    # make sure the necessary files are loaded
    main.load_the_files(opt=True)

    # get the normalization coefficients
    if NORMALIZE:
        swiki_max = max(main.unigram_frequencies.values())
        #ilen_max = max(list(map(len, unigram_frequencies.keys())))
        ilen_max = 28   # too much garbage, hard to normalize
                        # set to 28, for "antidisestablishmentarianism"
        #wnet_max = max([get_wordnet_score(w) for w in unigram_frequencies])
        wnet_max = 75   # for "break", given by the above expression
    else:
        swiki_max = ilen_max = wnet_max = 1.0

    global check_range, norm_coefficients
    check_range = [1.0, 10.0, 100.0, 1000.0, 100000.0, 1000000.0, 10000000.0]
    norm_coefficients = [ilen_max, wnet_max, swiki_max, 1.0]

    results = Counter()
    old_position = (0,0,0,0)

    score = evaluate_solution(old_position)
    results[old_position] = score
    print("Normalized system score for "+str(old_position)+":", score)
    i = 0; j = 1

    while True:
        i += 1
        log("%d positions done, %d calculated"%(i,j))

        # look at the neighbors
        neighbors = get_neighbors(results, old_position)

        # evaluate them
        for pos in neighbors:
            j += 1
            score = evaluate_solution(pos)
            results[pos] = score
            print("\t"+str(pos)+": ", score)
            log("%d positions done, %d calculated"%(i,j))

        # see if any one of them is better
        best = results[old_position]
        new_position = None
        for pos in neighbors:
            if results[pos] > best:
                best = results[pos]
                new_position = pos

        if new_position:
            old_position = new_position
        else:
            break

    log("done") 
    print("best result: %s, score is %s" \
            %(str(old_position), str(results[old_position])))
    for res in results.most_common(10):
        print("position %s\t\tscore:%s\n"%(str(res[0]), str(res[1])))

if __name__ == "__main__":
    hill_climbing_search()
