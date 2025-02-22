import tkinter as tk
import time
from tkinter import ttk
import logging
import windnd  # 用于拖拽
from .tree_plus import tree_obj_mouse_highlight, tree_obj_clear, tree_obj_find


class tree_tag:
    def __init__(self, app, frame_tags, bar_v, tree_file_search):
        self.app = app
        self.frame_tags = frame_tags
        self.bar_v = bar_v
        self.conf = app.conf
        self.tree_file_search = tree_file_search  # 这个之后要解耦
        self.lst_tags = []
        self.tree_body = ttk.Treeview(self.frame_tags,
                                      columns=['tags'],
                                      # columns = ['index','type','folders','folder_path'],
                                      displaycolumns=['tags'],
                                      selectmode=tk.BROWSE,
                                      show="headings",
                                      style='Taglist.Treeview',
                                      # show="tree",
                                      # cursor='hand2',
                                      yscrollcommand=self.bar_v.set)  # , height=18)

        self.tree_body.heading("tags", text="全部标签", anchor='w', command=self.tree_tag_search)
        self.tree_body.column('tags', width=int(self.conf.ui_ratio * self.conf.ui_conf['FRAME_RIGHT_WIDTH']),
                              anchor='w')
        # 滚动条联动
        self.bar_v.config(command=self.tree_body.yview)
        #
        self.tree_body.bind('<ButtonRelease-1>', self.on_tag_choose)
        self.tree_body.bind('<KeyRelease-Up>', self.on_tag_choose)
        self.tree_body.bind('<KeyRelease-Down>', self.on_tag_choose)
        self.tree_body.bind("<Motion>", self.mouse_highlight)

    def on_tag_choose(self, event=None):
        """
        点击标签的处理
        """
        res = ''
        for item in self.tree_body.selection():
            res = self.tree_body.item(item, "values")[0]
        if res in ['（全部）']:
            res = ''
        if res == '':
            self.set_search_tag_selected(0)
        else:
            self.set_search_tag_selected(res)
        self.tree_file_search()

    def get_tag(self):
        """
        获取标签项（只是内容字符串，目前还不是列表）。
        """
        the_tag = ''
        USE_SELECTION = False
        if USE_SELECTION:  # 不会运行这些
            for item in self.app.tree_body.selection():
                the_tag = self.app.tree_body.item(item, "values")[0]
                break
        else:
            the_tag = self.app.v_tag.get()  # TODO app.v_tag 是个隐藏的bug，不可见但一直在发挥作用，并不合适。
        #
        if the_tag in ['（全部）']:
            the_tag = ''
        logging.debug('标签里面是' + the_tag)
        return the_tag

    def set_tag(self):
        """
        指定当前选中的标签项目
        """
        pass

    def get_lst_tags(self):
        """
        获取完整的标签列表
        """
        pass

    def set_lst_tag(self, lst_tags_in):
        """
        标签列表的排序
        TODO 这个函数的功能需要重构，这个也是 tag 的最后工作
        """
        # 令@开头的标签在最前
        lst_top = []
        lst_en = []
        lst_cn = []
        for tag_name in lst_tags_in:
            if tag_name == '':
                continue
            if str(tag_name).startswith('@'):
                lst_top.append(tag_name)
            else:
                lst_en.append(tag_name)
        # 英文无论大小写都一起排序
        lst_en = sorted(lst_en, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
        # 组合起来
        lst_tags_in = lst_top + lst_en + lst_cn
        #
        # 列表：
        tmp_sub_tag = self.tree_body.selection()
        tree_obj_clear(self.tree_body, self.app)
        #
        self.app.tree_lst_sub_tag.insert('', 0, values=("（全部）",), tags=['line1'])
        tmp = 0
        for tag_name in lst_tags_in:
            tmp += 1
            # print(tag_name)
            if str(tag_name).strip() == '':
                continue
            self.tree_body.insert('', tmp, values=(tag_name,),
                                  tags=['line1', ] if tmp % 2 == 0 else ['line2', ])  # 必须加逗号，否则对存在空格的不可用
            # image=IMAGE_FOLDER,
        self.app.tree_lst_sub_tag.update()
        #
        # 下拉框：
        self.app.v_tag['value'] = [''] + lst_tags_in
        try:
            if self.app.v_tag.get() != '':
                find_res = tree_obj_find(full_path=self.app.v_tag.get(),
                                         need_update=False,
                                         the_tree=self.app.tree_lst_sub_tag,
                                         the_bar=self.app.bar_sub_tag_v,
                                         the_col=0)
                if find_res == -1:  # 如果没找到的话
                    tmp = self.app.tree_lst_sub_tag.get_children()[0]
                    self.app.tree_lst_sub_tag.selection_set(tmp)
            else:
                tmp = self.app.tree_lst_sub_tag.get_children()[0]
                self.app.tree_lst_sub_tag.selection_set(tmp)
        except Exception as e:
            logging.error(f"error in tree_tag 137: {e}")
        #
        self.lst_tags = lst_tags_in

    def set_search_tag_selected(self, ind):
        """
        设置标签，选中指定的项目。
        如果输入的是字符串，则选中字符串。
        """
        # 如果是字符串的话；
        if type(ind) is str:
            try:
                tags2 = self.app.v_tag['values']
                self.set_search_tag_selected(tags2.index(ind))
            except:
                self.set_search_tag_selected(0)
        # 如果是数字的话
        elif type(ind) is int:
            #
            # 下拉框
            self.app.v_tag.current(ind)
            #
            # 列表：
            # tree_obj_find('（全部）',the_tree=app.tree_body,the_bar=app.bar_sub_tag_v,the_col=0)
        else:
            self.app.v_tag.current(0)

    def tree_tag_search(self, event=None):
        """
        这是个目前没有用的函数。
        """
        pass

    def mouse_highlight(self, event, clear_only=False):
        """
        文件夹树的鼠标悬浮效果。
        :param event:
        :param clear_only:
        :return:
        """
        tree_obj_mouse_highlight(event, self.app, clear_only=clear_only, the_tree=self.tree_body)
