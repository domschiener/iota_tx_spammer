import signal
import os
import multiprocessing
import time
import random
import json
import urllib2

processes = []
address = "ANEROPGWWGGKZTHOTNBZVFZYQGWHHSOYLGQJKARMKCJCIZNAOKMKXYMUGAETM9FTUHHCIYKBEGTXFVJHO"

def cleanup():
    print "Cleaing up all processes ..."
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

def sendRequest(seed, command, callback):
    try:
        startTime = time.time()
        request = urllib2.Request(url="http://localhost:999", data=command)
        url = urllib2.urlopen(request)
        elapsedTime = (time.time() - startTime)

        returnValue = url.read()
        callback(seed, json.loads(returnValue), elapsedTime)

    except Exception:
        print "Could not send request to Node"

def genAddress(seed):
    print "Generating new address!"
    command = "{'command': 'generateNewAddress', 'seed': '" + seed + "', 'securityLevel': 1, 'minWeightMagnitude': 13}"
    sendRequest(seed, command, genAddressCallback)

def genAddressCallback(seed, returnValue, elapsedTime):
    print "Generated new address %s in %d seconds\n" % (returnValue['address'], elapsedTime)
    genAddress(seed)

def genTx(seed):
    print "Generating new transaction!"
    command = "{'command': 'transfer', 'seed': '" + seed + "', 'securityLevel': 1, 'address': '" + address + "', 'value': '1', 'message': '', 'minWeightMagnitude': 13}"
    sendRequest(seed, command, genTxCallback)

def main():
    #
    # Get the number of cores and launch a spammer on each
    #

    try:
        numcpus = multiprocessing.cpu_count()

        for i in range(0, numcpus):
            seed = genSeed()
            processes.append(multiprocessing.Process(target=genAddress, args=(seed,)))
            processes[-1].start()
            print "Spawned Process: %d\n" % (len(processes))

    except Exception:
        print "Error, something went wrong."

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    print "Starting spammer"
    main()
