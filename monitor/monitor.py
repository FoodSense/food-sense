import mcp3008

class Monitor:
    def __init__(self):
        print('Initializing System Monitoring object')
        
        self.__adc = mcp3008.MCP3008.fixed([mcp3008.CH0])adc
        
    def getTemp(self):
        print('Reading temperature')
        
        value = self.__adc()
        print(value)