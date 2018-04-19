import tkinter as tk
import threading
import time
import sys

try:
    from foodsense import foodSense
except ImportError:
    print('Failed to import foodSense module')
    sys.exit(1)

class GUI(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

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

    def startClick(self):
        t = threading.Thread(target=foodSense)
        t.start()
        #t.join()

    def stopClick(self):
        print('Stop clicked')
        t.stop

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
