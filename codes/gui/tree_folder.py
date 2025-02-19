"""
文件夹树
"""
import tkinter as tk
import time
from tkinter import ttk
import logging
import windnd  # 用于拖拽


class frame_tree_folder:
    def __init__(self):
        pass


class tree_folder:
    def __init__(self, app, frame_obj, bar_v_obj, bar_h_obj):
        self.app = app
        self.tree = ttk.Treeview(frame_obj,
                                 selectmode=tk.BROWSE,
                                 style='Dark.Treeview',
                                 show="tree",
                                 yscrollcommand=bar_v_obj.set,
                                 xscrollcommand=bar_h_obj.set,
                                 )  # , height=18)
        bar_h_obj.config(command=self.tree.xview)
        bar_v_obj.config(command=self.tree.yview)
        #
        # 函数绑定
        windnd.hook_dropfiles(self.tree, func=self.star_add_drag)
        self.tree.bind('<ButtonRelease-1>', self.on_choose)
        self.tree.bind('<KeyRelease-Up>', self.on_choose)
        self.tree.bind('<KeyRelease-Down>', self.on_choose)
        self.tree.bind("<Motion>", self.mouse_highlight_add)
        self.tree.bind("<Button-3>", self.right_click)  # 绑定文件夹区域的右键功能
        #
        self.tree.bind('<Control-v>', tree_file_put_down)

    def get_selected_folder(self) -> dict:
        """
        获取当前选中的文件夹
        """

    def search_folder(self, event=None):
        """
        按文件夹名称搜索
        """
        keyword_folder = self.app.entry_search_folder.get()  # 应该修改为方法，而不是直接访问控件

        if keyword_folder is None:
            keyword_folder = ''
        if len(keyword_folder.strip()) <= 0:
            keyword_folder = ''
        self.app.keyword_folder = keyword_folder
        self.update()  # tree_folder_update()

    def on_choose(self, event=None):
        """
        点击选中文件夹之后的动作，原为 tree_folder_on_choose
        """

    def update(self):
        """
        原为 tree_folder_update
        """

    def star_add_drag(self):
        pass

    def right_click(self, event=None):
        """
        右键菜单
        """

    def mouse_highlight_add(self, event=None):
        pass

    def rename_folder(self, event=None):
        """
        重命名文件夹
        """