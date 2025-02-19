import tkinter as tk
from tkinter import ttk
import logging

dict_file_drag = {"复制": "copy", "移动": "move", "每次询问": "ask"}
dict_window_mode = {"标签模式": "tag", "子文件夹模式": "sub_folder"}
dict_tag_mode = {"包含匹配": 1, "严格全字匹配": 0}
dict_yes_no = {"是": 1, "否": 0}

LOGO_PATH = './resources/icons/LOGO.ico'
FOLDER_TYPE = 2


class window_settings:
    """
    设置窗口
    """
    def __init__(self, conf, app, update_func,):
        """
        初始化。需要的参数：
        conf 配置文件
        app 主程序
        update_func 刷新函数
        """
        self.conf = conf
        self.app = app
        self.update_func = update_func

        self.form = tk.Toplevel(self.app.window)
        self.form.title('设置')
        self.form.resizable(False, False)  # 限制尺寸
        self.form.transient(self.app.window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
        self.form.grab_set()

        self.frame_setting2 = ttk.Frame(self.form, width=800)
        self.bt_setting_yes = ttk.Button(self.frame_setting2, text='确定', command=self.on_yes)
        self.bt_setting_cancel = ttk.Button(self.frame_setting2, text='取消', command=self.form.destroy)

        self.frame_setting1 = ttk.Frame(self.form, padding=(0, 10, 0, 0))
        self.v_inp_sep = ttk.Entry(self.frame_setting1, width=16, text=self.conf.V_SEP)
        self.label_set_folder_depth = ttk.Label(self.frame_setting1, text='识别为标签的文件夹层数')
        self.v_inp_folder_depth = ttk.Combobox(self.frame_setting1, width=16)  # ,textvariable=v2fdepth)
        self.v_last_folder_as_tag = ttk.Combobox(self.frame_setting1, width=16)  # ,textvariable=v2fdepth)
        self.v_inp_note_type = ttk.Combobox(self.frame_setting1, width=16)  # ,textvariable=v2fdepth)
        self.v_inp_drag_type = ttk.Combobox(self.frame_setting1, width=16)
        self.v_tag_easy = ttk.Combobox(self.frame_setting1, width=16)
        self.v_inp_mode = ttk.Combobox(self.frame_setting1, width=16)  # ,textvariable=v2fdepth)

    def on_yes(self, event=None):
        """
        点击确定之后，使参数生效
        """
        # 获得新参数
        need_reboot = False
        # 先处理要重启的：
        #
        if dict_window_mode[self.v_inp_mode.get()] != self.conf.TREE_SUB_SHOW \
                or dict_yes_no[self.v_last_folder_as_tag.get()] != self.conf.FOLDER_AS_TAG:
            if tk.messagebox.askokcancel("请确认", "部分设置需要重启才能生效。确定要保存设置并【关闭程序】吗？"):
                need_reboot = True
            else:
                return
        #
        self.conf.NOTE_EXT = self.v_inp_note_type.get()
        self.conf.set_json_options('note_ext', self.conf.NOTE_EXT, need_write=False)
        #
        self.conf.V_FOLDERS = self.v_inp_folder_depth.get()
        self.conf.set_json_options('vfolders', self.conf.V_FOLDERS, need_write=False)
        #
        self.conf.V_SEP = self.v_inp_sep.get()
        self.conf.set_json_options('sep', self.conf.V_SEP, need_write=False)
        #
        self.conf.FILE_DRAG_MOVE = dict_file_drag[self.v_inp_drag_type.get()]
        self.conf.set_json_options('file_drag_enter', self.conf.FILE_DRAG_MOVE, need_write=False)
        #
        self.conf.TREE_SUB_SHOW = dict_window_mode[self.v_inp_mode.get()]
        self.conf.set_json_options('TREE_SUB_SHOW', self.conf.TREE_SUB_SHOW)
        #
        self.conf.FOLDER_AS_TAG = dict_yes_no[self.v_last_folder_as_tag.get()]
        self.conf.set_json_options('FOLDER_AS_TAG', self.conf.FOLDER_AS_TAG)
        #
        self.conf.TAG_EASY = dict_tag_mode[self.v_tag_easy.get()]
        self.conf.set_json_options('TAG_EASY', self.conf.TAG_EASY)
        #
        # 关闭窗口
        self.form.destroy()
        # 然后刷新文件列表
        if need_reboot:
            self.app.window.destroy()
        else:
            # update_main_window(None, reload_setting=True)
            self.update_func(None, reload_setting=True)
        pass

    def show(self, ):  #
        """
        设置窗口
        """
        screenwidth = self.conf.SCREEN_WIDTH
        screenheight = self.conf.SCREEN_HEIGHT
        w_width = int(500*self.conf.ui_ratio)  # int(screenwidth*0.8)
        w_height = int(400*self.conf.ui_ratio)  # int(screenheight*0.8)
        # 主窗口中央：
        x_pos = self.app.window.winfo_x() + (self.app.window.winfo_width() - w_width) / 2
        y_pos = self.app.window.winfo_y() + (self.app.window.winfo_height() - w_height) / 2
        # x_pos = (screenwidth - w_width) / 2
        # y_pos = (screenheight - w_height) / 2
        self.form.geometry('%dx%d+%d+%d' % (w_width, w_height, x_pos, y_pos))
        self.form.deiconify()
        self.form.lift()
        self.form.focus_force()
        self.form.iconbitmap(LOGO_PATH)  # 左上角图标
        # v2sep=tk.StringVar()
        # v2sep.set(conf.V_SEP)

        # v2sep=conf.V_SEP

        self.frame_setting2.pack(side=tk.BOTTOM, expand=0, fill=tk.X)
        self.frame_setting2.columnconfigure(0, weight=1)
        self.frame_setting2.columnconfigure(1, weight=1)
        #
        # 设置主要框架
        self.frame_setting1.pack(expand=1, fill=tk.BOTH)
        self.frame_setting1.columnconfigure(0, weight=1)
        self.frame_setting1.columnconfigure(1, weight=1)

        # frame_setting2.grid_configure()

        lable_set_sep = ttk.Label(self.frame_setting1, text='标签分隔符')
        lable_set_sep.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.v_inp_sep.delete(0,'end')
        self.v_inp_sep.insert(0, self.conf.V_SEP)
        self.v_inp_sep.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        self.label_set_folder_depth.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        lst_folder_depth = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
        self.v_inp_folder_depth['values'] = lst_folder_depth
        self.v_inp_folder_depth['state'] = 'readonly'
        tmp_n = lst_folder_depth.index(str(self.conf.V_FOLDERS))
        self.v_inp_folder_depth.current(tmp_n)
        self.v_inp_folder_depth.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

        nr = 2
        #
        # 是否将最后的目录视为标签
        nr += 1
        tmp_label_ = ttk.Label(self.frame_setting1, text='将最后一层文件夹作为标签 *')
        tmp_label_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
        #
        self.v_last_folder_as_tag['values'] = list(dict_yes_no.keys())
        self.v_last_folder_as_tag['state'] = 'readonly'
        self.v_last_folder_as_tag.current(0)
        tmp_list = list(dict_yes_no.values())
        logging.debug(f'{tmp_list}')
        tmp_n = tmp_list.index(self.conf.FOLDER_AS_TAG)
        self.v_last_folder_as_tag.current(tmp_n)
        self.v_last_folder_as_tag.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)
        # 笔记类型
        nr += 1
        lable_set_note_type = ttk.Label(self.frame_setting1, text='笔记类型')
        lable_set_note_type.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)

        self.v_inp_note_type['values'] = self.conf.NOTE_EXT_LIST
        self.v_inp_note_type['state'] = 'readonly'
        self.v_inp_note_type.current(0)
        tmp_n = self.conf.NOTE_EXT_LIST.index(self.conf.NOTE_EXT)
        self.v_inp_note_type.current(tmp_n)
        self.v_inp_note_type.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

        # 拖动是移动还是复制
        nr += 1
        # lable_drag_type
        tmp_label_ = ttk.Label(self.frame_setting1, text='拖拽添加文件的操作')
        tmp_label_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
        #
        the_combo = self.v_inp_drag_type
        the_dict = dict_file_drag
        the_val = self.conf.FILE_DRAG_MOVE
        #
        the_combo['values'] = list(the_dict.keys())
        the_combo['state'] = 'readonly'
        the_combo.current(0)
        tmp_list = list(the_dict.values())
        tmp_n = tmp_list.index(the_val)
        the_combo.current(tmp_n)
        the_combo.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

        # 拖动是移动还是复制
        nr += 1
        # lable_drag_type
        tmp_label_ = ttk.Label(self.frame_setting1, text='标签搜索模式')
        tmp_label_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
        #
        the_combo = self.v_tag_easy
        the_dict = dict_tag_mode
        the_val = self.conf.TAG_EASY
        #
        the_combo['values'] = list(the_dict.keys())
        the_combo['state'] = 'readonly'
        the_combo.current(0)
        tmp_list = list(the_dict.values())
        tmp_n = tmp_list.index(the_val)
        the_combo.current(tmp_n)
        the_combo.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

        # 布局是标签模式还是子文件夹模式  # TODO 不再生效
        nr += 1
        tmp_label_ = tk.Label(self.frame_setting1, text='显示模式 *')
        if FOLDER_TYPE == 1:
            tmp_label_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
        #
        self.v_inp_mode['values'] = list(dict_window_mode.keys())
        self.v_inp_mode['state'] = 'readonly'
        self.v_inp_mode.current(0)
        tmp_list = list(dict_window_mode.values())
        print(tmp_list)
        tmp_n = tmp_list.index(self.conf.TREE_SUB_SHOW)
        self.v_inp_mode.current(tmp_n)
        if FOLDER_TYPE == 1:
            self.v_inp_mode.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)
        #
        nr += 1
        tmp_label_ = ttk.Label(self.frame_setting1, text='（注意：标*的项目需要重启生效）')
        tmp_label_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)

        # 下面的设置区域
        nr = 100
        self.bt_setting_yes.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.EW)
        # bt_setting_yes.pack(side=tk.LEFT,expand=0,fill=tk.X)

        self.bt_setting_cancel.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)
        # bt_setting_cancel.pack(side=tk.LEFT,expand=0,fill=tk.X)

        # app.window.wait_window(self.form)
