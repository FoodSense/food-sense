from queue import Queue
from scale import Scale

queue = Queue()

scale = Scale(queue)
scale.setReferenceUnit(-25.725)
scale.reset()
scale.tare()

scale.getWeight()
