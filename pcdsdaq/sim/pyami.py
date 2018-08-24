import logging
import random

import numpy as np

connect_success = True
logger = logging.getLogger(__name__)


def connect(ami_str):
    logger.debug('simulated pyami connect')
    if not connect_success:
        raise RuntimeError('simulated fail')
    else:
        Entry._connected = True


class Entry:
    _connected = False

    def __init__(self, ami_name, ami_type, filter_string=None):
        logger.debug('Initializing test pyami Entry %s', ami_name)
        self._ami_name = ami_name
        if not connect_success:
            raise RuntimeError('simulated fail: bad connection')
        if not Entry._connected:
            raise RuntimeError('simulated fail: did not call connect')
        self._filt = filter_string
        self._count = random.randint(1, 100)
        self._values = [random.random() for i in range(self._count)]

    def get(self):
        return dict(mean=np.mean(self._values),
                    rms=np.sqrt(np.mean(np.square(self._values))),
                    err=0,
                    entries=len(self._values))

    def clear(self):
        logger.debug('Clearing test pyami queue for %s', self._ami_name)
        self._values.clear()
