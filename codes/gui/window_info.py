import tkinter as tk
from tkinter import ttk
import logging

LOGO_PATH = './resources/icons/LOGO.ico'


class window_info:
    def __init__(self, conf, app, version):
        self.conf = conf
        self.app = app
        self.version = version

    def show(self):
        """
        显示关于窗口。
        不需要任何参数。
        """
        screenwidth = self.conf.SCREEN_WIDTH
        screenheight = self.conf.SCREEN_HEIGHT
        w_width = int(660*self.conf.ui_ratio)
        w_height = int(560*self.conf.ui_ratio)
        info_window = tk.Toplevel(self.app.window, background='white')
        info_window.geometry(
            '%dx%d+%d+%d' % (w_width, w_height, (screenwidth - w_width) / 2, (screenheight - w_height) / 2))
        info_window.title('关于标签文库')

        info_window.transient(self.app.window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
        info_window.grab_set()  # 模态

        info_window.deiconify()
        info_window.lift()
        info_window.focus_force()
        info_window.iconbitmap(LOGO_PATH)  # 左上角图标

        info_frame = tk.Frame(info_window, padx=5, pady=5, background='white')
        info_frame.pack(expand=0, fill=tk.BOTH)

        tmp = tk.Label(info_frame, background='white', text='\n')
        tmp.pack()
        tmp = tk.Label(info_frame, background='white', text='标签文库 / Tagdox', fg='#2d7d9a', font=('微软雅黑', 16))
        tmp.pack()
        tmp = tk.Label(info_frame, background='white', text='\n马剑 个人开发')
        tmp.pack()
        tmp = tk.Label(info_frame, background='white', text='版本：' + self.version + '')
        tmp.pack()
        tmp = tk.Label(info_frame, background='white', text='Powered by Python and Tkinter\n')
        tmp.pack()

        global p_logo
        p_logo = tk.PhotoImage(file='.//resources/imgs/二维码设计.png')
        logolbl = tk.Label(info_frame, background='white', text='A', image=p_logo)
        logolbl.pack()

        # tmp = tk.Label(info_frame,background='white', text='（欢迎扫码访问产品动态）')
        # tmp.pack()
