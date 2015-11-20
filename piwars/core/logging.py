# -*- coding: utf-8 -*-
import os, sys
import logging
import logging.handlers

from . import config        
from . import comms

class PubsubHandler(logging.Handler):
    
    def __init__(self, hostname, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publisher = comms.Publisher(hostname, port)
    
    def emit(self, record):
        try:
            self.publisher.publish(self.format(record))
        except Exception:
            self.handleError(record)

LOGGING_NAME = __package__ or "piwars"
LOGGING_FILENAME = "%s.log" % LOGGING_NAME
LOGGING_FILEPATH = LOGGING_FILENAME

level = logging.DEBUG
console_formatter = logging.Formatter("%(message)s")
pubsub_formatter = logging.Formatter("%(levelname)s %(message)s")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s")

handler = logging.FileHandler(
    LOGGING_FILEPATH,
    mode="a",
    encoding="utf-8"
)
handler.setLevel(level)
handler.setFormatter(formatter)

stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(level)
stderr_handler.setFormatter(console_formatter)

pubsub_handler = PubsubHandler(config.PUBSUB_LISTEN_ON_IP, config.PUBSUB_LISTEN_ON_PORT)
pubsub_handler.setLevel(level)
pubsub_handler.setFormatter(pubsub_formatter)

def logger(name):
    _logger = logging.getLogger("%s.%s" % (LOGGING_NAME, name))
    _logger.setLevel(level)
    _logger.addHandler(handler)
    _logger.addHandler(stderr_handler)
    _logger.addHandler(pubsub_handler)
    return _logger
    