from tkinter import ttk
import tkinter as tk

class tdTreeview(ttk.Treeview):
    def __init__(self,base):
        super.__init__(self,base)
        self.name = 'test'


if __name__=='__main__':
    root=tk.Tk()
    a=tdTreeview(root)
