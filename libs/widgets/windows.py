import tkinter as tk
from tkinter import ttk

LOGO_PATH = './src/LOGO.ico'
LARGE_FONT = 10  # 表头字号
MON_FONTSIZE = 9  # 正文字号


class TdProgressWindow:
    """
    一个出现在主窗口中间的进度条
    """

    # input_window = ''  # =tk.Toplevel(self.form0)

    def __init__(self, parent, prog_value=0, prog_text='', ui_ratio=1) -> None:
        """
        进度条，输入进度数值
        """

        # 变量设置
        self.progress = 0
        self.form0 = parent
        self.ui_ratio = ui_ratio
        self.input_value = ''
        self.input_window = tk.Toplevel(self.form0)
        print('———————————— 进度条激活 ——————————')
        self.input_window.title('进度')
        self.my_prog = tk.DoubleVar()  # 进度
        self.my_text = prog_text
        self.my_prog.set(prog_value)
        #
        # 窗口设置
        self.input_window.overrideredirect(True)  # 这句话可以去掉标题栏，同时也会没有阴影
        self.w_width = round(800*self.ui_ratio)
        self.w_height = round(100*self.ui_ratio)
        #
        # 屏幕中央：
        # self.screenwidth = SCREEN_WIDTH
        # self.screenheight = SCREEN_HEIGHT
        # self.x_pos = (self.screenwidth - self.w_width) / 2
        # self.y_pos = (self.screenheight - self.w_height) / 2
        #
        # 主窗口中央：
        self.x_pos = self.form0.winfo_x() + (self.form0.winfo_width() - self.w_width) / 2
        self.y_pos = self.form0.winfo_y() + (self.form0.winfo_height() - self.w_height) / 2

        self.input_window.geometry('%dx%d+%d+%d' % (self.w_width, self.w_height, self.x_pos, self.y_pos))
        # self.input_window.title(self.title)
        self.input_window.transient(self.form0)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
        self.input_window.withdraw()

        try:
            self.input_window.iconbitmap(LOGO_PATH)  # 左上角图标
        except:
            pass

        self.iframe = tk.Frame(self.input_window, padx=20, pady=20)
        self.iframe.pack(expand=0, fill=tk.BOTH)
        # 标签
        self.pct = tk.Label(self.iframe)
        self.pct.pack()
        # 进度条
        self.prog_bar = ttk.Progressbar(self.iframe, variable=self.my_prog)
        self.prog_bar.pack(expand=0, fill=tk.BOTH)
        #
        self.prog_bar.bind("<FocusOut>", self.on_focus_out)
        self.prog_bar.bind('<1>', self.force_close)

    def force_close(self, event=None):
        self.input_window.destroy()

    def on_focus_out(self, event=None):
        """
        失去焦点的事件，自动关闭窗口，避免最小化等操作时程序锁死
        """
        # print(event.widget)
        if event.widget == self.prog_bar:
            print("失去焦点")
            self.force_close(self)

    def set(self, value):
        self.progress = value
        self.my_prog.set(self.progress)
        self.pct.configure(text=self.my_text + str(int(value)) + '%')
        self.input_window.update()
        # self.pct.update()
        # self.prog_bar.update()
        if value == 0:
            self.input_window.withdraw()
        elif value > 0:
            self.input_window.deiconify()  # 置顶
            # self.input_window.lift() # 置顶，但是会导致后面失去输入能力
            # self.input_window.focus_force()

            self.input_window.grab_set()  # 模态

        if value >= 100:
            self.input_window.withdraw()
            # self.input_window.overrideredirect(False) 
            self.input_window.destroy()
            self.__destroy__()


