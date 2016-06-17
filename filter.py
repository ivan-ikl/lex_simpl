#!/usr/bin/python3

import sys
import time
from collections import Counter, defaultdict
from operations import *

start_time = time.time()

def log(message):
    now = "[%.4f] "%(time.time() - start_time)
    print(now + message, file=sys.stderr)

def usage():
    print("Usage:")
    print(" "+sys.argv[0]+" min_value input_file [output_file]")

def main():

    if len(sys.argv) not in [3,4]:
        usage(); sys.exit(-1)

    cutoff = int(sys.argv[1])

    log("Starting, time is "+time.ctime())

    with open(sys.argv[2]) as input_file:
        context_vectors = load_context_vectors(input_file)
    log("loaded in the context vectors")

    filter_context_vectors(context_vectors, cutoff)
    log("filtered the context vectors with cutoff %d"%(cutoff,))

    if len(sys.argv)==4:
        try:
            output_file = open(sys.argv[3], "w")
        except:
            log("invalid output_file name, printing to stdout instead")
            output_file = sys.stdout
    else:
        output_file = sys.stdout

    save_context_vectors(context_vectors, output_file)
    log("done.")

if __name__=="__main__":
    main()
