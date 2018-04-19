import tkinter as tk
import time

def test():
    print('test')

    root.after(100, test)

root = tk.Tk()
test()
root.mainloop()
