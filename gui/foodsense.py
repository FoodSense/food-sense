#!/usr/bin/python3
from queue import Queue
from queue import Empty
import RPi.GPIO as GPIO
import tkinter as tk
import threading
import time
import sys

try:
    from firebase import Firebase
    from detect import Detect
    from monitoring import Monitoring
    from scale import Scale
except ImportError:
    print('Failed to import required Food Sense modules')
    sys.exit(1)


class Thread(threading.Thread):
    
    # Initialize Thread class
    def __init__(self, queue):
        print('Initializing Thread')

        # Initilize thread
        threading.Thread.__init__(self)
        self.event = threading.Event()

        # Assign queue
        self.q = queue

    # Run Food Sense in thread
    def run(self):
        # Set up LED pin
        LED=27
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED, GPIO.OUT)

        # Initialize objects
        f = Firebase(self.q)
        d = Detect(f, self.q)
        m = Monitoring(f, self.q)
        s = Scale(self.q)

        # Set scale calibration
        s.setReferenceUnit(-25.725)
        s.reset()
        s.tare()

        self.q.put('Ready')
        
        # Loop until stop event is set
        while not self.event.is_set():

            # Loop while RPi is on AC power
            while m.powerOn:

                # Check if stop has been set
                if self.event.is_set():
                    break

                # Loop while fridge door is closed
                while m.doorClosed():
                    if not m.powerOn():
                        break
                    m.checkTemp()
                    
                    # Check if stop hsa been set
                    if self.event.is_set():
                        break
                else:
                    print('Door was opened')
                    self.q.put('Door opened')
                    GPIO.output(LED, True)
                    m.startDoorTimer()
                    
                    while m.doorOpen():
                        print('Waiting for door to close')
                        
                        m.checkDoorTimer()
                        m.checkTemp()
                    else:
                        print('Door closed')
                        self.q.put('Door closed')

                        s.getWeight()
                        d.getImage()
                        d.detectItem()
                        d.parseResponse(s.weight)
                        GPIO.output(LED, False)
                        
                        print('Done')
                        self.q.put('Done')
            else:
                m.powerSave()

        f.close()   # Firebase app must be closed before we can create another instance


class GUI(tk.Frame):

    # Initialize GUI class
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        print('Initializing GUI')

        # Unititialized thread object
        self.thread = None

        # Queue to communicate from FS thread
        self.queue = Queue()

        # Set up text box and vertical scroll bar
        self.text = tk.Text(self, height=6, width=10)
        self.vsb = tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='top', fill='both', expand=True)
        
        # Start button
        self.startButton = tk.Button(self, command=self.startClick)
        self.startButton.configure(text='Start Food Sense', background='Green')
        self.startButton.pack(side='left', fill='both', expand=True)

        # Stop button
        self.stopButton = tk.Button(self, command=self.stopClick)
        self.stopButton.configure(text='Stop Food Sense', background='Red')
        self.stopButton.pack(side='right', fill='both', expand=True)

    # Start Food Sense thread
    def startClick(self):
        print('Start clicked')
        self.queue.put('Starting Food Sense')

        self.thread = Thread(self.queue)
        self.thread.daemon = True
        self.thread.start()

    # Stop Food Sense thread
    def stopClick(self):
        print('Stop clicked')
        self.queue.put('Stopping Food Sense')
        
        self.thread.event.set()
        self.therad = None
        time.sleep(5)

    # Send output to gui
    def updateScreen(self):

        try:
            msg = self.queue.get_nowait()
            self.text.insert('end', msg + '\n')
            self.text.see('end')
        except Empty:
            pass
                    
        self.after(500, self.updateScreen)


if __name__ == '__main__':
    window = tk.Tk()
    w,h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry('%dx%d+0+0' % (w,h))
    window.wm_title('Food Sense')
    
    frame = GUI(window)
    frame.pack(fill='both', expand=True)
    frame.updateScreen()

    window.mainloop()
