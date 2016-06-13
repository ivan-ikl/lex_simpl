#!/usr/bin/env python
# encoding: utf-8

"""
Adapted from scorer.py (originally by Sujay Kumar Jauhar on 2011-11-27)
"""
import sys
import re
import itertools
import io
import main
GOLD_RANKINGS_FILENAME = "./test-data/substitutions.gold-rankings"

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
    

if __name__ == "__main__":
    
    #get gold rankings and store in structure
    with open(GOLD_RANKINGS_FILENAME) as goldFile:
        gold_rankings = getSystemRankings(goldFile)
    
    weights = [1.0, 1.0, 1.0]
    stream = io.StringIO()
    main.main( weights=weights, output_stream=stream, opt=True )
    stream.seek(0)
    system_rankings = getSystemRankings(stream)
    
    score = getScore(system_rankings, gold_rankings)
    
    print('Normalized system score:', score)
