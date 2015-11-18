#!python3
import datetime
import json
import random
import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

levels = "debug info warning error".split()
words = "the quick brown fox jumps over the lazy dog".split()

while True:
    word = random.choice(words)
    level = random.choice(levels)
    timestamp = datetime.datetime.utcnow().isoformat()
    record = {
        "timestamp" : timestamp, 
        "level" : level,
        "word" : word
    }
    print("Sending:", record)
    #~ string = json.dumps(record)
    string = "%s %s %s" % (level, timestamp, word)
    socket.send_string(string)
    time.sleep(0.75)