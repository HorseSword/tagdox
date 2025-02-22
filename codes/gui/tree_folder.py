"""
文件夹树
"""
import shutil
import tkinter as tk
import time
from tkinter import ttk
from tkinter import filedialog

import logging
import windnd  # 用于拖拽
import os
#
from ..logic.common import exec_list_sort
from ..logic.file_utils import exec_remove_to_trash
from .tree_plus import tree_obj_clear, tree_obj_mouse_highlight

#
FOLDER_TYPE = 2
ALL_FOLDERS = 2  # 文件夹列表是否带“（全部）”,1 在前面，2在末尾（默认），其余没有
CLEAR_AFTER_CHANGE_FOLDER = 2  # 切换文件夹后，是否清除筛选。0 是保留，其他是清除。


class folder_obj:
    def __init__(self):
        self.folder_item = None
        self.short_name = ''
        self.path_full = ''
        self.depth = -1


class tree_folder:
    def __init__(self, app, frame_obj, bar_v_obj, bar_h_obj):
        self.app = app
        self.frame = frame_obj
        self.bar_h = bar_h_obj
        self.bar_v = bar_v_obj
        self.tree_body = ttk.Treeview(self.frame,
                                      selectmode=tk.BROWSE,
                                      style='Dark.Treeview',
                                      show="tree",
                                      yscrollcommand=self.bar_v.set,
                                      xscrollcommand=self.bar_h.set,
                                      )  # , height=18)
        self.bar_h.config(command=self.tree_body.xview)
        self.bar_v.config(command=self.tree_body.yview)
        #
        self.pointed_folder = folder_obj()  # 鼠标指向的
        self.current_folder = folder_obj()  # 当前打开的
        self.last_folder = folder_obj()  # 上次打开的
        #
        self.lst_folder_short = []
        #
        # 函数绑定
        # windnd.hook_dropfiles(self.tree_body, func=self.star_add_drag)
        self.tree_body.bind('<ButtonRelease-1>', self.on_choose)
        self.tree_body.bind('<KeyRelease-Up>', self.on_choose)
        self.tree_body.bind('<KeyRelease-Down>', self.on_choose)
        self.tree_body.bind("<Motion>", self.mouse_highlight_add)
        self.tree_body.bind("<Button-3>", self.right_click_menu)  # 绑定文件夹区域的右键功能
        #
        self.tree_body.bind('<Control-c>', self.folder_copy)
        self.tree_body.bind('<Control-x>', self.folder_cut)
        self.tree_body.bind('<Control-v>', self.folder_paste)

    def get_selected_folder_info(self) -> folder_obj:
        """
        获取当前选中的文件夹
        """
        folder_short = ''
        path_long = ''
        path_depth = 0
        folder = folder_obj()
        if len(self.tree_body.selection()) > 0:
            item = self.tree_body.selection()[0]
            item_values = self.tree_body.item(item, "values")
            folder_short = item_values[0]
            if len(item_values) > 1:
                path_long = item_values[-1]
                if folder_short == '（全部）':
                    folder_short = ''
                path_depth = int(item_values[1])
            # folder_long = str(folder_short).replace('\\', '/')

            folder.folder_item = item
            folder.depth = int(path_depth)
            folder.short_name = folder_short
            folder.path_full = path_long

        return folder

    def get_pointed_folder_info(self, event=None) -> folder_obj:
        """
        获取当前指向的对象的方法
        """
        tmp_folder_obj = folder_obj()
        item_id = self.tree_body.identify_row(event.y)
        if item_id:
            item_values = self.tree_body.item(item_id, "values")
            tmp_folder_obj.folder_item = item_id
            tmp_folder_obj.short_name = item_values[0]
            if len(item_values) > 1:
                tmp_folder_obj.depth = int(item_values[1])
                tmp_folder_obj.path_full = item_values[-1]
        return tmp_folder_obj

    def search_folder_by_name(self, event=None):
        """
        按文件夹名称搜索
        """
        keyword_folder = self.app.entry_search_folder.get()  # 应该修改为方法，而不是直接访问控件

        if keyword_folder is None:
            keyword_folder = ''
        if len(keyword_folder.strip()) <= 0:
            keyword_folder = ''
        self.app.keyword_folder = keyword_folder
        self.refresh()  # tree_folder_update()

    def set_group(self, event=None, group_name=None, short_name=None, need_update=True):
        """
        设置文件夹的group参数
        TODO 增加
        """
        if group_name is None:
            group_name = self.app.show_window_input('请输入分组名称', '文件夹分组名称')
            if group_name is None:
                return None
        #
        long_name = self.pointed_folder.path_full
        # 在 json 里面找到对应项目并增加分组
        n = 0
        for i in self.app.conf.json_data['folders']:
            if i['pth'] == long_name:
                self.app.conf.json_data['folders'][n] = {"pth": long_name, "group": group_name}
                break
            n += 1
        # 刷新目录
        if need_update:
            self.update_folder_and_json_file()

    def get_group_children(self):
        """
        获取分组内的文件夹列表
        原 tree_folder_get_group_children
        """
        lst_child_folders = []
        #
        the_root = self.tree_body.selection()[0]
        for c in self.tree_body.get_children(the_root):
            lst_child_folders.append(self.tree_body.item(c, "values")[-1])
        return lst_child_folders

    def get_depth(self, itm=None):
        """
        获取深度，如果没有指定对象，就是当前选中的文件夹对象。
        """
        if itm is None:
            item = self.tree_body.selection()[0]
        else:
            item = itm
        #
        tmp_values = self.tree_body.item(item, "values")
        if len(tmp_values) <= 1:
            path_depth = 0
        else:
            path_depth = tmp_values[1]
        return int(path_depth)

    def get_parent_node(self, depth=0):
        """
        获取选中项的根节点 item（文件夹分组）
        输入参数为数字，可以获取指定深度的结点。
        tree_folder_get_parent_node
        """
        itm = self.tree_body.selection()[0]
        the_item = itm
        while self.get_depth(the_item) > depth:
            the_item = self.tree_body.parent(the_item)
        return the_item

    def on_choose(self, event=None, refresh=1, sub_folder=None):
        """
        点击选中文件夹之后的动作，原为 tree_folder_on_choose
        参数：refresh：默认是1，代表了运行之后是否刷新列表。\n
        sub_folder：输入完整路径，但是没有被任何函数调用过
        """
        self.last_folder = self.current_folder
        self.current_folder = self.get_selected_folder_info()
        self.update_current_folder()  # 2022年10月13日新增，点击的时候刷新
        try:
            self.mouse_highlight_add(event)  # 添加这句话，保证当前左键点击项目获得高亮
        except Exception as e:
            logging.warning(f'warning 2919 = {e}')
        #
        self.app.flag.flag_root_folder = 1
        # if flag.flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
        # return
        #
        # 缓存之前选中的文件夹；
        #
        if sub_folder is None:  # 如果没有指定输入参数
            lst_path_ori = self.app.conf.lst_my_path_long_selected.copy()
        else:
            lst_path_ori = []
        #
        # 加载新选中的文件夹；
        #
        folder_short = self.current_folder.short_name  # 获取当前选中的文件夹；
        need_disabled = 0
        #
        if self.current_folder.depth == 0:  # 如果选中的文件夹是0级；
            logging.info('进入 tree_folder_on_choose 函数 tree_folder_get_depth() == 0 分支')
            # conf.lst_my_path_long_selected = conf.lst_my_path_long.copy()
            self.app.conf.lst_my_path_long_selected = self.get_group_children()
            # 设置按钮为无效
            need_disabled = 1
            self.app.cb_current_folder_olny.configure(state=tk.DISABLED)
            # 折叠子文件夹
            for folder_0 in self.tree_body.get_children():
                folder_1 = self.tree_body.get_children(folder_0)
                for itm in folder_1:
                    self.tree_body.item(itm, open=False)  # 一级文件夹全部关闭
                    #
        else:  # 如果是1级以上文件夹；
            logging.info('进入 tree_folder_on_choose 函数 else 分支')
            self.app.cb_current_folder_olny.configure(state=tk.NORMAL)
            #
            folder_long = self.current_folder.path_full
            #
            # 如果选中1级文件夹，就折叠其他所有一级文件夹，并展开当前选中的文件夹：
            # vls=get_folder_values_v2()
            # print('vls=',vls)
            folder_type = self.current_folder.depth
            #
            if folder_type >= 1:
                #
                # 折叠其他root下的一级文件夹
                my_root = self.get_parent_node()
                for folder_0 in self.tree_body.get_children():
                    if self.tree_body.item(folder_0, "text") \
                            == self.tree_body.item(my_root, "text"):  # 跳过当前的跟文件夹
                        continue
                    folder_1 = self.tree_body.get_children(folder_0)
                    for itm in folder_1:
                        self.tree_body.item(itm, open=False)  # 一级文件夹全部关闭
                #
                for itm in self.tree_body.selection():
                    folder_0 = self.tree_body.parent(itm)  # 选中项父节点
                    lst_children_folder = self.tree_body.get_children(folder_0)  # 选中项同级节点
                    #
                    # 折叠本root下的同级文件夹
                    for child in lst_children_folder:
                        self.tree_body.item(child, open=False)  # 其余所有非选中项，折叠
                #
                # 展开子文件夹
                for itm in self.tree_body.selection():
                    self.tree_body.item(itm, open=True)  # 选中项展开
                    #
                    folder_2 = self.tree_body.get_children(itm)
                    for itm2 in folder_2:
                        self.tree_body.item(itm2, open=False)  # 选中项的子文件夹折叠
            #
            logging.debug('folder_long=' + str(folder_long))
            self.app.conf.lst_my_path_long_selected = [folder_long, ]
            # 设置按钮有效
            need_disabled = 0

        self.do_always_open()
        logging.debug('tree_folder_on_choose 函数 tree_folder_always_open 执行完毕')

        # 调整按钮和控件的可用性：
        if need_disabled:
            self.app.bt_new_note.configure(state=tk.DISABLED)
            self.app.bt_readme.configure(state=tk.DISABLED)
            self.app.bt_folder_drop.configure(state=tk.DISABLED)
            self.app.v_sub_folders.current(0)
            self.app.v_sub_folders.configure(state=tk.DISABLED)
            self.app.checkbutton_folder_layers.configure(state=tk.DISABLED)
        else:
            self.app.bt_new_note.configure(state=tk.NORMAL)
            self.app.bt_readme.configure(state=tk.NORMAL)
            self.app.bt_folder_drop.configure(state=tk.NORMAL)
            self.app.v_sub_folders.configure(state='readonly')
            self.app.checkbutton_folder_layers.configure(state='readonly')
        #
        # 如果前后的选项没有变化的话，就不刷新文件夹列表
        #
        if lst_path_ori == self.app.conf.lst_my_path_long_selected:  # 如果选项没变化
            logging.debug('选项没有变化')
            logging.debug(lst_path_ori)
            pass
        else:  # 选项发生变化：
            # tree_obj_clear(self.app.XX_tree_lst_sub_folder)  # 新增语句 TODO 可能要删掉
            if refresh:
                # app_refresh(conf.lst_my_path_long_selected)
                self.app.refresh(CLEAR_AFTER_CHANGE_FOLDER, fast_mode=True)
            self.app.tree_file.yview_moveto(0)

        # flag.flag_running=0 # 标记为没有任务
        self.app.flag.flag_root_folder = 0
        logging.debug('tree_folder_on_choose 函数结束')
        # update_current_folder_list()  # 2022年10月13日新增，点击的时候刷新

    def get_group_list(self):
        """
        获取排序后的文件夹分组列表。这里已经排序完成。
        """
        # 根目录的名称列表
        lst_root_text = list(set(self.app.conf.dict_folder_groups.values()))
        # 排序
        lst_root_text = exec_list_sort(lst_root_text, char_sep=self.app.conf.V_SEP)
        if self.app.conf.DEFAULT_GROUP_NAME in lst_root_text:  # 默认文件夹分组永远在前
            lst_root_text.remove(self.app.conf.DEFAULT_GROUP_NAME)
            lst_root_text = [self.app.conf.DEFAULT_GROUP_NAME] + lst_root_text
        return lst_root_text

    def refresh(self, event=None, need_select=True):
        """
        原为 tree_folder_update
        根据 conf.lst_my_path_short ，将文件夹列表刷新一次。
        作用是：刷新主文件夹列表。暂不包括子文件夹刷新。
        没有输入输出。
        """
        lst_root_text = self.get_group_list()
        self.app.conf.lst_my_path_short \
            = exec_list_sort(self.app.conf.lst_my_path_short,
                             char_sep=self.app.conf.V_SEP)

        if self.app.flag.flag_inited:
            (b1, b2) = self.bar_v.get()
        else:
            b1 = b2 = 0

        def find_node_pos_by_text(node, text, pos_min=0):
            """
            返回对应的位置编号
            node
            text
            pos_min 是最小的位置，默认为0. 只会返回不小于这个值的查询位置。
            """
            is_found = 0
            pos = 0
            if node is None:
                items = self.tree_body.get_children()
            else:
                items = self.tree_body.get_children(node)
            for tmp_item in items:
                if self.tree_body.item(tmp_item, 'text') == text and pos >= pos_min:
                    is_found = 1
                    break
                pos += 1
            if is_found:
                return pos
            else:
                return -1

        #
        # 保存当前的根文件夹（分组）的名称、顺位
        try:
            tmp_group = self.get_parent_node()
            tmp_group_text = self.tree_body.item(tmp_group, 'text')
            group_pos = find_node_pos_by_text(None, tmp_group_text)
            #
            tmp_folder1 = self.get_parent_node(1)
            tmp_folder1_text = self.tree_body.item(tmp_folder1, 'text')
            # folder1_pos=0
            # for i in self.tree_body.get_children(tmp_group):
            #     if self.tree_body.item(i,'text') == tmp_folder1_text:
            #         break
            #     folder1_pos+=1
        except:
            group_pos = 0
            folder1_pos = 0
        #
        # 保存现在选中的主文件夹；
        v_method = 2
        tmp_lst_open = []  # 保存一路上来的文件夹名称

        try:
            tmp_folder1 = 0
            tmp_n = 0
            # tmp_root = tmp_group  # 此处有bug TODO 看起来并没用到，直接注释掉呢？

            if len(self.tree_body.selection()) > 0:
                tmp_s = self.tree_body.selection()[0]
                for _ in range(1000):  # 不可能有1000层的文件夹吧
                    tmp_lst_open.append(self.tree_body.item(tmp_s, "text"))
                    tmp_p = self.tree_body.parent(tmp_s)
                    need_debug = self.tree_body.item(tmp_p, "values")
                    if int(self.tree_body.item(tmp_p, "values")[1]) <= 1:
                        break
                    else:
                        tmp_s = tmp_p

        except Exception as e:
            logging.error(f'ERROR 1049 : {e}')
            tmp_folder1 = 0

        # 先清空一次；
        tree_obj_clear(self.tree_body)
        #
        tmp = 1
        #
        # 建立根文件夹
        n_root = 0
        lst_root_item = []
        for root_text in lst_root_text:
            lst_root_item.append(
                self.tree_body.insert('', n_root, text=root_text, tags=['folder0'], values=("（全部）", 0,), open=True))
            n_root += 1
        # root1=self.tree_body.insert('',1,text='新建分组',values=("（全部）",),open=True)
        #
        # 开始添加文件夹
        for i in self.app.conf.lst_my_path_short:
            #
            # 获得group_name
            # if str.lower(i).find('^') <0:
            #     group_name='关注的文件夹'
            # else:
            #     group_name='新建分组'
            group_name = self.app.conf.dict_folder_groups[i]
            # 找到根节点
            tmp_root_pos = lst_root_text.index(group_name)
            root_node = lst_root_item[tmp_root_pos]
            #
            tmp += 1
            logging.debug('i = ' + i)  # 添加初级文件夹
            # 值编码：显示名称、类型、完整路径(总是放在最后一个)
            full_dir1 = self.app.conf.dict_path[str(i)]
            value0 = (str(i),
                      1,
                      full_dir1)
            t1 = self.tree_body.insert(root_node, tmp, text=str(i),
                                       image=self.app.PIC_DICT['folder_50_20'],
                                       values=value0, tags=['folder1'])
            #
            # 二级目录及以后
            self.add_sub_folder_here(t1, full_dir1, 2)
            #
        #
        # 刷新后，选中第几个项目：
        if v_method == 2 and self.app.flag.flag_inited:
            tmp_lst_open.reverse()
            #
            # 判断位置
            group_pos = find_node_pos_by_text(None, tmp_group_text)
            if group_pos < 0:
                group_pos = 0
            item_group = self.tree_body.get_children()[group_pos]  # 分组结点（0级目录）
            #
            folder1_pos = find_node_pos_by_text(item_group, tmp_folder1_text)
            if folder1_pos < 0:
                folder1_pos = 0
            item_folder1 = self.tree_body.get_children(item_group)[folder1_pos]  # 根结点（1级目录）
            self.tree_body.item(item_folder1, open=True)  # 展开1级节点
            self.tree_body.selection_set(item_folder1)  # 选中
            tmp_i = item_folder1
            try:
                for tmp_text in tmp_lst_open:

                    logging.debug('tmp_text=', tmp_text)
                    #
                    folder2_pos = find_node_pos_by_text(tmp_i, tmp_text)
                    if folder2_pos < 0:
                        logging.warning(str('\n没有找到：' + tmp_text + ', 退出'))
                        break
                    tmp_i = self.tree_body.get_children(tmp_i)[folder2_pos]  # 根结点（1级目录）
                    self.tree_body.item(tmp_i, open=True)  # 展开节点
                    self.tree_body.selection_set(tmp_i)  # 选中

                try:
                    self.tree_body.update()
                    self.tree_body.yview_moveto((b1 + b2) / 2)
                    logging.info(f'b1 = {b1}, b2 = {b2}')

                except:
                    pass
                logging.info('进入 tree_folder_on_choose 函数')
                self.on_choose()
                #
            except Exception as e:
                logging.error('error 1059: ' + str(e))
                pass

            # try:
            #     self.tree_body.see(self.tree_body.focus())  # 2023年11月30日 测试 另一种显示高亮项目的逻辑
            # except:
            #     logging.error('高亮定位并没有成功')

        else:  # 如果没有 app.flag.flag_inited 的话，默认选中第一个文件夹
            #
            logging.debug('刷新文件夹：选中的文件夹是：' + str(tmp_folder1))
            if need_select:
                try:
                    tmp_line = 1130
                    item_group = self.tree_body.get_children()[group_pos]
                    tmp_line = 1132
                    to_select = self.tree_body.get_children(item_group)[tmp_folder1]
                    tmp_line = 1134
                    self.tree_body.selection_set(to_select)  # 选中第一个文件夹
                    #
                    tmp_line = 1136
                    try:
                        self.on_choose()  # 右边也重载一次
                    except:
                        pass
                    #
                except Exception as e:
                    logging.error(f'error 1079: {e}，行号 = {tmp_line}')

        try:
            self.do_always_open()
            self.app.window.update()
            self.tree_body.yview_moveto(b1)  # 尽量保持原来的位置
            #
            selected_items = self.tree_body.selection()
            if selected_items:
                selected_item = selected_items[0]
                bbox = self.tree_body.bbox(selected_item)
                # TODO： 如果看不到文件夹，就使用 see 强制找到，否则就保留之前的位置。尚未测试成功。
                if bbox:
                    pass
                else:
                    logging.warning('看不见，怎么都看不见！')
                    self.tree_body.see(selected_item)  # 2023年11月30日 测试 另一种显示高亮项目的逻辑
                    # self.tree_body.see(self.tree_body.selection())  # 2023年11月30日 测试 另一种显示高亮项目的逻辑

        except Exception as e:
            logging.error('ERROR 1127 ' + str(e))

    def add_sub_folder_here(self, root_node, root_dir, new_depth, if_cont=True, is_root_searched=False):
        """
        用于为 tree_folder 增加子文件夹。
        其中，可以根据筛选条件判定是否需要保留文件夹。
        :param root_node: 根节点
        :param root_dir: 根路径
        :param new_depth: 深度编号，也就是新增节点的深度，一般定义为根节点+1
        :param if_cont: 是否继续增加子结点
        """
        # logging.debug('root_dir = ' + str(root_dir) + ', new_depth = ' + str(new_depth))
        tmp = 1  # 添加节点的序列号
        max_depth_update = new_depth + 3  # 最大的搜索深度
        keyword_folder = str(self.app.keyword_folder).lower()  # 搜索关键词
        is_new_node_searched = False
        #
        for root_, dirs_, files_ in os.walk(root_dir):
            # dirs_.sort()
            if '_nomedia' in files_:
                # logging.info('即将删除节点: ' + str(root_) + 'root_node = ' + str(root_node))
                self.tree_body.delete(root_node)
                return
            #
            dirs_sorted = exec_list_sort(dirs_, char_sep=self.app.conf.V_SEP)  # 当前目录下的子文件夹排序
            for sub_dir_ in dirs_sorted:
                tmp += 1
                if sub_dir_ in self.app.conf.EXP_FOLDERS:  # 排除文件夹
                    continue
                if self.app.conf.EXP_DOT_FOLDERS and str(sub_dir_).startswith('.'):  # 忽略.开头的文件夹
                    continue
                else:  # 子文件夹不在排除范围的话，
                    full_dir_ = root_dir + '/' + sub_dir_
                    value_tmp_ = (root_dir, new_depth, full_dir_)  # values 格式 根路径，深度，全路径(-1)
                    #
                    if len(keyword_folder) > 0 and sub_dir_.lower().find(keyword_folder) >= 0:
                        # 符合筛选条件的
                        new_node = self.tree_body.insert(root_node, tmp, text=sub_dir_,
                                                         image=self.app.PIC_DICT['folder_25_20'],
                                                         values=value_tmp_,
                                                         tags=['folder_searched', 'folder_kept'],
                                                         )
                        is_new_node_searched = True
                    elif 'folder_kept' in self.tree_body.item(root_node, "tags"):
                        new_node = self.tree_body.insert(root_node, tmp, text=sub_dir_,
                                                         image=self.app.PIC_DICT['folder_25_20'],
                                                         values=value_tmp_,
                                                         tags=['folder2', 'folder_kept'],
                                                         )
                    elif is_root_searched or new_depth < max_depth_update:
                        # self.tree_body.item(root_node, "text").lower().find(keyword_folder) >=0 \
                        # 不符合筛选条件，但父结点或者深度符合的
                        new_node = self.tree_body.insert(root_node, tmp, text=sub_dir_,
                                                         image=self.app.PIC_DICT['folder_25_20'],
                                                         values=value_tmp_,
                                                         tags=['folder2'],
                                                         )
                    else:  # 不满足任何添加节点的条件时，不添加
                        new_node = False
                    #
                    # 继续迭代下钻
                    if new_depth <= max_depth_update:  # app.flag.flag_inited: # 刚启动的时候，不需要加载全部文件夹，从而提高加载速度
                        if new_node:
                            self.add_sub_folder_here(new_node, full_dir_, new_depth + 1,
                                                     is_root_searched=(is_root_searched or is_new_node_searched))
                    else:
                        if new_node and if_cont:
                            self.add_sub_folder_here(new_node, full_dir_, new_depth + 1, if_cont=False,
                                                     is_root_searched=(is_root_searched or is_new_node_searched))
            #
            break  # 对应的是 os.walk 停止，不再下钻，只处理当前层就结束
        #
        # 删掉父结点 # 判定条件：父结点不符合筛选条件，且没有子结点的
        if len(keyword_folder) > 0:  # 如果开了筛选
            # and not is_root_searched
            if self.tree_body.item(root_node, "text").lower().find(keyword_folder) >= 0:
                # 父结点能找到关键词的
                tmp_old_tags = list(self.tree_body.item(root_node, "tags"))
                self.tree_body.item(root_node, tags=list(set(tmp_old_tags + ['folder_kept', 'folder_searched'])))
            elif 'folder_kept' in self.tree_body.item(root_node, "tags"):
                # 父结点不带关键词，但带保留标签的
                pass
            elif len(self.tree_body.get_children(root_node)) <= 0:
                # 没有子结点的
                self.tree_body.delete(root_node)
                #

    def update_current_folder(self):
        """
        测试：想要设计为点击左侧文件夹的时候，刷新当前文件夹内部结构，
        这样可以提高效率。
        """
        # 基本思路：删掉子文件，然后重新加载子文件夹
        #
        # 获取当前点击的节点
        root_depth = 0
        for root_node in self.tree_body.selection():
            root_dir = self.tree_body.item(root_node, "values")[-1]
            try:
                root_depth = int(self.tree_body.item(root_node, "values")[1])
            except Exception as e:
                root_depth = 0
            logging.debug('root_dir = ' + str(root_dir))
            logging.debug('root_depth=' + str(root_depth))
            break

        if root_depth:  # 1:
            # 删掉子目录
            for item in self.tree_body.get_children(root_node):
                self.tree_body.delete(item)

            # 添加子目录节点，并展开当前节点
            try:
                self.insert_folder_item_here(root_node, root_dir, root_depth + 1)
                if self.app.flag.flag_inited:
                    self.tree_body.update()  # TODO bug
            except Exception as e:
                logging.error(f"error 1159: 文件夹读取失败: {e}")
        self.do_always_open()

    def do_always_open(self, event=None):
        """
        常开文件夹功能
        以@或者#开头的，设置为常开。
        """
        for itm_folder_0 in self.tree_body.get_children():  # 文件夹分组
            name_folder0 = self.tree_body.item(itm_folder_0, "text")
            lst_folder_1 = self.tree_body.get_children(itm_folder_0)  # 一级文件夹，也就是默认的
            for itm_folder1 in lst_folder_1:
                name_folder1 = self.tree_body.item(itm_folder1, "text")
                # if name_folder0[0] in ['@', '#'] or name_folder0 in ['默认文件夹分组']:
                #     if name_folder1[0] in ['@','#']:
                #         self.tree_body.item(itm_folder1, open=True)
                if self.app.conf.dict_path[name_folder1] in self.app.conf.lst_open:
                    self.tree_body.item(itm_folder1, open=True)

    def always_open_switch(self, folder_path=None, new_state=None):
        """
        切换文件夹的常开状态，之后刷新
        """
        if new_state == 'on':
            self.app.conf.folder_open_on(folder_path=folder_path)
        elif new_state == 'off':
            self.app.conf.folder_open_off(folder_path=folder_path)
        self.refresh()

    def insert_folder_item_here(self, root_node, root_dir, new_depth,
                                if_cont=True, is_root_searched=False):
        """
        用于为 tree_folder 增加子文件夹。
        其中，可以根据筛选条件判定是否需要保留文件夹。
        :param root_node: 根节点
        :param root_dir: 根路径
        :param new_depth: 深度编号，也就是新增节点的深度，一般定义为根节点+1
        :param if_cont: 是否继续增加子结点
        """
        # logging.debug('root_dir = ' + str(root_dir) + ', new_depth = ' + str(new_depth))
        tmp = 1  # 添加节点的序列号
        max_depth_update = new_depth + 3  # 最大的搜索深度
        keyword_folder = str(self.app.keyword_folder).lower()  # 搜索关键词
        is_new_node_searched = False
        #
        for root_, dirs_, files_ in os.walk(root_dir):
            # dirs_.sort()
            if '_nomedia' in files_:
                # logging.info('即将删除节点: ' + str(root_) + 'root_node = ' + str(root_node))
                self.tree_body.delete(root_node)
                return
            #
            dirs_sorted = exec_list_sort(dirs_, self.app.conf.V_SEP)  # 当前目录下的子文件夹排序
            for sub_dir_ in dirs_sorted:
                tmp += 1
                if sub_dir_ in self.app.conf.EXP_FOLDERS:  # 排除文件夹
                    continue
                if self.app.conf.EXP_DOT_FOLDERS and str(sub_dir_).startswith('.'):  # 忽略.开头的文件夹
                    continue
                else:  # 子文件夹不在排除范围的话，
                    full_dir_ = root_dir + '/' + sub_dir_
                    value_tmp_ = (root_dir, new_depth, full_dir_)  # values 格式 根路径，深度，全路径(-1)
                    #
                    if len(keyword_folder) > 0 and sub_dir_.lower().find(keyword_folder) >= 0:
                        # 符合筛选条件的
                        new_node = self.tree_body.insert(root_node, tmp, text=sub_dir_,
                                                         image=self.app.PIC_DICT['folder_25_20'],
                                                         values=value_tmp_,
                                                         tags=['folder_searched', 'folder_kept'],
                                                         )
                        is_new_node_searched = True
                    elif 'folder_kept' in self.tree_body.item(root_node, "tags"):
                        new_node = self.tree_body.insert(root_node, tmp, text=sub_dir_,
                                                         image=self.app.PIC_DICT['folder_25_20'],
                                                         values=value_tmp_,
                                                         tags=['folder2', 'folder_kept'],
                                                         )
                    elif is_root_searched or new_depth < max_depth_update:
                        # self.tree_body.item(root_node, "text").lower().find(keyword_folder) >=0 \
                        # 不符合筛选条件，但父结点或者深度符合的
                        new_node = self.tree_body.insert(root_node, tmp, text=sub_dir_,
                                                         image=self.app.PIC_DICT['folder_25_20'],
                                                         values=value_tmp_,
                                                         tags=['folder2'],
                                                         )
                    else:  # 不满足任何添加节点的条件时，不添加
                        new_node = False
                    #
                    # 继续迭代下钻
                    if new_depth <= max_depth_update:  # flag.flag_inited: # 刚启动的时候，不需要加载全部文件夹，从而提高加载速度
                        if new_node:
                            self.insert_folder_item_here(new_node, full_dir_, new_depth + 1,
                                                         is_root_searched=(is_root_searched or is_new_node_searched))
                    else:
                        if new_node and if_cont:
                            self.insert_folder_item_here(new_node, full_dir_, new_depth + 1, if_cont=False,
                                                         is_root_searched=(is_root_searched or is_new_node_searched))
            #
            break  # 对应的是 os.walk 停止，不再下钻，只处理当前层就结束
        #
        # 删掉父结点 # 判定条件：父结点不符合筛选条件，且没有子结点的
        if len(keyword_folder) > 0:  # 如果开了筛选
            # and not is_root_searched
            if self.tree_body.item(root_node, "text").lower().find(keyword_folder) >= 0:
                # 父结点能找到关键词的
                tmp_old_tags = list(self.tree_body.item(root_node, "tags"))
                self.tree_body.item(root_node, tags=list(set(tmp_old_tags + ['folder_kept', 'folder_searched'])))
            elif 'folder_kept' in self.tree_body.item(root_node, "tags"):
                # 父结点不带关键词，但带保留标签的
                pass
            elif len(self.tree_body.get_children(root_node)) <= 0:
                # 没有子结点的
                self.tree_body.delete(root_node)
                #

    def create_sub_folder(self, event=None):
        """
        新建子文件夹，也就是新建文件夹的意思。目前正在使用。
        """
        # 获取当前文件夹

        cur_folder = self.pointed_folder.path_full

        # 获取名称
        new_folder_name = ''
        lp = 1
        #
        while lp:
            path = self.app.show_window_input('新建文件夹', '请输入文件夹名称', new_folder_name)
            if path is None:
                return False
            else:
                new_folder_name = path
            #
            # 补充完整路径
            tmp_path = cur_folder + '/' + path
            #
            # 新路径是否存在
            isExists = os.path.exists(tmp_path)
            # 判断结果
            if not isExists:
                # 如果不存在则创建目录
                # 创建目录操作函数
                try:
                    os.makedirs(tmp_path)

                    logging.debug(f'{tmp_path} 创建成功')
                    lp = 0
                    #
                    # 创建之后刷新一次
                    # update_sub_folder_list(refresh=False)  # TODO 似乎完全没用，先注释掉
                    self.app.refresh(0, fast_mode=True)
                    # app_refresh(reload_setting=2)
                    if FOLDER_TYPE == 2:
                        self.refresh()
                    return True
                except:
                    t = tk.messagebox.showerror(title='ERROR', message='文件夹创建失败，当前位置可能不允许创建文件夹')
                    lp = 0
            else:
                # 如果目录存在则不创建，并提示目录已存在
                t = tk.messagebox.showerror(title='ERROR', message=(tmp_path + ' 目录已存在，请重新设定文件夹名称'))
                # return False

    def star_add_drag(self, files):
        filenames = list()  # 可以得到文件路径编码, 可以看到实际上就是个列表。
        folders = []
        # print(files)
        for item in files:
            item = item.decode('gbk')  # 此处可能存在编码错误，而且，为啥要编码？？
            # item=item.replace('\xa0',' ').decode('gbk')
            if os.path.isdir(item):
                folders.append(item)
            elif os.path.isfile(item):
                filenames.append(item)
        if len(folders) > 0:
            self.star_add(folders)

    def star_add_via_dialog(self, event=None):
        """
        通过点击的方式，添加新的目录
        """
        res = filedialog.askdirectory()  # 选择目录，返回目录名
        res_lst = [res]
        if res == '':
            logging.debug('取消添加文件夹')
        else:
            logging.debug(f"通过对话框的方式添加{res}")
            self.star_add(res_lst)

    def star_from_menu(self, event=None, group_name=None):
        """
        通过菜单添加关注的文件夹.
        产生渠道：将所选文件夹添加到关注
        """
        folder_path = self.pointed_folder.path_full
        self.star_add([folder_path], group_name=group_name)

    def star_remove(self):
        """
        取消关注选中的文件夹。
        没有输入输出。
        """
        # 获取当前选中的文件夹
        long_name = self.pointed_folder.path_full
        short_name = self.pointed_folder.short_name

        # 增加确认
        if tk.messagebox.askokcancel("操作确认",
                                     "真的要取消关注文件夹【" + short_name + "】吗？\n该文件夹将从关注列表中移除，但其本身数据并不会受到影响。"):
            pass
        else:
            return
        # 在 json 里面找到对应项目并删除
        n = 0
        for i in self.app.conf.json_data['folders']:
            if i['pth'] == long_name:
                self.app.conf.json_data['folders'].pop(n)
                break
            n += 1
        # 刷新目录
        self.update_folder_and_json_file()

    def star_add(self, path_list, group_name=None):
        """
        添加关注的目录,输入必须是列表。
        列表内是文件夹完整路径。
        """
        need_update = 0
        for tmp_path_long in path_list:
            if len(tmp_path_long) > 0:  # 用于避免空白项目，虽然不知道哪里来的
                tmp_path_long = str(tmp_path_long).replace("\\", '/')
                if group_name:
                    tmp_tar = {"pth": tmp_path_long, "group": group_name}
                else:
                    tmp_tar = {"pth": tmp_path_long}
                #
                # 判断是否已经存在
                if tmp_path_long in self.app.conf.lst_my_path_long:
                    tk.messagebox.showerror(title='错误',
                                            message='以下路径已存在，不需要添加：' + tmp_path_long)
                    logging.warning('以下路径已存在，不需要添加：' + str(tmp_path_long))
                else:
                    self.app.conf.json_data['folders'].append(tmp_tar)
                    need_update = 1
        # 刷新目录
        if need_update:
            self.update_folder_and_json_file()
            # 刷新之后应该再刷新文件一次；
            self.app.refresh(fast_mode=True)
            # app_refresh(fast_mode=True)

    def right_click_menu(self, event=None):
        """
        文件夹区域的右键菜单
        """
        # 更新指向的对象信息
        self.pointed_folder = self.get_pointed_folder_info(event)
        folder_depth = self.pointed_folder.depth
        #
        # 子菜单：用于移动文件夹分组
        tmp_lst_groups = self.get_group_list()
        if self.app.conf.DEFAULT_GROUP_NAME in tmp_lst_groups:
            tmp_lst_groups.remove(self.app.conf.DEFAULT_GROUP_NAME)
        menu_folder_group = tk.Menu(self.app.window, tearoff=0)
        menu_folder_group.add_command(label=self.app.conf.DEFAULT_GROUP_NAME,
                                      command=lambda x=self.app.conf.DEFAULT_GROUP_NAME: self.set_group(
                                          group_name=x))
        if len(tmp_lst_groups) > 0:
            menu_folder_group.add_separator()
        for i in tmp_lst_groups:
            menu_folder_group.add_command(label=i, command=lambda x=i: self.set_group(group_name=x))
        if len(tmp_lst_groups) > 0:
            menu_folder_group.add_separator()
        menu_folder_group.add_command(label="自定义分组…", command=self.set_group)
        #
        # 子菜单：用于添加关注文件夹时，设置分组
        # tmp_lst_groups = tree_folder_get_group_list()
        # if conf.DEFAULT_GROUP_NAME in tmp_lst_groups:
        #     tmp_lst_groups.remove(conf.DEFAULT_GROUP_NAME)  # 这部分前面已经有了，所以可以省略
        menu_folder_pin_group = tk.Menu(self.app.window, tearoff=0)
        menu_folder_pin_group.add_command(label=self.app.conf.DEFAULT_GROUP_NAME,
                                          command=lambda x=self.app.conf.DEFAULT_GROUP_NAME: self.star_from_menu(
                                              group_name=x))
        if len(tmp_lst_groups) > 0: menu_folder_pin_group.add_separator()
        for i in tmp_lst_groups:
            menu_folder_pin_group.add_command(label=i, command=lambda x=i: self.star_from_menu(group_name=x))
        # if len(tmp_lst_groups) > 0: menu_folder_pin_group.add_separator()
        # menu_folder_pin_group.add_command(label="自定义分组…", command=tree_folder_star_from_menu)
        # TODO 之后完善自定义新增分组的功能
        # 文件夹区域右键菜单
        menu_folder = tk.Menu(self.app.window, tearoff=0)
        # 检查文件夹是否存在
        folder_path = self.pointed_folder.path_full
        is_folder_exists = os.path.isdir(folder_path)
        if is_folder_exists:
            if folder_depth >= 1: menu_folder.add_command(label="打开所选文件夹（使用资源管理器）",
                                                          command=self.open_folder_in_explorer)
            if folder_depth == 1: menu_folder.add_separator()
            if folder_depth == 1:
                if folder_path in self.app.conf.lst_open:
                    menu_folder.add_command(label="取消常开模式",
                                            command=lambda x=folder_path: self.always_open_switch(folder_path=x,
                                                                                                  new_state='off'))
                else:
                    menu_folder.add_command(label="设置为常开模式",
                                            command=lambda x=folder_path: self.always_open_switch(folder_path=x,
                                                                                                  new_state='on'))
            if folder_depth >= 1: menu_folder.add_separator()
            if folder_depth >= 1: menu_folder.add_command(label="新建子文件夹", command=self.create_sub_folder)
            if folder_depth > 1: menu_folder.add_command(label="重命名文件夹", command=self.folder_rename)
            if folder_depth > 1: menu_folder.add_command(label="删除文件夹", command=self.folder_delete)
            if folder_depth >= 1: menu_folder.add_separator()

            if folder_depth > 1: menu_folder.add_command(label="剪切文件夹（程序内）", command=self.folder_cut)
            if folder_depth >= 1: menu_folder.add_command(label="粘贴为子文件夹",
                                                          state=tk.DISABLED if len(
                                                              self.app.folder_to_move) < 1 else tk.NORMAL,
                                                          command=self.folder_paste)
        else:  # 当前点击的文件夹不存在
            if folder_depth >= 1: menu_folder.add_command(label="打开所选文件夹（文件夹不存在）", state=tk.DISABLED)
            if folder_depth >= 1: menu_folder.add_separator()
            if folder_depth >= 1: menu_folder.add_command(label="新建子文件夹（文件夹不存在）", state=tk.DISABLED)
            if folder_depth > 1: menu_folder.add_command(label="重命名文件夹（文件夹不存在）", state=tk.DISABLED)
            if folder_depth > 1: menu_folder.add_command(label="删除文件夹（文件夹不存在）", state=tk.DISABLED)
            if folder_depth >= 1: menu_folder.add_separator()
            if folder_depth > 1: menu_folder.add_command(label="剪切文件夹（文件夹不存在）", state=tk.DISABLED)
            if folder_depth >= 1: menu_folder.add_command(label="粘贴为子文件夹（文件夹不存在）", state=tk.DISABLED, )

        if folder_depth == 0: menu_folder.add_command(label="重命名分组", command=self.rename_group)
        if folder_depth >= 0: menu_folder.add_separator()

        # if folder_depth > 1: menu_folder.add_command(label="添加当前选中文件夹到关注列表", command=tree_folder_star_from_menu)
        if folder_depth > 1: menu_folder.add_cascade(label="添加当前选中文件夹到关注列表", menu=menu_folder_pin_group)
        if folder_depth == 1: menu_folder.add_command(label="取消关注", command=self.star_remove)
        if folder_depth == 1: menu_folder.add_cascade(label="调整文件夹分组", menu=menu_folder_group)
        if folder_depth >= 1: menu_folder.add_separator()

        # menu_folder.add_command(label="添加文件夹到关注列表…", command=tree_folder_star_add_by_dialog)
        menu_folder.add_command(label="刷新文件夹列表", command=self.refresh)
        menu_folder.post(event.x_root, event.y_root)

    def mouse_highlight_remove(self, event=None, clear_only=None):
        tree_obj_mouse_highlight(event, app=self.app, clear_only=True, the_tree=self.tree_body)

    def mouse_highlight_add(self, event=None, clear_only=False):
        tree_obj_mouse_highlight(event, app=self.app, clear_only=clear_only, the_tree=self.tree_body)

    def rename_folder(self, event=None):
        """
        重命名文件夹
        """

    def folder_copy(self, event=None):
        """
        模拟复制
        """

    def folder_cut(self, event=None):
        """
        模拟剪切
        """
        self.folder_clipboard_clear()
        fd = self.pointed_folder.path_full
        self.app.folder_to_move = fd
        self.app.tree_file.file_clipboard_clear()

    def folder_paste(self, event=None, tar_folder_from=None,
                     tar_folder_to=None, need_update=True):
        """
        模拟粘贴
        """
        if tar_folder_from is None:
            folder_to_move = self.app.folder_to_move
            fd_from = folder_to_move
        else:
            fd_from = tar_folder_from
        #
        if tar_folder_to is None:
            fd_to = self.pointed_folder.path_full
            # fd_to = get_folder_long_v2()
        else:
            fd_to = tar_folder_to

        #
        # 检查目标位置是否已经有同名文件夹；
        (old_head, old_tail) = os.path.split(fd_from)
        new_path_full = fd_to + '/' + old_tail
        new_path_full = new_path_full.replace('\\', '/')
        #
        # 先检查原始位置和新位置是否完全一致；
        if old_head.replace('\\', '/') == fd_to.replace('\\', '/'):
            tk.messagebox.showerror(title='错误',
                                    message='原始位置和目标位置完全相同，操作无效。')
            logging.debug('原始位置和目标位置一致，不移动文件夹')
            # tree_folder_clipoard_clear()
            return None
        # 然后检查目标位置是否是原始位置的子文件夹：
        # 算法是，检查新位置是否包括原位置的完整路径
        if (fd_to.replace('\\', '/') + '/').startswith(fd_from.replace('\\', '/') + '/'):
            tk.messagebox.showerror(title='错误',
                                    message='目标位置是原位置的子文件夹，不允许这样操作。')
            print('目标位置是原位置的子文件夹，不允许这样操作', fd_to.replace('\\', '/'), fd_from.replace('\\', '/'))
            # tree_folder_clipoard_clear()
            return None
        #
        tmp_todo = 1
        tmp_rename = 0  # 是否需要重命名
        while os.path.isdir(new_path_full) and tmp_todo:
            tmp_rename = 1
            logging.debug('目标位置已存在同名文件夹')
            if tk.messagebox.askokcancel("请注意", "目标位置存在同名文件夹。需要改变文件夹的名称后继续移动文件夹吗？"):
                # 输入新文件名
                res = self.app.show_window_input('重命名', '请输入新的文件夹名称', old_tail, True)
                if res is None:
                    tmp_todo = 0
                else:
                    new_path_full = fd_to + '/' + res
                    new_path_full = new_path_full.replace('\\', '/')
            else:
                tmp_todo = 0
        #
        if tmp_todo == 0:
            return None
        #
        # 移动
        try:
            if tmp_rename:
                os.rename(fd_from, new_path_full)
            else:
                shutil.move(fd_from, fd_to)
            self.folder_clipboard_clear()
            #
            if need_update:
                self.refresh()
                self.app.refresh(fast_mode=True)

        except Exception as e:
            tk.messagebox.showerror(title='错误',
                                    message='文件夹移动失败！错误代码：' + str(e))
            print('\n文件夹移动失败！错误代码：', e)

    def folder_clipboard_clear(self, event=None):
        """
        清空文件夹剪切板
        """
        self.app.folder_to_move = ''

    def folder_rename(self):
        """
        文件夹重命名
        """

    def folder_delete(self, event=None):
        """
        删除文件夹（到回收站）。
        """
        fd = self.pointed_folder.path_full
        folder_base, folder_name = os.path.split(fd)

        if tk.messagebox.askokcancel("删除确认", "要将文件夹【" + str(folder_name) + "】删除到回收站吗？"):
            # 删除操作
            exec_remove_to_trash(fd)
            self.refresh()
            # 清空文件剪切板
            # tree_file_pick_nothing()  # 是否要清空还需要考虑 TODO

    def rename_group(self, event=None):
        """
        重命名文件夹分组
        """
        # 获得旧分组名称
        fd_0 = self.pointed_folder.folder_item  # 新方法：直接获取鼠标指向的对象，不需要看展开项目
        # fd_0 = app.tree_lst_folder.selection()[0]
        group_name_old = self.tree_body.item(fd_0, "text")
        #
        # 获得新名称
        group_name = self.app.show_window_input('请输入分组名称', '文件夹分组名称', group_name_old)
        if group_name is None:
            return None
        #
        # 写分组值
        for fd_1 in self.tree_body.get_children(self.pointed_folder.folder_item):
            sht_name = self.tree_body.item(fd_1, "values")[0]  # sht_name = app.tree_lst_folder.item(fd_1, "text")
            logging.debug(sht_name)
            self.set_group(group_name=group_name, short_name=sht_name, need_update=False)
            pass
        # 刷新并写入配置文件
        self.update_folder_and_json_file()

    def open_folder_in_explorer(self):
        METHOD = 1
        if METHOD == 1:
            # 打开左侧高亮文件夹
            try:
                print(self.app.tree_lst_folder.item(self.app.last_focus, "values"))
                l_folder = self.app.tree_lst_folder.item(self.app.last_focus, "values")[-1]
                print(l_folder)
                self.app.run(l_folder)
                return
            except Exception as e:
                print(e)
                print('并没有获取到app.last_focus')
                pass
        elif METHOD == 2:
            # 获得当前选中的长目录
            if len(self.app.conf.lst_my_path_long_selected) != 1:
                pass
            else:
                try:
                    self.app.run(self.app.conf.get_current_path())
                except:
                    pass

    def update_folder_and_json_file(self, ind=None, need_update=True):  # 刷新左侧的文件夹列表
        """
        刷新 json 文件，并根据文件内容刷新文件夹列表。
        输入参数是要选中的文件夹编号。
        """
        # 更新json文件
        self.app.conf.exec_json_file_write(data=self.app.conf.json_data)
        self.app.conf.exec_json_file_load()
        #
        # 更新左侧列表
        self.refresh(need_select=False)
        #
        # 选中指定的文件夹
        self.tree_body.update()
        #
        if ind is not None:
            if FOLDER_TYPE == 1:
                # app.tree_lst_folder.selection_set(ind)
                tmp_lst_folder = self.tree_body.get_children()
                self.tree_body.selection_set(tmp_lst_folder[ind])
            elif FOLDER_TYPE == 2:
                root = self.tree_body.get_children()[0]
                to_select = self.tree_body.get_children(root)[ind]
                self.tree_body.selection_set(to_select)  # 选中第一个文件夹
        #
        # 刷新
        self.on_choose()

    def search_clear(self, event=None):
        """
        清除文件夹的搜索
        """
        self.app.entry_search_folder.delete(0, 'end')
        self.search_folder_by_name()
