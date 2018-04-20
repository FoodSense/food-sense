from queue import Queue
from queue import Empty
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
        threading.Thread.__init__(self)
        
        self.event = threading.Event()
        self.q = queue
        self.q.put('Initializing Thread')

    # Run Food Sense in thread
    def run(self):
        self.q.put('Starting Food Sense')
        
        # Initialize objects
        f = Firebase(self.q)
        d = Detect(f, self.q)
        m = Monitoring(f, self.q)
        s = Scale(self.q)

        # Set scale calibration
        s.setReferenceUnit(-25.725)
        s.reset()
        s.tare()

        # Loop until stop event is set
        while not self.event.is_set():

            # Loop while RPi is on AC power
            while m.powerOn:
                self.q.put('Power is on')
                time.sleep(1)

                # Check if stop hsa been set
                if self.event.is_set():
                    break

                # Loop while fridge door is closed
                while m.doorClosed():
                    self.q.put('Door is closed')
                    m.checkTemp()
                    time.sleep(1)
                    
                    # Check if stop hsa been set
                    if self.event.is_set():
                        break

                    if m.doorOpen():
                        self.q.put('Door was opened')
                        m.startDoorTimer()
                        
                        while m.doorOpen():
                            self.q.put('Waiting for door to close')
                            m.checkDoorTimer()
                            m.checkTemp()
                            time.sleep(1)
                        else:
                            self.q.put('Door was closed')

                            s.getWeight()
                            d.getImage()
                            d.detectItem()
                            d.parseResponse(s.weight)
                    else:
                        pass
                else:
                    self.q.put('Door must be closed on program startup')
            else:
                m.powerSave()
        else:
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
        self.text = tk.Text(self, height=6, width=40)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='top', fill='both', expand=True)
        
        # Start button
        self.startButton = tk.Button(self, command=self.startClick)
        self.startButton.configure(text='Start', background="Green")
        self.startButton.pack(side='left', fill='both', expand=True)

        # Stop button
        self.stopButton = tk.Button(self, command=self.stopClick)
        self.stopButton.configure(text="Stop", background="Red")
        self.stopButton.pack(side='right', fill='both', expand=True)

    # Start Food Sense thread
    def startClick(self):
        print('Start clicked')

        self.thread = Thread(self.queue)
        self.thread.start()

    # Stop Food Sense thread
    def stopClick(self):
        print('Stop clicked')

        self.thread.event.set()
        self.therad = None
        time.sleep(5)

    # Send output to gui
    def updateScreen(self):
        print('Updating screen')

        try:
            msg = self.queue.get_nowait()
            self.text.insert('end', msg + '\n')
            self.text.see('end')
        except Empty:
            pass
                    
        self.after(1000, self.updateScreen)

if __name__ == '__main__':
    window = tk.Tk()
    
    frame = GUI(window)
    frame.pack(fill='both', expand=True)
    frame.updateScreen()

    window.mainloop()
