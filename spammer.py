import sys
import signal
import multiprocessing
import time
import random
import json
import urllib2
import os

processes = []
address = "LUGOG9XGRF99PDGZNOCNFVICJXSGJZHBQJAOUGOKH9QKLVOWAWJAIEIOBDHEPMSWKVLTHMWQLAOFVDFPN"

def cleanup(a, b):
    print "Cleaning up all processes ..."
    for p in processes:
        p.terminate()

def writeToFile(process, value):
    try:
        fileName = "./" + process + ".txt"
        f = open(fileName, 'a+')
        f.write(json.dumps(value))
        f.write('\n')
        f.close()

        return True

    except Exception as inst:
        print type(inst)
        print inst
        print "Could not write to file %s" % (process)

        return False

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
    print "%s total Address count: %d\n" % (currProcess, numTx)
    writeToFile(currProcess, elapsedTime)
    genAddress(seed, numTx)

def genTx(seed, numTx):
    unconfirmedCount = 0
    while True:
        print "Waiting confirmation"
        time.sleep(5)
        command = "{'command': 'getTransfers', 'seed': '" + seed + "', 'securityLevel': 1}"
        request = urllib2.Request(url="http://localhost:999", data=command)
        data = urllib2.urlopen(request).read()
        data = json.loads(data)

        notConfirmed = False
        for i in range(0, len(data['transactions'])):
            if (data['transactions'][i]['persistence'] == 0):
                notConfirmed = True
                break

        if notConfirmed is False:
            break
        print "Not confirmed yet %s" % (seed)
        unconfirmedCount += 1

        if (unconfirmedCount > 3):
            print "Converted into address spammer"
            genAddress(seed, numTx)

    command = "{'command': 'transfer', 'seed': '" + seed + "', 'securityLevel': 1, 'address': '" + address + "', 'value': '1', 'message': '', 'minWeightMagnitude': 13}"
    sendRequest(seed, numTx, command, genTxCallback)

def genTxCallback(seed, numTx, returnValue, elapsedTime):
    print "\nGenerated new tx in %d seconds" % (elapsedTime)
    numTx += 1
    currProcess = multiprocessing.current_process().name
    print "%s total Tx count: %d\n" % (currProcess, numTx)
    writeToFile(currProcess, elapsedTime)

    genTx(seed, numTx)

def main(argv):

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
            # if (len(seeds) < numcpus):
            #     print "Not enough seeds. Seed count should equal your CPU count"
            #     return

            for i in range(0, len(seeds)):
                processSeed = seeds[len(processes)]
                print processSeed
                processes.append(multiprocessing.Process(target=genTx, args=(processSeed, 0)))
                processes[-1].start()
                print "Spawned Tx Process: %d\n" % (len(processes))

            for i in range(0, numcpus - len(seeds)):
                processSeed = genSeed()
                processes.append(multiprocessing.Process(target=genAddress, args=(processSeed, 0)))
                processes[-1].start()
                print "Spawned Addr Process: %d\n" % (len(processes))

    except Exception:
        print "Error, something went wrong."

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    print "Starting spammer"
    main(sys.argv[1:])
