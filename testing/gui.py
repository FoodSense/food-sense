from tkinter import *
from queue import *
import threading
import time

class ThreadedTask(threading.Thread):
    def __init__(self, queue):
        print('Init ThreadedTask')
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        print('Run called')
        i += 1
        self.queue.put(i)
        time.sleep(5)
        
        self.after(100, run)
              
    
class GUI:
    def __init__(self, master):
        print('Initializing GUI')
        
        self.master = master
        self.queue = Queue()

        # Create start button
        self.startButton = Button(self.master, command=self.startClick)
        self.startButton.configure(
            text="Start", background="Green",
            padx=50
            )
        self.startButton.pack(side=TOP)

        # Create stop button
        self.stopButton = Button(self.master, command=self.stopClick)
        self.stopButton.configure(
            text="Stop", background="Red",
            padx=50
            )
        self.stopButton.pack(side=TOP)

    def startClick(self):
        print('Start button pressed')

        ThreadedTask(self.queue).start()
        self.master.after(100, self.process_queue)

    def stopClick(self):
        print('Stop button pressed')

    def updateScreen(self, msg):
        print('Updating screen')
        print(msg)

    def process_queue(self):
        print('Processing queue')
        
        try:
            msg = self.queue.get_nowait()
            print('msg: {}'.format(msg))
            #self.updateScreen(msg)
        except Empty:
            print('Exception')
        self.master.after(100, self.process_queue)

window = Tk()    
gui = GUI(window)
window.mainloop()
