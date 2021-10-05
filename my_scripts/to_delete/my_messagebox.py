# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 09:01:25 2021

@author: MaJian

做一个独立的弹窗。

"""
import tkinter as tk
import tkinter.ttk as ttk
class myMessageBox:
    
    def __init__(self,base_window,box_title='未定义标题',box_msg='未定义内容',init_text=''):
        self.window=base_window
        self.title=box_title
        self.init_text=init_text # 初始值
        self.msg=box_msg
        self.screenwidth = self.window.winfo_screenwidth()
        self.screenheight = self.window.winfo_screenheight()
        self.w_width = 500
        self.w_height = 200
        self.x_pos=(self.screenwidth-self.w_width)/2
        self.y_pos=(self.screenheight-self.w_height)/2
        self.txt=tk.StringVar(value=init_text)
    
        self.input_window=tk.Toplevel(self.window)
        self.input_window.geometry('%dx%d+%d+%d'%(self.w_width, self.w_height, self.x_pos,self.y_pos))
        self.input_window.title(self.title)
        # self.input_window.withdraw()
        self.input_window.deiconify()
        self.input_window.lift()
        self.input_window.focus_force()

        self.iframe=tk.Frame(self.input_window,padx=20,pady=20)
        self.iframe.pack(expand=0,fill=tk.BOTH)
    
        self.lb=tk.Label(self.iframe,text=self.msg)
        self.lb.pack(anchor='sw')
    
        self.et=tk.Entry(self.iframe)
        self.et.insert(0,self.init_text)
        self.et.bind('<Return>',self.get_inp_value)
        self.et.pack(expand=0,fill=tk.X)
        
        self.bt_yes=ttk.Button(self.iframe,text='确定',command=self.get_inp_value)
        self.bt_yes.pack(pady=20)
        # self.grab_set() # 模态，无效
        self.et.focus()
        # self.resizable(0,0)
        
  
    def get_inp_value(self,event=None):
        self.txt.value=self.et.get()
        print(self.txt.value)
        return self.txt
    
    # def __del__(self):
    #     '''
    #     析构函数

    #     '''
    #     # self.get_inp_value()
    #     return self.txt
    #     del self
        
    #     pass

def call_my_msgbox(root,title,text,init_value):
    box = myMessageBox(root,title,text,init_value)
    return box
    
    
#%%
if __name__ == '__main__':
    root=tk.Tk()
    box = call_my_msgbox(root,'请问','可以用了吗','默认值')
    val=box.txt
    root.mainloop()
    # pass