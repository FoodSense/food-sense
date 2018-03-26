from hx711 import HX711

class Scale:
    def __init__(self, data, sck):
        print('Initializing Scale object')
        
        self.__hx711 = HX711(data, sck, 128, 'A')
        self.weight = None

    # Record the current weight on the scale
    def getWeight(self):
        print('Reading scale')
        
        