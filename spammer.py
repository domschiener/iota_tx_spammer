import sys
import signal
import os
import multiprocessing
import time
import random
import json
import urllib2

processes = []
address = "ANEROPGWWGGKZTHOTNBZVFZYQGWHHSOYLGQJKARMKCJCIZNAOKMKXYMUGAETM9FTUHHCIYKBEGTXFVJHO"

def cleanup(a, b):
    print "Cleaning up all processes ..."
    for p in processes:
        os.kill(p.pid, signal.SIGQUIT)

def genSeed():
    #
    # Generates a random seed
    #

    chars = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seed = ""
    while (len(seed) < 81):
        seed += chars[random.randint(0, len(chars) - 1)]

    print "Generated random seed!"
    return seed

def sendRequest(seed, numTx, command, callback):
    try:
        startTime = time.time()
        request = urllib2.Request(url="http://localhost:999", data=command)
        url = urllib2.urlopen(request)
        elapsedTime = (time.time() - startTime)

        returnValue = url.read()
        callback(seed, numTx, json.loads(returnValue), elapsedTime)

    except Exception:
        print "Could not send request to Node"

def genAddress(seed, numTx):
    command = "{'command': 'generateNewAddress', 'seed': '" + seed + "', 'securityLevel': 1, 'minWeightMagnitude': 13}"
    sendRequest(seed, numTx, command, genAddressCallback)

def genAddressCallback(seed, numTx, returnValue, elapsedTime):
    print "\nGenerated new address %s in %d seconds" % (returnValue['address'], elapsedTime)
    numTx += 1
    currProcess = multiprocessing.current_process().name
    print "%s total Tx count: %d\n" % (currProcess, numTx)
    genAddress(seed, numTx)

def genTx(seed, numTx):
    command = "{'command': 'transfer', 'seed': '" + seed + "', 'securityLevel': 1, 'address': '" + address + "', 'value': '1', 'message': '', 'minWeightMagnitude': 13}"
    sendRequest(seed, numTx, command, genTxCallback)

def genTxCallback(seed, numTx, returnValue, elapsedTime):
    print "\nGenerated new tx in %d seconds\n" % (elapsedTime)
    numTx += 1
    currProcess = multiprocessing.current_process().name
    print "%s total Tx count: %d\n" % (currProcess, numTx)
    genTx(seed, numTx)

def main(argv):
    #
    # Get the number of cores and launch a spammer on each
    #

    # Predefined seeds for tx spamming. One seed (with iotas) for each core
    seeds = []
    option = argv[0]

    try:
        numcpus = multiprocessing.cpu_count()

        # Option 0 is for spamming addresses
        if (option == '0'):
            for i in range(0, numcpus):
                processSeed = genSeed()
                processes.append(multiprocessing.Process(target=genAddress, args=(processSeed, 0)))
                processes[-1].start()
                print "Spawned Process: %d\n" % (len(processes))
        else:
            if (len(seeds) != numcpus):
                print "Not enough seeds. Seed count should equal your CPU count"
                return

            for i in range(0, numcpus):
                processSeed = seeds[len(processes)]
                processes.append(multiprocessing.Process(target=genTx, args=(processSeed, 0)))
                processes[-1].start()
                print "Spawned Process: %d\n" % (len(processes))

    except Exception:
        print "Error, something went wrong."

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    print "Starting spammer"
    main(sys.argv[1:])
