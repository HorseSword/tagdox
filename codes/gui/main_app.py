"""

"""
import tkinter as tk
import time
from tkinter import ttk
import logging


class td_main_app:
    """
    主窗口类
    """
    def __init__(self, conf) -> None:
        """
        界面部分。
        也就是UI的设计。
        """
        self.last_focus = None
        self.the_tree = None
        self.keyword_folder = ''  # 用于搜索文件夹的
        self.file_open_time = time.time()  # 最近一次tree_file_open 的时间；
        self.window = tk.Tk()
        self.conf = conf
        conf.ui_ratio = 1.5  # 界面的放大倍率，之后会提供前端修改的功能
        #
        # 调整清晰度 ############################################
        try:
            # 放在这里，是为了兼容不能打开ctypes的计算机。
            from ctypes import windll

            # 告诉操作系统使用程序自身的dpi适配
            windll.shcore.SetProcessDpiAwareness(1)
            # 获取屏幕的缩放因子
            ScaleFactor = windll.shcore.GetScaleFactorForDevice(0)  # 当前屏幕放大百分数（125）
            # 设置程序缩放
            self.window.tk.call('tk', 'scaling', ScaleFactor / 75)
            #
            conf.SCREEN_WIDTH = self.window.winfo_screenwidth() * ScaleFactor / 100  # 必须考虑分辨率导致的偏移
            conf.SCREEN_HEIGHT = self.window.winfo_screenheight() * ScaleFactor / 100  #
            logging.info (('screen info: w,h = ', conf.SCREEN_WIDTH, conf.SCREEN_HEIGHT))

        except:
            conf.SCREEN_WIDTH = self.window.winfo_screenwidth()
            conf.SCREEN_HEIGHT = self.window.winfo_screenheight()
        finally:
            conf.ui_ratio = (conf.SCREEN_WIDTH / 1920)
        #
        #
        self.PIC_DICT = {
            "龙猫": tk.PhotoImage(file=".//resources/imgs/龙猫.gif"),
            #
            "menu": tk.PhotoImage(file="./resources/icons/menu.png"),
            "menu_2": tk.PhotoImage(file="./resources/icons/menu_2.png"),
            "menu_3": tk.PhotoImage(file="./resources/icons/menu_4.png"),
            "search_20": tk.PhotoImage(file="./resources/icons/search_20.png"),
            "search_black": tk.PhotoImage(file="./resources/icons/search_20_black.png"),
            "cancel_20": tk.PhotoImage(file="./resources/icons/cancel_20.png"),
            "cancel_black": tk.PhotoImage(file="./resources/icons/cancel_20_black.png"),
            #
            "word": tk.PhotoImage(file="./resources/icons/word.png"),
            "excel": tk.PhotoImage(file="./resources/icons/excel.png"),
            "ppt": tk.PhotoImage(file="./resources/icons/ppt.png"),
            "pdf": tk.PhotoImage(file="./resources/icons/pdf.png"),
            "zip": tk.PhotoImage(file="./resources/icons/zip.png"),
            "img": tk.PhotoImage(file="./resources/icons/img.png"),
            "html": tk.PhotoImage(file="./resources/icons/html.png"),
            "md": tk.PhotoImage(file="./resources/icons/md.png"),
            "file": tk.PhotoImage(file="./resources/icons/file.png"),
            #
            "folder_100_20": tk.PhotoImage(file="./resources/icons/folder_100_20.png"),
            "folder_75_20": tk.PhotoImage(file="./resources/icons/folder_75_20.png"),
            "folder_50_20": tk.PhotoImage(file="./resources/icons/folder_50_20.png"),
            "folder_25_20": tk.PhotoImage(file="./resources/icons/folder_25_20.png"),
        }
        #
        self.COLOR_DICT = {
            "blue": "#3a92c5",
            "blue_light": "#8CCDF2",
            "cyan": "#2EB8AC",
            "cyan_light": "#5cd6cc",
            "gray": "bfbfbf",
            "green": "#21a366",
            "green_1": "#107c41",
            "green_2": "#185c37",
            "darkback_1": "2a333c",
            "darkback_2": "1e1e1e",
        }
        #
        self.SCREEN_WIDTH = conf.SCREEN_WIDTH
        self.SCREEN_HEIGHT = conf.SCREEN_HEIGHT
        #
        # 窗体设计 ############################################
        #
        self.window.title(cst.TAR + ' ' + cst.VER)
        screenwidth = conf.SCREEN_WIDTH
        screenheight = conf.SCREEN_HEIGHT
        w_width = int(conf.SCREEN_WIDTH * 0.9)
        w_height = int(conf.SCREEN_HEIGHT * 0.8)
        x_pos = (conf.SCREEN_WIDTH - w_width) / 2
        y_pos = (conf.SCREEN_HEIGHT - w_height) / 2
        self.window.geometry('%dx%d+%d+%d' % (w_width, w_height, x_pos, y_pos))
        # window.resizable(0,0) #限制尺寸
        self.window.minsize(600, 500)
        self.window.state('zoomed')  # 最大化
        self.str_btm = tk.StringVar()  # 最下面显示状态用的
        self.str_btm.set("加载中")
        self.prog = tk.DoubleVar()  # 进度
        self.prog_win = None
        self.BAR_V_WIDTH = int(16 * conf.ui_ratio)  # 滚动条宽度
        self.BAR_H_WIDTH = int(16 * conf.ui_ratio)
        #
        self.clipboard_files = []  # 程序内剪切板
        self.clipboard_items = []  # 程序内剪切板
        self.clipboard_state = 'move'
        self.clipboard_folder = ''  # 待移动的文件夹
        #
        #
        # 框架设计 ############################################
        #
        self.frame_window = ttk.Frame(self.window, padding=(0, 0, 0, 0), relief='flat', borderwidth=0)
        self.frame_window.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=0, pady=0)
        #
        # 文件夹区
        self.frame_left = ttk.Frame(self.frame_window,
                                   # style="Dark.Treeview",
                                   # width=int(w_width * 0.4),
                                   padding=(0, 0, 0, 0),
                                   borderwidth=0,
                                   width=int(conf.ui_ratio * conf.ui_conf['FRAME_FOLDER_WIDTH']),  # 没有用，因为 Frame 默认是根据控件大小改变的。
                                   relief='flat')  # ,)
        self.frame_left.pack(side=tk.LEFT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
        self.frame_left.pack_propagate(0)  # 设置为0则框架不被内部撑大。默认是1.
        #
        # 文件夹区域纵向滚动条
        self.bar_folder_v = tk.Scrollbar(self.frame_left, width=self.BAR_V_WIDTH)
        # self.bar_folder_v = ttk.Scrollbar(self.frame_folder)#, width=16)
        self.bar_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
        # 文件夹区域横向滚动条
        self.bar_folder_h = tk.Scrollbar(self.frame_left, orient='horizontal',
                                         width=self.BAR_V_WIDTH, )
        # self.bar_folder_h.pack(side = tk.BOTTOM, expand = 0, fill = tk.X)  # TODO 暂时没有功能所以不放
        #
        # 菜单区
        self.frame_folder_top = ttk.Frame(self.frame_left,
                                   relief='flat',
                                   style='Dark.TFrame',
                                   # width=int((320 - 16 * 1) * conf.ui_ratio),
                                   height =int(40 * conf.ui_ratio),
                                   # borderwidth=0,
                                   padding=(10, 10, 10, 2), # 内边距，左上右下
                                   )  # , borderwidth=1 ,relief='solid')  # ,width=600) LabelFrame
        self.frame_folder_top.pack(side=tk.TOP, expand=0, fill=tk.X, padx=0, pady=0)  # padx=10, pady=5)
        self.frame_folder_top.pack_propagate(0)  # 使框架固定尺寸
        #
        # 文件夹在frameLeft内部
        self.frame_folder = ttk.Frame(self.frame_left, style='Dark.TFrame', relief='flat', borderwidth=0, )
        # height=SCREEN_HEIGHT * 0.8)  # ,width=600),width=int(w_width*0.4)
        self.frame_folder.pack(side=tk.TOP, expand=1, fill=tk.BOTH, padx=0, pady=0)  # padx=10,pady=5)
        # frame_folder.grid(column=0,row=0)
        #
        # 子文件夹区（也在frameLeft内部）
        self.XX_frameSubFolder = ttk.Frame(self.frame_left, relief='flat')  # ,width=600)
        if FOLDER_TYPE == 1:  # 已经作废，不可能再生效
            self.XX_frameSubFolder.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH, padx=0, pady=2)  # padx=10,pady=5)
        #

        # self.frame_tags.pack(side=tk.BOTTOM, expand=1, fill=tk.Y, padx=10, pady=5)  # padx=10,pady=5)
        #
        # 文件夹下面的控制区
        self.frameFolderCtl = ttk.Frame(self.frame_left, height=int(10*conf.ui_ratio), borderwidth=0, relief=tk.SOLID)
        # self.frameFolderCtl.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=5)
        # 上面功能区：frame_top
        self.frame_top = ttk.Frame(self.frame_window,
                                relief='flat',
                                borderwidth=0,
                                # relief='solid',
                                height=int(120 * conf.ui_ratio),
                                   padding=(8,10,8,5),
                                )  # , borderwidth=1 ,relief='solid')  # ,width=600) LabelFrame
        self.frame_top.pack(expand=0, fill=tk.X, padx=0, pady=0)  # padx=10, pady=5)
        self.frame_top.propagate()
        # 主功能区
        self.frame_main = ttk.Frame(self.frame_window, border=0)  # ,height=800)
        self.frame_main.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)  # padx=10, pady=0)
        # 标签区
        # self.frame_tags = ttk.Frame(self.frame_left)  # ,width=600)
        self.frame_tags = ttk.Frame(self.frame_main, width= int(conf.ui_ratio * conf.ui_conf['FRAME_RIGHT_WIDTH']))
        self.frame_tags.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
        #
        # readme 区域
        self.frame_readme = ttk.Frame(self.frame_tags, height=1)
        self.frame_readme.pack(side=tk.BOTTOM, expand=0, fill=tk.X, )
        self.frame_readme.pack_propagate(0)  # 设置为0则框架不被内部撑大。默认是1.
        #
        # self.str_readme = tk.StringVar()  # 最下面显示状态用的
        # self.str_readme.set("这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，\n它将会在单词边界处自动换行。")
        # text = ttk.Label(self.frame_readme,textvariable=self.str_readme)  # wrap="word" 使文本在单词边界处进行换行
        # text.pack()
        #
        self.har_readme_v = tk.Scrollbar(self.frame_readme,  # orient='horizontal',
                                         width=self.BAR_V_WIDTH, )
        self.text_readme = tk.Text(self.frame_readme, wrap='word',borderwidth=0,
                                   padx=10,pady=10,
                                   background='#e8e8e7',#'#e8e8e7',
                                   font=conf.FONT_TREE_BODY,
                                   yscrollcommand=self.har_readme_v.set,
                                   relief='flat')
        self.har_readme_v.pack(side = tk.RIGHT, expand = 0, fill = tk.Y)
        self.text_readme.pack(fill=tk.BOTH, expand=1)
        self.har_readme_v.config(command=self.text_readme.yview)
        #
        self.frame_tree_files = ttk.Frame(self.frame_main,)  # ,height=800)
        self.frame_tree_files.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)  # padx=10, pady=0)
        #
        # 底部区
        self.frame_bottom = ttk.Frame(self.frame_window, height=int(120*conf.ui_ratio), padding=(0, 0, 0, 0), relief='flat')
        self.frame_bottom.pack(side=tk.BOTTOM, expand=0, fill=tk.X, padx=0, pady=0)
        #
        ##############
        # 控件
        ##############
        #
        self.bt_folder_add = ttk.Button(self.frame_top, text='添加文件夹到关注列表')  # state=tk.DISABLED,,command=setting_fun
        self.bt_folder_drop = ttk.Button(self.frameFolderCtl, text='移除文件夹')
        #
        self.v_sub_folders = ttk.Combobox(self.frame_top)  # 子文件夹选择框
        self.v_tag = ttk.Combobox(self.frame_top)  # 标签选择框
        self.entry_search_files = ttk.Entry(self.frame_top)  # 搜索框
        self.v_folders = ttk.Combobox(self.frame_folder)  # 文件夹选择框
        #
        # 主文件树
        self.tree_main = td_tree_file(self.frame_tree_files, self.frame_bottom)
        self.bar_tree_v = self.tree_main.bar_tree_v
        # self.bar_tree_v = tk.Scrollbar(self.frame_main)  # 右侧滚动条
        self.bar_tree_h = self.tree_main.bar_tree_h
        # self.bar_tree_h = tk.Scrollbar(self.frame_main, orient=tk.HORIZONTAL)  # 底部滚动条
        self.tree_file = self.tree_main.body
        #
        # # 标签区
        # # self.frame_tags = ttk.Frame(self.frame_left)  # ,width=600)
        # self.frame_tags = ttk.Frame(self.frame_main, width=int(conf.ui_ratio*300))
        # self.frame_tags.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
        #
        # 文件夹列表
        if True:
            # self.bar_folder_v = tk.Scrollbar(self.frame_folder, width=int(16*conf.ui_ratio))
            # # self.bar_folder_v = ttk.Scrollbar(self.frame_folder)#, width=16)
            # self.bar_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
            #
            self.tree_lst_folder = ttk.Treeview(self.frame_folder,
                                                selectmode=tk.BROWSE,
                                                style='Dark.Treeview',
                                                show="tree",
                                                yscrollcommand=self.bar_folder_v.set,
                                                xscrollcommand=self.bar_folder_h.set,
                                                )  # , height=18)
            self.bar_folder_v.config(command=self.tree_lst_folder.yview)
            self.bar_folder_h.config(command=self.tree_lst_folder.xview)
            # self.tree_lst_folder.heading("folders", text="已关注的文件夹", anchor='w')
            # self.tree_lst_folder.column('folders', width=300, anchor='w')
            #
            self.tree_lst_folder.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=0, pady=0)
        #
        # 子文件夹列表
        if True:
            self.bar_sub_folder_v = tk.Scrollbar(self.XX_frameSubFolder, width=int(16*conf.ui_ratio))
            self.XX_tree_lst_sub_folder = ttk.Treeview(self.XX_frameSubFolder,
                                                    columns=['folders'],
                                                    # columns = ['index','type','folders','folder_path'],
                                                    displaycolumns=['folders'],
                                                    selectmode=tk.BROWSE,
                                                    show="headings",
                                                    # show="tree",
                                                    # cursor='hand2',
                                                    style="Dark.Treeview",
                                                    yscrollcommand=self.bar_sub_folder_v.set)  # , height=18)

            self.XX_tree_lst_sub_folder.heading("folders", text="子文件夹", anchor='w')
            self.XX_tree_lst_sub_folder.column('folders', width=int(conf.ui_ratio*300), anchor='w')
            self.bar_sub_folder_v.config(command=self.XX_tree_lst_sub_folder.yview)
            #
            self.bar_sub_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
            self.XX_tree_lst_sub_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
        #
        # 标签列表：
        if True:
            self.v_tag_search = tk.Entry(self.frame_tags)
            self.bar_sub_tag_v = tk.Scrollbar(self.frame_tags, width=self.BAR_V_WIDTH)
            #
            self.tree_lst_sub_tag = ttk.Treeview(self.frame_tags,
                                                 columns=['tags'],
                                                 # columns = ['index','type','folders','folder_path'],
                                                 displaycolumns=['tags'],
                                                 selectmode=tk.BROWSE,
                                                 show="headings",
                                                 style='Taglist.Treeview',
                                                 # show="tree",
                                                 # cursor='hand2',

                                                 yscrollcommand=self.bar_sub_tag_v.set)  # , height=18)

            self.tree_lst_sub_tag.heading("tags", text="全部标签", anchor='w', command=tree_tag_search)
            self.tree_lst_sub_tag.column('tags', width=int(conf.ui_ratio * conf.ui_conf['FRAME_RIGHT_WIDTH']), anchor='w')
            self.bar_sub_tag_v.config(command=self.tree_lst_sub_tag.yview)
            #
            self.bar_sub_tag_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
            self.tree_lst_sub_tag.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
        #
        # tree_lst_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=10)
        # XX_tree_lst_sub_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=10)
        #
        vPDX = 10  # 10
        vPDY = 5  # 5

        self.bt_clear = ttk.Button(self.frame_top,
                                   style='Menu.TButton',
                                   text='X',
                                   # image=self.PIC_DICT['cancel_20'],
                                   width=3,
                                   padding=0,
                                   command=exec_clear_search_items)

        # bt_search=tk.Button(frame_top,text='搜索', command=tree_file_search,bd=0,activebackground='red')
        self.bt_search = ttk.Button(self.frame_top,
                                    # style='Light.TButton',
                                    text='搜索',
                                    # padding=(0, 0, 0, 0),
                                    # image=self.PIC_DICT['search_20'],
                                    command=tree_file_search)  # ,bd=0,activebackground='red')

        if True:  # 子文件夹搜索
            self.lable_sub_folders = tk.Label(self.frame_top, text='子文件夹')

            self.v_sub_folders['value'] = [''] + lst_sub_path
            self.v_sub_folders['state'] = 'readonly'

            self.v_sub_folders.bind('<<ComboboxSelected>>', on_sub_folders_choose)

        # set_search_tag_values(lst_tags)

        self.v_tag['state'] = 'readonly'  # 只读
        self.v_tag.bind('<<ComboboxSelected>>', tree_file_search)
        self.v_tag.bind('<Return>', tree_file_search)  # 绑定回车键

        self.lable_search = ttk.Label(self.frame_top, text='关键词')
        self.entry_search_files.bind('<Return>', tree_file_search)  # 绑定回车键
        #
        self.bt_settings = ttk.Button(self.frame_folder_top, #frame_folder_top, frame_top
                                      # style='Menu.TButton',
                                      # width=304,
                                      # image=self.PIC_DICT['menu_3'],
                                      # compound=tk.LEFT,
                                      # background='green',
                                      # relief='flat',
                                      # padding=(10, 4, 10, 4),
                                      padding=(0, 0, 0, 0),
                                      # pady = 0,
                                      # width= 300,
                                      text='菜单',
                                      # anchor="center",
                                      )  # ,command=show_online_help)
        #
        # 布局： #####
        #
        # 从右向左排
        nx=0
        # nx+=1
        self.bt_settings.pack(side=tk.LEFT, expand=0, fill= tk.Y,
                              padx = 5,
                              # padx=0 if nx % 2 == 0 else vPDX,
                              pady=2)  # 搜索按钮
        # expand=1, fill=tk.Y, padx=5, pady=10)  #
        nx += 1
        self.bt_search.pack(side=tk.RIGHT, expand=0,
                            padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  # 搜索按钮
        nx += 1
        self.bt_clear.pack(side=tk.RIGHT, expand=0, fill=tk.Y,
                           padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        #
        nx += 1
        self.entry_search_files.pack(side=tk.RIGHT, expand=0, fill = tk.Y,
                           padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        nx += 1
        self.lable_search.pack(side=tk.RIGHT, expand=0,
                               padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        #
        nx += 1
        #
        # 只看当前文件夹
        self.v_this_folder = tk.IntVar()
        self.v_this_folder.set(0)
        self.cb_current_folder_olny = ttk.Checkbutton(self.frame_top,
                                           text='只显示当前文件夹内容',
                                           variable=self.v_this_folder,
                                           command=tree_file_search,
                                           onvalue=1, offvalue=0)
        self.cb_current_folder_olny.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)
        #
        # 文件夹分层
        self.v_folder_layers = tk.IntVar()
        self.v_folder_layers.set(1)
        self.checkbutton_folder_layers = ttk.Checkbutton(self.frame_top,
                                             text='按子文件夹分组',
                                             variable=self.v_folder_layers,
                                             command=tree_file_search,
                                             onvalue=1, offvalue=0)
        self.checkbutton_folder_layers.pack(side=tk.RIGHT, expand=0,
                                            padx=0 if nx % 2 == 0 else vPDX,
                                            pady=vPDY)
        #
        # 只看笔记
        self.v_note_only = tk.IntVar()
        self.v_note_only.set(0)
        self.cb_note = ttk.Checkbutton(self.frame_top,
                                       text='只显示笔记',
                                       variable=self.v_note_only,
                                       command=tree_file_search,
                                       onvalue=1, offvalue=0)
        # self.cb_note.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)
        #
        self.bt_test = ttk.Button(self.frame_top, text='测试功能', command=function_for_testing)
        if DEVELOP_MODE:
            self.bt_test.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        #
        # 布局
        self.bar_tree_h.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=2)  # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E
        self.tree_file.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=2, pady=1)
        self.bar_tree_v.pack(side=tk.LEFT, expand=0, fill=tk.Y, padx=2, pady=1)  # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

        vPDX = 10
        vPDY = 5

        # 进度条
        self.frame_prog = ttk.Frame(self.frame_bottom)
        # frame_prog.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY)
        self.progressbar_file = ttk.Progressbar(self.frame_prog, variable=self.prog, mode='determinate')
        self.progressbar_file.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)

        # self.lable_sum = tk.Label(self.frame_bottom, text=self.str_btm, textvariable=self.str_btm)
        self.lable_sum = ttk.Label(self.frame_top, text=self.str_btm, textvariable=self.str_btm)
        self.lable_sum.pack(side=tk.LEFT, expand=0, padx=5, pady=vPDY)  #

        self.bt_clear_folder_search = ttk.Button(self.frame_folder_top,
                                   # style='Menu.TButton',
                                   text='X',
                                   width = 3,
                                   # image=self.PIC_DICT['cancel_20'],
                                                 padding=0,
                                   command=tree_folder_search_clear,
                                                 )
        self.bt_clear_folder_search.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=5, pady=2)
        #
        # self.lable_search_folder = ttk.Label(self.frame_folder_top, text='文件夹')
        self.entry_search_folder = ttk.Entry(self.frame_folder_top,)
        self.entry_search_folder.pack(side=tk.RIGHT, expand=1, fill=tk.BOTH, padx=5, pady=2)
        self.entry_search_folder.bind('<Return>', tree_folder_search)  # 绑定回车键
        #
        # self.bt_settings.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=5, pady=2)
        #
        # 站位空白块，用于出现在滚动条顶部空间
        # self.canvas_space = tk.Canvas(self.frame_folder_top, bg='#e8e8e7',
        #                               relief='flat', borderwidth=0,
        #                               width=(16*conf.ui_ratio),
        #                               )
        # self.canvas_space.pack(side=tk.RIGHT, fill='y', expand=0,)
        #
        # self.bt_folder_add.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #
        # self.bt_new_note = ttk.Button(self.frame_top, text='新建笔记')  # ,state=tk.DISABLED)#,command=update_main_window)
        # self.bt_new_note.pack(side=tk.LEFT, expand=0, padx=0, pady=vPDY)  #
        #
        self.bt_reload = ttk.Button(self.frame_bottom,
                                    text='刷新',
                                    command=update_main_window,
                                    )
        self.bt_reload.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        self.bt_add_tag = ttk.Button(self.frame_bottom, text='添加标签',
                                     command=tree_file_tag_add_via_dialog)  # , command=input_new_tag
        self.bt_add_tag.pack(side=tk.RIGHT, expand=0, padx=0, pady=vPDY)  #

        self.bt_new_note = ttk.Button(self.frame_bottom, text='新建笔记')  # ,state=tk.DISABLED)#,command=update_main_window)
        self.bt_new_note.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        self.bt_readme = ttk.Button(self.frame_bottom, text='readme')  # ,state=tk.DISABLED)#,command=update_main_window)
        self.bt_readme.pack(side=tk.RIGHT, expand=0, padx=0, pady=vPDY)  #

        # 新标签的输入框（不再使用）
        self.combobox_tag = ttk.Combobox(self.frame_bottom, width=int(16*conf.ui_ratio))
        # combobox_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        self.combobox_tag.bind('<Return>', input_new_tag)
        self.combobox_tag['value'] = lst_tags
        #
        # self.lable_tag = tk.Label(self.frame_bottom, text='添加新标签')
        # lable_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        #
        # 其他初始化设定
        if ALL_FOLDERS == 1:
            self.bt_folder_drop.configure(state=tk.DISABLED)
        #
        # 测试气泡
        # b = tix.Balloon(window, statusbar=None)
        # b.bind_widget(bt_clear,balloonmsg='test',statusmsg=None)
        #
        self.bar_tree_v.config(command=self.tree_file.yview)
        self.bar_tree_h.config(command=self.tree_file.xview)
        # 样式
        self.window.iconbitmap(LOGO_PATH)  # 左上角图标 #

    def update_readme(self, text_in = None):
        """
        用于更新 readme 里面的内容
        """
        text_to_show = text_in
        current_path = conf.get_current_path()
        #
        if text_in is None:
            text_to_show = '（当前目录没有说明文档）'
            try:
                # 检查当前是否是文件夹，也就是二级目录
                tmp_files = os.listdir(current_path)
                # 检查当前文件夹内是否有readme.md
                # 读取前5000字
                if 'readme.md' in tmp_files or 'README.md' in tmp_files:
                    app.frame_readme.configure(height= conf.ui_conf['FRAME_README_HEIGHT']) # 原来是600
                    try:
                        with open(current_path+'/readme.md', 'rb') as f:
                            text_to_show = f.read(5000).decode('utf-8')
                    except Exception as e:
                        with open(current_path+ '/readme.md', 'rb') as f:
                            text_to_show = f.read(5000).decode('gbk','ignore')
                    if len(text_to_show)==0:
                        text_to_show = '（当前目录的说明文档 readme.md 内容为空）'
                else:
                    app.frame_readme.configure(height=1)  # 隐藏高度
                    #
            except Exception as e:
                text_to_show = str(e)
        #
        self.text_readme.configure(state='normal')
        self.text_readme.delete('1.0', tk.END)
        self.text_readme.insert(tk.END, text_to_show)
        self.text_readme.configure(state='disabled')

    def bind_funcs(self):
        # 功能绑定
        #
        self.bt_folder_add.configure(command=tree_folder_star_add_by_dialog)  # 增加文件夹
        self.bt_folder_drop.configure(command=tree_folder_star_remove)  # 减少文件夹
        #
        # 设置拖拽反映函数
        windnd.hook_dropfiles(self.tree_lst_folder, func=tree_folder_star_add_drag)
        windnd.hook_dropfiles(self.tree_file, func=tree_file_drag_enter_popupmenu)
        windnd.hook_dropfiles(self.tree_lst_sub_tag, func=tree_file_drag_enter_move)
        #
        # 各种功能的绑定
        # tree_lst_folder.bind('<<ListboxSelect>>',tree_folder_on_choose)
        # tree_lst_folder.bind('<Button-1>',tree_folder_on_choose)
        self.tree_lst_folder.bind('<ButtonRelease-1>', tree_folder_on_choose)
        self.tree_lst_folder.bind('<KeyRelease-Up>', tree_folder_on_choose)
        self.tree_lst_folder.bind('<KeyRelease-Down>', tree_folder_on_choose)
        self.tree_lst_folder.bind("<Motion>", tree_folder_mouse_highlight_add)
        self.tree_lst_folder.bind("<Button-3>", tree_folder_right_click)  # 绑定文件夹区域的右键功能
        #
        self.XX_tree_lst_sub_folder.bind('<ButtonRelease-1>', on_sub_folders_choose)
        self.XX_tree_lst_sub_folder.bind('<KeyRelease-Up>', on_sub_folders_choose)
        self.XX_tree_lst_sub_folder.bind('<KeyRelease-Down>', on_sub_folders_choose)
        self.XX_tree_lst_sub_folder.bind("<Button-3>", XX_show_popup_menu_sub_folder)  # 绑定文件夹区域的右键功能
        #
        self.tree_lst_sub_tag.bind('<ButtonRelease-1>', tree_tag_on_choose)
        self.tree_lst_sub_tag.bind('<KeyRelease-Up>', tree_tag_on_choose)
        self.tree_lst_sub_tag.bind('<KeyRelease-Down>', tree_tag_on_choose)
        self.tree_lst_sub_tag.bind("<Motion>", tree_tag_mouse_highlight)
        #
        # 程序内快捷键
        self.window.bind_all('<Control-r>', tree_file_create_readme)  # 绑定添加笔记的功能。
        self.window.bind_all('<Control-n>', exec_create_note)  # 绑定添加笔记的功能。
        self.window.bind_all('<Control-f>', jump_to_search)  # 跳转到搜索框。
        self.window.bind_all('<Control-t>', tree_file_tag_add_via_dialog)  # 快速输入标签。
        self.window.bind_all('<Control-p>', tree_folder_search)
        #
        # self.tree_file.bind('<Control-X>', tree_file_cut_ctn)  # 拿起。
        # self.tree_file.bind('<Control-x>', tree_file_cut)  # 拿起。
        # self.tree_file.bind('<Control-C>', tree_file_copy_cnt)  # 拿起。
        # self.tree_file.bind('<Control-c>', tree_file_copy)  # 拿起。
        # self.tree_file.bind('<Control-v>', tree_file_put_down)  # 放下。
        self.tree_lst_folder.bind('<Control-v>', tree_file_put_down)  # 放下，点选文件夹之后仍然可以操作，可以提高用户体验。
        # self.tree_file.bind('<F2>', tree_file_rename)  # 重命名
        # self.tree_file.bind('<Delete>', tree_file_delete)  # 重命名
        # self.tree_file.bind("<Motion>", tree_obj_mouse_highlight)

        self.frame_folder_top.bind("<Motion>", tree_folder_mouse_highlight_remove)

        # self.tree_file.bind('<Double-Button-1>', tree_file_open)
        # self.tree_file.bind('<Return>', tree_file_open)
        # self.tree_file.bind("<Button-3>", tree_file_right_click)  # 绑定文件区域的右键功能
        # self.tree_file.bind("<Button-1>", tree_file_left_click)  # 绑定文件区域的右键功能
        # self.tree_file.bind("<ButtonRelease-3>", show_popup_menu_file)  # 绑定文件夹区域的右键起功能
        # self.tree_file.bind('<F5>', update_main_window)  # 刷新。
        # self.tree_file.bind('<space>', self.call_space)  # 刷新。
        # #
        # self.tree_file.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记
        self.tree_lst_folder.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记
        #
        # window.bind_all('<Control-t>',jump_to_tag) # 跳转到标签框。
        #
        # 按钮功能绑定
        # bt_setting.configure(command=show_window_setting) #

        # bt_folder_drop.configure(command=tree_file_tag_add_via_dialog)  # 加标签
        # bt_settings.configure(command=show_popup_menu_main)  # 菜单按钮
        self.bt_settings.bind("<ButtonRelease-1>", show_popup_menu_main)  # 菜单按钮
        self.bt_new_note.configure(command=exec_create_note)
        self.bt_readme.configure(command=tree_file_create_readme)
