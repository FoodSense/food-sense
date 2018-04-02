from hx711.hx711 import HX711

class Scale:
    def __init__(self, data, sck):
        print('Initializing Scale object')
       
        self.DATA = data
        self.SCK = sck

        self.hx711 = HX711(self.DATA, self.SCK)
        self.weight = None

    # Record the current weight on the scale
    def getWeight(self):
        print('Reading scale')