# 自制输入窗体
class TdInputWindow:
    """
    输入窗体类。
    实现了一个居中的模态窗体。
    """
    input_value = ''

    def __init__(self, parent, title='未命名', msg='未定义', default_value='', selection_range=None, ui_ratio=1.0) -> None:
        """
        自制输入窗体的初始化；
        参数：
        selection_range 是默认选中的范围。
        """

        # 变量设置
        self.form0 = parent  # 父窗格
        #
        self.ui_ratio = ui_ratio
        self.input_value = ''
        self.title = title
        self.msg = msg
        self.default_value = default_value
        self.input_window = tk.Toplevel(self.form0)
        #
        self.input_window.transient(self.form0)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
        self.input_window.grab_set()  # 模态

        #
        # 窗口设置
        # self.input_window.overrideredirect(True) # 这句话可以去掉标题栏，同时也会没有阴影
        # 上面功能启用之后，好像快捷键会出现问题。
        self.w_width = round(800*self.ui_ratio)
        self.w_height = round(160*self.ui_ratio)
        #
        # 屏幕中央：
        # self.screenwidth = SCREEN_WIDTH
        # self.screenheight = SCREEN_HEIGHT
        # self.x_pos = (self.screenwidth - self.w_width) / 2
        # self.y_pos = (self.screenheight - self.w_height) / 2
        #
        # 主窗口中央：
        self.x_pos = self.form0.winfo_x() + (self.form0.winfo_width() - self.w_width) / 2
        self.y_pos = self.form0.winfo_y() + (self.form0.winfo_height() - self.w_height) / 2

        self.input_window.geometry('%dx%d+%d+%d' % (self.w_width, self.w_height, self.x_pos, self.y_pos))
        self.input_window.title(self.title)
        #

        try:
            self.input_window.iconbitmap(LOGO_PATH)  # 左上角图标
        except:
            pass

        self.iframe = tk.Frame(self.input_window, padx=20, pady=10)
        self.iframe.pack(expand=0, fill=tk.BOTH)

        # 文本框
        self.lb = tk.Label(self.iframe, text=self.msg, font="微软雅黑 " + str(MON_FONTSIZE))
        self.lb.pack(anchor='sw', pady=5)
        self.input_window.update()

        # 输入框
        self.et = ttk.Entry(self.iframe, font="微软雅黑 " + str(MON_FONTSIZE))
        self.et.insert(0, self.default_value)
        self.et.pack(expand=0, fill=tk.X, pady=5)

        # self.et.selection_range(0, len(self.et.get()))
        if selection_range is None:
            self.et.selection_range(0, len(self.et.get()))
        else:
            self.et.selection_range(0, selection_range)
        self.et.focus()  # 获得焦点

        # self.et.focus()
        # 键盘快捷键
        self.input_window.bind_all('<Return>', self.bt_yes_click)
        self.input_window.bind_all('<Escape>', self.bt_cancel_click)

        self.iframe_bt = tk.Frame(self.input_window, padx=10, pady=10)
        self.iframe_bt.pack()
        # self.iframe_bt.pack(expand=0,fill=tk.BOTH)
        # 按钮
        self.bty = ttk.Button(self.iframe_bt, text='确定', command=self.bt_yes_click)
        self.bty.pack(side=tk.LEFT, padx=20)
        self.btc = ttk.Button(self.iframe_bt, text='取消', command=self.bt_cancel_click)
        self.btc.pack(side=tk.LEFT, padx=20)

        self.input_window.deiconify()
        self.input_window.lift()
        self.input_window.focus_force()

        self.input_window.bind("<FocusOut>", self.on_focus_out)

        self.form0.wait_window(self.input_window)  # 要用这句话拦截主窗体的代码运行

    def on_focus_out(self, event=None):
        """
        失去焦点的事件，自动关闭窗口，避免最小化等操作时程序锁死
        """
        # print(event.widget)
        if event.widget == self.input_window:
            print("输入框失去焦点")
            self.bt_cancel_click(self)

    def bt_cancel_click(self, event=None):
        self.input_window.unbind_all('<Return>')
        self.input_window.unbind_all('<Escape>')
        self.input_window.destroy()

    def bt_yes_click(self, event=None) -> str:
        self.input_window.unbind_all('<Return>')
        self.input_window.unbind_all('<Escape>')
        try:
            self.input_value = self.et.get()  #
        except Exception as e:
            print(e)
        # print(self.input_value)
        self.input_window.destroy()
        return self.input_value

    def __str__(self) -> str:
        return self.input_value

    def __del__(self) -> str:
        self.input_value = ''
        # self.input_window.destroy()
        return ''


class TdSpaceWindow:
    """
    空格窗体类。
    实现了一个居中的模态窗体。
    """
    input_value = ''

    def __init__(self, parent,
                 title='未命名',
                 msg='未定义',
                 default_value='',
                 selection_range=None,
                 width=960,
                 height=560,
                 ui_ratio=1,
                 ) -> None:
        """
        自制输入窗体的初始化；
        参数：
        selection_range 是默认选中的范围。
        """

        # 变量设置
        self.form0 = parent  # 父窗格
        #
        self.ui_ratio = ui_ratio
        self.input_value = ''
        self.title = title
        self.msg = msg
        self.default_value = default_value
        self.sub_window = tk.Toplevel(self.form0)
        #
        self.sub_window.transient(self.form0)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
        # self.sub_window.grab_set()  # 模态，此功能生效后，窗口外不可以点击。注释掉就可以操作了。

        #
        # 窗口设置
        # self.sub_window.overrideredirect(True) # 这句话可以去掉标题栏，同时也会没有阴影
        self.w_width = round(width * self.ui_ratio)
        self.w_height = round(height * self.ui_ratio)
        #
        # 屏幕中央：
        # self.screenwidth = SCREEN_WIDTH
        # self.screenheight = SCREEN_HEIGHT
        # self.x_pos = (self.screenwidth - self.w_width) / 2
        # self.y_pos = (self.screenheight - self.w_height) / 2
        #
        # 主窗口中央：
        self.x_pos = self.form0.winfo_x() + (self.form0.winfo_width() - self.w_width) / 2
        self.y_pos = self.form0.winfo_y() + (self.form0.winfo_height() - self.w_height) / 2

        self.sub_window.geometry('%dx%d+%d+%d' % (self.w_width, self.w_height, self.x_pos, self.y_pos))
        self.sub_window.title(self.title)
        #

        try:
            self.sub_window.iconbitmap(LOGO_PATH)  # 左上角图标
        except:
            pass

        self.iframe = tk.Frame(self.sub_window, padx=20, pady=10)
        self.iframe.pack(expand=1, fill=tk.BOTH)

        # 文本框
        self.lb = tk.Label(self.iframe, text=self.msg,
                           wraplength=900,
                           justify="left",
                           font="微软雅黑 10")
        self.lb.pack(anchor='sw', pady=5)
        self.lb.focus()  # 获得焦点
        self.sub_window.update()

        self.sub_window.bind_all('<space>', self.on_exit)
        #
        # 失去焦点自动退出
        self.sub_window.bind('<FocusOut>', self.on_focus_out)

    def on_focus_out(self, event=None):
        """
        失去焦点的事件，自动关闭窗口，避免最小化等操作时程序锁死
        """
        # print(event.widget)
        if event.widget == self.sub_window:
            print("失去焦点")
            self.on_exit(self)

    def on_exit(self, event=None):
        self.sub_window.destroy()
