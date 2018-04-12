import io
import sys
import time
import tkinter as tk
from contextlib import redirect_stdout

class Thing():
    def doStuff(self):
        print('stuff') 

    def doMoreStuff(self):
        print('more stuff')
        
    def loopStuff(self):
        for i in range(20):
            print('test')

class GUI(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        class IORedirector(object):
            def __init__(self,TEXT_INFO):
                self.TEXT_INFO = TEXT_INFO

        class StdoutRedirector(IORedirector):
            def write(self,str):
                self.TEXT_INFO.config(text=self.TEXT_INFO.cget('text') + str)

        # Text field
        self.text = tk.Text(self, height=10, width=40)
        
        # Vertical scroll bar
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        
        # Conifgure elements
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        
        f = io.StringIO()
        with redirect_stdout(f):
            thing = Thing()
            thing.doStuff()
            thing.doMoreStuff()
            thing.loopStuff()
        self.text.insert("end", f.getvalue() + "\n")
        self.text.see("end")
        #self.add_timestamp()

    def add_timestamp(self):
        self.text.insert("end", time.ctime() + "\n")
        self.text.see("end")
        self.after(1000, self.add_timestamp)


window = tk.Tk()
frame = GUI(window)
frame.pack(fill="both", expand=True)
window.mainloop()