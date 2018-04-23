#!/usr/bin/python3
import statistics
import sys

try:
    from hx711 import HX711
except ImportError:
    print('Error importing HX711 module')
    sys.exit(1)


class Scale:
    def __init__(self, queue, dout=22, pd_sck=17, source=None, samples=20, spikes=4, sleep=0.1):
        print('Initializing Scale')

        # Queue
        self.q = queue

        # Class member variables
        self.source = source or HX711(dout, pd_sck)
        self.samples = samples
        self.spikes = spikes
        self.sleep = sleep
        self.history = []
        
        # Weight value that will be used by storage class
        self.weight = 0
        self.prevWeight = 0
    
    def newMeasure(self):
        value = self.source.getWeight()
        self.history.append(value)

    def getMeasure(self):
        """Useful for continuous measurements."""
        self.newMeasure()
        # cut to old values
        self.history = self.history[-self.samples:]

        avg = statistics.mean(self.history)
        deltas = sorted([abs(i-avg) for i in self.history])

        if len(deltas) < self.spikes:
            max_permitted_delta = deltas[-1]
        else:
            max_permitted_delta = deltas[-self.spikes]

        valid_values = list(filter(
            lambda val: abs(val - avg) <= max_permitted_delta, self.history
        ))

        return statistics.mean(valid_values)

    def getWeight(self, samples=None):
        """Get weight for once in a while. It clears history first."""
        self.history = []

        [self.newMeasure() for i in range(samples or self.samples)]

        self.prevWeight = self.weight
        val = self.getMeasure()

        if val > 0:
            val = 0 - val
        elif val < 0:
            val = abs(val)
        else:
            pass

        self.weight = round(val / 50) * 50
        
        print('Weight recorded: {} g'.format(self.weight))
        self.q.put('Weight recorded: {} g'.format(self.weight))

    def tare(self, times=25):
        self.source.tare(times)

    def setOffset(self, offset):
        self.source.setOffset(offset)

    def setReferenceUnit(self, reference_unit):
        self.source.setReferenceUnit(reference_unit)

    def powerDown(self):
        self.source.powerDown()

    def powerUp(self):
        self.source.powerUp()

    def reset(self):
        self.source.reset()
