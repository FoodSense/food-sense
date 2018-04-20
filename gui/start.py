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
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    
    def run(self):
        print('Starting Food Sense')
        
        #with Firebase() as f, Detect(f) as d, Monitoring(f) as m, Scale() as s:

        f = Firebase()
        d = Detect(f)
        m = Monitoring(f)
        s = Scale()

        # Set scale calibration
        s.setReferenceUnit(-25.725)
        s.reset()
        s.tare()

        # Loop until stop event is set
        while not self.event.is_set():

            # Loop while RPi is on AC power
            while m.powerOn:
                print('Power is on')
                time.sleep(1)

                # Check if stop hsa been set
                if self.event.is_set():
                    break

                # Loop while fridge door is closed
                while m.doorClosed():
                    print('Door is closed')
                    m.checkTemp()
                    time.sleep(1)
                    
                    # Check if stop hsa been set
                    if self.event.is_set():
                        break

                    if m.doorOpen():
                        print('Door was opened')
                        m.startDoorTimer()
                        
                        while m.doorOpen():
                            print('Waiting for door to close')
                            m.checkDoorTimer()
                            m.checkTemp()
                            time.sleep(1)
                        else:
                            print('Door was closed')

                            s.getWeight()
                            d.getImage()
                            d.detectItem()
                            d.parseResponse(scale.weight)
                    else:
                        pass
                else:
                    print('Door must be closed on program startup')
            else:
                m.powerSave()
        else:
            f.close()

class GUI(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        # Unititialized thread object
        self.thread = None

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
        self.thread = Thread()
        self.thread.start()

    # Stop Food Sense thread
    def stopClick(self):
        print('Stop clicked')
        self.thread.event.set()
        self.therad = None
        time.sleep(5)

    def updateScreen(self):
        print('Updating screen')

        self.text.insert('end', time.ctime() + '\n')
        self.text.see('end')
        self.after(1000, self.updateScreen)

if __name__ == '__main__':
    window = tk.Tk()
    frame = GUI(window)
    frame.pack(fill='both', expand=True)
    window.mainloop()
