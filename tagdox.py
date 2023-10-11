# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""

import os
import tkinter as tk
from tkinter import ttk
# import tkinter.tix as Tix 
# from tkinter import tix
# from tkinter import Text, Variable
import json
from tkinter import filedialog
from tkinter import simpledialog
from tkinter.constants import NORMAL
# from tkinter import font
# from tkinter.constants import INSERT
import windnd  # 用于拖拽
#
from os.path import isdir
from os.path import isfile
import time
import threading  # 多线程
# import multiprocessing
from multiprocessing import Pool  # 进程
from multiprocessing import Process
# from docx import Document  # 用于创建word文档
# import ctypes # 用于调整分辨率 #
# from win32com.shell import shell, shellcon  # 此处报错是编辑器的问题，可以忽略
import shutil
import queue
# 
import subprocess  # 用于打开文件所在位置并选中文件
#
# 自建库
from libs.common_funcs import *
# 控件库
from libs.widgets.windows import TdProgressWindow as TdProgressWindow
from libs.widgets.windows import TdInputWindow as TdInputWindow
from libs.widgets.windows import TdSpaceWindow as TdSpaceWindow
#
from libs.markdown import MarkdownRel  # 对 markdown 的特殊处理

from codes.logic.conf import td_conf
#
# import my_logger
# import send2trash # 回收站（目前作废）

class td_const():
    """
    用于存储常量
    """
    def __init__(self):
        self.URL_HELP = 'https://gitee.com/horse_sword/tagdox'  # 帮助的超链接，目前是 gitee 主页
        self.URL_ADV = 'https://gitee.com/horse_sword/tagdox/issues'  # 提建议的位置
        self.URL_CHK_UPDATE = 'https://gitee.com/horse_sword/tagdox/releases'  # 检查更新的位置
        self.TAR = 'Tagdox / 标签文库'  # 程序名称
        self.VER = 'v0.26.1.0'  # 版本号

conf = td_conf()  # 关键参数
cst = td_const()  # 常量

"""
## 近期更新说明

#### v0.26.1.0 2023年10月11日
增加功能：为readme功能增加了快捷按钮。

#### v0.26.0.0 2023年10月11日
增加功能：可以解析当前文件夹内的readme.md文件，并作为文件夹备注显示在列表下面。

#### v0.25.1.9 2023年10月6日
增加功能：可以在左侧文件夹列表自动忽略点开头的文件夹。这个功能以后可以作为设置项。

#### v0.25.1.8 2023年9月27日
修正了空格唤起的文件预览框缩放不正确的问题。
将图标等素材统一移动到 resources 文件夹下。

#### v0.25.1.7 2023年7月25日
将左侧列表的缩进设置为40，提高区分度。之后考虑做成自适应或者可调节的。

#### v0.25.1.6 2023年1月24日
补充了弹窗对高分屏的适配。

#### v0.25.1.5 2023年1月22日
增加了对1080p以上分辨率的缩放适配.

#### v0.25.1.4 2022年10月15日
fixed: #I5VX6P 修复了点击分组（0级目录）的时候，不能查看分组文件的bug。
优化文件夹取消关注的表达。

#### v0.25.1.3 2022年10月13日
优化了点击左侧文件夹的时候，增加了对当前文件夹的刷新的逻辑。
之前启动的时候，文件夹是完整加载，效率太低。现在优化为只加载一层子文件夹，加载速度显著提升。

#### v0.25.1.2 2022年8月15日
增加标签页拖拽为剪切移动的功能；调整标签为左对齐。

#### v0.25.1.1 2022年7月20日
优化询问拖拽是否保留原始文件的表达。

#### v0.25.1.0 2022年7月5日
外部文件拖拽进入主窗口时，可以通过对话框设定是否保留原始文件。

#### v0.25.0.1 2022年5月22日
修复了文件夹区域左键单击时，当前对象没有正常高亮的bug。

#### v0.25.0.0 2022年5月22日
左侧文件夹列表优化，现在右键操作可直接作用于鼠标选中对象，而不是只能操作打开的文件夹。

"""

# %%
#
# 常量，开发用，不准备进入设置的
DEVELOP_MODE = 0  # 开启调试模式
LOGO_PATH = './resources/icons/LOGO.ico'
cALL_FILES = ''  # 标签为空的表达方式，默认是空字符串
PROG_STEP = 500  # 进度条刷新参数
CLEAR_AFTER_CHANGE_FOLDER = 2  # 切换文件夹后，是否清除筛选。0 是保留，其他是清除。
DIR_LST = ['▲', '▼']  # 列排序标题行
HEADING_LST = ['#0', 'tags', 'modify_time', 'size', 'file0']
HEADING_LST_TXT = ['名称', '标签', '修改时间', '大小(kB)', '完整路径']
MULTI_PROC = 1  # 并发进程数，设置为1或更低就单独进程。
MULTI_FILE_COUNT = 400
# DEFAULT_GROUP_NAME = '默认文件夹分组'
#
# 可以做到设置里面的常量
ALL_FOLDERS = 2  # 文件夹列表是否带“（全部）”,1 在前面，2在末尾（默认），其余没有
DRAG_FILES_ADD_TAG = True  # 为拖拽进来的新增文件统一添加当前选中的标签
# TREE_SUB_SHOW = ['tag', 'sub_folder'][1]  # 决定左侧布局是标签模式还是子文件夹模式。// 可修改  // 已经基本上作废

FOLDER_TYPE = 2
TAG_METHOD = 'FILE_STREAM'  # 或者 FILENAME
MARKDOWN_IMGS = True  # 是否移动markdown的时候，移动相应的相对路径文件；
#
# %%
#######################################################################


def exec_tree_clear(tree_obj) -> None:  #
    """
    通用函数。
    通用的 treeview 清除函数，因为是通用的，所以必须带参数。
    参数是 具体的 treeview 对象。
    """
    x = tree_obj.get_children()
    for item in x:
        tree_obj.delete(item)
    if flag.flag_inited == 1:
        app.window.update()


def exec_list_sort(lst):
    """
    通用函数，按我的规矩为列表排序的函数。

    """
    if not type(lst) is list:
        return None
    #
    lst2 = lst.copy()
    #
    # 令@开头的标签在最前
    lst_at = []
    lst_en = []
    lst_cn = []
    for i in lst2:
        if i == '':
            continue
        if str(i).startswith('@'):
            lst_at.append(i)
        else:
            lst_en.append(i)
    # 英文无论大小写都一起排序
    # 如果是^开头，就忽略这个符号，直接正常排序
    lst_en = sorted(lst_en, key=lambda x: str.lower(x.replace(conf.V_SEP, '').replace('\xa0', ' ')).encode('gbk'))
    # 中文也排序
    lst_cn = sorted(lst_cn, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    # 组合起来
    lst2 = lst_at + lst_en + lst_cn
    #
    return lst2


def safe_get_name(new_name) -> str:
    """

    输入: 目标全路径;
    返回: 安全的新路径（可用于重命名、新建等）
    输入和输出都是字符串。

    """
    n = 1
    [tmp_path, tmp_new_name] = os.path.split(new_name)

    p = tmp_new_name.find(conf.V_SEP)
    if p >= 0:
        name_1 = tmp_new_name[:p]
        name_2 = tmp_new_name[p:]
    else:
        p = tmp_new_name.rfind('.')
        if p >= 0:
            name_1 = tmp_new_name[:p]
            name_2 = tmp_new_name[p:]
        else:  # 连'.'都没有的话
            name_1 = tmp_new_name
            name_2 = ''

    tmp_new_full_name = new_name
    while isfile(tmp_new_full_name):
        tmp_new_name = name_1 + '(' + str(n) + ')' + name_2
        tmp_new_full_name = tmp_path + '/' + tmp_new_name
        n += 1
    # print(tmp_new_full_name)
    return (tmp_new_full_name)


def exec_safe_rename(old_name, new_name):
    """
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 如果重命名成功，返回添加数字之后的最终文件名；
    如果重命名失败，返回原始文件名。
    """
    old_name = old_name.replace('\\', '/')
    new_name = new_name.replace('\\', '/')
    '''
    n=1
    [tmp_path,tmp_new_name]=os.path.split(new_name)
    # tmp_path=''
    # tmp_new_name=new_name
    p=tmp_new_name.find(conf.V_SEP)
    if p>=0:
        name_1=tmp_new_name[:p]
        name_2=tmp_new_name[p:]
    else:
        p=tmp_new_name.rfind('.')
        if p>=0:
            name_1=tmp_new_name[:p]
            name_2=tmp_new_name[p:]
        else: # 连'.'都没有的话
            name_1=tmp_new_name
            name_2=''
    
    tmp_new_full_name=new_name   
    while isfile(tmp_new_full_name):
        tmp_new_name=name_1+'('+ str(n)+')'+name_2
        tmp_new_full_name=tmp_path+'/'+tmp_new_name
        n+=1
    print(tmp_new_full_name)
    '''
    tmp_new_full_name = safe_get_name(new_name)
    try:
        os.rename(old_name, tmp_new_full_name)
        return (tmp_new_full_name)
    except:
        print('安全重命名失败！')
        return (old_name)
        pass


def exec_safe_copy(old_name: str, new_name: str, opt_type: str = 'copy'):
    """
    安全复制或移动文件。

    :param opt_type:  'copy' 或 'move'。
    :param old_name: 旧的文件完整路径
    :param new_name: 新的文件完整路径（含文件名）
    :return: 操作之后的文件路径，移动失败返回原始路径，移动成功返回新路径。
    """
    old_name = old_name.replace('\\', '/')
    new_name = new_name.replace('\\', '/')
    #
    # 完全相同的路径不需要执行移动操作
    if old_name == new_name and opt_type == 'move':
        print('原始路径和新路径一致，跳过')
        return (old_name)
    #
    tmp_new_full_name = safe_get_name(new_name)
    print('开始安全复制')
    print(old_name)
    print(tmp_new_full_name)
    if opt_type == 'copy':
        try:
            shutil.copy(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name) 
            print('安全复制成功')
            # os.rename(old_name,tmp_new_full_name)
            return (tmp_new_full_name)
        except:
            tk.messagebox.showerror(title='错误',
                                    message='文件复制失败。')
            print('对以下文件复制失败！')
            print(old_name)
            return (old_name)
            pass
    elif opt_type == 'move':
        try:
            shutil.move(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name) 
            print('安全移动成功')
            # os.rename(old_name,tmp_new_full_name)
            return (tmp_new_full_name)
        except:
            tk.messagebox.showerror(title='错误',
                                    message='文件移动失败。')
            print('对以下文件移动失败！')
            print(old_name)
            return (old_name)
            pass


# style = ttk.Style()

# def fixed_map(option):
#     # Fix for setting text colour for Tkinter 8.6.9
#     # From: https://core.tcl.tk/tk/info/509cafafae
#     #
#     # Returns the style map for 'option' with any styles starting with
#     # ('!disabled', '!selected', ...) filtered out.

#     # style.map() returns an empty list for missing options, so this
#     # should be future-safe.
#     return [elm for elm in ttk.Style.map('Treeview', query_opt=option) if
#             elm[:2] != ('!disabled', '!selected')]

# style.map('Treeview', foreground2=fixed_map('foreground'), background2=fixed_map('background'))

#######################################################################
# %%

def set_prog_bar(inp, maxv=100):
    """
    手动设置进度条。
    """
    app.prog.set(inp)
    app.progressbar_file.update()  # 刷新进度条
    if inp == 0 or inp == 100:
        app.progressbar_file.pack_forget()
    else:
        app.progressbar_file.pack()
    #
    # try:
    #     prog_win
    # except:
    #     var_exists = False
    # else:
    #     var_exists = True
    # print('进度条：')
    # print(var_exists)
    try:
        if inp <= 1:
            # if var_exists == True:
            #     prog_win.set(100)
            #     del prog_win
            app.prog_win = TdProgressWindow(app.window, inp)

        elif inp == 100:
            app.prog_win.set(inp)
            # del prog_win
        else:
            app.prog_win.set(inp)
    except:
        pass


def get_data(ipath=None, update_sub_path=1, need_set_prog=True, is_global=True):
    """
    根据所传入的文件夹列表 ipath，
    （1）刷新 子文件夹列表。
    （2）返回所有文件形成的 lst_files_to_go 列表。这个列表可以在 get_dt 里面调用。
    此过程消耗时间较多。
    参数 ipath 未指定时，自动取为全局变量 conf.lst_my_path_long;
    update_sub_path 的作用是强制修改子文件夹列表【不完善】
    参数 need_set_prog 如果是 False，就不显示或更新进度条。
    """
    print('调用 get_data 函数')

    if is_global:
        global lst_sub_path
    else:
        lst_sub_path = []
        pass

    if ipath is None:
        ipath = conf.lst_my_path_long

    # flag.flag_running=1 # 标记为运行中。

    lst_sub_path_copy = lst_sub_path.copy()
    if flag.flag_inited == 1:
        exec_tree_clear(app.tree)  #
        if need_set_prog: set_prog_bar(1, 30)
        app.str_btm.set("正在加载基础数据……")
        app.window.update()

    time0 = time.time()
    lst_files_to_go = []  # 获取所有文件的完整路径

    n = 1
    n_max = len(ipath)
    lst_sub_path = []

    PROG_STEP = 2
    print('\nget_data函数中获得的参数：')
    print(ipath)
    have_sub_folder = 0
    #
    for vPath in ipath:
        have_sub_folder = 0  # 应该在这
        n += 1  # 第一轮循环的时候n就是2
        #
        if flag.flag_inited == 1 and n % PROG_STEP == 0:
            PROG_STEP *= 2
            tmp_prog = 1 + 29 * n / n_max
            if tmp_prog > 30:
                tmp_prog = 30
            if need_set_prog: set_prog_bar(tmp_prog)

        for root, dirs, files in os.walk(vPath):
            have_sub_folder += 1
            tmp = []
            vpass = 0
            #
            #
            # 文件
            if '_nomedia' in files:
                vpass = 1
                continue
                # break # 这里可能不应该用break

            #
            tmp_path = get_split_path(root)  # 对每个根文件夹，检查
            for tmp2 in tmp_path:
                if len(tmp2) < 1:
                    continue
                if tmp2 in conf.EXP_FOLDERS:
                    vpass = 1
                    break
                elif tmp2[0] == '.':  # 排除.开头的文件夹内容
                    vpass = 1
                    break
            #

            for name in files:
                tmp.append(os.path.join(root, name))
                # if name == '_nomedia':
                #     vpass = 1
                #     break  # 之前居然没写break，难怪那么慢

            if not vpass == 1:
                # 子文件夹
                # new_sub_path = root.replace('\\', '/')
                # new_sub_path = new_sub_path.replace(vPath + '/', '') # 去掉前面部分
                # if (new_sub_path not in lst_sub_path) \
                #         and (str(new_sub_path).find('/') < 0) \
                #         and (str(new_sub_path) not in conf.EXP_FOLDERS): # 只将一级子目录添加到列表中
                #     lst_sub_path.append(new_sub_path)
                # 子文件夹新方法：
                if have_sub_folder <= 1:
                    lst_sub_path += dirs
                #
                lst_files_to_go += tmp

            if flag.flag_break:  # 强行中断
                break
        if flag.flag_break:
            break

    print('——————  加载 文件列表 消耗时间：——————\n')
    print(time.time() - time0)
    #
    # 更新子文件夹列表
    try:
        lst_sub_path.sort()
        lst_sub_path_copy.sort()
        #
        if lst_sub_path == lst_sub_path_copy:
            # update_sub_path = 0 # 这句话是为了避免刷新时候，重复加载子文件夹列表。
            # 但是从逻辑上有【bug】，在只有一个文件夹的时候，可能导致点击全部之后，不再刷新。
            # 有两种方法解决问题：
            # （1）注释这句话；
            # （2）只有一个文件夹的时候，不显示“全部”文件夹。但对于文件夹移动位置仍然有bug。
            pass
        else:
            print(lst_sub_path)
            print(lst_sub_path_copy)
    except:
        pass

    if update_sub_path:  # 如果参数为1的话，
        try:
            print('即将刷新子文件夹')
            lst_sub_path.sort()
            app.v_sub_folders['value'] = [''] + lst_sub_path  # 强制修改子文件夹列表，但这样写【不太好】。
            app.v_sub_folders.current(0)
            #
            update_sub_folder_list(lst_sub_path)
        except Exception as e:
            print(e)
            pass
    else:
        lst_sub_path = lst_sub_path_copy
    # if flag.flag_inited==1:
    #     set_prog_bar(30,30)

    return lst_files_to_go


def get_file_part(tar):  # 
    """
    分拆。
    【疑似bug】对带有空格的路径解析异常

    :param tar: 是完整文件路径。
    :returns: （文件）路径，以字典的形式，返回对应的所有文件信息。
    """

    [fpath, ffname] = os.path.split(tar)  # fpath 所在文件夹、ffname 原始文件名
    [fname, fename] = os.path.splitext(ffname)  # fname 文件名前半部分，fename 扩展名
    lst_sp = fname.split(conf.V_SEP)  # 拆分为多个片段
    fname_0 = lst_sp[0] + fename  # fname_0 去掉标签之后的文件名
    ftags = lst_sp[1:]  # ftags 标签部分
    #
    # 增加NTFS流的标签解析
    if TAG_METHOD == 'FILE_STREAM':
        try:
            with open(tar + ":tags", "r", encoding="utf8") as f:
                ftags += (set(list(map(lambda x: x.strip(), f.readlines()))))
        except FileNotFoundError:
            pass
        except Exception as e:
            # print(e)
            pass

    mtime = os.stat(tar).st_mtime  # 修改时间
    file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    ctime = os.stat(tar).st_ctime  # 创建时间
    file_create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))

    fsize = os.path.getsize(tar)  # 文件大小，字节
    fsize_k = fsize / (1024)  # 换算到kB
    if 0 < fsize_k < 0.1:
        fsize_k = 0.1
    fsize_k = round(fsize_k, 1)

    # 对文件目录的解析算法2：
    tmp = get_split_path(fpath)
    tmp2 = []
    try:  # 只要最后若干层的目录，取变量 conf.V_FOLDERS
        for i in range(conf.V_FOLDERS):
            tmp2.append(tmp[-i - 1])
    except:
        pass

    for i in tmp2:
        i2 = i.split(conf.V_SEP)
        try:
            i3 = i2[1:]  # 取标签符号后面的
            # i3 = i2[0:] # 取整个子文件夹
        except:
            i3 = []
        ftags += i3
    #
    # 增加：最后若干层子文件夹作为标签的功能（默认1层）：
    for i in range(conf.FOLDER_AS_TAG):
        try:
            if str(tmp[-1 - i][0]) == conf.V_SEP:
                continue
            tags_from_folder = tmp[-1 - i].split(conf.V_SEP)
            for j in range(len(tags_from_folder)):
                tags_from_folder[j] = str(tags_from_folder[j]).replace(" ", "_")
            ftags += tags_from_folder
        except Exception as e:
            print(e)
            pass

    # 对当前文件，进行标签整理、去重并排序
    ftags = list(set(ftags))
    ftags.sort()
    #
    # 去掉空标签：
    i = 0
    while i < len(ftags):
        if ftags[i] == '':
            ftags.pop(i)
        else:
            i += 1
    # print(ftags)

    # 统一斜杠方向
    fpath = fpath.replace('\\', '/')
    tar = tar.replace('\\', '/')

    return {'fname_0': fname_0,  # 去掉标签之后的文件名
            'ftags': ftags,
            'ffname': ffname,  # 原始文件名，带标签的
            'filename_origional': ffname,  # 原始文件名，带标签、扩展名的
            'fpath': fpath,
            'f_path_only': fpath,
            'fname': fname,
            'filename_no_ext': fname,  # 去掉扩展名的文件名
            'fename': fename,  # 扩展名
            'file_ext': fename,  # 扩展名
            'full_path': tar,  # 全路径
            'fsize': fsize_k,  #
            'file_full_path': tar,  # 完整路径，和输入参数完全一样
            'file_mdf_time': file_modify_time,
            'file_crt_time': file_create_time
            }


def dt_sort_by(elem):
    """
    主题表格排序
    """
    tmp = str(elem[conf.ORDER_BY_N])
    if conf.ORDER_BY_N == 3:
        return float(tmp)  # 数字
    else:
        tmp = str.lower(tmp)
        tmp = tmp.replace('\xa0', ' ')  # GBK 不支持 'xa0' 的解码。这个是特殊空格。
        return tmp.encode('gbk')  # 需要gbk才能中文正确排序


def sub_get_dt(lst_file_in):
    # 子循环
    tmp_dt = []
    for tar in lst_file_in:
        tmp = get_file_part(tar)
        tmp_v = (str(tmp['fname_0']), tmp['ftags'], str(tmp['file_mdf_time']), tmp['fsize'], str(tmp['full_path']))
        tmp_dt.append(tmp_v)
    q.put(tmp_dt)
    print([conf.V_FOLDERS, conf.V_SEP, conf.NOTE_EXT])
    return tmp_dt


def process_update_data(lst1):
    """
    用于后台加载数据。

    :param lst1: 传入的是完整路径列表。
    """
    print('———— 后台数据加载开始 ————')

    lst_files_to_go = []
    n = 0
    flag.flag_break = 0
    time0 = time.time()
    global dicT

    for vPath in lst1:
        n += 1  # 第一轮循环的时候n就是2
        #

        for root, dirs, files in os.walk(vPath):
            tmp = []
            vpass = 0
            #
            #
            # 文件
            if '_nomedia' in files:
                vpass = 1
                continue
                # break # 这里可能不应该用break

            #
            tmp_path = get_split_path(root)  # 对每个根文件夹，检查
            for tmp2 in tmp_path:
                if len(tmp2) < 1:
                    continue
                if tmp2 in conf.EXP_FOLDERS:
                    vpass = 1
                    break
                elif tmp2[0] == '.':  # 排除.开头的文件夹内容
                    vpass = 1
                    break
            #

            for name in files:
                tmp.append(os.path.join(root, name))
                # if name == '_nomedia':
                #     vpass = 1
                #     break  # 之前居然没写break，难怪那么慢

            if not vpass == 1:
                #
                lst_files_to_go += tmp

            if flag.flag_break:  # 强行中断
                break
        if flag.flag_break:
            break

    for one_file in lst_files_to_go:
        # 先查字典，这样可以显著加速查询
        one_file = one_file.replace('\\', '/')
        if one_file in dicT.keys():
            pass
        else:
            tmp = get_file_part(one_file)
            tmp_v = (str(tmp['fname_0']),
                     tmp['ftags'],
                     str(tmp['file_mdf_time']),
                     tmp['fsize'],
                     tmp['fename'],
                     str(tmp['full_path']))
            # tmp_v = (str(tmp['fname_0']), tmp['ftags'], str(tmp['file_mdf_time']), tmp['fsize'], str(tmp['full_path']))
            try:
                dicT[one_file] = tmp_v
            except Exception as e:
                print(e)
                pass
    #
    print(f'时间消耗：{time.time() - time0}')
    print('———— 后台数据加载完毕 ————')


def get_dt(lst_file0=None, need_set_prog=True, FAST_MODE=True):
    """
    是最消耗时间的函数，也是获取数据的核心函数。
    输入参数是文件列表，lst_file0。
    这个参数的缺省值是来自于 get_data() 函数的 lst_files_to_go ，提供了所有文件。

    根据 lst_files_to_go 里面的文件列表，返回 (dT, lst_tags) .\n
    注意这里(dT, lst_tags)都不是全局变量，需要从返回值获得。

    只有 dicT 是全局变量，用于存储临时值，加快运行速度。
    """
    print('进入 get_dt 函数')
    global dicT  #

    if flag.flag_break:
        return (None, None)

    if lst_file0 is None:
        lst_file0 = lst_files_to_go.copy()

    if flag.flag_inited == 1:
        app.str_btm.set("正在解析标签……")
        app.window.update()
        if need_set_prog: set_prog_bar(30)

    time0 = time.time()

    n = 1
    n_max = len(lst_file0)

    dT = list()

    if MULTI_PROC > 1 and len(lst_file0) > MULTI_FILE_COUNT:  # 如果是并发状态：
        MAX_PROC = MULTI_PROC
        res_proc = []
        tmp_len = int(len(lst_file0) / MAX_PROC)
        tmp_file_in = []
        for i in range(MAX_PROC):
            if i < MAX_PROC - 1:
                tmp_file_in.append(lst_file0[i * tmp_len:(i + 1) * tmp_len])
            else:
                tmp_file_in.append(lst_file0[i * tmp_len:])
        #
        p = Pool(MAX_PROC)  # 设置默认并发数。可以忽略
        # pl=[]
        res_tmp = []
        t = []
        for i in range(MAX_PROC):
            # res_tmp.append('')
            # res_tmp[i]=p.apply(sub_get_dt,args=(tmp_file_in[i],))
            # res_proc.append(res_tmp.get())
            # pl[-1].start()
            t.append(threading.Thread(target=sub_get_dt, args=(tmp_file_in[i],)))
            t[-1].start()

        # p.close()
        # p.join()
        if need_set_prog: set_prog_bar(50)
        for i in t:
            i.join()
        while not q.empty():
            tmp_get_dt = q.get()
            # print(tmp_get_dt)
            dT += tmp_get_dt
        if need_set_prog: set_prog_bar(70)
        # tmp_part=[]
        # print('组合之前：——————')
        # print(time.time()-time0)
        # for i in res_tmp:
        # dT+=i
        print('组合之后：——————')
        print(time.time() - time0)
        #
        #
    else:  # 单线程

        for one_file in lst_file0:
            one_file = one_file.replace('\\', '/')
            # 更新进度条
            n += 1
            if flag.flag_inited == 1 and n % PROG_STEP == 0:
                if need_set_prog: set_prog_bar(30 + 60 * n / n_max)
            # 先查字典，这样可以显著加速查询
            if FAST_MODE and one_file in dicT.keys():
                tmp_v = list(dicT[one_file])

                # mtime = os.stat(one_file).st_mtime # 修改时间
                # file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                # tmp_v[2]=file_modify_time
                # # 文件大小
                # fsize = os.path.getsize(one_file)  # 文件大小，字节
                # fsize_k = fsize / (1024)  # 换算到kB
                # fsize_k = round(fsize_k, 1)
                # tmp_v[3]=fsize_k
                # tmp_v=tuple(tmp_v)

            else:

                tmp = get_file_part(one_file)
                # dT.append([tmp['fname_0'],tmp['ftags'],tmp['fpath'],tmp['full_path']])
                # 增加检查重复项的逻辑：
                # tmp_v=[tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path']]
                # tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path'])
                tmp_v = (str(tmp['fname_0']),
                         tmp['ftags'],
                         str(tmp['file_mdf_time']),
                         tmp['fsize'],
                         tmp['fename'],
                         str(tmp['full_path']))
                try:

                    dicT[one_file] = tmp_v
                except Exception as e:
                    print(e)
                    pass
            # if not tmp_v in dT:
            #     dT.append(tmp_v) # 查重有点费时间
            dT.append(tmp_v)
            #
            if flag.flag_break:  # 如果被中断的话
                break

    print('加载dT消耗时间：')
    print(time.time() - time0)

    # 去重
    dT2 = []
    for i in dT:
        if not i in dT2:
            dT2.append(i)
    dT = dT2
    # dT=list(set(dT))

    if flag.flag_inited == 1:
        if need_set_prog: set_prog_bar(90)

    # 获取所有tag
    tmp = []
    for i in dT:
        tmp += i[1]

    lst_tags = list(set(tmp))
    lst_tags = sorted(lst_tags, key=lambda x: x.replace('\xa0', ' ').encode('gbk'))
    lst_tags = [cALL_FILES] + lst_tags
    # lst_tags.sort()

    try:
        dT.sort(key=dt_sort_by, reverse=conf.ORDER_DESC)
    except:
        print('dT排序出现错误！')

    return (dT, lst_tags)


# %%
#######################################################################
# %%
def show_window_info():
    """
    显示关于窗口。
    不需要任何参数。
    """
    screenwidth = conf.SCREEN_WIDTH
    screenheight = conf.SCREEN_HEIGHT
    w_width = int(660*conf.ui_ratio)
    w_height = int(560*conf.ui_ratio)
    info_window = tk.Toplevel(app.window, background='white')
    info_window.geometry(
        '%dx%d+%d+%d' % (w_width, w_height, (screenwidth - w_width) / 2, (screenheight - w_height) / 2))
    info_window.title('关于标签文库')

    info_window.transient(app.window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
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
    tmp = tk.Label(info_frame, background='white', text='版本：' + cst.VER + '')
    tmp.pack()
    tmp = tk.Label(info_frame, background='white', text='Powered by Python and Tkinter\n')
    tmp.pack()

    global p_logo
    p_logo = tk.PhotoImage(file='.//resources/imgs/二维码设计.png')
    logolbl = tk.Label(info_frame, background='white', text='A', image=p_logo)
    logolbl.pack()

    # tmp = tk.Label(info_frame,background='white', text='（欢迎扫码访问产品动态）')
    # tmp.pack()


def show_window_input(title_value, body_value='', init_value='', is_file_name=True):
    """
    接管输入框的过程，以后可以将自定义输入框替换到这里。

    目前的用法：输入参数 1 标题，2 正文，3 默认值；

    返回输入框的结果。如果输入内容为空，返回 None。

    参数 is_file_name 为 True 的时候，将文件名不能带的特殊字符自动去掉。

    """
    # 获得输入值
    res = str(TdInputWindow(app.window, title=title_value, msg=body_value,
                            default_value=init_value, ui_ratio=conf.ui_ratio,)).strip()
    if len(res) == 0:
        print('没有得到输入内容')
        return None

    # 特殊处理
    if is_file_name:
        res = res.replace('\\', '_')
        res = res.replace('/', '_')
        res = res.replace('?', '_')
        res = res.replace('|', '_')
        res = res.replace('*', '_')
        res = res.replace('"', '_')
        res = res.replace('<', '_')
        res = res.replace('>', '_')
        res = res.replace(':', '_')
    return res
    pass


# %% 文件夹方面的

def update_folder_list(event=None, need_select=True):
    """
    根据 conf.lst_my_path_short ，将文件夹列表刷新一次。

    作用是：刷新主文件夹列表。暂不包括子文件夹刷新。

    没有输入输出。
    """
    global tree_lst_folder

    # 根目录的名称列表
    # lst_root_text = list(set(dict_folder_groups.values()))
    # # 排序
    # lst_root_text = exec_list_sort(lst_root_text)
    # if DEFAULT_GROUP_NAME in lst_root_text: # 默认文件夹分组永远在前
    #     lst_root_text.remove(DEFAULT_GROUP_NAME)
    #     lst_root_text = [DEFAULT_GROUP_NAME] + lst_root_text
    #
    lst_root_text = get_folder_group_list()
    conf.lst_my_path_short = exec_list_sort(conf.lst_my_path_short)

    def find_node_pos_by_text(node, text, pos_min=0):
        """
        返回对应的位置编号
        node
        text
        pos_min 是最小的位置，默认为0. 只会返回不小于这个值的查询位置。
        """
        find_succ = 0
        pos = 0
        if node is None:
            items = app.tree_lst_folder.get_children()
        else:
            items = app.tree_lst_folder.get_children(node)
        for i in items:
            if app.tree_lst_folder.item(i, 'text') == text and pos >= pos_min:
                find_succ = 1
                break
            pos += 1
        if find_succ:
            return pos
        else:
            return -1

    #
    # 保存当前的根文件夹（分组）的名称、顺位
    try:
        tmp_group = get_folder_root_node()
        tmp_group_text = app.tree_lst_folder.item(tmp_group, 'text')
        group_pos = find_node_pos_by_text(None, tmp_group_text)
        #
        tmp_folder1 = get_folder_root_node(1)
        tmp_folder1_text = app.tree_lst_folder.item(tmp_folder1, 'text')
        # folder1_pos=0
        # for i in app.tree_lst_folder.get_children(tmp_group):
        #     if app.tree_lst_folder.item(i,'text') == tmp_folder1_text:
        #         break
        #     folder1_pos+=1
    except:
        group_pos = 0
        folder1_pos = 0
    #
    # 保存现在选中的主文件夹；
    v_method = 2
    tmp_lst_open = []  # 保存一路上来的文件夹名称
    if flag.flag_inited:
        (b1, b2) = app.bar_folder_v.get()
    try:
        tmp_folder1 = 0
        tmp_n = 0
        tmp_root = tmp_group

        for tmp_s in app.tree_lst_folder.selection():
            pass
            #
        for _ in range(1000):  # 不可能有1000层的文件夹吧
            tmp_lst_open.append(app.tree_lst_folder.item(tmp_s, "text"))
            tmp_p = app.tree_lst_folder.parent(tmp_s)
            need_debug = app.tree_lst_folder.item(tmp_p, "values")
            if int(app.tree_lst_folder.item(tmp_p, "values")[1]) <= 1:
                break
            else:
                tmp_s = tmp_p

    except Exception as e:
        print(e)
        tmp_folder1 = 0

    # 先清空一次；
    exec_tree_clear(app.tree_lst_folder)

    #
    def add_sub_folder_here(root_node, root_dir, depth):
        """
        局部函数，用于增加子文件夹。
        参数 root_node 根节点
        root_dir 根路径
        depth 深度编号
        """
        tmp = 1
        for root_, dirs_, files_ in os.walk(root_dir):
            # dirs_.sort()
            dirs_sorted = exec_list_sort(dirs_)
            for sub_dir_ in dirs_sorted:
                tmp += 1
                if sub_dir_ in conf.EXP_FOLDERS:  # 排除文件夹
                    continue
                if '_nomedia' in files_:
                    continue
                #
                full_dir_ = root_dir + '/' + sub_dir_
                value_tmp_ = (root_dir, depth, full_dir_)  # values 格式 根路径，深度，全路径(-1)
                t3 = app.tree_lst_folder.insert(root_node, tmp, text=sub_dir_,
                                            image=PIC_DICT['folder_25_20'],
                                            values=value_tmp_, tags=['folder2'])
                # 继续迭代下钻
                if flag.flag_inited: # 刚启动的时候，不需要加载全部文件夹，从而提高加载速度
                    add_sub_folder_here(t3, full_dir_, depth + 1)
            break  #


    #
    tmp = 1
    #
    # 建立根文件夹
    n_root = 0
    lst_root_item = []
    for root_text in lst_root_text:
        lst_root_item.append(
            app.tree_lst_folder.insert('', n_root, text=root_text, tags=['folder0'], values=("（全部）",), open=True))
        n_root += 1
    # root1=app.tree_lst_folder.insert('',1,text='新建分组',values=("（全部）",),open=True)
    #
    # 开始添加文件夹
    for i in conf.lst_my_path_short:
        #
        # 获得group_name
        # if str.lower(i).find('^') <0:
        #     group_name='关注的文件夹'
        # else:
        #     group_name='新建分组'
        group_name = conf.dict_folder_groups[i]
        # 找到根节点
        tmp_root_pos = lst_root_text.index(group_name)
        root_node = lst_root_item[tmp_root_pos]
        #
        tmp += 1
        print(i)
        # 值编码：显示名称、类型、完整路径(总是放在最后一个)
        full_dir1 = conf.dict_path[str(i)]
        value0 = (str(i),
                  1,
                  full_dir1)
        t1 = app.tree_lst_folder.insert(root_node, tmp, text=str(i),
                                    image=PIC_DICT['folder_50_20'],
                                    values=value0, tags=['folder1'])
        #
        # 二级目录及以后
        add_sub_folder_here(t1, full_dir1, 2)
        #
    # 
    # 刷新后，选中第几个项目：
    #
    if v_method == 2 and flag.flag_inited:
        # print("\n\n\ntmp_lst_open=",tmp_lst_open,'\n\n\n')
        tmp_lst_open.reverse()
        #
        # 判断位置
        group_pos = find_node_pos_by_text(None, tmp_group_text)
        if group_pos < 0:
            group_pos = 0
        item_group = app.tree_lst_folder.get_children()[group_pos]  # 分组结点（0级目录）
        #
        folder1_pos = find_node_pos_by_text(item_group, tmp_folder1_text)
        if folder1_pos < 0:
            folder1_pos = 0
        item_folder1 = app.tree_lst_folder.get_children(item_group)[folder1_pos]  # 根结点（1级目录）
        app.tree_lst_folder.item(item_folder1, open=True)  # 展开1级节点
        app.tree_lst_folder.selection_set(item_folder1)  # 选中
        tmp_i = item_folder1
        try:
            for tmp_text in tmp_lst_open:

                print('tmp_text=', tmp_text)
                #
                folder2_pos = find_node_pos_by_text(tmp_i, tmp_text)
                if folder2_pos < 0:
                    print('\n没有找到：', tmp_text, ', 退出')
                    break
                tmp_i = app.tree_lst_folder.get_children(tmp_i)[folder2_pos]  # 根结点（1级目录）
                app.tree_lst_folder.item(tmp_i, open=True)  # 展开节点
                app.tree_lst_folder.selection_set(tmp_i)  # 选中

            try:
                app.tree_lst_folder.update()
                app.tree_lst_folder.yview_moveto(b1)
            except:
                pass
            on_folder_choose()
            #
        except Exception as e:
            print(e)
            pass

    else:  # 如果没有 flag.flag_inited 的话，默认选中第一个文件夹
        #
        print('刷新文件夹：选中的文件夹是：', tmp_folder1)
        if need_select:
            try:
                item_group = app.tree_lst_folder.get_children()[group_pos]
                to_selct = app.tree_lst_folder.get_children(item_group)[tmp_folder1]
                app.tree_lst_folder.selection_set(to_selct)  # 选中第一个文件夹
                #
                on_folder_choose()  # 右边也重载一次
                #
            except Exception as e:
                print(e)
                pass


def update_current_folder_list(event=None, ):
    """
    测试：想要设计为点击左侧文件夹的时候，刷新当前文件夹内部结构，
    这样可以提高效率。
    """
    # 基本思路：删掉子文件，然后重新加载子文件夹
    def add_sub_folder_here(root_node, root_dir, depth, if_cont=True):
        """
        局部函数，用于增加子文件夹。
        参数 root_node 根节点
        root_dir 根路径
        depth 深度编号
        """
        tmp = 1
        for root_, dirs_, files_ in os.walk(root_dir):
            # dirs_.sort()
            dirs_sorted = exec_list_sort(dirs_)
            for sub_dir_ in dirs_sorted:
                tmp += 1
                if sub_dir_ in conf.EXP_FOLDERS:  # 排除文件夹
                    continue
                if conf.EXP_DOT_FOLDERS and str(sub_dir_).startswith('.'):
                    continue
                if '_nomedia' in files_:
                    continue
                #
                full_dir_ = root_dir + '/' + sub_dir_
                value_tmp_ = (root_dir, depth +1, full_dir_)  # values 格式 根路径，深度，全路径(-1)
                t3 = app.tree_lst_folder.insert(root_node, tmp, text=sub_dir_,
                                            image=PIC_DICT['folder_25_20'],
                                            values=value_tmp_, tags=['folder2'])
                # 继续迭代下钻
                if if_cont:
                    add_sub_folder_here(t3, full_dir_, depth + 1, False)
            break  #

    # 获取当前点击的节点
    for root_node in app.tree_lst_folder.selection():
        root_dir = app.tree_lst_folder.item(root_node, "values")[-1]
        try:
            root_depth = int(app.tree_lst_folder.item(root_node, "values")[1])
        except Exception as e:
            root_depth = 0
        print(root_dir)
        print(root_depth)
        break

    if root_depth:#1:
        # 删掉子目录
        for item in app.tree_lst_folder.get_children(root_node):
            app.tree_lst_folder.delete(item)

        # 添加子目录节点，并展开当前节点
        try:
            add_sub_folder_here(root_node, root_dir, root_depth)
            app.tree_lst_folder.update()
        except Exception as e:
            print('2022年10月13日：文件夹读取失败')
            pass

def update_sub_folder_list_via_menu(event=None):
    """
    在右键菜单里面执行刷新子文件夹列表操作。
    """
    update_sub_folder_list()
    update_main_window(0, fast_mode=True)  # reload_setting=2)


def update_sub_folder_list(sub_folder_list=None, refresh=True):
    """
    将子文件夹列表刷新一次。
    输入是要填充的子文件夹列表。
    参数 refresh =True 就选中全部子文件夹，=False 选中之前的。
    """
    #
    tmp_sub_folder = app.tree_lst_sub_folder.selection()  # 保存当前值
    #
    # 清空一次
    exec_tree_clear(app.tree_lst_sub_folder)
    #
    # 主文件夹为全部的时候，不返回任何子文件夹
    if get_folder_short() in ["（全部）", ""]:
        print('主文件夹为全部，所以不更新子文件夹')
        return
    #
    # 如果没有指定的话，
    if sub_folder_list is None:
        sub_folder_list = []
        # 如果没有指定的话，就读取当前主文件夹的列表
        try:
            vPath = get_folder_long()
            for root, dirs, files in os.walk(vPath):
                sub_folder_list = dirs
                break
            pass
        except:
            pass
    #
    tmp = 0
    #
    # 先插入一个“全部”
    app.tree_lst_sub_folder.insert('', tmp, values=("（全部）"), tags=['line1'] if tmp % 2 == 0 else ['line2'])
    # 排序
    sub_folder_list = sorted(sub_folder_list, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    #
    for i in sub_folder_list:
        if i in conf.EXP_FOLDERS:
            continue
        tmp += 1
        print(i)
        app.tree_lst_sub_folder.insert('', tmp, values=(i,),
                                   tags=['line1'] if tmp % 2 == 0 else ['line2'])  # 必须加逗号，否则对存在空格的不可用
        # image=IMAGE_FOLDER,
    # 
    # 恢复之前的选项；
    try:
        if refresh is None:
            pass
        elif refresh:  # refresh =True 代表重置当前选项，也就是选中最开始的。
            tmp = app.tree_lst_sub_folder.get_children()[0]
            # app.tree_lst_folder.focus(tmp)
            app.tree_lst_sub_folder.selection_set(tmp)
        else:  # 否则选中之前的；
            try:
                app.tree_lst_sub_folder.selection_set(tmp_sub_folder)
            except:
                tmp = app.tree_lst_sub_folder.get_children()[0]
                app.tree_lst_sub_folder.selection_set(tmp)
        # 刷新一次；
        # update_main_window(0,fast_mode=True)#reload_setting=2)
    except Exception as e:
        print(e)
        update_folder_list()
        pass


def show_tree_order():
    """
    用来显示 tree 排序的视觉效果（也就是加三角）
    """
    DIR_VALUE = DIR_LST[1] if conf.ORDER_DESC else DIR_LST[0]
    app.tree.heading(HEADING_LST[conf.ORDER_BY_N], text=HEADING_LST_TXT[conf.ORDER_BY_N] + DIR_VALUE)


def tree_order_base(inp):
    """
    主列表排序的入口程序。
    """

    global dT, lst_tags
    # 恢复标题
    app.tree.heading(HEADING_LST[conf.ORDER_BY_N], text=HEADING_LST_TXT[conf.ORDER_BY_N])
    #
    if conf.ORDER_BY_N == inp:  # 如果同样位置点击，就切换排序方式
        conf.ORDER_DESC = not conf.ORDER_DESC
    else:  # 如果不同位置点击，就预置排序方式
        conf.ORDER_BY_N = inp
        if conf.ORDER_BY_N == 2:  # 按修改时间排序的，第一次是最新的在前面。
            conf.ORDER_DESC = True
        else:
            conf.ORDER_DESC = False  # 其余排序方法，都是升序。
    # update_main_window(0) # 这个方法虽然可以排序，但是效率太低
    #
    # 可视化
    show_tree_order()

    # 新的排序方法
    dT.sort(key=dt_sort_by, reverse=conf.ORDER_DESC)
    exec_search()
    set_search_tag_values(lst_tags)
    app.v_inp['value'] = lst_tags


def tree_order_filename(inp=None):
    tree_order_base(0)


def tree_order_tag(inp=None):
    tree_order_base(1)


def tree_order_modi_time(inp=None):
    tree_order_base(2)


def tree_order_size(inp=None):
    tree_order_base(3)


def tree_order_path(inp=None):
    tree_order_base(4)


# %%


def get_search_tag_selected(event=None):
    '''
    获取标签项（只是内容字符串，目前还不是列表）。
    '''
    the_tag = ''
    if conf.TREE_SUB_SHOW == 'tag':
        for item in app.tree_lst_sub_tag.selection():
            the_tag = app.tree_lst_sub_tag.item(item, "values")[0]
            break
    else:
        the_tag = app.v_tag.get()
    #
    if the_tag in ['（全部）']:
        the_tag = ''
    print('标签里面是' + the_tag)
    return the_tag


def tree_tag_search(event=None):
    """
    这是个目前没有用的函数。
    """
    print('tree_tag_search')
    pass


def set_search_tag_values(v_lst):
    #
    global lst_tags
    lst_tags = v_lst

    '''
    为标签添加内容
    '''
    # 令@开头的标签在最前
    lst_at = []
    lst_en = []
    lst_cn = []
    for i in v_lst:
        if i == '':
            continue
        if str(i).startswith('@'):
            lst_at.append(i)
        else:
            lst_en.append(i)
    # 英文无论大小写都一起排序
    lst_en = sorted(lst_en, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    # 组合起来
    v_lst = lst_at + lst_en + lst_cn
    #
    # 下拉框：
    app.v_tag['value'] = [''] + v_lst
    #
    # 列表：
    tmp_sub_tag = app.tree_lst_sub_tag.selection()
    exec_tree_clear(app.tree_lst_sub_tag)

    # if get_folder_short() in ["（全部）", ""]:
    #     return

    tmp = 0
    app.tree_lst_sub_tag.insert('', tmp, values=("（全部）"), tags=['line1'] if tmp % 2 == 0 else ['line2'])

    for i in v_lst:
        tmp += 1
        # print(i)
        if str(i).strip() == '':
            continue
        app.tree_lst_sub_tag.insert('', tmp, values=(i,),
                                tags=['line1'] if tmp % 2 == 0 else ['line2'])  # 必须加逗号，否则对存在空格的不可用
        # image=IMAGE_FOLDER,
    app.tree_lst_sub_tag.update()
    try:
        if app.v_tag.get() != '':
            find_res = exec_tree_find(app.v_tag.get(), False, app.tree_lst_sub_tag, app.bar_sub_tag_v, 0)
            if find_res == -1:  # 如果没找到的话
                tmp = app.tree_lst_sub_tag.get_children()[0]
                app.tree_lst_sub_tag.selection_set(tmp)
        else:
            tmp = app.tree_lst_sub_tag.get_children()[0]
            app.tree_lst_sub_tag.selection_set(tmp)
            # else:
            # app.tree_lst_sub_tag.selection_set(tmp_sub_tag)
            pass
    except Exception as e:
        print(e)
        pass
    # if app.v_tag.get() != '':
    #     exec_tree_find(app.v_tag.get(),False,app.tree_lst_sub_tag,app.bar_sub_tag_v,0)


def set_sub_folder_selected(inp):
    if type(inp) is str:
        tmp_n = lst_sub_path.index(inp)
        app.v_sub_folders.current(tmp_n + 1)
    elif type(inp) is int:
        app.v_sub_folders.current(inp)


def set_search_tag_selected(ind):
    """
    设置标签，选中指定的项目。
    如果输入的是字符串，则选中字符串。
    """
    # 如果是字符串的话；
    if type(ind) is str:
        try:
            tags2 = app.v_tag['values']
            set_search_tag_selected(tags2.index(ind))
        except:
            set_search_tag_selected(0)
    # 如果是数字的话
    elif type(ind) is int:
        #
        # 下拉框
        app.v_tag.current(ind)
        #
        # 列表：
        # exec_tree_find('（全部）',the_tree=app.tree_lst_sub_tag,the_bar=app.bar_sub_tag_v,the_col=0)
    else:
        app.v_tag.current(0)


def on_sub_tag_choose(event=None):
    """
    点击sub_tag之后
    """
    res = ''
    for item in app.tree_lst_sub_tag.selection():
        res = app.tree_lst_sub_tag.item(item, "values")[0]
    if res in ['（全部）']:
        res = ''
    if res == '':
        set_search_tag_selected(0)
    else:
        set_search_tag_selected(res)
    exec_search()


def get_search_items(event=None, res_lst=False):
    """
    获取标签下拉框里面的标签。
    不过，现在也兼职了对输入框的搜索。
    返回值是列表 res。
    或者参数 True的时候，返回 res_tag,res_keyword,res_path
    """
    res = []
    res_tag = []
    res_keyword = []
    res_path = []
    #
    # 标签
    if len(get_search_tag_selected()) > 0:
        res_tag = [get_search_tag_selected()]
        res += res_tag
    #
    # 关键词
    if len(app.v_search.get()) > 0:
        res_keyword = str(app.v_search.get()).split(' ')
        res += res_keyword
    #
    # 子文件夹
    if len(get_sub_folder_selected()) > 0:
        tmp_path = conf.lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
        print('进入子文件夹：')
        print(tmp_path)
        res_path = [tmp_path]
        res += res_path
    else:
        # 还要考虑子文件夹从有到无时候的处理；
        pass
        '''
        # 还要刷新子文件夹的标签
        tmp_tag=app.v_tag.get() # 获取当前标签
        #刷新标签列表
        new_files = get_data(res,update_sub_path=0)
        (dt2,tags2)=get_dt(new_files)
        print(tags2)
        set_search_tag_values(['']+tags2)
        if len(tmp_tag)>0:
            # 恢复标签
            set_search_tag_selected(tags2.index(tmp_tag)+1)
            pass
        '''
    if res_lst:
        return res_tag, res_keyword, res_path
    else:
        return res


def get_sub_folder_selected():
    """
    获取子文件夹名称（没有输入，返回字符串，或者空白）
    【还不完善】
    """
    if conf.TREE_SUB_SHOW == 'sub_folder':  # sub_folder 模式，子文件夹是选项
        METHOD = 2
    elif conf.TREE_SUB_SHOW == 'tag':  # tag模式，子文件夹是下拉框
        METHOD = 1
    #
    if METHOD == 1:
        if get_folder_short in ['', '（全部）']:
            return ''
        else:
            return app.v_sub_folders.get()
    # 方法2：
    elif METHOD == 2:
        res = ''
        for item in app.tree_lst_sub_folder.selection():
            res = app.tree_lst_sub_folder.item(item, "values")[0]
        if res in ['（全部）']:
            res = ''
        return res


def update_tags_in_sub_folder(tmp_path, must=0):
    '''
    切换子文件夹之后触发。刷新标签。
    输入参数是文件夹路径（str）。
    返回值是新的标签列表。
    参数 must 是强制刷新子文件夹标签的意思。
    '''
    # 这里，如果是子文件夹切换，还要刷新文件夹的标签【bug】
    #
    # if flag.flag_root_folder:
    global dT
    print(f'正在加载该目录的标签：{tmp_path}')
    if must or flag.flag_sub_folders_changed:
        # 加载新标签列表
        tmp_tag = get_search_tag_selected()  # 获取当前标签
        # 刷新标签列表 刷新期间不能操作进度条！
        new_files = get_data([tmp_path], update_sub_path=0, need_set_prog=False)
        (dt2, tags2) = get_dt(new_files, need_set_prog=False)

        # dT=dt2
        # print(f'\ndt2={dt2}')
        set_search_tag_values(tags2)
        if flag.flag_inited:
            app.v_inp['value'] = tags2
        if len(tmp_tag) > 0:
            # 恢复标签
            try:
                set_search_tag_selected(tags2.index(tmp_tag))
            except:
                set_search_tag_selected(0)
        else:
            set_search_tag_selected(0)
            pass
        print(f'获取的标签是：{tags2}')
        return tags2
    else:
        # 子文件夹没有切换的时候，不需要刷新标签
        pass
    pass


def get_search_items_sub_folder(event=None, res_lst=False):
    '''
    获取子文件夹内的文件.
    在函数中，包括了【对标签的刷新】。
    '''
    try:
        if len(get_sub_folder_selected()) > 0:
            tmp_path = conf.lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
            print('运行到 get_search_items_sub_folder, 进入子文件夹：')
            print(tmp_path)
        else:
            tmp_path = conf.lst_my_path_long_selected[0]
    except:
        if res_lst:
            return [], [], []
        else:
            return []
    tmp_path = str(tmp_path).replace('\\', '/')

    update_tags_in_sub_folder(tmp_path)
    '''
    # 这里，如果是子文件夹切换，还要刷新文件夹的标签【bug】
    #
    # if flag.flag_root_folder:
    if not flag.flag_sub_folders_changed:
        # 子文件夹没有切换的时候，不需要刷新标签
        pass
    else:
        # 加载新标签列表
        tmp_tag = get_search_tag_selected()  # 获取当前标签
        # 刷新标签列表
        new_files = get_data([tmp_path], update_sub_path=0)
        (dt2, tags2) = get_dt(new_files)
        # print(tags2)
        set_search_tag_values(tags2)
        if flag.flag_inited:
            app.v_inp['value'] = tags2
        if len(tmp_tag) > 0:
            # 恢复标签
            try:
                set_search_tag_selected(tags2.index(tmp_tag))
            except:
                set_search_tag_selected(0)
        else:
            set_search_tag_selected(0)
            pass'''
    # res = get_search_items()
    if res_lst == False:
        res = get_search_items(res_lst=False)
        return res
    else:
        res_tag, res_keyword, res_path = get_search_items(res_lst=True)
        return res_tag, res_keyword, res_path


def get_icon_ext(dot_ext):
    """
    根据扩展名，返回图标
    """
    ext = str.lower(dot_ext)
    #
    if ext in ['.docx', '.doc', '.wps']:
        tmp_imag = app.PIC_DICT['word']
    elif ext in ['.xlsx', '.xls', 'xlsm', '.et']:
        tmp_imag = app.PIC_DICT['excel']
    elif ext in ['.pptx', '.ppt']:
        tmp_imag = app.PIC_DICT['ppt']
    elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.svg']:
        tmp_imag = app.PIC_DICT['img']
    elif ext in ['.7z', '.zip', '.rar']:
        tmp_imag = app.PIC_DICT['zip']
    elif ext in ['.md']:
        tmp_imag = app.PIC_DICT['md']
    elif ext in ['.html', '.mht', '.url', '.htm']:
        tmp_imag = app.PIC_DICT['html']
    elif ext in ['.pdf']:
        tmp_imag = app.PIC_DICT['pdf']
    else:
        tmp_imag = app.PIC_DICT['file']
    return tmp_imag


def exec_tree_add_items(tree_obj, dT, search_items=None) -> None:
    """
    关键函数：增加主框架的内容
    先获得搜索项目以及 tag
    进度从 90 增加到 100
    """
    app.str_btm.set('正在刷新列表……')
    time0 = time.time()
    res_tag, res_keyword, res_path = get_search_items_sub_folder(res_lst=True)
    # tmp_search_items = get_search_items_sub_folder()  # 列表
    #
    k = 0
    k1 = 0  # 存储根目录下的编号
    k2 = 0
    k_all = 0

    print('筛选条件：')
    # print(tmp_search_items)
    print(f'标签是 {res_tag}')
    print(f'关键词是 {res_keyword}')
    print(f'路径是{res_path}')
    n = 0
    n_max = len(dT)
    refresh_unit = 4
    print(f'检查的路径是{res_path}')
    #
    # print('app.v_this_folder = ', app.v_this_folder.get())
    print('主路径是 = ', conf.lst_my_path_long_selected)
    #
    # 前置条件检查：
    var_note_only = app.v_note_only.get()  # 只看笔记
    var_this_folder = app.v_this_folder.get()  # 只看当前文件夹
    var_group_by_folder = app.v_folder_layers.get()  # 按文件夹分组
    is_this_folder = 1  # 是否是当前文件夹
    item_sub_folder = None
    tmp_current_path = conf.lst_my_path_long_selected[0].replace('\\', '/')  # 当前路径
    #
    # 如果是分组模式，就检查子文件夹，并预先要做分组：

    if var_group_by_folder and len(conf.lst_my_path_long_selected) == 1:
        lst_sub_folders_full = []
        lst_sub_folders = []
        lst_sub_items = []
        lst_k = []
        for _root, _dirs, _ in os.walk(tmp_current_path):
            lst_sub_folders += _dirs  # 子文件夹
            break
        for _dir in exec_list_sort(lst_sub_folders):
            if _dir in conf.EXP_FOLDERS:
                continue
            lst_sub_folders_full.append(_dir)
            lst_sub_items.append(tree_obj.insert('', 'end',
                                             text=_dir,
                                             tags=['line_folder'],  # if k % 2 == 1 else ['line2'],
                                             values=(0, '', '', '', '', '')))
            lst_k.append(0)
            tree_obj.item(lst_sub_items[-1], open=True)
    #
    for i in range(len(dT)):  # 对每一条进行测试：
        n += 1
        #
        tmp = dT[i]  # 一整行
        try:
            if str(tmp[0]).startswith('~'):  # 排除word临时文件
                continue
        except Exception as e:
            print(e)
            pass
        #
        # 搜索的时候转小写，避免找不到类似于MySQL这样的标签
        # 大小写转换仅限标签

        canadd = 1
        #
        # 只看当前文件夹
        the_node = ''
        if len(conf.lst_my_path_long_selected) == 1 and canadd == 1:
            if var_group_by_folder or var_this_folder:  # app.v_this_folder.get() == 1:
                [tmp_fpath, tmp_ffname] = os.path.split(tmp[-1])
                # print(str.lower(tmp_fpath))
                # print(str.lower(conf.lst_my_path_long_selected[0]))
                if str.lower(tmp_fpath) == str.lower(tmp_current_path):
                    is_this_folder = True
                    # the_node = ''
                else:
                    is_this_folder = False
                    if var_this_folder:
                        canadd = 0
                    else:
                        for f_index in range(len(lst_sub_folders_full)):
                            # 文件夹
                            tmp_sub_pth = str.lower('/'.join([tmp_current_path, lst_sub_folders_full[f_index]]))
                            # 完整文件路径（不含文件名）
                            tmp_full_pth = str.lower(tmp_fpath).replace('\\', '/')
                            #
                            # print(tmp_sub_pth, tmp_full_pth) # 调试用
                            if tmp_sub_pth+'/' in tmp_full_pth+'/':  # 判断文件在哪个子文件夹内。添加斜线是为了避免文本包含。
                                the_node = lst_sub_items[f_index]
                                lst_k[f_index] += 1
                                k2 = lst_k[f_index]
                                break

        #
        # 只看笔记
        if canadd == 1:
            if var_note_only == 1:  # app.v_note_only.get() == 1:
                if not ('笔记' in tmp[0] or '笔记' in tmp[1]):
                    canadd = 0
        # 路径包含
        if canadd == 1:  #
            #
            for pth in res_path:
                #
                if str.lower(tmp[-1]).find(str.lower(pth)) < 0:  # 全路径搜索
                    # print(f'路径不符合，当前路径为{str.lower(tmp[-1])}')
                    canadd = 0
                    break  # 有这句话就是 and 关系。
                #
        # 标签包含
        if canadd == 1:  #
            tag_lower = []
            for j in tmp[1]:
                tag_lower.append(str.lower(j))

            for tag in res_tag:
                tag = str.lower(tag)
                if tag == '' or tag == cALL_FILES or (tag in tag_lower):
                    canadd = 1
                    # break
                elif conf.TAG_EASY == 1 and str.lower(tmp[0]).find(tag) >= 0:  # 标签简单模式
                    canadd = 1
                else:
                    canadd = 0
                    break  # 有这句话就是 and 关系。
        #
        # 关键词搜索
        if canadd == 1:  #
            for keyw in res_keyword:
                #
                if True:  # 文件名和标签搜索
                    if ';'.join(tag_lower).find(str.lower(keyw)) >= 0:
                        canadd = 1
                    elif str.lower(tmp[0]).find(str.lower(keyw)) >= 0:
                        canadd = 1
                    else:
                        canadd = 0
                        break
                else:  # 全路径搜索
                    if keyw == '' or str.lower(tmp[-1]).find(str.lower(keyw)) < 0:
                        canadd = 0
                        break  # 有这句话就是 and 关系。
        #
        # 从这里开始，要正式插入内容了；
        if canadd == 1:  #
            ext = tmp[4]  # 扩展名
            tmp_imag = get_icon_ext(ext)
            # k += 1
            # # 插入节点的分组
            # the_node = ''
            # if var_group_by_folder:
            #     if is_this_folder:
            #         the_node = ''
            #     else:
            #         if item_sub_folder is None:
            #             item_sub_folder = tree_obj.insert('', 'end',
            #                                           text='子文件夹内容',
            #                                           tags=['line1'],  # if k % 2 == 1 else ['line2'],
            #                                           values=(0, '', '', '', '', ''))
            #             tree_obj.item(item_sub_folder, open=True)
            #
            #         the_node = item_sub_folder

            # 开始插入内容，插入位置是『the_node』
            if the_node == '':
                k1 += 1
                k = k1
            else:
                k = k2
            #
            tree_obj.insert(the_node, k,  # k,
                        text='  ' + tmp[0],
                        image=tmp_imag,
                        tags=['line1'] if k % 2 == 1 else ['line2'],
                        values=(k, tmp[0], tmp[1], tmp[2], tmp[3], tmp[-1]))
            k_all += 1
        #
        if True:  # 用于更新进度条
            refresh_unit = int(n_max / 1)
            #
            if k % refresh_unit == 0:  # 刷新
                # refresh_unit=refresh_unit*4
                if flag.flag_inited:
                    p = (90 + 9 * n / n_max)
                    if p > 99: p = 99
                    set_prog_bar(p)
            # tree_obj.update() # 提前刷新，优化用户体验
            # app.str_btm.set('即将完成……')
        else:
            pass
    #
    # 最后再把文件夹放在最后面：
    #
    if var_group_by_folder and len(conf.lst_my_path_long_selected) == 1:
        for itm in lst_sub_items:
            # k1+=1
            if len(tree_obj.get_children(itm)) == 0:
                tree_obj.detach(itm)
            else:
                tree_obj.move(itm, '', 'end')

    print('添加列表项消耗时间：')
    print(time.time() - time0)

    # app.str_btm.set("找到 " + str(k) + " 个结果，用时"+str(time.time()-time0)+"秒")
    # "在"+str(len(dT))+"个项目中找到 " + str(k) + " 个文件，"
    app.str_btm.set("找到 " + str(k_all) + " 个文件")  # "，用时"+str(time.time()-time0)+"秒")
    if flag.flag_inited:
        set_prog_bar(100)
        tree_obj.focus()
    # flag.flag_running=0


def get_folder_short():
    """
    返回左侧列表文件夹名称 (简称)，需要用 get_folder_s2l(tmp) 转化为长路径。
    不考虑子文件夹。
    res= v_folders.get()
    res='（全部）'

    """
    for item in app.tree_lst_folder.selection():
        res = app.tree_lst_folder.item(item, "values")

    # res=app.tree_lst_folder.get(app.tree_lst_folder.curselection())
    try:
        res = res[0]
        if res == '（全部）':
            res = ''
    except:
        res = ''
    # print(res)
    return res


def get_folder_long():
    """
    合并获取短路径和长路径的逻辑。
    返回值是代表文件夹长路径的字符串。
    其中包括了对斜杠的处理。
    """
    if FOLDER_TYPE == 1:
        short_folder = get_folder_short()
        if short_folder == '':
            return short_folder
        else:
            res = get_folder_s2l(short_folder)
            res = str(res).replace('\\', '/')
    #
    elif FOLDER_TYPE == 2:
        res = get_folder_short()
        res = str(res).replace('\\', '/')
    #
    return res


def get_folder_root_node(depth=0):
    """
    获取选中项的根节点 item（文件夹分组）
    输入参数为数字，可以获取指定深度的结点。
    """
    itm = app.tree_lst_folder.selection()[0]
    the_item = itm
    while get_folder_depth(the_item) > depth:
        the_item = app.tree_lst_folder.parent(the_item)
    #
    return (the_item)


def get_folder_group():
    """
    获取分组内的文件夹列表
    """
    lst_child_folders = []
    #
    the_root = app.tree_lst_folder.selection()[0]
    for c in app.tree_lst_folder.get_children(the_root):
        lst_child_folders.append(app.tree_lst_folder.item(c, "values")[-1])
        pass
    return lst_child_folders


def get_folder_group_list():
    """
    获取排序后的文件夹分组列表。这里已经排序完成。
    """
    # 根目录的名称列表
    lst_root_text = list(set(conf.dict_folder_groups.values()))
    # 排序
    lst_root_text = exec_list_sort(lst_root_text)
    if conf.DEFAULT_GROUP_NAME in lst_root_text:  # 默认文件夹分组永远在前
        lst_root_text.remove(conf.DEFAULT_GROUP_NAME)
        lst_root_text = [conf.DEFAULT_GROUP_NAME] + lst_root_text
    return lst_root_text


def get_folder_long_v2():
    """
    树架构下的文件夹列表获取方法。
    这种架构下，文件夹列表的-1列就是长路径名。
    返回值：文件夹完整路径。
    """
    for item in app.tree_lst_folder.selection():
        path_long = app.tree_lst_folder.item(item, "values")[-1]
    return path_long


def get_folder_depth(itm=None):
    """获取文件夹的深度编码"""
    if itm is None:
        item = app.tree_lst_folder.selection()[0]
    else:
        item = itm
    #
    tmp_values = app.tree_lst_folder.item(item, "values")
    if len(tmp_values) <= 1:
        path_depth = 0
    else:
        path_depth = tmp_values[1]
    return int(path_depth)


def get_folder_values_v2(point=False):
    """
    优化架构下的文件夹列表获取方法。
    """
    if point:
        res = app.tree_lst_folder.item(app.last_focus, "values")
    else:
        for item in app.tree_lst_folder.selection():
            res = app.tree_lst_folder.item(item, "values")
    return res


def exec_run(filepath):
    """
    运行文件或路径
    """
    os.startfile(filepath)  # 这个方法好像不太合适，会导致占用。


# 获取当前点击行的值
def exec_tree_file_open(event=None):  # 单击
    """
    打开列表选中项目。
    按理说，兼容多文件。

    """
    # 为了避免短时间三次点击鼠标导致重复打开，增加计时功能；
    if (time.time() - app.file_open_time) < 1:  # 要求至少间隔1秒。
        app.file_open_time = time.time()
        return
    else:
        app.file_open_time = time.time()

    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        item_text = app.tree.item(item, "values")
        print('正在打开文件：')
        tmp_tar = item_text[-1]
        print(tmp_tar)
        try:
            if is_tree_item_enable(item):
                exec_run(tmp_tar)  # 打开这个文件
        except:
            print('打开文件失败')


def is_tree_item_enable(itm):
    """
    用于检查选中项目是否可用（如果是分组，就不可用）
    """
    item_text = app.tree.item(itm, 'values')
    tmp_tar = item_text[-1]
    if tmp_tar == '':
        return 0
    else:
        return 1


def exec_file_duplicate(tar=None):  # 文件原地建立副本
    """
    为文件建立副本
    """
    pass


def exec_tree_file_rename(tar=None):  # 对文件重命名
    """
    重命名tree选中的文件。需要有tree的选中项目。
    每个文件重命名一次，按理说兼容多文件，但是这个命令不应该给多文件执行。
    """
    if len(app.tree.selection()) > 1:
        print('暂不支持多文件重命名')
        return
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        # 获得目标文件
        item_text = app.tree.item(item, "values")
        tmp_full_path = item_text[-1]
        tmp_file_name = get_split_path(tmp_full_path)[-1]  # 文件名
        #
        #
        print('正在重命名：')
        print('路径：', tmp_full_path)
        print('文件名：', tmp_file_name)
        # res = simpledialog.askstring('文件重命名',prompt='请输入新的文件名',initialvalue =tmp_file_name) # 有bug，不能输入#号
        [fname, fename] = os.path.splitext(tmp_file_name)  # 文件名，扩展名，其中扩展名包括点号。
        print(fname, '  ', fename)
        res = show_window_input('文件重命名', body_value='请输入新的文件名', init_value=fname)  # 有bug，不能输入#号
        #
        if res is not None:
            try:
                tmp_new_name = '/'.join(get_split_path(tmp_full_path)[0:-1] + [res + fename])
                print('tmp_new_name=', tmp_new_name)
                # os.rename(tmp_full_path,tmp_new_name)
                final_name = exec_safe_rename(tmp_full_path, tmp_new_name)
                update_main_window(0, fast_mode=True)
                exec_tree_find(final_name)
            except:
                t = tk.messagebox.showerror(title='ERROR', message='重命名失败！文件可能被占用，或者您没有操作权限。')
                # print(t)
                pass


def exec_tree_file_delete(tar=None):
    """
    删除tree选中项对应的文件。
    兼容多文件，但是每个文件要确认一次，可能体验不太好。
    """
    flag_deleted = 0
    if tk.messagebox.askokcancel("删除确认", "要将选中项删除到回收站吗？"):
        #
        for item in app.tree.selection():
            if not is_tree_item_enable(item):
                continue
            # 获取文件全路径
            item_text = app.tree.item(item, "values")
            tmp_full_path = item_text[-1]
            # 再次确认
            if not isfile(tmp_full_path):
                print('并不存在文件：' + str(tmp_full_path))
                #
            else:
                flag_deleted = 1
                try:
                    exec_remove_to_trash(tmp_full_path)
                    #
                    if len(app.tree.selection()) == 1:
                        update_main_window(0)
                except:
                    t = tk.messagebox.showerror(title='ERROR', message='删除失败，文件可能被占用！' + str(tmp_full_path))
                    print('删除失败，文件可能被占用')
                # 刷新

        if len(app.tree.selection()) > 1:
            if flag_deleted:
                update_main_window(0)


def function_for_testing(event=None):  #
    """
    用于调试一些测试性的功能，
    为了避免 event 输入，所以套了一层。

    """
    res = TdInputWindow(app.window, '输入框', 'aaaa', '外部输入')
    print('自制输入框的返回值：')
    print(res)
    # print('进入测试功能')

    pass


def tree_scroll_to_selection(full_path='', the_tree=None, the_bar=None, the_col=None):
    """
    用于将tree滚动到选中项目的位置上；
    """
    #
    #
    n_selected = 0
    n_cnt = 0
    if the_tree is None:
        the_tree = app.tree
    if the_bar is None:
        the_bar = app.bar_tree_v
    if the_col is None:
        the_col = -1
    # the_tree = app.tree
    # the_item = None
    try:
        (b1, b2) = the_bar.get()
    except:
        print(f'查询滚动条位置出现错误')
        print(the_bar.get())
        return -1
    b0 = b2 - b1  # 滚动条长度

    #
    # 从第一行开始，
    def check_node(itm, n, c):
        for itm0 in the_tree.get_children(itm):
            c += 1
            tmp_value = the_tree.item(itm0, "values")
            if tmp_value[the_col] == full_path:
                the_tree.selection_add(itm0)  # 增加选中项目
            if itm0 in the_tree.selection() and n == 0:
                n = c
            if len(the_tree.get_children(itm0)) > 0 and the_tree.item(itm0, 'open'):
                n, c = check_node(itm0, n, c)
        return n, c

    n_selected, n_cnt = check_node(None, n_selected, n_cnt)

    b_top = n_selected / n_cnt - 0.5 * b0
    b_bottom = n_selected / n_cnt + 0.5 * b0

    if b_top <= 0:
        b_top = 0
    elif b_bottom >= 1:
        b_top = 1 - b0

    the_tree.yview_moveto(b_top)
    print("n_selected, n_cnt = ", n_selected, n_cnt)
    print('b_top=', b_top)
    return n_selected, n_cnt


def exec_tree_find(full_path='', need_update=True, the_tree=None, the_bar=None, the_col=None):  #
    """
    用于在 任意 treeview（默认是tree） 里面找到项目，并加高亮。
    输入参数是查找值（完整路径）。
    need_update 代表是否要刷新列表。一般否是要刷新才能保证正确，
    如果是批量查询，可以自己提前刷新，然后取消函数刷新，可以增加速度。
    只支持单项目查找，多个查询需要重复运算。
    如果返回-1，代表没有找到。
    """
    if full_path == '' or full_path is None:
        return -1
    #
    # 默认值
    if the_tree is None:
        the_tree = app.tree
    if the_bar is None:
        the_bar = app.bar_tree_v
    if the_col is None:
        the_col = -1
    #
    # 根据完整路径，找到对应的文件并高亮
    if need_update:
        the_tree.update()  # 必须在定位之前刷新列表，否则定位会错误
    # if False:
    #     tc = the_tree.get_children()
    #     tc_cnt = len(tc)
    #     print('条目数量为：%s' % tc_cnt)
    #     n = 0
    #     print('开始查找高亮的位置')
    #     try:
    #         (b1, b2) = the_bar.get()
    #     except:
    #         print(f'查询滚动条位置出现错误')
    #         print(the_bar.get())
    #         return -1
    #     b0 = b2 - b1
    #     # b0=0
    #     print('b0=')
    #     print(b0)
    #
    #     for i in tc:
    #         tmp = the_tree.item(i, "values")
    #         # print(tmp[the_col])
    #         if tmp[the_col] == full_path:
    #             # the_tree.focus(i) #这个并不能高亮
    #             the_tree.selection_add(i)
    #             # the_tree.selection_add(tc[0])
    #
    #
    #                 print('在第%d处检查到了相应结果' % n)
    #                 print(1953)
    #                 b1 = n / tc_cnt - 0.5 * b0
    #                 b2 = n / tc_cnt + 0.5 * b0
    #                 print((b0, b1, b2))
    #                 if b1 < 0:
    #                     b1 = 0
    #                     b2 = b0
    #                 elif b2 > 1:
    #                     b2 = 1
    #                     b1 = 1 - b0
    #                 print((b1, b2))
    #                 # the_bar.set(b1,b2)
    #                 the_tree.yview_moveto(b1)
    #             return n
    #             break
    #         else:
    #             n += 1
    #     print('居然没找到：')
    #     print(full_path)
    #
    #     return -1
    #     # for i in range()
    # else:
    n_selected, n_cnt = tree_scroll_to_selection(full_path)
    return n_selected


def exec_tree_find_lst(inp_lst):
    """
    传入一个列表。tree高亮。
    输入参数是要查询的内容，必须是列表。
    """
    app.tree.update()
    if type(inp_lst) is not list:
        print('输入参数不是列表！')
        return

    for tmp_final_name in inp_lst:
        tmp_final_name = tmp_final_name.replace('\\', '/')
        print(f'正在定位 {tmp_final_name}')
        exec_tree_find(tmp_final_name, need_update=False)  # 为加标签之后的项目高亮


def tree_open_folder(event=None, VMETHOD=1):
    """
    打开当前文件所在的目录.
    参数VMETHOD=1（默认）是打开文件夹，
    =2 是打开文件夹并选中文件（有点慢）。
    不需要传入路径参数，本函数会自动从tree里面读取。
    """
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        item_text = app.tree.item(item, "values")
        tmp_file = item_text[-1]
        tmp_file = tmp_file.replace('/', '\\')
        #
        if VMETHOD == 1:  # 打开文件夹
            tmp_folder = '/'.join(get_split_path(tmp_file)[0:-1])
            # tmp_folder=item_text[-2]
            print(tmp_folder)
            exec_run(tmp_folder)  # 打开这个文件
        #
        elif VMETHOD == 2:  # 打开文件夹并选中文件。
            # 注意，方法2路径必须是\，而且select,后面不能有空格
            tmp = r'explorer /select,"' + tmp_file + '"'
            print(tmp)
            #
            subprocess.Popen(tmp)
            # subprocess.Popen("'"+tmp+"', shell=True")
            #
            # os.system(tmp)  # 性能极差，不知道哪的原因
            # os.system(tmp)  # 性能极差，不知道哪的原因
            # os.system(r'explorer /select,d:\hello.txt') # 这是打开文件夹并选中文件的方法

    pass


def tree_open_folder_select(event=None):
    tree_open_folder(VMETHOD=2)


def tree_open_current_folder(event=None):
    """
    没有选中文件的时候，打开当前文件夹。
    支持打开子文件夹。
    """
    if len(get_sub_folder_selected()) > 0:
        tmp_path = conf.lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
    elif len(conf.lst_my_path_long_selected) > 1:
        print('输入多个文件夹，即将打开第一个')
        tmp_path = conf.lst_my_path_long_selected[0]
    else:
        tmp_path = conf.lst_my_path_long_selected[0]
    try:
        exec_run(tmp_path)
    except:
        t = tk.messagebox.showerror(title='ERROR', message='打开文件夹失败！')


def exec_folder_from_menu(event=None):
    """通过菜单添加关注的文件夹"""
    # folder_path = get_folder_long_v2()
    folder_path = app.tree_lst_folder.item(app.last_focus,"values")[-1]
    exec_folder_add([folder_path])


def exec_folder_add_from_sub(event=None):
    """
    通过子文件夹的方式添加关注文件夹
    """
    try:
        if len(get_sub_folder_selected()) > 0:
            tmp_path = conf.lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
            exec_folder_add([tmp_path])
    except:
        print('请检查 exec_folder_add_from_sub 函数')


def exec_sub_folder_new(event=None):
    """
    新建子文件夹，也就是新建文件夹的意思。目前正在使用。
    """
    # 获取当前文件夹
    if True:
        cur_folder = app.tree_lst_folder.item(app.last_focus,"values")[-1]
    else:
        if len(conf.lst_my_path_long_selected) == 1:
            cur_folder = conf.lst_my_path_long_selected[0]
        else:
            t = tk.messagebox.showerror(title='ERROR', message='未选中唯一文件夹')
            return False

    # 获取名称
    new_folder_name = ''
    lp = 1
    #
    while lp:
        path = show_window_input('新建文件夹', '请输入文件夹名称', new_folder_name)
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

                print(tmp_path + ' 创建成功')
                lp = 0
                #
                # 创建之后刷新一次
                update_sub_folder_list(refresh=False)
                update_main_window(0, fast_mode=True)
                # update_main_window(reload_setting=2)
                if FOLDER_TYPE == 2:
                    update_folder_list()
                return True
            except:
                t = tk.messagebox.showerror(title='ERROR', message='文件夹创建失败，当前位置可能不允许创建文件夹')
                lp = 0
        else:
            # 如果目录存在则不创建，并提示目录已存在
            t = tk.messagebox.showerror(title='ERROR', message=(tmp_path + ' 目录已存在，请重新设定文件夹名称'))
            # return False


def exec_folder_del(event=None):
    """
    将文件夹删掉（移动到回收站）
    """
    if True:
        fd = app.tree_lst_folder.item(app.last_focus,"values")[-1]
        folder_base,folder_name = os.path.split(fd)
    else:
        fd = get_folder_long_v2()
        fd = fd.replace('\\', '/')
    if tk.messagebox.askokcancel("删除确认", "要将文件夹【"+str(folder_name)+"】删除到回收站吗？"):
        # 删除操作
        exec_remove_to_trash(fd)
        update_folder_list()
        # 清空文件剪切板
        exec_tree_file_pick_nothing()


def exec_folder_rename(event=None):
    """
    文件夹重命名
    """
    if True:
        old_path = app.tree_lst_folder.item(app.last_focus,"values")[-1]
        old_base,old_folder = os.path.split(old_path)
    else:
        tmp_i = app.tree_lst_folder.selection()[0]
        old_path = app.tree_lst_folder.item(tmp_i, "values")[-1]  # 完整路径
        old_base = app.tree_lst_folder.item(tmp_i, "values")[0]
        old_folder = app.tree_lst_folder.item(tmp_i, "text")
    # old_folder = str.replace(old_path,old_base,'')
    #
    # 新文件夹名称
    new_folder = show_window_input('重命名文件夹', '请输入文件夹名称', old_folder)
    if new_folder is None:
        return
    new_path = old_base + '/' + new_folder
    #
    # 新文件夹名称是否存在
    isExists = os.path.exists(new_path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        try:
            os.rename(old_path, new_path)
            print(new_path + ' 创建成功')
            # 刷新一次
            update_folder_list()
            return True
        except:
            t = tk.messagebox.showerror(title='ERROR',
                                        message='文件夹重命名失败，可能是有内部文件正在被访问，或没有操作权限。')
    else:
        # 如果目录存在则不创建，并提示目录已存在
        t = tk.messagebox.showerror(title='ERROR', message=(new_path + ' 目录已存在，请输入另外的名称。'))
        return False


def exec_sub_folder_rename(event=None):
    """
    子文件夹重命名
    """
    # 确定旧文件夹名称
    # 获取当前文件夹

    old_path = app.tree_lst_folder.item(app.last_focus,"values")[-1] # 不带斜线
    _, old_folder = os.path.split(old_path)

    # if len(get_sub_folder_selected()) > 0:
    #     old_folder = get_sub_folder_selected()
    #     old_path = conf.lst_my_path_long_selected[0] + '/' + old_folder
    #
    # 新文件夹名称
    new_folder = show_window_input('重命名文件夹', '请输入文件夹名称', old_folder)
    if new_folder is None:
        return
    new_path = conf.lst_my_path_long_selected[0] + '/' + new_folder
    #
    # 新文件夹名称是否存在
    isExists = os.path.exists(new_path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        try:
            os.rename(old_path, new_path)
            print(new_path + ' 创建成功')
            # 刷新一次
            update_sub_folder_list(refresh=None)
            exec_tree_find(new_folder, True, app.tree_lst_sub_folder, app.bar_sub_folder_v, 0)
            update_main_window(0, fast_mode=True)
            return True
        except:
            t = tk.messagebox.showerror(title='ERROR',
                                        message='文件夹重命名失败，可能是有内部文件正在被访问，或没有操作权限。')
    else:
        # 如果目录存在则不创建，并提示目录已存在
        t = tk.messagebox.showerror(title='ERROR', message=(new_path + ' 目录已存在，请输入另外的名称。'))
        return False


def input_new_tag(event=None, tag_name=None):
    """
    输入新的标签，为选中项添加标签。
    tag_name 是输入的标签。
    """
    # new_name=''
    if tag_name is None:  # 默认从输入框获取
        new_tag = app.v_inp.get()
        new_tag = str(new_tag).strip()
    else:
        new_tag = tag_name

    if new_tag is None or new_tag == '':
        print("取消新标签")
        return

    taged_files = []
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        item_text = app.tree.item(item, "values")
        tmp_full_name = item_text[-1]
        # tmp_file_name = get_file_part(tmp_full_name)['ffname'] # 没有用到

        # new_tag = tk.simpledialog.askstring(title="添加标签", prompt="请输入新的标签")#, initialvalue=tmp)

        if new_tag == None or new_tag == '':
            print("取消新标签")
        else:
            taged_files.append(exec_file_add_tag(tmp_full_name, new_tag))
            # print(new_name)
    if len(app.tree.selection()) > 1:  # 多文件的只在最后刷新。
        # (b1, b2) = bar_tree_v.get()
        update_main_window(0)
        exec_tree_find_lst(taged_files)
        # for i in taged_files:
        # exec_tree_find(i)

        # exec_tree_find(taged_files[-1]) 
        # app.tree.yview_moveto(b1)


def exec_tree_add_tag_via_dialog(event=None):
    """
    以输入框的方式添加标签。

    """
    # 没有选中项的时候，直接跳过
    if len(app.tree.selection()) == 0:
        t = tk.messagebox.showerror(title='错误', message='添加标签之前，请先选中至少一个文件。')
        print('没有选中任何项目')
        return

    new_tag = show_window_input('添加标签', '请输入标签', '')
    if new_tag is None:
        return
    try:
        new_tag = str(new_tag).strip()
    except:
        pass
    input_new_tag(tag_name=new_tag)


def update_one_of_dicT(filename):
    """
    更新dicT中的一项，
    包括对文件名斜杠的处理。


    :return:
    """
    global dicT
    filename = filename.replace('\\', '/')
    tmp = get_file_part(filename)
    tmp_v = (str(tmp['fname_0']),
             tmp['ftags'],
             str(tmp['file_mdf_time']),
             tmp['fsize'],
             tmp['fename'],
             str(tmp['full_path']))
    dicT[filename] = tmp_v


def exec_file_add_tag(filename, tag0, need_update=True):
    """
    增加标签
    """
    filename = filename.replace('\\', '/')
    tmp_final_name = filename
    ntfs_error = False
    #
    # 增加NTFS流的标签解析
    if TAG_METHOD == 'FILE_STREAM' and not os.path.splitext(filename)[1] in conf.EXP_EXTS:
        # 先看有没有这个标签
        tmp = get_file_part(filename)
        tags_old = tmp['ftags']
        if tag0 in tags_old:  # 如果已经有的话，直接忽略
            pass
        else:
            #
            # 增加标签
            tags_old.append(tag0)
            tags_old.sort()
            try:
                with open(filename + ":tags", "w", encoding="utf8") as f:
                    f.writelines(list(map(lambda x: x + "\n", tags_old)))
            except:
                ntfs_error = True
            #
            # 更新缓存
            update_one_of_dicT(filename)
            # global dicT
            # tmp_v = (str(tmp['fname_0']),
            #          tags_old,
            #          str(tmp['file_mdf_time']),
            #          tmp['fsize'],
            #          tmp['fename'],
            #          str(tmp['full_path']))
            # dicT[filename] = tmp_v
        # return tmp_final_name

    if TAG_METHOD != 'FILE_STREAM' or ntfs_error or os.path.splitext(filename)[1] in conf.EXP_EXTS:
        tag_list = tag0.split(conf.V_SEP)
        tag_old = get_file_part(filename)['ftags']  # 已有标签
        file_old = get_file_part(filename)['ffname']  # 原始的文件名
        path_old = get_file_part(filename)['fpath']  # 路径
        [fname, fename] = os.path.splitext(file_old)  # 文件名前半部分，扩展名

        old_n = path_old + '/' + fname + fename
        new_n = old_n
        for i in tag_list:
            if i not in tag_old:
                new_n = path_old + os.sep + fname + conf.V_SEP + i + fename
                print(old_n)
                print(new_n)
                try:
                    # os.rename(old_n,new_n)
                    tmp_final_name = exec_safe_rename(old_n, new_n)
                    old_n = new_n  # 多标签时避免重命名错误
                except:
                    tk.messagebox.showerror(title='ERROR', message='为文件添加标签失败！')
                    print('为文件添加标签失败')
                    pass
    # 刷新并选中
    if len(app.tree.selection()) == 1 and need_update:
        update_main_window(0, fast_mode=True)  # 此处可以优化，避免完全重载
        try:
            tmp_final_name = tmp_final_name.replace('\\', '/')
            print('添加标签完成，正在定位%s' % (tmp_final_name))
            exec_tree_find(tmp_final_name)  # 为加标签之后的项目高亮
        except:
            pass
    return tmp_final_name


# def file_add_star(event=None):
#     '''
#     加收藏。
#     目前是为文件增加 TAG_STAR 对应的值。
#     通常是 @PIN。
#     // 本函数目前作废，没有启用。
#     '''
#     TAG_STAR='@PIN'
#     for item in app.tree.selection():
#         item_text = app.tree.item(item, "values")
#         tmp_full_name = item_text[-1]
#     exec_file_add_tag(tmp_full_name,TAG_STAR)


def exec_fast_add_tag(tag):
    """
    以右键的方式快速为文件加收藏。
    目前是为文件增加 TAG_STAR 对应的值。
    """
    TAG_STAR = tag
    taged_files = []
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        item_text = app.tree.item(item, "values")
        tmp_full_name = item_text[-1]
        taged_files.append(exec_file_add_tag(tmp_full_name, TAG_STAR))
    if len(app.tree.selection()) > 1:
        # (b1, b2) = bar_tree_v.get()
        update_main_window(0)
        # app.tree.yview_moveto(b1)
        for file_1 in taged_files:
            exec_tree_find(file_1)
        # exec_tree_find(taged_files[-1])


def exec_clear_entry(tar):
    """
    前端函数，将输入框清空。
    必须要指定要清空的输入框对象。
    """
    try:
        tar.delete(0, len(tar.get()))
    except:
        pass
    pass


def exec_clear_search_items(event=None):
    update_main_window(666, fast_mode=True)


def update_main_window(event=None, reload_setting=False, fast_mode=False):
    """
    刷新。
    切换目录之后自动执行此功能。

    输入参数0的话，保留子文件夹、搜索框、标签框。
    输入参数1，保留子文件夹、标签框，(清除搜索框)。推荐使用参数1；
    其余参数，(清空子文件夹、标签框、搜索框)。

    """
    global lst_files_to_go, dT
    global lst_tags, lst_sub_path

    app.update_readme()
    # if conf.TREE_SUB_SHOW =='tag' and event is None:
    #     event=1

    # 原始值
    old_tag = get_search_tag_selected()
    old_sub_folder = get_sub_folder_selected()

    if reload_setting == True:
        # 按需加载设置参数
        conf.exec_json_file_load(load_folders=False)

    tmp_sub_folder = get_sub_folder_selected()
    #
    if len(tmp_sub_folder) > 0:
        path_lst = [conf.lst_my_path_long_selected[0] + '/' + tmp_sub_folder]
    else:
        path_lst = conf.lst_my_path_long_selected.copy()

    if event == 0:
        # 什么都不做
        pass
    elif event == 1:
        '''
        保留子文件夹；保留标签；
        清空搜索框
        '''
        # tmp_sub_folder=get_sub_folder_selected()
        exec_clear_entry(app.v_search)
    else:
        '''
        清空搜索框；
        标签留空；
        '''
        exec_clear_entry(app.v_search)
        set_search_tag_selected(0)
        if conf.TREE_SUB_SHOW == 'tag':  # 在 tag 模式，需要连子文件夹也刷新
            set_sub_folder_selected(0)
        print('已经全部清空')

        # app.v_inp.delete(0,len(app.v_inp.get()))
    # app.v_inp.delete(0,len(app.v_inp.get()))

    # on_folder_choose(refresh=0)
    print('—— 刷新核心过程 start ———')
    #
    if conf.TREE_SUB_SHOW == 'tag':
        path_lst = conf.lst_my_path_long_selected
    elif conf.TREE_SUB_SHOW == 'sub_folder':
        path_lst = conf.lst_my_path_long_selected

    if len(tmp_sub_folder) > 0:  # 如果子文件夹选中，则不刷新子文件夹
        # 注意，这里修改了 lst_files_to_go 所以会导致全局的文件列表出现错乱。
        lst_files_to_go = get_data(path_lst, 0)
    else:
        lst_files_to_go = get_data(path_lst)
    print(f'\n ———— 当前的数据来自文件夹：{path_lst}\n')
    # lst_files_to_go = get_data(conf.lst_my_path_long_selected)
    #
    (dT, lst_tags) = get_dt(FAST_MODE=fast_mode)
    # if event in [0]: 
    #     (dT, lst_tags) = get_dt(FAST_MODE=fast_mode)
    # else:
    #     (dT, lst_tags) = get_dt() # 此处有待商榷
    #
    print('—— 刷新核心过程 end ———')
    # exec_tree_clear(app.tree)
    #
    # 恢复子文件夹选项（即将作废）
    if event in [0, 1] and conf.TREE_SUB_SHOW == 'sub_folder':
        try:  # 用一种【不太优雅】，但是暴力有效的方法修复了bug……
            if len(tmp_sub_folder) > 0:
                tmp_n = lst_sub_path.index(tmp_sub_folder)
                set_sub_folder_selected(tmp_n + 1)
                print('子文件夹修复完毕')
        except:
            print('进入这个分支')
            app.v_sub_folders.current(0)
    #
    # 恢复标签
    app.window.update()
    if conf.TREE_SUB_SHOW == 'tag':
        if event in [0, 1]:  # 【此处从逻辑上好像有bug】
            tags_ = update_tags_in_sub_folder(conf.lst_my_path_long_selected[0] + '/' + old_sub_folder, 1)
    elif conf.TREE_SUB_SHOW == 'sub_folder':
        if len(conf.lst_my_path_long_selected) > 1:
            # tags_=update_tags_in_sub_folder(conf.lst_my_path_long_selected)
            pass
        else:
            tags_ = update_tags_in_sub_folder(conf.lst_my_path_long_selected[0] + '/' + old_sub_folder, 1)
        if event in [0, 1]:
            set_search_tag_selected(old_tag)
    exec_search()  # 目的是按照刷新后的筛选条件对内容进行筛选
    #

    try:
        if event in [0, 1] and conf.TREE_SUB_SHOW == 'tag':
            '''
            if old_sub_folder =='':
                tags_=update_tags_in_sub_folder(conf.lst_my_path_long_selected[0],1)
            else:
                tags_=update_tags_in_sub_folder(conf.lst_my_path_long_selected[0]+'/'+ tmp_sub_folder,1)
            '''
            pass
        else:
            set_search_tag_values(lst_tags)  # 这个导致总是刷新全部标签
    except Exception as e:
        print(e)

    # if not (event  in [0,1] and conf.TREE_SUB_SHOW =='tag'):
    #     set_search_tag_values(lst_tags) # 这个导致总是刷新全部标签

    app.v_inp['value'] = lst_tags  # 这句没啥用吧

    try:
        set_prog_bar(100)
    except:
        pass
    #
    # 刷新之后，令文件列表获得焦点(貌似无效)
    # app.tree.focus()


def show_online_help(event=None):
    '''
    提供帮助文件。
    目前的方式主要是跳转到在线帮助文件。以后考虑到内网打不开网页，需要增加一个离线的方面。
    '''
    exec_run(cst.URL_HELP)


def show_online_advice(event=None):
    """
    在线反馈
    """
    exec_run(cst.URL_ADV)


def show_online_check_update(event=None):
    """
    在线反馈
    """
    exec_run(cst.URL_CHK_UPDATE)


def show_window_closing(need_asking=True):
    """
    退出程序。
    """
    if need_asking:
        if tk.messagebox.askokcancel("退出", "真的要退出吗"):
            app.window.destroy()
    else:
        app.window.destroy()


# 搜索框

def get_folder_s2l(folder_short_name):
    '''
    文件夹短路径转长路径。
    '''
    return conf.dict_path[folder_short_name]
    pass


def on_folder_choose(event=None, refresh=1, sub_folder=None):  # 点击新的文件夹之后
    """
    选择左侧文件夹后启动。\n
    参数：refresh：默认是1，代表了运行之后是否刷新列表。\n
    sub_folder：输入完整路径，但是没有被任何函数调用过
    """
    # 
    # if conf.TREE_SUB_SHOW=='tag':
    #     pass
    # elif conf.TREE_SUB_SHOW=='sub_folder': # 如果是子文件夹模式，先清空子文件夹；
    #     exec_tree_clear(app.tree_lst_sub_folder) # 新增语句
    #     pass
    update_current_folder_list() # 2022年10月13日新增，点击的时候刷新

    exec_tree_folder_mouse_highlight(event)  # 添加这句话，保证当前左键点击项目获得高亮

    #
    flag.flag_root_folder = 1
    # if flag.flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
    # return
    print('调用 on_folder_choose 函数')
    #
    # 缓存之前选中的文件夹；
    #
    if sub_folder is None:  # 如果没有指定输入参数
        lst_path_ori = conf.lst_my_path_long_selected.copy()
    else:
        lst_path_ori = []
    #
    # 加载新选中的文件夹； 
    #
    folder_short = get_folder_short()  # 获取当前选中的文件夹；
    need_disabled = 0
    #
    if get_folder_depth() == 0:  # 如果选中的文件夹是0级；
        # conf.lst_my_path_long_selected = conf.lst_my_path_long.copy()
        conf.lst_my_path_long_selected = get_folder_group()
        # 设置按钮为无效
        need_disabled = 1
        app.this_folder.configure(state=tk.DISABLED)
        # 折叠子文件夹
        for folder_0 in app.tree_lst_folder.get_children():
            folder_1 = app.tree_lst_folder.get_children(folder_0)
            for itm in folder_1:
                app.tree_lst_folder.item(itm, open=False)  # 一级文件夹全部关闭
    #
    # 如果是1级以上文件夹；
    else:
        app.this_folder.configure(state=tk.NORMAL)
        #
        folder_long = get_folder_long_v2()
        #
        # 如果选中1级文件夹，就折叠其他所有一级文件夹，并展开当前选中的文件夹：
        # vls=get_folder_values_v2()
        # print('vls=',vls)
        folder_type = get_folder_depth()
        #
        if folder_type >= 1:
            #
            # 折叠其他root下的一级文件夹
            my_root = get_folder_root_node()
            for folder_0 in app.tree_lst_folder.get_children():
                if app.tree_lst_folder.item(folder_0, "text") == app.tree_lst_folder.item(my_root, "text"):  # 跳过当前的跟文件夹
                    continue
                folder_1 = app.tree_lst_folder.get_children(folder_0)
                for itm in folder_1:
                    app.tree_lst_folder.item(itm, open=False)  # 一级文件夹全部关闭
            #
            for itm in app.tree_lst_folder.selection():
                folder_0 = app.tree_lst_folder.parent(itm)  # 选中项父节点
                folder_1 = app.tree_lst_folder.get_children(folder_0)  # 选中项同级节点
            #
            # 折叠本root下的同级文件夹
            for itm in folder_1:
                app.tree_lst_folder.item(itm, open=False)  # 其余所有非选中项，折叠
            #
            # 展开子文件夹
            for itm in app.tree_lst_folder.selection():
                app.tree_lst_folder.item(itm, open=True)  # 选中项展开
                #
                folder_2 = app.tree_lst_folder.get_children(itm)
                for itm2 in folder_2:
                    app.tree_lst_folder.item(itm2, open=False)  # 选中项的子文件夹折叠
        #
        print('folder_long=', folder_long)
        conf.lst_my_path_long_selected = [folder_long]
        # 设置按钮有效
        need_disabled = 0
    # 
    # 调整按钮和控件的可用性：
    if need_disabled:
        app.bt_new.configure(state=tk.DISABLED)
        app.bt_readme.configure(state=tk.DISABLED)
        app.bt_folder_drop.configure(state=tk.DISABLED)
        app.v_sub_folders.current(0)
        app.v_sub_folders.configure(state=tk.DISABLED)
        app.folder_layers.configure(state=tk.DISABLED)
    else:
        app.bt_new.configure(state=tk.NORMAL)
        app.bt_readme.configure(state=tk.NORMAL)
        app.bt_folder_drop.configure(state=tk.NORMAL)
        app.v_sub_folders.configure(state='readonly')
        app.folder_layers.configure(state='readonly')
    #
    # 如果前后的选项没有变化的话，就不刷新文件夹列表
    #
    if lst_path_ori == conf.lst_my_path_long_selected:  # 如果选项没变化
        print('选项没有变化')
        print(lst_path_ori)
        pass
    else:  # 选项发生变化：
        if conf.TREE_SUB_SHOW == 'sub_folder':
            exec_tree_clear(app.tree_lst_sub_folder)  # 新增语句
        if refresh:
            # update_main_window(conf.lst_my_path_long_selected)
            update_main_window(CLEAR_AFTER_CHANGE_FOLDER, fast_mode=True)
        app.tree.yview_moveto(0)

    # flag.flag_running=0 # 标记为没有任务
    flag.flag_root_folder = 0
    print('on_folder_choose 函数结束')
    # update_current_folder_list()  # 2022年10月13日新增，点击的时候刷新


def on_folder_choose_v2(event=None, refresh=1, sub_folder=None):  # 点击新的文件夹之后
    """
    选择左侧文件夹后启动。
    注意，这个V2函数并没有启用。
    """
    #
    flag.flag_root_folder = 1
    # if flag.flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
    # return
    print('调用 on_folder_choose 函数')
    if sub_folder is None:
        lst_path_ori = conf.lst_my_path_long_selected.copy()
    else:
        lst_path_ori = []

    tmp = get_folder_short()
    if tmp == '':
        conf.lst_my_path_long_selected = conf.lst_my_path_long.copy()
        # 设置按钮为无效
        app.bt_new.configure(state=tk.DISABLED)
        app.bt_readme.configure(state=tk.DISABLED)
        app.bt_folder_drop.configure(state=tk.DISABLED)
        app.v_sub_folders.current(0)
        app.v_sub_folders.configure(state=tk.DISABLED)
        app.folder_layers.configure(state=tk.DISABLED)

    elif sub_folder is not None:
        tmp = sub_folder
        conf.lst_my_path_long_selected = [tmp]
        # 设置按钮有效
        app.bt_new.configure(state=tk.NORMAL)
        app.bt_readme.configure(state=tk.NORMAL)
        app.bt_folder_drop.configure(state=tk.NORMAL)
        app.v_sub_folders.configure(state='readonly')
        app.folder_layers.configure(state='readonly')
        pass
    else:
        tmp = get_folder_s2l(tmp)  # 将显示值转换为实际值
        conf.lst_my_path_long_selected = [tmp]
        # 设置按钮有效
        app.bt_new.configure(state=tk.NORMAL)
        app.bt_readme.configure(state=tk.NORMAL)
        app.bt_folder_drop.configure(state=tk.NORMAL)
        app.v_sub_folders.configure(state='readonly')
        app.folder_layers.configure(state='readonly')

    if not lst_path_ori == conf.lst_my_path_long_selected:  # 如果前后的选项没有变化的话，就不刷新文件夹列表
        if refresh == 1:
            # update_main_window(conf.lst_my_path_long_selected)
            update_main_window(CLEAR_AFTER_CHANGE_FOLDER)
        app.tree.yview_moveto(0)

    # flag.flag_running=0 # 标记为没有任务
    flag.flag_root_folder = 0
    print('on_folder_choose 函数结束')


def X_sub_folder_choose_not_used(event=None):
    '''
    还没弄完。功能没有被启用。
    '''
    global lst_sub_path
    if get_sub_folder_selected() == '':
        on_folder_choose()

    print('sub处理前')
    print('lst_sub_path=', lst_sub_path)
    print('conf.lst_my_path_long_selected=', conf.lst_my_path_long_selected)
    tmp_lst_sub_path = lst_sub_path.copy()
    tmp_lst_my_path = conf.lst_my_path_long_selected.copy()

    tmp_path = conf.lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
    tmp_folder = tmp_path

    on_folder_choose(sub_folder=tmp_folder)
    conf.lst_my_path_long_selected = tmp_lst_my_path.copy()
    tmp_lst_sub_path.sort()
    app.v_sub_folders['value'] = [''] + tmp_lst_sub_path  # 强制修改子文件夹列表，但这样写不太好
    lst_sub_path = tmp_lst_sub_path.copy()
    print('sub处理后')
    print(lst_sub_path)
    print(conf.lst_my_path_long_selected)
    # app.v_sub_folders.current(0)


def exec_search(event=None):
    '''
    选择标签之后、选择子文件夹后、输入搜索词按回车后触发。
    纯前端函数。
    清空tree，并按照dT为tree增加行。
    '''
    if conf.TREE_SUB_SHOW == 'sub_folder':
        app.v_tag.configure(state=tk.DISABLED)
    exec_tree_clear(app.tree)
    # exec_tree_add_items(app.tree,dT,tag=tmp_tag)
    # if flag.flag_sub_folders_changed == 1:
    # get_data(get_sub_folder_selected())
    # (dT, lst_tags) =get_dt()
    exec_tree_add_items(app.tree, dT)
    app.tree.update()
    if conf.TREE_SUB_SHOW == 'sub_folder':
        app.v_tag.configure(state='readonly')


def on_sub_folders_choose(event=None):
    '''
    切换子文件夹后执行
    '''
    # 如果正在加载中就直接停止
    if conf.TREE_SUB_SHOW == 'tag':  # 运行期间，不允许切换子文件夹
        app.v_sub_folders.configure(state=tk.DISABLED)
    flag.flag_sub_folders_changed = 1
    # 这里需要刷新DT之后再进入
    exec_search()

    flag.flag_sub_folders_changed = 0
    if conf.TREE_SUB_SHOW == 'tag':
        app.v_sub_folders.configure(state='readonly')  # 此方法有效
        # update_main_window(CLEAR_AFTER_CHANGE_FOLDER)
    elif conf.TREE_SUB_SHOW == 'sub_folder':  # 子文件夹模式切换的时候，清空标签
        set_search_tag_selected(0)


# %%


def show_window_setting():  #
    """
    设置窗口
    """
    #
    dict_file_drag = {"复制": "copy", "移动": "move", "每次询问": "ask"}
    dict_window_mode = {"标签模式": "tag", "子文件夹模式": "sub_folder"}
    dict_tag_mode = {"包含匹配": 1, "严格全字匹配": 0}
    dict_yes_no = {"是": 1, "否": 0}

    def setting_yes(event=None):
        '''
        点击确定之后，使参数生效
        '''
        # 获得新参数
        need_reboot = False
        # 先处理要重启的：
        #
        if dict_window_mode[v_inp_mode.get()] != conf.TREE_SUB_SHOW \
                or dict_yes_no[v_last_folder_as_tag.get()] != conf.FOLDER_AS_TAG:
            if tk.messagebox.askokcancel("请确认", "部分设置需要重启才能生效。确定要保存设置并【关闭程序】吗？"):
                need_reboot = True
            else:
                return
        #
        conf.NOTE_EXT = v_inp_note_type.get()
        conf.set_json_options('note_ext', conf.NOTE_EXT, need_write=False)
        #
        conf.V_FOLDERS = v_inp_folder_depth.get()
        conf.set_json_options('vfolders', conf.V_FOLDERS, need_write=False)
        #
        conf.V_SEP = v_inp_sep.get()
        conf.set_json_options('sep', conf.V_SEP, need_write=False)
        #
        conf.FILE_DRAG_MOVE = dict_file_drag[v_inp_drag_type.get()]
        conf.set_json_options('file_drag_enter', conf.FILE_DRAG_MOVE, need_write=False)
        #
        conf.TREE_SUB_SHOW = dict_window_mode[v_inp_mode.get()]
        conf.set_json_options('TREE_SUB_SHOW', conf.TREE_SUB_SHOW)
        #
        conf.FOLDER_AS_TAG = dict_yes_no[v_last_folder_as_tag.get()]
        conf.set_json_options('FOLDER_AS_TAG', conf.FOLDER_AS_TAG)
        #
        conf.TAG_EASY = dict_tag_mode[v_tag_easy.get()]
        conf.set_json_options('TAG_EASY', conf.TAG_EASY)
        #
        # 关闭窗口
        form_setting.destroy()
        # 然后刷新文件列表
        if need_reboot:
            app.window.destroy()
        else:
            update_main_window(None, reload_setting=True)
        pass

    def add_combo():
        pass

    form_setting = tk.Toplevel(app.window)
    form_setting.title('设置')
    form_setting.resizable(0, 0)  # 限制尺寸
    form_setting.transient(app.window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
    form_setting.grab_set()
    screenwidth = conf.SCREEN_WIDTH
    screenheight = conf.SCREEN_HEIGHT
    w_width = int(500*conf.ui_ratio)  # int(screenwidth*0.8)
    w_height = int(400*conf.ui_ratio)  # int(screenheight*0.8)
    # 主窗口中央：
    x_pos = app.window.winfo_x() + (app.window.winfo_width() - w_width) / 2
    y_pos = app.window.winfo_y() + (app.window.winfo_height() - w_height) / 2
    # x_pos = (screenwidth - w_width) / 2
    # y_pos = (screenheight - w_height) / 2
    form_setting.geometry('%dx%d+%d+%d' % (w_width, w_height, x_pos, y_pos))
    form_setting.deiconify()
    form_setting.lift()
    form_setting.focus_force()
    form_setting.iconbitmap(LOGO_PATH)  # 左上角图标
    # v2sep=tk.StringVar()
    # v2sep.set(conf.V_SEP)

    # v2sep=conf.V_SEP
    frame_setting2 = ttk.Frame(form_setting, width=800)
    frame_setting2.pack(side=tk.BOTTOM, expand=0, fill=tk.X)
    frame_setting2.columnconfigure(0, weight=1)
    frame_setting2.columnconfigure(1, weight=1)
    #
    # 设置主要框架
    frame_setting1 = ttk.Frame(form_setting, padding=(0, 10, 0, 0))
    frame_setting1.pack(expand=1, fill=tk.BOTH)
    frame_setting1.columnconfigure(0, weight=1)
    frame_setting1.columnconfigure(1, weight=1)

    # frame_setting2.grid_configure()

    lable_set_sep = ttk.Label(frame_setting1, text='标签分隔符')
    lable_set_sep.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

    v_inp_sep = ttk.Entry(frame_setting1, width=16, text=conf.V_SEP)
    exec_clear_entry(v_inp_sep)
    v_inp_sep.insert(0, conf.V_SEP)
    v_inp_sep.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

    lable_set_folder_depth = ttk.Label(frame_setting1, text='识别为标签的文件夹层数')
    lable_set_folder_depth.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

    v_inp_folder_depth = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    lst_folder_depth = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
    v_inp_folder_depth['values'] = lst_folder_depth
    v_inp_folder_depth['state'] = 'readonly'
    tmp_n = lst_folder_depth.index(str(conf.V_FOLDERS))
    v_inp_folder_depth.current(tmp_n)
    v_inp_folder_depth.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

    nr = 2
    #
    # 是否将最后的目录视为标签
    nr += 1
    lable_ = ttk.Label(frame_setting1, text='将最后一层文件夹作为标签 *')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_last_folder_as_tag = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    v_last_folder_as_tag['values'] = list(dict_yes_no.keys())
    v_last_folder_as_tag['state'] = 'readonly'
    v_last_folder_as_tag.current(0)
    tmp_list = list(dict_yes_no.values())
    print(tmp_list)
    tmp_n = tmp_list.index(conf.FOLDER_AS_TAG)
    v_last_folder_as_tag.current(tmp_n)
    v_last_folder_as_tag.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 笔记类型

    nr += 1
    lable_set_note_type = ttk.Label(frame_setting1, text='笔记类型')
    lable_set_note_type.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)

    v_inp_note_type = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    v_inp_note_type['values'] = conf.NOTE_EXT_LIST
    v_inp_note_type['state'] = 'readonly'
    v_inp_note_type.current(0)
    tmp_n = conf.NOTE_EXT_LIST.index(conf.NOTE_EXT)
    v_inp_note_type.current(tmp_n)
    v_inp_note_type.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 拖动是移动还是复制
    nr += 1
    # lable_drag_type
    lable_ = ttk.Label(frame_setting1, text='拖拽添加文件的操作')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_inp_drag_type = ttk.Combobox(frame_setting1, width=16)
    the_combo = v_inp_drag_type
    the_dict = dict_file_drag
    the_val = conf.FILE_DRAG_MOVE
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
    lable_ = ttk.Label(frame_setting1, text='标签搜索模式')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_tag_easy = ttk.Combobox(frame_setting1, width=16)
    the_combo = v_tag_easy
    the_dict = dict_tag_mode
    the_val = conf.TAG_EASY
    #
    the_combo['values'] = list(the_dict.keys())
    the_combo['state'] = 'readonly'
    the_combo.current(0)
    tmp_list = list(the_dict.values())
    tmp_n = tmp_list.index(the_val)
    the_combo.current(tmp_n)
    the_combo.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 布局是标签模式还是子文件夹模式
    nr += 1
    lable_ = tk.Label(frame_setting1, text='显示模式 *')
    if FOLDER_TYPE == 1:
        lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_inp_mode = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    v_inp_mode['values'] = list(dict_window_mode.keys())
    v_inp_mode['state'] = 'readonly'
    v_inp_mode.current(0)
    tmp_list = list(dict_window_mode.values())
    print(tmp_list)
    tmp_n = tmp_list.index(conf.TREE_SUB_SHOW)
    v_inp_mode.current(tmp_n)
    if FOLDER_TYPE == 1:
        v_inp_mode.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 布局是标签模式还是子文件夹模式
    nr += 1
    lable_ = ttk.Label(frame_setting1, text='（注意：标*的项目需要重启生效）')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)

    # 下面的设置区域
    nr = 100
    bt_setting_yes = ttk.Button(frame_setting2, text='确定', command=setting_yes)
    bt_setting_yes.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.EW)
    # bt_setting_yes.pack(side=tk.LEFT,expand=0,fill=tk.X)

    bt_setting_cancel = ttk.Button(frame_setting2, text='取消', command=form_setting.destroy)
    bt_setting_cancel.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)
    # bt_setting_cancel.pack(side=tk.LEFT,expand=0,fill=tk.X)

    # app.window.wait_window(form_setting)


def exec_folder_add_click(event=None):  #
    """
    通过点击的方式，添加新的目录
    """
    res = filedialog.askdirectory()  # 选择目录，返回目录名
    res_lst = [res]
    print(res)
    if res == '':
        print('取消添加文件夹')
    else:
        exec_folder_add(res_lst)


def exec_folder_add_drag(files):  #
    """
    通过拖拽的方式，添加目录。
    """
    filenames = list()  # 可以得到文件路径编码, 可以看到实际上就是个列表。
    folders = []
    # print(files)
    for item in files:
        item = item.decode('gbk')  # 此处可能存在编码错误，而且，为啥要编码？？
        # item=item.replace('\xa0',' ').decode('gbk')
        if isdir(item):
            folders.append(item)
        elif isfile(item):
            filenames.append(item)
    if len(folders) > 0:
        exec_folder_add(folders)


def exec_tree_drag_enter_popupmenu(files, method=None):
    """
    ###########################################
    弹出菜单，判断是移动还是复制。
    #######################################
    """
    # 弹出对话框
    if conf.FILE_DRAG_MOVE in ['copy', 'move']:
        exec_tree_drag_enter(files)
    elif conf.FILE_DRAG_MOVE == 'area':
        exec_tree_drag_enter(files, method)
    else:  # 如果是弹窗选择的话：
        res = tk.messagebox.askyesno(title='拖拽文件到指定位置', message='是否保留原文件？\n点击“是”保留，点击“否”删除。')
        print(res)
        if res:
            exec_tree_drag_enter(files, "copy")
        else:
            exec_tree_drag_enter(files, "move")


def exec_tree_drag_enter_move(files):
    exec_tree_drag_enter(files, "move")


def exec_tree_drag_enter(files, drag_type=None):
    """
    以拖拽的方式将文件拖动到tree范围内，将执行复制命令。
    注意，不是移动，只是复制。
    exec_safe_copy 的参数可以强制指定，也可以读取系统值。
    drag_type = copy 是复制， = move 是移动。
    """
    # 变量定义
    flag.flag_folder_changed = 0
    v_method = 2  # 树形架构下，采用方案2
    #
    print('files=', files)
    #
    arg_change_glob = False
    #
    if drag_type is None:  # 参数为空的时候，读取变量值
        drag_type = conf.FILE_DRAG_MOVE
        pass
    else:
        if arg_change_glob:
            conf.FILE_DRAG_MOVE = drag_type  # 并不会生效

    if drag_type not in ['copy', 'move']:
        drag_type = 'copy'
    #
    # 确定目录（目标）
    if len(app.tree_lst_folder.selection()) == 0:
        tk.messagebox.showerror(title='错误',
                                message='必须在左侧选定文件夹后，才能执行拖拽操作。')
        # 如果没有任何文件夹被选中
        return

    if v_method == 2:
        if get_folder_depth() == 0:  # 选中的是文件夹分组。而不是文件夹
            if tk.messagebox.askokcancel("注意", "当前选中的是文件夹分组（而不是文件夹），因此拖拽目标默认为当前分组第一个文件夹。是否继续？"):
                try:
                    tmp_root_node = app.tree_lst_folder.selection()[0]
                    tmp_f1_node = app.tree_lst_folder.get_children(tmp_root_node)[0]
                    long_name = app.tree_lst_folder.item(tmp_f1_node, "values")[-1]
                    # 默认存到第一个子文件夹中；
                except:
                    tk.messagebox.showerror(title='错误',
                                            message='拖拽操作执行不成功。请检查文件夹访问是否正常。')
                    return
            else:
                return
        elif get_folder_depth() >= 1:
            long_name = get_folder_long_v2()
        pass
    #
    # 获取对象（k已经没什么用）
    k = len(app.tree.get_children())
    #
    # 获取标签
    res_tag, res_keyword, res_path = get_search_items_sub_folder(res_lst=True)
    #
    new_file_lst = []

    # 特殊排序，将markdown文件放在后面操作
    files1 = []
    files2 = []
    for item in files:
        try:
            itm = item.decode('gbk')
        except:
            itm = item
            pass
        if len(str(itm)) > 3 and str(itm)[-3:] in conf.EXP_EXTS:
            files2.append(item)
        else:
            files1.append(item)

    files = files1 + files2  #
    # print('\nfiles=',files)
    #
    for item in files:
        # [item_path, item_name] = os.path.split(item)
        #
        try:
            item = item.decode('gbk')  # 因为拖进来的时候，files是b'xxx'编码的。需要转码。
        except:
            print('转码失败，', item, '不能被转码为gbk')
            pass
        if not isfile(item):
            print(item, '不是文件')
            if isdir(item):
                exec_folder_paste(tar_folder_from=item, tar_folder_to=long_name, need_update=False)
                flag.flag_folder_changed = 1
                flag.flag_file_changed = 1
                continue
            else:
                continue  # 跳过

        print(item)
        # 先安全复制
        old_name = item
        [fpath, ffname] = os.path.split(old_name)  # fpath 所在文件夹、ffname 原始文件名
        [fname, fename] = os.path.splitext(ffname)  # fname 文件名前半部分，fename 扩展名
        #
        if DRAG_FILES_ADD_TAG:  # 为拖拽进来的新增文件统一添加当前选中的标签
            if len(str(fname).split(conf.V_SEP)) > 0:
                tag_orig = str(fname).split(conf.V_SEP)[1:]
            for tag in res_tag:
                if not tag in tag_orig:
                    fname = fname + conf.V_SEP + tag
            ffname = fname + fename
        #
        new_name = long_name + '/' + ffname
        if drag_type in ['copy', 'move']:
            #
            # 2021年10月30日新增：markdown特殊处理
            if MARKDOWN_IMGS is True and len(old_name) > 3 and old_name[-3:] in conf.EXP_EXTS:
                MarkdownRel.copy_md_linked_files(old_name, long_name)
            #
            res = exec_safe_copy(old_name, new_name, opt_type=drag_type)
            app.str_btm.set('拖动添加文件成功')
        #     res=safe_move(old_name, new_name, opt_type='copy')
        #     app.str_btm.set('文件拖拽成功')
        print('res=')
        print(res)
        new_file_lst.append(res)
        # 再显示到列表中
        k += 1
        # tmp=get_file_part(res)
        # tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path'])
        # tmp=tmp_v
        # app.tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        flag.flag_file_changed = 1

    # 刷新：
    if flag.flag_folder_changed:
        update_folder_list()
        # update_main_window(fast_mode=True)
        pass

    if flag.flag_file_changed:
        update_main_window(0, fast_mode=True)  # 这里不刷新的话，后面排序或者筛选都会出错。
        # 高亮文件
        try:
            exec_tree_find_lst(new_file_lst)
            # exec_tree_find(res)
            # app.tree.yview_moveto(1)
        except:
            pass


def update_folder_and_json_file(ind=None, need_update=True):  # 刷新左侧的文件夹列表
    """
    刷新 json 文件，并根据文件内容刷新文件夹列表。
    输入参数是要选中的文件夹编号。
    """
    # 更新json文件
    conf.exec_json_file_write(data=conf.json_data)
    conf.exec_json_file_load()
    #
    # 更新左侧列表
    update_folder_list(need_select=False)
    #
    # 选中指定的文件夹
    app.tree_lst_folder.update()
    #
    if ind is not None:
        if FOLDER_TYPE == 1:
            # app.tree_lst_folder.selection_set(ind)
            tmp_lst_folder = app.tree_lst_folder.get_children()
            app.tree_lst_folder.selection_set(tmp_lst_folder[ind])
        elif FOLDER_TYPE == 2:
            root = app.tree_lst_folder.get_children()[0]
            to_selct = app.tree_lst_folder.get_children(root)[ind]
            app.tree_lst_folder.selection_set(to_selct)  # 选中第一个文件夹
            pass
    #
    # 刷新
    if True:  # need_update: 这里可以优化，以后上下移动文件夹可以避免重载
        on_folder_choose()


def exec_folder_clear_clipoard(event=None):
    global folder_to_move
    folder_to_move = ''


def exec_folder_cut(event=None):
    """
    文件夹拿起来（剪切）
    """
    exec_folder_clear_clipoard()
    #
    # fd = get_folder_long_v2()  # 用函数获取
    fd = app.tree_lst_folder.item(app.last_focus,"values")[-1]  # 用 last_focus 获取
    global folder_to_move
    folder_to_move = fd
    # 清空文件剪切板
    exec_tree_file_pick_nothing()


def exec_folder_paste(event=None, tar_folder_from=None,
                      tar_folder_to=None, need_update=True):
    """
    文件夹粘贴（放下）

    """
    if tar_folder_from is None:
        global folder_to_move
        fd_from = folder_to_move
    else:
        fd_from = tar_folder_from
    #
    if tar_folder_to is None:
        fd_to = app.tree_lst_folder.item(app.last_focus, "values")[-1]  # 用 last_focus 获取
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
        print('原始位置和目标位置一致，不移动文件夹')
        # exec_folder_clear_clipoard()
        return None
    # 然后检查目标位置是否是原始位置的子文件夹：
    # 算法是，检查新位置是否包括原位置的完整路径
    if (fd_to.replace('\\', '/') + '/').startswith(fd_from.replace('\\', '/') + '/'):
        tk.messagebox.showerror(title='错误',
                                message='目标位置是原位置的子文件夹，不允许这样操作。')
        print('目标位置是原位置的子文件夹，不允许这样操作', fd_to.replace('\\', '/'), fd_from.replace('\\', '/'))
        # exec_folder_clear_clipoard()
        return None
    #
    tmp_todo = 1
    tmp_rename = 0  # 是否需要重命名
    while isdir(new_path_full) and tmp_todo:
        tmp_rename = 1
        print('目标位置已存在同名文件夹')
        if tk.messagebox.askokcancel("请注意", "目标位置存在同名文件夹。需要改变文件夹的名称后继续移动文件夹吗？"):
            # 输入新文件名
            res = show_window_input('重命名', '请输入新的文件夹名称', old_tail, True)
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
        exec_folder_clear_clipoard()
        #
        if need_update:
            update_folder_list()
            update_main_window(fast_mode=True)

    except Exception as e:
        tk.messagebox.showerror(title='错误',
                                message='文件夹移动失败！错误代码：' + str(e))
        print('\n文件夹移动失败！错误代码：', e)


def exec_folder_set_group(event=None, group_name=None, short_name=None, need_update=True):
    """设置文件夹的group参数"""
    if group_name is None:
        group_name = show_window_input('请输入分组名称', '文件夹分组名称')
        if group_name is None:
            return None
    #
    if True:
        if short_name is None:
            long_name = app.tree_lst_folder.item(app.last_focus,"values")[-1]
        elif short_name == '':
            pass
        else:
            long_name = get_folder_s2l(short_name)  # 将显示值转换为实际值
            print(long_name)
    else:
        if short_name is None:
            # 获取当前选中的文件夹
            short_name = get_folder_short()
            print(short_name)
            #
        if short_name == '':
            pass
        else:
            long_name = get_folder_s2l(short_name)  # 将显示值转换为实际值
            print(long_name)

    # 在 json 里面找到对应项目并增加分组
    n = 0
    for i in conf.json_data['folders']:
        if i['pth'] == long_name:
            conf.json_data['folders'][n] = {"pth": long_name, "group": group_name}
            break
        n += 1

    # 刷新目录
    if need_update:
        update_folder_and_json_file()


def exec_folder_rename_group(event=None):
    """
    重命名文件夹分组
    """
    # 获得旧分组名称
    fd_0 = app.last_focus # 新方法：直接获取鼠标指向的对象，不需要看展开项目
    # fd_0 = app.tree_lst_folder.selection()[0]
    group_name_old = app.tree_lst_folder.item(fd_0, "text")
    #
    # 获得新名称
    group_name = show_window_input('请输入分组名称', '文件夹分组名称', group_name_old)
    if group_name is None:
        return None
    #
    # 写分组值
    # for fd_0 in app.tree_lst_folder.selection():
    fd_0 = app.last_focus
    for fd_1 in app.tree_lst_folder.get_children(fd_0):
        sht_name = app.tree_lst_folder.item(fd_1, "values")[0]  # sht_name = app.tree_lst_folder.item(fd_1, "text")
        print(sht_name)
        exec_folder_set_group(group_name=group_name, short_name=sht_name, need_update=False)
        pass
    # 刷新并写入配置文件
    update_folder_and_json_file()


def exec_folder_add(tar_list):
    """
    添加关注的目录,输入必须是列表。
    列表内是文件夹完整路径。
    """
    need_update = 0
    for tmp_path_long in tar_list:
        if len(tmp_path_long) > 0:  # 用于避免空白项目，虽然不知道哪里来的
            tmp_path_long = str(tmp_path_long).replace("\\", '/')
            tmp_tar = {"pth": tmp_path_long}
            #
            # 判断是否已经存在
            if not tmp_path_long in conf.lst_my_path_long:
                conf.json_data['folders'].append(tmp_tar)
                need_update = 1
            else:
                tk.messagebox.showerror(title='错误',
                                        message='以下路径已存在，不需要添加：' + tmp_path_long)
                print('以下路径已存在，不需要添加：', tmp_path_long)
    # 刷新目录
    if need_update:
        update_folder_and_json_file()
        # 刷新之后应该再刷新文件一次；
        update_main_window(fast_mode=True)


def exec_folder_drop():  # 删除关注的目录
    """
    取消关注选中的文件夹。
    没有输入输出。
    """
    # 获取当前选中的文件夹
    if True:
        long_name = app.tree_lst_folder.item(app.last_focus,"values")[-1]
        short_name = app.tree_lst_folder.item(app.last_focus,"values")[0]
    else:
        short_name = get_folder_short()
        print(short_name)
        if short_name == '':
            pass
        else:
            long_name = get_folder_s2l(short_name)  # 将显示值转换为实际值
            print(long_name)
    # 增加确认
    if tk.messagebox.askokcancel("操作确认", "真的要取消关注文件夹【"+short_name+"】吗？\n该文件夹将从关注列表中移除，但其本身数据并不会受到影响。"):
        pass
    else:
        return
    # 在 json 里面找到对应项目并删除
    n = 0
    for i in conf.json_data['folders']:
        if i['pth'] == long_name:
            conf.json_data['folders'].pop(n)
            break
        n += 1
    # 刷新目录
    update_folder_and_json_file()


def exec_folder_move_up(event=None, d='up'):
    """
    文件夹列表上下移动，默认上移，参数可以为 'up' 、 'down'、'top'。
    conf.json_data['folders']是列表，
    每一项的'pth'是长路径。
    """
    #
    # 获取当前选中的文件夹
    short_name = get_folder_short()
    print(short_name)
    if short_name == '':
        pass
    else:
        long_name = get_folder_s2l(short_name)  # 将显示值转换为实际值
        print(long_name)
    # 在 json 里面找到对应项目，并交换顺序
    tar_lst = conf.json_data['folders']  # 这个列表只包括文件夹，不包括“所有”。
    n = 0
    min_pos = 0
    max_pos = len(tar_lst) - 1
    #
    if d == 'top':
        n2 = 0
        for i in tar_lst:
            if i['pth'] == long_name:
                if n == 0:
                    return
                part_0 = tar_lst[0:n]
                part_1 = tar_lst[n]
                if n + 1 <= max_pos:
                    part_2 = tar_lst[n + 1:]
                else:
                    part_2 = []
                conf.json_data['folders'] = [part_1] + part_0 + part_2
                print('文件夹置顶成功')
                break
            n += 1
        pass
    else:
        for i in tar_lst:
            n2 = n - 1 if d == 'up' else n + 1

            if i['pth'] == long_name:
                # print('文件夹位置参数=')
                # print((n,n2,min_pos,max_pos))
                if n2 < min_pos or n2 > max_pos:  # 目标序号超出
                    print('不能按要求交换顺序')
                    # t=tk.messagebox.showerror(title = 'ERROR',message='不能按要求交换顺序。')
                    return
                else:
                    tar_lst[n], tar_lst[n2] = tar_lst[n2], tar_lst[n]
                    print('文件夹交换顺序成功')
                    break
            n += 1
    # 刷新目录，测试逻辑正确
    if ALL_FOLDERS == 1:  # “所有文件夹” 在最前
        n2 += 1
    else:
        pass
    update_folder_and_json_file(n2, need_update=False)  # 还需要选中目标文件夹
    pass


def exec_folder_move_down(event=None):
    """
    向下移动
    """
    exec_folder_move_up(d='down')


def exec_folder_move_top(event=None):
    """
    置顶
    """
    exec_folder_move_up(d='top')


def exec_folder_open(tar=None):  # 打开目录
    METHOD=1
    if METHOD ==1:
        # 打开左侧高亮文件夹
        try:
            print(app.tree_lst_folder.item(app.last_focus, "values"))
            l_folder = app.tree_lst_folder.item(app.last_focus,"values")[-1]
            print(l_folder)
            exec_run(l_folder)
            return
        except Exception as e:
            print(e)
            print('并没有获取到app.last_focus')
            pass
    elif METHOD ==2:
        # 获得当前选中的长目录
        if len(conf.lst_my_path_long_selected) != 1:
            pass
        else:
            try:
                exec_run(conf.lst_my_path_long_selected[0])
            except:
                pass


def exec_create_txt_note(event=None):
    exec_create_note(my_ext='.txt')

def exec_create_note_readme(event=None):
    pth = conf.lst_my_path_long_selected[0]
    file_path = pth + '/readme.md'
    try:
        if os.path.isfile(file_path):
            os.startfile(file_path)  # 打开这个文件
        else:
            with open(file_path,'w+') as f:
                pass
            os.startfile(file_path)  # 打开这个文件
    except Exception as e:
        print(e)

def exec_create_note(event=None, my_ext=None):  # 添加笔记
    if my_ext is None:
        pass
    else:
        old_ext = conf.NOTE_EXT
        conf.NOTE_EXT = my_ext

    tags = ['笔记']
    if not get_search_tag_selected() == '':  # 新笔记自动增加选中的标签
        tags += [get_search_tag_selected()]

    if len(conf.lst_my_path_long_selected) != 1:
        t = tk.messagebox.showerror(title='ERROR', message='未选中文件夹，新建笔记功能暂不可用')
        print('新建笔记功能锁定，暂不可用')
        return
    #
    the_note_name = conf.NOTE_NAME_DEFAULT
    # res = simpledialog.askstring('新建 Tagdox 笔记',prompt='请输入文件名',initialvalue =the_note_name)
    res = show_window_input('新建 Tagdox 笔记（' + conf.NOTE_EXT + "）", body_value='请输入文件名', init_value=the_note_name)
    if res is not None:
        print('获得新笔记标题：')
        print(res)
        the_note_name = res
        if len(tags) > 0:
            stags = conf.V_SEP + conf.V_SEP.join(tags)
        else:
            stags = ''

        if TAG_METHOD == 'FILE_STREAM' and not conf.NOTE_EXT in conf.EXP_EXTS:  # 如果流模式，就不通过文件名的方式加标签了；
            stags = ''

        if len(conf.lst_my_path_long_selected) > 1:
            pass

        if len(conf.lst_my_path_long_selected) == 1:
            pth = conf.lst_my_path_long_selected[0]

            if not event == 'exec_create_note_here':
                # 增加对子文件夹的判断逻辑。
                # 新建的位置正确，但是刷新之后找不到新笔记，而且子文件夹自动消失，体验不好。
                psub = get_sub_folder_selected()
                if len(psub) > 0:
                    pth = pth + '/' + psub

            print('即将在此新建笔记：')
            print(pth)
            if True:  # pth in conf.lst_my_path_long: # 后面这个判断有点多余
                fpth = pth + '/' + the_note_name + stags + conf.NOTE_EXT

                # 检查是否有这个文件
                i = 0
                while isfile(fpth):
                    i += 1
                    fpth = pth + '/' + the_note_name + '(' + str(i) + ')' + stags + conf.NOTE_EXT

                # 创建文件
                print('创建文件：')
                print(fpth)
                try:
                    if conf.NOTE_EXT in conf.NOTE_EXT_LIST:
                        with open(fpth, 'w') as _:
                            pass
                    elif conf.NOTE_EXT in ['.docxXXXXX']:
                        # d=Document()
                        # d.save(fpth)
                        pass
                    # 打开
                    exec_run(fpth)  # 打开这个文件

                    if TAG_METHOD == 'FILE_STREAM':  # 流模式下新增标签的方法
                        for tg in tags:
                            exec_file_add_tag(fpth, tg, need_update=False)

                    # 刷新
                    if event == 'exec_create_note_here':  # 【这里有bug，刷新之后不能显示内容】
                        update_main_window(1, fast_mode=True)
                        exec_tree_find(fpth)
                        # return fpth
                    else:
                        update_main_window(1, fast_mode=True)  # 没有这句话会搜不到
                        exec_tree_find(fpth)
                    # else:
                    #     return fpth
                except:
                    t = tk.messagebox.showerror(title='ERROR', message='新建笔记失败')

    else:
        pass
    #
    # 恢复笔记扩展名
    if my_ext is None:
        pass
    else:
        conf.NOTE_EXT = old_ext


def exec_create_note_here(event=None):
    """
    树状图里面，可以右击直接在选中文件的相同位置新建笔记。
    """
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        item_text = app.tree.item(item, "values")
        tmp_full_name = item_text[-1]
    tmp_path = '/'.join(get_split_path(tmp_full_name)[0:-1])
    print('当前路径')
    print(tmp_path)
    lst_tmp = conf.lst_my_path_long_selected.copy()
    conf.lst_my_path_long_selected = [tmp_path]

    fpth = exec_create_note('exec_create_note_here')
    conf.lst_my_path_long_selected = lst_tmp.copy()

    if fpth is not None:
        update_main_window(1)
        exec_tree_find(fpth)
    pass


# %%
def jump_to_search(event=None):
    """
    输入快捷键快速搜索的功能。
    """
    tmp_search_value = app.v_search.get()
    res = show_window_input('快速搜索', body_value='请输入搜索关键词，多个关键词之间用空格隔开。',
                            init_value=tmp_search_value)
    if res is not None:
        exec_clear_entry(app.v_search)
        res = res.strip()
        app.v_search.insert(0, res)
        exec_search()
        app.v_search.focus()


def jump_to_tag(event=None):
    app.v_inp.focus()


# %%
# 弹出菜单

def show_popup_menu_main(event):
    """
    主菜单，点击设置按钮可以弹出。
    设置菜单的弹出
    """
    menu_main = tk.Menu(app.window, tearoff=0)
    menu_main.add_command(label='设置…', command=show_window_setting)
    menu_main.add_separator()
    menu_main.add_command(label="添加文件夹到关注列表…", command=exec_folder_add_click)
    menu_main.add_separator()
    # menu_main.add_command(label='使用说明')#,command=show_online_help)
    menu_main.add_command(label='访问主页（联网）', command=show_online_help)
    menu_main.add_command(label='建议和反馈（联网）', command=show_online_advice)
    menu_main.add_command(label='检查更新（联网）', command=show_online_check_update)
    menu_main.add_command(label='关于…', command=show_window_info)
    menu_main.add_separator()
    menu_main.add_command(label='退出', command=show_window_closing)
    #
    menu_main.post(event.x_root, event.y_root)


def show_popup_menu_folder(event):
    """
    文件夹区域的右键菜单
    """
    v_lst = get_folder_values_v2(True)
    try:
        # print(app.last_focus == '')
        vtype = int(v_lst[1])
    except:
        if(app.last_focus == ''):
            vtype=-1
        else:
            vtype = 0
    print('vtype=', vtype)
    # 检查文件夹是否存在
    ise = os.path.isdir(app.tree_lst_folder.item(app.last_focus,"values")[-1])

    #
    # 备用语句：state=tk.DISABLED if int(vtype)>1 else tk.NORMAL, 
    #
    menu_folder_group = tk.Menu(app.window, tearoff=0)
    tmp_lst_groups = get_folder_group_list()
    if conf.DEFAULT_GROUP_NAME in tmp_lst_groups:
        tmp_lst_groups.remove(conf.DEFAULT_GROUP_NAME)
    menu_folder_group.add_command(label=conf.DEFAULT_GROUP_NAME,
                                  command=lambda x=conf.DEFAULT_GROUP_NAME: exec_folder_set_group(group_name=x))
    if len(tmp_lst_groups) > 0: menu_folder_group.add_separator()
    for i in tmp_lst_groups:
        menu_folder_group.add_command(label=i, command=lambda x=i: exec_folder_set_group(group_name=x))
    if len(tmp_lst_groups) > 0: menu_folder_group.add_separator()
    menu_folder_group.add_command(label="自定义分组…", command=exec_folder_set_group)
    #
    menu_folder = tk.Menu(app.window, tearoff=0)

    if ise:
        if vtype >= 1: menu_folder.add_command(label="打开所选文件夹", command=exec_folder_open)
        if vtype >= 1: menu_folder.add_separator()
        if vtype >= 1: menu_folder.add_command(label="新建子文件夹", command=exec_sub_folder_new)
        if vtype > 1: menu_folder.add_command(label="重命名文件夹", command=exec_folder_rename)
        if vtype > 1: menu_folder.add_command(label="删除文件夹", command=exec_folder_del)
        if vtype >= 1: menu_folder.add_separator()

        if vtype > 1: menu_folder.add_command(label="剪切文件夹", command=exec_folder_cut)
        if vtype >= 1: menu_folder.add_command(label="粘贴为子文件夹",
                                               state=tk.DISABLED if len(folder_to_move) < 1  else tk.NORMAL,
                                               command=exec_folder_paste)
    else: # 当前点击的文件夹不存在
        if vtype >= 1: menu_folder.add_command(label="打开所选文件夹（文件夹不存在）", state=tk.DISABLED,command=exec_folder_open)
        if vtype >= 1: menu_folder.add_separator()
        if vtype >= 1: menu_folder.add_command(label="新建子文件夹（文件夹不存在）", state=tk.DISABLED, command=exec_sub_folder_new)
        if vtype > 1: menu_folder.add_command(label="重命名文件夹（文件夹不存在）", state=tk.DISABLED, command=exec_folder_rename)
        if vtype > 1: menu_folder.add_command(label="删除文件夹（文件夹不存在）", state=tk.DISABLED, command=exec_folder_del)
        if vtype >= 1: menu_folder.add_separator()
        if vtype > 1: menu_folder.add_command(label="剪切文件夹（文件夹不存在）", state=tk.DISABLED, command=exec_folder_cut)
        if vtype >= 1: menu_folder.add_command(label="粘贴为子文件夹（文件夹不存在）", state=tk.DISABLED,)

    if vtype == 0: menu_folder.add_command(label="重命名分组", command=exec_folder_rename_group)
    if vtype >= 0:menu_folder.add_separator()

    if vtype > 1: menu_folder.add_command(label="添加当前选中文件夹到关注列表", command=exec_folder_from_menu)
    if vtype == 1: menu_folder.add_command(label="取消关注", command=exec_folder_drop)
    if vtype == 1: menu_folder.add_cascade(label="设置文件夹分组", menu=menu_folder_group)
    if vtype >= 1: menu_folder.add_separator()

    # menu_folder.add_command(label="添加文件夹到关注列表…", command=exec_folder_add_click)
    menu_folder.add_command(label="刷新文件夹列表", command=update_folder_list)
    menu_folder.post(event.x_root, event.y_root)

    #
    # 后续：
    # 新建子文件夹
    # 新建同级文件夹
    # 重命名文件夹
    # 将所选文件夹添加到关注
    # 全部折叠


def show_popup_menu_sub_folder(event):
    """
    子文件夹区域的右键菜单
    """
    if True:
        menu_sub_folder = tk.Menu(app.window, tearoff=0)
        menu_sub_folder.add_command(label='打开当前文件夹', command=tree_open_current_folder)
        if len(get_sub_folder_selected()) > 0:
            menu_sub_folder.add_command(label='将所选文件夹添加到关注', command=exec_folder_add_from_sub)
        else:
            menu_sub_folder.add_command(label='将所选文件夹添加到关注', state=tk.DISABLED)
        menu_sub_folder.add_separator()
        menu_sub_folder.add_command(label='新建文件夹', command=exec_sub_folder_new)
        if len(get_sub_folder_selected()) > 0:
            menu_sub_folder.add_command(label='重命名所选文件夹', command=exec_sub_folder_rename)
        else:
            menu_sub_folder.add_command(label='重命名所选文件夹', state=tk.DISABLED)
        menu_sub_folder.add_separator()
        # menu_sub_folder.add_command(label='刷新', command=update_main_window)
        menu_sub_folder.add_command(label='刷新子文件夹列表', command=update_sub_folder_list_via_menu)
        #
        menu_sub_folder.post(event.x_root, event.y_root)


def exec_tree_file_drop_tag(event=None):
    """
    删除标签

    这里event 就是标签。单一标签。
    """
    if event is None:
        return
    #
    tag_value = event
    res_lst = []
    #
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        item_text = app.tree.item(item, "values")
        tmp_full_name = item_text[-1]  # 完整文件名
        # NTFS流模式
        if TAG_METHOD == 'FILE_STREAM':
            # 读取流中的标签
            tags_in_st = []
            try:
                with open(tmp_full_name + ":tags", "r", encoding="utf8") as f:
                    tags_in_st = list(set(list(map(lambda x: x.strip(), f.readlines()))))
            except Exception as e:
                pass
            #
            if tag_value in tags_in_st:
                # 移除标签
                tags_in_st.remove(tag_value)
                # 重写流
                tags_in_st.sort()
                try:
                    with open(tmp_full_name + ":tags", "w", encoding="utf8") as f:
                        f.writelines(list(map(lambda x: x + "\n", tags_in_st)))
                    # 更新缓存
                    update_one_of_dicT(tmp_full_name)
                except:
                    pass
                #
        # 删除文件名里面的标签
        res = get_file_part(tmp_full_name)
        file_path = res['f_path_only']
        file_name_ori = res['filename_origional']
        file_ext = res['fename']
        # 新增：检查一下是否在文件名中
        file_tags_old = res['ftags']
        if tag_value in file_tags_old:
            pass
        else:
            # 如果不在，表示已经从流中删除，
            res_lst.append(tmp_full_name)
            continue

        if file_ext == '':
            print(file_name_ori)
            tmp_rv = list(file_name_ori)
            tmp_rv.reverse()
            tmp_rv = ''.join(tmp_rv)
            print(tmp_rv)
            #
            tmp_r_tag = list(conf.V_SEP + tag_value)
            tmp_r_tag.reverse()
            tmp_r_tag = ''.join(tmp_r_tag)
            print(tmp_r_tag)
            #
            tmp_rv = tmp_rv.replace(tmp_r_tag, '', 1)
            #
            tmp_rv = list(tmp_rv)
            tmp_rv.reverse()
            tmp_rv = ''.join(tmp_rv)
            #
            file_name_ori = tmp_rv
            print('从右向左替换')
            print(file_name_ori)
        new_name = file_name_ori.replace(conf.V_SEP + tag_value + conf.V_SEP, conf.V_SEP)
        new_name = new_name.replace(conf.V_SEP + tag_value + '.', ".")

        new_full_name = file_path + '/' + new_name
        print('原始文件名：')
        print(tmp_full_name)
        print('去掉标签后：')
        print(new_full_name)
        print('被去掉的标签：')
        print(tag_value)
        # os.rename(tmp_full_name,new_full_name)
        if tmp_full_name != new_full_name:
            tmp_final_name = exec_safe_rename(tmp_full_name, new_full_name)
        res_lst.append(new_full_name)

    update_main_window(0, fast_mode=True)  # 此处可以优化，避免完全重载
    exec_tree_find_lst(res_lst)
    # for tmp_final_name in res_lst:
    #     tmp_final_name = tmp_final_name.replace('\\', '/')
    #     print('删除标签完成，正在定位%s' % (tmp_final_name))
    #     exec_tree_find(tmp_final_name)  # 为加标签之后的项目高亮


def exec_tree_right_click(event):
    """
    右键点击 app.tree 区域

    :param event:
    :return:
    """
    tmp = app.tree.identify_row(event.y)
    if tmp not in app.tree.selection():
        app.tree.selection_set(tmp)
    exec_tree_mouse_highlight(event, clear_only=True)


def exec_tree_left_click(event):
    """
    左键单击tree区域，
    如果不设置，那么点击空白并不会影响选中项目；体验不好。
    :param event:
    :return:
    """
    # print(event.keycode)
    # if event.keysym in ['<Shift_L>','<Shift_R>','<Control_L>','<Control_R>']:  # 按 ctrl 或者 shift 的时候不操作
    # print(event)
    # return
    tmp = app.tree.identify_row(event.y)
    print(len(tmp))

    # if tmp not in app.tree.get_children():
    if len(tmp) == 0:  # not in app.tree.get_children():
        app.tree.selection_set(tmp)
    # exec_tree_mouse_highlight(event, clear_only=True)


def exec_tree_folder_right_click(event):
    """
    右键点击 folder 区域

    :param event:
    :return:
    """
    exec_tree_folder_mouse_highlight(event) # 刷新 app.focus 保证右击在正确对象上
    tmp = app.tree_lst_folder.identify_row(event.y)
    # 选中被点击的对象，之前是直接选中，但体验比较差
    # if tmp not in app.tree_lst_folder.selection():
    #     app.tree_lst_folder.selection_set(tmp)
    # 执行切换文件夹的功能
    # on_folder_choose()
    # 显示菜单
    show_popup_menu_folder(event)


def show_popup_menu_file(event):
    """
    文件区域的右键菜单
    """
    n_selection = len(app.tree.selection())
    # for item in app.tree.selection():
    #     item_text = app.tree.item(item, "values")
    #     tmp_full_name = item_text[-1]
    #     n_selection += 1
    #
    menu_tags_to_drop = tk.Menu(app.window, tearoff=0)
    menu_tags_to_add = tk.Menu(app.window, tearoff=0)
    menu_create_note = tk.Menu(app.window, tearoff=0)  # 新建笔记

    menu_create_note.add_command(label='.docx', command=lambda x=1: exec_create_note(None, '.docx'))
    menu_create_note.add_command(label='.md', command=lambda x=1: exec_create_note(None, '.md'))
    menu_create_note.add_command(label='.txt', command=lambda x=1: exec_create_note(None, '.txt'))
    menu_create_note.add_command(label='.rtf', command=lambda x=1: exec_create_note(None, '.rtf'))
    menu_create_note.add_command(label='.mm', command=lambda x=1: exec_create_note(None, '.mm'))

    #
    if len(conf.QUICK_TAGS) > 0:
        for i in conf.QUICK_TAGS:
            menu_tags_to_add.add_command(label=i, command=lambda x=i: exec_fast_add_tag(x))
        menu_tags_to_add.add_separator()
    menu_tags_to_add.add_command(label='自定义标签…', command=exec_tree_add_tag_via_dialog)
    #
    menu_file = tk.Menu(app.window, tearoff=0)
    menu_file.add_command(label="打开文件", command=exec_tree_file_open, accelerator='Enter')
    # menu_file.add_command(label="在相同位置创建笔记",command=exec_create_note_here)
    menu_file.add_separator()
    if len(conf.lst_my_path_long_selected) == 1:
        menu_file.add_command(label="新建笔记（" + conf.NOTE_EXT + "）", command=exec_create_note, accelerator='Ctrl+N')
        menu_file.add_cascade(label="新建更多格式的笔记", menu=menu_create_note)
    else:
        menu_file.add_command(label="新建笔记", state=tk.DISABLED, command=exec_create_note, accelerator='Ctrl+N')
    menu_file.add_separator()
    if n_selection == 1:
        # menu_file.add_command(label="打开选中项所在文件夹", command=tree_open_folder)
        menu_file.add_command(label="打开所在文件夹", command=tree_open_folder_select)
    elif n_selection > 1:
        menu_file.add_command(label="打开选中项所在文件夹", state=tk.DISABLED, command=tree_open_folder)
    # menu_file.add_command(label="打开当前文件夹", command=tree_open_current_folder)
    menu_file.add_separator()
    menu_file.add_command(label='添加标签 ', command=exec_tree_add_tag_via_dialog, accelerator='Ctrl+T')
    menu_file.add_cascade(label="快速添加标签", menu=menu_tags_to_add)
    if n_selection == 1:
        menu_file.add_cascade(label="移除标签", menu=menu_tags_to_drop)
    elif n_selection > 1:
        menu_file.add_cascade(label="移除标签", menu=menu_tags_to_drop)
    menu_file.add_separator()
    # menu_file.add_command(label="发送无标签副本到桌面（开发中）",state=tk.DISABLED)#,command=exec_tree_file_rename)
    # menu_file.add_command(label="复制到剪切板（开发中）",state=tk.DISABLED)#,command=exec_tree_file_rename)
    # menu_file.add_command(label="移动到文件夹（开发中）",state=tk.DISABLED)#,command=exec_tree_file_rename)
    # menu_file.add_command(label="粘贴（开发中）",state=tk.DISABLED)#,command=exec_tree_file_rename)
    if n_selection == 1:
        menu_file.add_command(label="重命名", command=exec_tree_file_rename, accelerator='F2')
    elif n_selection > 1:
        menu_file.add_command(label="重命名", state=tk.DISABLED, command=exec_tree_file_rename, accelerator='F2')
    menu_file.add_command(label="删除", command=exec_tree_file_delete, accelerator='Del')
    menu_file.add_separator()
    menu_file.add_command(label="剪切", command=exec_tree_file_cut, accelerator='Ctrl+X')
    menu_file.add_command(label="复制", command=exec_tree_file_copy, accelerator='Ctrl+C')
    menu_file.add_command(label="粘贴", state=tk.DISABLED if len(lst_pick_up_files) == 0 else tk.NORMAL,
                          command=exec_tree_file_put_down, accelerator='Ctrl+V')
    # menu_file.add_command(label="取消", state=tk.DISABLED if len(lst_pick_up_files) == 0 else tk.NORMAL,
    #                       command=exec_tree_file_pick_nothing)

    menu_file.add_separator()
    menu_file.add_command(label="刷新", command=update_main_window, accelerator='F5')
    #
    # 没有选中项目的时候
    #
    menu_file_no_selection = tk.Menu(app.window, tearoff=0)
    # menu_file_no_selection.add_command(label="打开文件",state=tk.DISABLED,command=exec_tree_file_open)
    menu_file_no_selection.add_command(label="打开当前文件夹", command=tree_open_current_folder)
    menu_file_no_selection.add_separator()
    if len(conf.lst_my_path_long_selected) == 1:
        menu_file_no_selection.add_command(label="新建笔记（" + conf.NOTE_EXT + "）", command=exec_create_note,
                                           accelerator='Ctrl+N')
        menu_file_no_selection.add_cascade(label="新建更多格式的笔记", menu=menu_create_note)
    else:
        menu_file_no_selection.add_command(label="新建笔记", state=tk.DISABLED, command=exec_create_note,
                                           accelerator='Ctrl+N')
    # menu_file_no_selection.add_command(label="重命名",state=tk.DISABLED)#,command=exec_folder_add_click)
    # menu_file_no_selection.add_command(label="添加收藏",state=tk.DISABLED)#,command=exec_folder_add_click)
    menu_file_no_selection.add_separator()
    menu_file_no_selection.add_command(label="剪切", state=tk.DISABLED, command=exec_tree_file_cut, accelerator='Ctrl+X')
    menu_file_no_selection.add_command(label="复制", state=tk.DISABLED, command=exec_tree_file_copy, accelerator='Ctrl+C')
    menu_file_no_selection.add_command(label="粘贴", state=tk.DISABLED if len(lst_pick_up_files) == 0 else tk.NORMAL,
                                       command=exec_tree_file_put_down, accelerator='Ctrl+V')
    # menu_file_no_selection.add_command(label="取消", state=tk.DISABLED if len(lst_pick_up_files) == 0 else tk.NORMAL,
    #                                    command=exec_tree_file_pick_nothing)
    menu_file_no_selection.add_separator()
    menu_file_no_selection.add_command(label="刷新", command=update_main_window)

    if n_selection == 1:  # 如果有选中项目的话，

        # tmp_file_name=get_split_path(tmp_full_name)[-1]
        for item in app.tree.selection():
            if not is_tree_item_enable(item):
                continue
            item_text = app.tree.item(item, "values")
            tmp_full_name = item_text[-1]
        tmp_file_name = get_file_part(tmp_full_name)['fname']
        tmp_tags_all = get_file_part(tmp_full_name)['ftags']
        tmp_tags = tmp_file_name.split(conf.V_SEP)
        # print(tmp_res)
        tmp_tags.pop(0)
        #
        # 新增：检查流中的标签
        if TAG_METHOD == 'FILE_STREAM':
            try:
                with open(tmp_full_name + ":tags", "r", encoding="utf8") as f:
                    tags_in_st = list(set(list(map(lambda x: x.strip(), f.readlines()))))
                for i in tags_in_st:
                    if i not in tmp_tags:
                        tmp_tags.append(i)
            except FileNotFoundError as e:
                pass
            except:
                pass

        try:
            for i in range(10000):  # 删除已有标签
                menu_tags_to_drop.delete(0)
        except:
            pass

        if len(tmp_tags_all) > 0:
            if len(tmp_tags) == 0:
                pass
            else:
                # menu_tags_to_drop.add_separator()
                for i in tmp_tags:
                    menu_tags_to_drop.add_command(label=i, command=lambda x=i: exec_tree_file_drop_tag(x))

            if len(tmp_tags_all) > len(tmp_tags):
                if len(tmp_tags) > 0:
                    menu_tags_to_drop.add_separator()
                menu_tags_to_drop.add_command(label='以下标签来自文件路径，不可直接删除', state=tk.DISABLED)

            for i in tmp_tags_all:
                if not i in tmp_tags:
                    menu_tags_to_drop.add_command(label=i, state=tk.DISABLED)

        else:
            menu_tags_to_drop.add_command(label='无可操作项目', state=tk.DISABLED)
            pass

        menu_file.post(event.x_root, event.y_root)

    elif n_selection > 1:  # 选中很多项目的时候
        try:
            for i in range(10000):  # 删除已有标签
                menu_tags_to_drop.delete(0)
        except:
            pass

        tmp_tags_from_files = []
        file_checked = 0
        for item in app.tree.selection():
            if not is_tree_item_enable(item):
                continue
            item_text = app.tree.item(item, "values")
            tmp_full_name = item_text[-1]
            tmp_file_name = get_file_part(tmp_full_name)['fname']
            tmp_tags_all = get_file_part(tmp_full_name)['ftags']  # 自带标签+路径标签
            tmp_tags = tmp_file_name.split(conf.V_SEP)  # 选中项自带标签
            # print(tmp_res)
            tmp_tags.pop(0)
            # 新增：检查流中的标签
            if TAG_METHOD == 'FILE_STREAM':
                try:
                    with open(tmp_full_name + ":tags", "r", encoding="utf8") as f:
                        tags_in_st = list(set(list(map(lambda x: x.strip(), f.readlines()))))
                    for i in tags_in_st:
                        if i not in tmp_tags:
                            tmp_tags.append(i)
                except FileNotFoundError as e:
                    pass
                except:
                    pass
            #
            if file_checked == 0:
                tmp_tags_from_files += tmp_tags
            else:
                # 取交集
                tmp_tags_from_files = list(set(tmp_tags_from_files).intersection(set(tmp_tags)))
                #
                # 方法2
                # for i in range(len(tmp_tags_from_files)):
                #     if tmp_tags_from_files[-1-i] not in tmp_tags:
                #         tmp_tags_from_files.pop(-1-i)
                #
                # 如果是取并集：
                # tmp_tags_from_files+=tmp_tags

            file_checked += 1

        if len(tmp_tags_from_files) > 0:
            tmp_tags_from_files = list(set(tmp_tags_from_files))
            for i in tmp_tags_from_files:
                menu_tags_to_drop.add_command(label=i, command=lambda x=i: exec_tree_file_drop_tag(x))
        else:
            menu_tags_to_drop.add_command(label='无可移除的共有标签', state=tk.DISABLED)
            pass
        menu_file.post(event.x_root, event.y_root)
    else:
        menu_file_no_selection.post(event.x_root, event.y_root)


def fixed_map(option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]


def fixed_map_v2(tar, option):
    return [elm for elm in style.map(tar, query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]


def exec_tree_folder_remove_mouse_highlight(event):
    exec_tree_folder_mouse_highlight(event, clear_only=True)


def exec_tree_folder_mouse_highlight(event, clear_only=False):
    """
    文件夹树的鼠标悬浮效果。
    :param event:
    :param clear_only:
    :param the_tree:
    :return:
    """
    the_tree = app.tree_lst_folder
    exec_tree_mouse_highlight(event, clear_only=clear_only, the_tree=the_tree)


def exec_tree_tag_remove_mouse_highlight(event):
    exec_tree_folder_mouse_highlight(event, clear_only=True)


def exec_tree_tag_mouse_highlight(event, clear_only=False):
    """
    文件夹树的鼠标悬浮效果。
    :param event:
    :param clear_only:
    :param the_tree:
    :return:
    """
    the_tree = app.tree_lst_sub_tag
    exec_tree_mouse_highlight(event, clear_only=clear_only, the_tree=the_tree)


def exec_tree_mouse_highlight(event, clear_only=False, the_tree=None):
    """
    鼠标指向的项目加背景色，可以作为通用函数，被各种树调用
    :param event:
    :return:
    """
    #
    # 定义操作目标
    if the_tree is None:
        the_tree = app.tree
    #
    _iid = the_tree.identify_row(event.y)

    # print(event.y)
    #

    def remove_last_tag():  # 移除之前高亮的项目
        if app.last_focus:
            if app.the_tree and app.the_tree is not the_tree:
                #
                try:  # 之前的去掉高亮
                    tags_old = list(app.the_tree.item(app.last_focus, "tags"))
                    tags_old.remove('line_mouse')
                    app.the_tree.item(app.last_focus, tags=tags_old)
                except:
                    pass
            else:
                try:  # 之前的去掉高亮
                    tags_old = list(the_tree.item(app.last_focus, "tags"))
                    tags_old.remove('line_mouse')
                    the_tree.item(app.last_focus, tags=tags_old)
                except:
                    pass

    if clear_only:
        remove_last_tag()
        app.last_focus = None
        app.the_tree = the_tree
        return

    if _iid != app.last_focus:
        remove_last_tag()
        """if app.last_focus:
            try:  # 之前的去掉高亮
                tags_old = list(app.tree.item(app.last_focus, "tags"))
                tags_old.remove('line_mouse')
                app.tree.item(app.last_focus, tags=tags_old)
            except:
                pass"""
        # 新项目加高亮
        tags_new = list(the_tree.item(_iid, "tags"))
        tags_new = ['line_mouse'] + tags_new
        the_tree.item(_iid, tags=tags_new)
        # print(self.tree.item(_iid,"value"))
        #
        # 新项目保存
        app.last_focus = _iid
        app.the_tree = the_tree


def set_style(style):
    """
    显示的样式
    """
    # style = ttk.Style()
    # 修复 treeview 背景色的bug；
    style.map('Treeview',
              foreground=fixed_map('foreground'),
              background=fixed_map('background')
              )
    style.map('TFrame',
              foreground=fixed_map_v2('Frame', 'foreground'),
              background=fixed_map_v2('Frame', 'background'),
              )
    # style.map('TButton', foreground=fixed_map_v2('TButton','foreground'), background=fixed_map_v2('TButton','background'))
    #
    MY_THEME = 'third_party'

    if MY_THEME == 'third_party':
        """
        第三方主题
        """
        app.window.tk.call('lappend', 'auto_path', './resources/styles/awthemes-10.4.0')
        app.window.tk.call('package', 'require', 'awlight')
        app.window.tk.call('package', 'require', 'awdark')
        #
        style.theme_use('awlight')  # awlight awdark clam X
        #
        LIGHT_THEME = True
        #
        # 标签生效顺序是，定义在前面的优先生效，和实际标签列表里面的顺序没有关系
        #
        if LIGHT_THEME:
            #
            # 独立设定效果
            app.tree.tag_configure('line_mouse', background="#dddfe2")
            app.tree_lst_folder.tag_configure('line_mouse', background="#242425",foreground="#2eb8ac",)
            # app.tree_lst_folder.tag_configure('line_mouse', background="#242425")
            app.tree_lst_sub_tag.tag_configure('line_mouse', background="#FFFFFF")
            app.tree_lst_sub_tag.tag_configure('line1', background="#EBEFF2")
            #
            #
            # 通用的
            for tar in [app.tree_lst_folder, app.tree_lst_sub_folder, app.tree]:
                # tar.tag_configure('line_mouse', background="#dddfe2")
                tar.tag_configure('line1', background="#F2F2F2")
                tar.tag_configure('line_folder', background="#dbe2e8")
                # tar.tag_configure('line1',background="#F8F8F8")
                # tar.tag_configure('line1',background="#FFFFFF")
                # tar.tag_configure('folder2',background="#FFFFFF")
                tar.tag_configure('folder0', foreground=app.COLOR_DICT['blue_light'])
                tar.tag_configure('folder2', background="#1e1e1e")
                tar.tag_configure('pick_up', foreground="#f37625",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
                tar.tag_configure('pick_copy', foreground="#2d7d9a",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))

        else:
            for tar in [app.tree_lst_folder, app.tree_lst_sub_folder, app.tree_lst_sub_tag, app.tree]:
                tar.tag_configure('line1', background="#343a40")
                # tar.tag_configure('line1',background="#F8F8F8")
                # tar.tag_configure('line1',background="#FFFFFF")
                # tar.tag_configure('folder2',background="#FFFFFF")
                # tar.tag_configure('folder2',background="#1e1e1e")
                tar.tag_configure('pick_up', foreground="#f37625",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
                tar.tag_configure('pick_copy', foreground="#2d7d9a",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))

        # app.window.tk.call('source', './resources/styles/ttk-Breeze-master/breeze.tcl')
        # style.theme_use('Breeze') # 

        style.configure("Treeview.Heading",
                        font=conf.FONT_TREE_HEADING, \
                        rowheight=int(conf.LARGE_FONT * 4 * conf.ui_ratio),
                        height=int(conf.LARGE_FONT * 4), \
                        background='white',
                        foreground='black',
                        relief='flat',
                        borderwidth=0,
                        padding=(int(conf.LARGE_FONT / 2), int(conf.LARGE_FONT / 2), 0, int(conf.LARGE_FONT / 2)),
                        )

        style.configure("Treeview",
                        font=conf.FONT_TREE_BODY,
                        rowheight=int(conf.MON_FONTSIZE * 4 * conf.ui_ratio),
                        fieldbackground='#e8e8e7',
                        background='#e8e8e7',
                        foreground='black',
                        relief='flat',
                        borderwidth=0,
                        )
        style.layout("Treeview", [('Dark.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        style.configure("Taglist.Treeview",
                        # font=conf.FONT_TREE_BODY,
                        # fontsize=-15,
                        # rowheight=int(conf.MON_FONTSIZE * 3.5), \
                        fieldbackground='#5c6164',  # 没有行部分的颜色
                        background='#dbe2e8',  # 空白行的颜色
                        foreground='black',
                        # relief='flat',
                        # borderwidth=0,
                        )
        style.configure("Dark.Treeview",
                        # font=conf.FONT_TREE_BODY,
                        # fontsize=-15,
                        # rowheight=int(conf.MON_FONTSIZE * 3.5), \
                        fieldbackground=app.COLOR_DICT['darkback_1'],  # 没有行部分的颜色
                        background='#2a333c',
                        foreground='white',
                        indent=40,
                        # rowheight=60, # 行间距
                        # relief='flat',
                        # borderwidth=0,
                        )
        style.layout("Dark.Treeview", [
            ('Dark.Treeview.treearea', {'sticky': 'nswe'}) # Remove the borders
        ])
        # style.configure("Dark.Treeview", rowheight=60)  # 调整行间距
        # style.configure("Dark.Treeview.Heading", font=("Arial", 14))  # 调整表头字体
        # style.configure("Dark.Treeview.Cell", padding=(100, 50))  # 调整图标与文字之间的间距 # 无效

        style.configure("TCombobox",
                        relief='flat',
                        background="#e8e8e7",
                        foreground='black',
                        )
        style.configure("TEntry",
                        relief='flat',
                        background="#e8e8e7",
                        foreground='black',
                        )

        style.configure("TFrame",
                        relief='flat',
                        background="#e8e8e7",
                        foreground='black',
                        )  # 静态

        style.configure("Dark.TFrame",
                        relief='flat',
                        background="#2a333c",
                        foreground='white',
                        )  # 静态

        style.configure("TButton",
                        relief='flat',
                        font=conf.FONT_TREE_BODY,
                        background=app.COLOR_DICT['blue'],  # '#3a92c5',
                        foreground='white',
                        )  # 静态

        style.map('TButton',
                  background=[('active', app.COLOR_DICT['cyan']),
                              ('pressed', app.COLOR_DICT['blue']),
                              ('disabled', '#bfbfbf')
                              ]
                  )

        # style.configure("Light.TButton",
        #                 background='#e8e8e7')  # app.COLOR_DICT['#2a333c'])

        style.configure("Menu.TButton",
                        background='#2a333c')  # app.COLOR_DICT['#2a333c'])

        style.map('Menu.TButton',
                  background=[
                      ('active', '#5f6368'),
                      ('pressed', '#414141'),
                  ]
                  )  #

        style.configure("TProgressbar",  # Horizontal.
                        relief='flat',
                        background=app.COLOR_DICT['blue'],  # '#3a92c5',
                        )


    elif MY_THEME == 'built-in':

        style.theme_use('clam')  # winnative clam
        #
        # treeview
        style.configure("Treeview.Heading", font=conf.FONT_TREE_HEADING, \
                        rowheight=int(conf.LARGE_FONT * 4 * conf.ui_ratio), height=int(conf.LARGE_FONT * 4), \
                        relief='flat', borderwidth=0)

        style.configure("Treeview", font=conf.FONT_TREE_BODY, \
                        rowheight=int(conf.MON_FONTSIZE * 3.5 * conf.ui_ratio), \
                        fieldbackground='white', background='#666666', \
                        relief='flat', borderwidth=0)
        # style.configure("Treeview.Item",font=5)
        style.configure("Dark.Treeview", fieldbackground='#333333', background='black')
        style.configure("Dark.Treeview.Heading", fieldbackground='blue', \
                        background='black', foreground='white')
        #
        # 框架
        style.configure("TFrame", fieldbackground='white', background='#EEEEEE', \
                        borderwidth=0, relief='flat')
        # 
        # 按钮
        style.configure("TButton", fieldbackground='#666666',
                        background='#999900',
                        activeforeground=" #ff0000", activebackground="#00ff00",
                        height=int(16*conf.ui_ratio),
                        borderwidth=1, relief='flat')
        #
        style.configure("TEntry", fieldbackground='#FFFFFF', background='#EEEEEE', \
                        borderwidth=1, relief='solid')

    else:
        style.configure("Treeview.Heading", font=conf.FONT_TREE_HEADING, \
                        rowheight=int(conf.LARGE_FONT * 4 * conf.ui_ratio), height=int(conf.LARGE_FONT * 4))
        style.configure("Treeview", font=conf.FONT_TREE_BODY, \
                        rowheight=int(conf.MON_FONTSIZE * 3.5 * conf.ui_ratio), relief='flat', borderwidth=0)
        # style.configure("Vertical.TScrollbar", width=8)

        for tar in [app.tree_lst_folder, app.tree_lst_sub_folder, app.tree_lst_sub_tag, app.tree]:
            tar.tag_configure('line1', background="#F2F2F2")
            # tar.tag_configure('line1',background="#F8F8F8")
            # tar.tag_configure('line1',background="#FFFFFF")
            # tar.tag_configure('folder2',background="#FFFFFF")
            tar.tag_configure('folder2', background="#F2F2F2")
            tar.tag_configure('pick_up', foreground="#f37625", font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
            tar.tag_configure('pick_copy', foreground="#2d7d9a", font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))


def exec_tree_file_pick_up(event=None, need_clear=False):
    """
    将选中的文件拿起来
    """
    global lst_pick_up_files
    global lst_pick_up_items
    global state_pick_up

    # if state_pick_up =='copy':
    #     state_pick_up = 'move'
    #     need_clear = True
    #
    # 每次复制或剪切的时候，文件夹的清理总是需要的
    exec_folder_clear_clipoard()
    #
    if need_clear:
        exec_tree_file_pick_nothing()
        # lst_pick_up_files = []
        # lst_pick_up_items = []
    #
    # 添加到列表中：
    for item in app.tree.selection():
        if not is_tree_item_enable(item):
            continue
        #
        item_text = app.tree.item(item, "values")
        tmp_full_name = item_text[-1]
        #
        item_tags = app.tree.item(item, 'tags')
        #
        if state_pick_up == 'move':
            new_tag = 'pick_up'
        elif state_pick_up == 'copy':
            new_tag = 'pick_copy'
        if not new_tag in list(item_tags):
            new_item_tags = list(item_tags) + [new_tag]
        else:
            new_item_tags = list(item_tags)
        #
        app.tree.item(item, tags=new_item_tags)
        #
        if not tmp_full_name in lst_pick_up_files:
            lst_pick_up_files.append(tmp_full_name)
        if not item in lst_pick_up_items:
            lst_pick_up_items.append(item)


def exec_tree_file_cut_ctn(event=None):
    """
    连续剪切
    """
    global state_pick_up
    if state_pick_up == 'copy':
        state_pick_up = 'move'
        exec_tree_file_pick_up(need_clear=True)
    else:
        exec_tree_file_pick_up(need_clear=False)


def exec_tree_file_cut(event=None):
    """
    剪切
    """
    global state_pick_up
    state_pick_up = 'move'
    exec_tree_file_pick_up(need_clear=True)


def exec_tree_file_copy_cnt(event=None):
    """
    连续复制
    """
    global state_pick_up
    if state_pick_up == 'move':
        state_pick_up = 'copy'
        exec_tree_file_pick_up(need_clear=True)
    else:
        exec_tree_file_pick_up(need_clear=False)


def exec_tree_file_copy(event=None):
    """
    选中的文件复制
    """
    global state_pick_up
    state_pick_up = 'copy'
    exec_tree_file_pick_up(need_clear=True)


def exec_tree_file_pick_nothing(event=None, fastmode=False):
    """
    清空pick列表
    """

    global lst_pick_up_files
    global lst_pick_up_items
    if not fastmode:
        for item in lst_pick_up_items:
            try:
                new_item_tags = list(app.tree.item(item, 'tags'))
                if 'pick_up' in new_item_tags:
                    new_item_tags.remove('pick_up')
                if 'pick_copy' in new_item_tags:
                    new_item_tags.remove('pick_copy')
                app.tree.item(item, tags=new_item_tags)
            except:
                pass
    lst_pick_up_files = []
    lst_pick_up_items = []


def exec_tree_file_put_down(event=None):
    """
    将选中的文件放下
    """
    global lst_pick_up_files
    global lst_pick_up_items
    # state_pick_up = 'move' 默认
    exec_tree_drag_enter(lst_pick_up_files, drag_type=state_pick_up)  # 调用的是拖动函数
    # lst_pick_up_files=[]
    # lst_pick_up_items = []
    exec_tree_file_pick_nothing(fastmode=True)


def exec_tree_file_group(event=None):
    """
    快速打包
    """
    file_lst = []  # 文件列表
    tar_folder = ''  # 目标位置
    #
    # 判断是否满足条件；
    if len(app.tree.selection()) <= 0:  # 没有选中文件
        return -1
    elif get_folder_depth() == 0:  # 选中的是文件夹分组。而不是文件夹
        return -1
    elif get_folder_depth() >= 1:
        current_folder = get_folder_long_v2()
    #
    # 获得文件列表：
    group_name = show_window_input('快速打包','请输入分组文件夹名称')
    if group_name is not None:
        tar_folder = current_folder + '/' + group_name

    for i in app.tree.selection():
        file_full_path = app.tree.item(i)  # 获得路径

    update_folder_list()  # 刷新文件夹列表
    # 刷新树


# %%
class td_main_app:
    """
    主窗口类
    """

    # options = {
    #     'V_SEP': '^',
    #     'ScaleFactor': None,
    #     'SCREEN_WIDTH': None,
    #     'SCREEN_HEIGHT': None,
    # }

    def __init__(self) -> None:
        """
        界面部分。
        也就是UI的设计。
        """
        self.last_focus = None
        self.the_tree = None
        self.file_open_time = time.time()  # 最近一次tree_file_open 的时间；
        self.window = tk.Tk()
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
            print ('w,h = ', conf.SCREEN_WIDTH, conf.SCREEN_HEIGHT)

        except:
            conf.SCREEN_WIDTH = self.window.winfo_screenwidth()
            conf.SCREEN_HEIGHT = self.window.winfo_screenheight()
        pass
        conf.ui_ratio = (conf.SCREEN_WIDTH / 1920)
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
        #
        # 框架设计 ############################################
        #
        self.frame_window = ttk.Frame(self.window, padding=(0, 0, 0, 0), relief='flat', borderwidth=0)
        self.frame_window.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=0, pady=0)
        #
        # 文件夹区
        self.frameLeft = ttk.Frame(self.frame_window,
                                   # style="Dark.Treeview",
                                   # width=int(w_width * 0.4),
                                   padding=(0, 0, 0, 0),
                                   borderwidth=0,
                                   width=int(conf.ui_ratio *320),  # 没有用，因为 Frame 默认是根据控件大小改变的。
                                   relief='flat')  # ,)
        self.frameLeft.pack(side=tk.LEFT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
        self.frameLeft.pack_propagate(0)  # 设置为0则框架不被内部撑大。默认是1.
        #
        self.bar_folder_v = tk.Scrollbar(self.frameLeft, width=int(16 * conf.ui_ratio))
        # self.bar_folder_v = ttk.Scrollbar(self.frameFolder)#, width=16)
        self.bar_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
        #
        # 菜单区
        self.frameMenu = ttk.Frame(self.frameLeft,
                                   relief='flat',
                                   style='Dark.TFrame',
                                   # width=int((320 - 16 * 1) * conf.ui_ratio),
                                   height =int(40 * conf.ui_ratio),
                                   # borderwidth=0,
                                   # padding=(0, 0, 0, 0),
                                   )  # , borderwidth=1 ,relief='solid')  # ,width=600) LabelFrame
        self.frameMenu.pack(side=tk.TOP, expand=0, fill=tk.X, padx=0, pady=0)  # padx=10, pady=5)
        self.frameMenu.pack_propagate(0)
        # 文件夹在frameLeft内部
        self.frameFolder = ttk.Frame(self.frameLeft, style='Dark.TFrame', relief='flat', borderwidth=0, )
        # height=SCREEN_HEIGHT * 0.8)  # ,width=600),width=int(w_width*0.4)
        self.frameFolder.pack(side=tk.TOP, expand=1, fill=tk.BOTH, padx=0, pady=0)  # padx=10,pady=5)
        # frameFolder.grid(column=0,row=0)
        #
        # 子文件夹区（也在frameLeft内部）
        self.frameSubFolder = ttk.Frame(self.frameLeft, relief='flat')  # ,width=600)
        if FOLDER_TYPE == 1:
            self.frameSubFolder.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH, padx=0, pady=2)  # padx=10,pady=5)
        #

        # self.frameSubTags.pack(side=tk.BOTTOM, expand=1, fill=tk.Y, padx=10, pady=5)  # padx=10,pady=5)
        #
        # 文件夹下面的控制区
        self.frameFolderCtl = ttk.Frame(self.frameLeft, height=int(10*conf.ui_ratio), borderwidth=0, relief=tk.SOLID)
        # self.frameFolderCtl.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=5)
        # 上面功能区：frame0
        self.frame0 = ttk.Frame(self.frame_window,
                                relief='flat',
                                borderwidth=0,
                                # relief='solid',
                                height=int(120 * conf.ui_ratio),
                                )  # , borderwidth=1 ,relief='solid')  # ,width=600) LabelFrame
        self.frame0.pack(expand=0, fill=tk.X, padx=0, pady=0)  # padx=10, pady=5)
        # 主功能区
        self.frameMain = ttk.Frame(self.frame_window, border=0)  # ,height=800)
        self.frameMain.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)  # padx=10, pady=0)
        # 标签区
        # self.frameSubTags = ttk.Frame(self.frameLeft)  # ,width=600)
        self.frameSubTags = ttk.Frame(self.frameMain, width=int(conf.ui_ratio * 300))
        self.frameSubTags.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
        #
        # readme 区域
        self.frameReadme = ttk.Frame(self.frameMain, height=150)
        self.frameReadme.pack(side=tk.BOTTOM, expand=0, fill=tk.X, )
        self.frameReadme.pack_propagate(0)  # 设置为0则框架不被内部撑大。默认是1.
        #
        # self.str_readme = tk.StringVar()  # 最下面显示状态用的
        # self.str_readme.set("这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，这是一段很长很长的文本，\n它将会在单词边界处自动换行。")
        # text = ttk.Label(self.frameReadme,textvariable=self.str_readme)  # wrap="word" 使文本在单词边界处进行换行
        # text.pack()
        self.text_readme = tk.Text(self.frameReadme, wrap='word',borderwidth=0,
                                   padx=40,pady=5,
                                   background='#f0f0f0',#'#e8e8e7',
                                   font=conf.FONT_TREE_BODY,
                                   relief='flat')
        self.text_readme.pack(fill=tk.BOTH, expand=1)
        #
        self.frameTreeFiles = ttk.Frame(self.frameMain,)  # ,height=800)
        self.frameTreeFiles.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)  # padx=10, pady=0)
        #
        # 底部区
        self.frameBtm = ttk.Frame(self.frame_window, height=int(120*conf.ui_ratio), padding=(0, 0, 0, 0), relief='flat')
        self.frameBtm.pack(side=tk.BOTTOM, expand=0, fill=tk.X, padx=0, pady=0)
        #
        ##############
        # 控件
        ##############
        #
        self.bt_folder_add = ttk.Button(self.frame0, text='添加文件夹到关注列表')  # state=tk.DISABLED,,command=setting_fun
        self.bt_folder_drop = ttk.Button(self.frameFolderCtl, text='移除文件夹')
        #
        self.v_sub_folders = ttk.Combobox(self.frame0)  # 子文件夹选择框
        self.v_tag = ttk.Combobox(self.frame0)  # 标签选择框
        self.v_search = ttk.Entry(self.frame0)  # 搜索框
        self.v_folders = ttk.Combobox(self.frameFolder)  # 文件夹选择框
        #
        # 主文件树
        self.tree_main = td_tree_file(self.frameTreeFiles, self.frameBtm)
        self.bar_tree_v = self.tree_main.bar_tree_v
        # self.bar_tree_v = tk.Scrollbar(self.frameMain)  # 右侧滚动条
        self.bar_tree_h = self.tree_main.bar_tree_h
        # self.bar_tree_h = tk.Scrollbar(self.frameMain, orient=tk.HORIZONTAL)  # 底部滚动条
        self.tree = self.tree_main.body
        #
        # # 标签区
        # # self.frameSubTags = ttk.Frame(self.frameLeft)  # ,width=600)
        # self.frameSubTags = ttk.Frame(self.frameMain, width=int(conf.ui_ratio*300))
        # self.frameSubTags.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
        # 文件夹列表

        if True:
            # self.bar_folder_v = tk.Scrollbar(self.frameFolder, width=int(16*conf.ui_ratio))
            # # self.bar_folder_v = ttk.Scrollbar(self.frameFolder)#, width=16)
            # self.bar_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
            #
            self.tree_lst_folder = ttk.Treeview(self.frameFolder,
                                                selectmode=tk.BROWSE,
                                                style='Dark.Treeview',
                                                show="tree",
                                                yscrollcommand=self.bar_folder_v.set)  # , height=18)
            self.bar_folder_v.config(command=self.tree_lst_folder.yview)

            # self.tree_lst_folder.heading("folders", text="已关注的文件夹", anchor='w')
            # self.tree_lst_folder.column('folders', width=300, anchor='w')
            #
            self.tree_lst_folder.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=0, pady=0)

            # update_folder_list(self.tree_lst_folder)

        # 子文件夹列表
        if True:
            self.bar_sub_folder_v = tk.Scrollbar(self.frameSubFolder, width=int(16*conf.ui_ratio))
            if conf.TREE_SUB_SHOW == 'sub_folder':
                pass

            self.tree_lst_sub_folder = ttk.Treeview(self.frameSubFolder,
                                                    columns=['folders'],
                                                    # columns = ['index','type','folders','folder_path'],
                                                    displaycolumns=['folders'],
                                                    selectmode=tk.BROWSE,
                                                    show="headings",
                                                    # show="tree",
                                                    # cursor='hand2',
                                                    style="Dark.Treeview",
                                                    yscrollcommand=self.bar_sub_folder_v.set)  # , height=18)

            self.tree_lst_sub_folder.heading("folders", text="子文件夹", anchor='w')
            self.tree_lst_sub_folder.column('folders', width=int(conf.ui_ratio*300), anchor='w')
            self.bar_sub_folder_v.config(command=self.tree_lst_sub_folder.yview)
            #
            # update_sub_folder_list(lst_sub_path) # 填充内容
            if conf.TREE_SUB_SHOW == 'sub_folder':
                self.bar_sub_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
                self.tree_lst_sub_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
        #
        # 标签列表：
        if True:
            self.v_tag_search = tk.Entry(self.frameSubTags)
            self.bar_sub_tag_v = tk.Scrollbar(self.frameSubTags, width=16)
            if conf.TREE_SUB_SHOW == 'tag':
                # v_tag_search.pack(side=tk.TOP,expand=0,fill=tk.X)
                pass

            self.tree_lst_sub_tag = ttk.Treeview(self.frameSubTags,
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
            self.tree_lst_sub_tag.column('tags', width=int(220*conf.ui_ratio), anchor='w')
            self.bar_sub_tag_v.config(command=self.tree_lst_sub_tag.yview)
            #
            if True:  # conf.TREE_SUB_SHOW == 'tag':
                self.bar_sub_tag_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
                self.tree_lst_sub_tag.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
        #
        # tree_lst_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=10)
        # tree_lst_sub_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=10)
        #
        vPDX = 10  # 10
        vPDY = 5  # 5

        self.bt_clear = ttk.Button(self.frame0,
                                   # style='Light.TButton',
                                   text='清空',
                                   # image=self.PIC_DICT['cancel_20'],
                                   command=exec_clear_search_items)

        # bt_search=tk.Button(frame0,text='搜索', command=exec_search,bd=0,activebackground='red')
        self.bt_search = ttk.Button(self.frame0,
                                    # style='Light.TButton',
                                    text='搜索',
                                    # image=self.PIC_DICT['search_20'],
                                    command=exec_search)  # ,bd=0,activebackground='red')

        if True:  # 子文件夹搜索
            self.lable_sub_folders = tk.Label(self.frame0, text='子文件夹')
            if conf.TREE_SUB_SHOW == 'tag':
                pass

            self.v_sub_folders['value'] = [''] + lst_sub_path
            self.v_sub_folders['state'] = 'readonly'

            self.v_sub_folders.bind('<<ComboboxSelected>>', on_sub_folders_choose)

        # set_search_tag_values(lst_tags)

        self.v_tag['state'] = 'readonly'  # 只读
        self.v_tag.bind('<<ComboboxSelected>>', exec_search)
        self.v_tag.bind('<Return>', exec_search)  # 绑定回车键

        self.lable_search = ttk.Label(self.frame0, text='关键词')
        self.v_search.bind('<Return>', exec_search)  # 绑定回车键

        #
        # 布局： #####
        #    

        nx = 1
        self.bt_clear.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        nx += 1
        self.bt_search.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        #
        nx += 1
        self.v_search.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        nx += 1
        self.lable_search.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        #
        if conf.TREE_SUB_SHOW == 'tag':
            nx += 1
            self.v_sub_folders.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
            nx += 1
            self.lable_sub_folders.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
        elif conf.TREE_SUB_SHOW == 'sub_folder':
            nx += 1
            self.lable_tag = ttk.Label(self.frame0, text='标签')
            #
            # 2021年12月2日 隐藏了标签下拉框
            # self.v_tag.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
            nx += 1
            # self.lable_tag.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)  #
            nx += 1
            #

            # 只看当前文件夹
            self.v_this_folder = tk.IntVar()
            self.v_this_folder.set(0)
            self.this_folder = ttk.Checkbutton(self.frame0,
                                               text='只显示当前文件夹内容',
                                               variable=self.v_this_folder,
                                               command=exec_search,
                                               onvalue=1, offvalue=0)
            self.this_folder.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)
            # 文件夹分层
            self.v_folder_layers = tk.IntVar()
            self.v_folder_layers.set(1)
            self.folder_layers = ttk.Checkbutton(self.frame0,
                                                 text='按子文件夹分组',
                                                 variable=self.v_folder_layers,
                                                 command=exec_search,
                                                 onvalue=1, offvalue=0)
            self.folder_layers.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)
            #
            # 只看笔记
            self.v_note_only = tk.IntVar()
            self.v_note_only.set(0)
            self.cb_note = ttk.Checkbutton(self.frame0,
                                           text='只显示笔记',
                                           variable=self.v_note_only,
                                           command=exec_search,
                                           onvalue=1, offvalue=0)
            # self.cb_note.pack(side=tk.RIGHT, expand=0, padx=0 if nx % 2 == 0 else vPDX, pady=vPDY)
            #
        self.bt_test = ttk.Button(self.frame0, text='测试功能', command=function_for_testing)
        if DEVELOP_MODE:
            self.bt_test.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        # 布局
        self.bar_tree_h.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=2)  # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

        self.tree.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=2, pady=1)

        self.bar_tree_v.pack(side=tk.LEFT, expand=0, fill=tk.Y, padx=2, pady=1)  # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

        vPDX = 10
        vPDY = 5

        # 进度条
        self.frame_prog = ttk.Frame(self.frameBtm)
        # frame_prog.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY)
        self.progressbar_file = ttk.Progressbar(self.frame_prog, variable=self.prog, mode='determinate')
        self.progressbar_file.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)

        # self.lable_sum = tk.Label(self.frameBtm, text=self.str_btm, textvariable=self.str_btm)
        self.lable_sum = ttk.Label(self.frame0, text=self.str_btm, textvariable=self.str_btm)
        self.lable_sum.pack(side=tk.LEFT, expand=0, padx=5, pady=vPDY)  #

        self.bt_settings = ttk.Button(self.frameMenu,
                                      style='Menu.TButton',
                                      # width=304,
                                      image=self.PIC_DICT['menu_3'],
                                      # compound=tk.LEFT,
                                      # background='green',
                                      # relief='flat',
                                      padding=(10, 4, 10, 4),
                                      text='菜单',
                                      )  # ,command=show_online_help)

        self.bt_settings.pack(side=tk.LEFT, expand=0, padx=5, pady=vPDY)  #
        #
        # 站位空白块，用于出现在滚动条顶部空间
        # self.canvas_space = tk.Canvas(self.frameMenu, bg='#e8e8e7',
        #                               relief='flat', borderwidth=0,
        #                               width=(16*conf.ui_ratio),
        #                               )
        # self.canvas_space.pack(side=tk.RIGHT, fill='y', expand=0,)
        #
        # self.bt_folder_add.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #
        # self.bt_new = ttk.Button(self.frame0, text='新建笔记')  # ,state=tk.DISABLED)#,command=update_main_window)
        # self.bt_new.pack(side=tk.LEFT, expand=0, padx=0, pady=vPDY)  #
        #
        self.bt_reload = ttk.Button(self.frameBtm,
                                    text='刷新',
                                    command=update_main_window,
                                    )
        self.bt_reload.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        self.bt_add_tag = ttk.Button(self.frameBtm, text='添加标签',
                                     command=exec_tree_add_tag_via_dialog)  # , command=input_new_tag
        self.bt_add_tag.pack(side=tk.RIGHT, expand=0, padx=0, pady=vPDY)  #

        self.bt_new = ttk.Button(self.frameBtm, text='新建笔记')  # ,state=tk.DISABLED)#,command=update_main_window)
        self.bt_new.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        self.bt_readme = ttk.Button(self.frameBtm, text='readme')  # ,state=tk.DISABLED)#,command=update_main_window)
        self.bt_readme.pack(side=tk.RIGHT, expand=0, padx=0, pady=vPDY)  #

        # 新标签的输入框
        self.v_inp = ttk.Combobox(self.frameBtm, width=int(16*conf.ui_ratio))
        # v_inp.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        self.v_inp.bind('<Return>', input_new_tag)
        self.v_inp['value'] = lst_tags
        #
        self.lable_tag = tk.Label(self.frameBtm, text='添加新标签')
        # lable_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        #            
        # 其他初始化设定
        if ALL_FOLDERS == 1:
            self.bt_folder_drop.configure(state=tk.DISABLED)
        #
        # tree.pack(expand = True, fill = tk.BOTH)
        #
        # 测试气泡
        # b = tix.Balloon(window, statusbar=None)
        # b.bind_widget(bt_clear,balloonmsg='test',statusmsg=None)
        #
        self.bar_tree_v.config(command=self.tree.yview)
        self.bar_tree_h.config(command=self.tree.xview)
        # 样式
        '''
        for tar in [self.tree_lst_folder,self.tree_lst_sub_folder,self.tree_lst_sub_tag,self.tree]:
            tar.tag_configure('line1',background="#F2F2F2")
            # tar.tag_configure('line1',background="#F8F8F8")
            # tar.tag_configure('line1',background="#FFFFFF")
            # tar.tag_configure('folder2',background="#FFFFFF")
            tar.tag_configure('folder2',background="#F2F2F2")
            tar.tag_configure('pick_up',foreground="#f37625",font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
            tar.tag_configure('pick_copy',foreground="#2d7d9a",font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))'''
        self.window.iconbitmap(LOGO_PATH)  # 左上角图标 #

    def update_readme(self, text_in = None):
        """
        用于更新 readme 里面的内容
        """
        text_to_show = text_in
        current_path = conf.lst_my_path_long_selected[0]
        #
        if text_in is None:
            text_to_show = '（当前目录没有说明文档）'
            try:
                # 检查当前是否是文件夹，也就是二级目录
                tmp_files = os.listdir(current_path)
                # 检查当前文件夹内是否有readme.md
                # 读取前5000字
                if 'readme.md' in tmp_files:
                    app.frameReadme.configure(height=240)
                    try:
                        with open(current_path+'/readme.md', 'rb') as f:
                            text_to_show = f.read(5000).decode('utf-8')
                    except Exception as e:
                        with open(current_path+ '/readme.md', 'rb') as f:
                            text_to_show = f.read(5000).decode('gbk','ignore')
                    if len(text_to_show)==0:
                        text_to_show = '（当前目录的说明文档 readme.md 内容为空）'
                else:
                    app.frameReadme.configure(height=1)  # 隐藏高度
                    #
            except Exception as e:
                text_to_show = str(e)

        self.text_readme.configure(state='normal')
        self.text_readme.delete('1.0', tk.END)
        self.text_readme.insert(tk.END, text_to_show)
        self.text_readme.configure(state='disabled')

    def bind_funcs(self):
        # 功能绑定
        #
        self.bt_folder_add.configure(command=exec_folder_add_click)  # 增加文件夹
        self.bt_folder_drop.configure(command=exec_folder_drop)  # 减少文件夹
        #
        # 设置拖拽反映函数
        windnd.hook_dropfiles(self.tree_lst_folder, func=exec_folder_add_drag)
        windnd.hook_dropfiles(self.tree, func=exec_tree_drag_enter_popupmenu)
        windnd.hook_dropfiles(self.tree_lst_sub_tag, func=exec_tree_drag_enter_move)
        # windnd.hook_dropfiles(self.tree, func=exec_tree_drag_enter)

        # 各种功能的绑定
        # tree_lst_folder.bind('<<ListboxSelect>>',on_folder_choose)
        # tree_lst_folder.bind('<Button-1>',on_folder_choose)
        self.tree_lst_folder.bind('<ButtonRelease-1>', on_folder_choose)
        self.tree_lst_folder.bind('<KeyRelease-Up>', on_folder_choose)
        self.tree_lst_folder.bind('<KeyRelease-Down>', on_folder_choose)
        self.tree_lst_folder.bind("<Motion>", exec_tree_folder_mouse_highlight)
        #
        # tree_lst_sub_folder.bind('<<TreeviewSelect>>', on_sub_folders_choose) # 会导致重复加载
        self.tree_lst_sub_folder.bind('<ButtonRelease-1>', on_sub_folders_choose)
        self.tree_lst_sub_folder.bind('<KeyRelease-Up>', on_sub_folders_choose)
        self.tree_lst_sub_folder.bind('<KeyRelease-Down>', on_sub_folders_choose)
        #
        self.tree_lst_sub_tag.bind('<ButtonRelease-1>', on_sub_tag_choose)
        self.tree_lst_sub_tag.bind('<KeyRelease-Up>', on_sub_tag_choose)
        self.tree_lst_sub_tag.bind('<KeyRelease-Down>', on_sub_tag_choose)
        self.tree_lst_sub_tag.bind("<Motion>", exec_tree_tag_mouse_highlight)

        # tree.tag_configure('line1', background='#EEEEEE')  # 灰色底纹
        #
        self.tree_lst_folder.bind("<Button-3>", exec_tree_folder_right_click)  # 绑定文件夹区域的右键功能
        # self.tree_lst_folder.bind("<ButtonRelease-3>", show_popup_menu_folder)  # 绑定文件夹区域的右键功能
        #
        self.tree_lst_sub_folder.bind("<Button-3>", show_popup_menu_sub_folder)  # 绑定文件夹区域的右键功能
        #
        # 程序内快捷键
        self.window.bind_all('<Control-n>', exec_create_note)  # 绑定添加笔记的功能。
        self.window.bind_all('<Control-f>', jump_to_search)  # 跳转到搜索框。
        self.window.bind_all('<Control-t>', exec_tree_add_tag_via_dialog)  # 快速输入标签。
        #
        # self.tree.bind('<Control-X>', exec_tree_file_cut_ctn)  # 拿起。
        # self.tree.bind('<Control-x>', exec_tree_file_cut)  # 拿起。
        # self.tree.bind('<Control-C>', exec_tree_file_copy_cnt)  # 拿起。
        # self.tree.bind('<Control-c>', exec_tree_file_copy)  # 拿起。
        # self.tree.bind('<Control-v>', exec_tree_file_put_down)  # 放下。
        self.tree_lst_folder.bind('<Control-v>', exec_tree_file_put_down)  # 放下，点选文件夹之后仍然可以操作，可以提高用户体验。
        # self.tree.bind('<F2>', exec_tree_file_rename)  # 重命名
        # self.tree.bind('<Delete>', exec_tree_file_delete)  # 重命名
        # self.tree.bind("<Motion>", exec_tree_mouse_highlight)

        self.frameMenu.bind("<Motion>", exec_tree_folder_remove_mouse_highlight)

        # self.tree.bind('<Double-Button-1>', exec_tree_file_open)
        # self.tree.bind('<Return>', exec_tree_file_open)
        # self.tree.bind("<Button-3>", exec_tree_right_click)  # 绑定文件区域的右键功能
        # self.tree.bind("<Button-1>", exec_tree_left_click)  # 绑定文件区域的右键功能
        # self.tree.bind("<ButtonRelease-3>", show_popup_menu_file)  # 绑定文件夹区域的右键起功能
        # self.tree.bind('<F5>', update_main_window)  # 刷新。
        # self.tree.bind('<space>', self.call_space)  # 刷新。
        # #
        # self.tree.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记
        self.tree_lst_folder.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记
        #
        # window.bind_all('<Control-t>',jump_to_tag) # 跳转到标签框。
        #
        # 按钮功能绑定
        # bt_setting.configure(command=show_window_setting) # 

        # bt_folder_drop.configure(command=exec_tree_add_tag_via_dialog)  # 加标签
        # bt_settings.configure(command=show_popup_menu_main)  # 菜单按钮
        self.bt_settings.bind("<ButtonRelease-1>", show_popup_menu_main)  # 菜单按钮
        self.bt_new.configure(command=exec_create_note)
        self.bt_readme.configure(command=exec_create_note_readme)

class td_tree_folder():
    """
    将左侧的文件夹列表提取出来作为独立的类
    """
    def __init__(self):
        """
        """
        self.name = 'foler_frame'
        self.body = null
        self.tree_folder = self.body

    def update(self):
        self.body

class td_tree_file():
    """
    """
    def __init__(self, frame_root, frame_bottom=None):
        """
        frame_root: 基础框架，存放tree用到的框架。
        frame_bottom: 底部框架，用于显示横向滚动条。
        """
        if frame_bottom is None:
            frame_bottom = frame_root
        # 主文件列表
        columns = ("index", "file", "tags", "modify_time", "size", "file0")
        column_text = ("序号", "文件名", "标签", "修改时间", "大小(kB)", "完整路径")
        tree_displaycolumns = ["tags", "modify_time", "size"]  # "file",
        col_dic = {
            "序号": {
                "name": "index",
                "text": "序号",
                "visb": False,
                "head_anch": "center",
                "body_anch": "center",
                "width": 30,
                "head_command": None
            },
            "文件名": {
                "name": "file",
                "text": "文件名",
                "visb": True,
                "head_anch": "w",
                "body_anch": "w",
                "width": 400,
                "head_command": tree_order_filename
            }
        }
        self.name = '文件列表'
        self.bar_tree_v = tk.Scrollbar(frame_root, width=int(16 * conf.ui_ratio))  # 右侧滚动条
        self.bar_tree_h = tk.Scrollbar(frame_bottom, orient=tk.HORIZONTAL, width=int(16 * conf.ui_ratio))  # 底部滚动条
        self.body = ttk.Treeview(frame_root,
                                 # show="headings",  # 如果有这句话，就不能显示图标
                                 columns=columns,
                                 displaycolumns=tree_displaycolumns, \
                                 # selectmode=tk.BROWSE, \
                                 selectmode='extended', \
                                 yscrollcommand=self.bar_tree_v.set,
                                 xscrollcommand=self.bar_tree_h.set,
                                 )  # , height=18)
        self.tree = self.body
        #
        self.tree.column('#0', width=700, anchor='w')  # ,stretch=tk.NO)
        self.tree.column('index', width=30, anchor='center')
        self.tree.column('file', width=600, minwidth=100, anchor='w')
        self.tree.column('tags', width=200, minwidth=100, anchor='w')
        self.tree.column('modify_time', width=120, minwidth=120, anchor='e')  # ,stretch=tk.NO)
        self.tree.column('size', width=60, minwidth=80, anchor='e')  # ,stretch=tk.NO)
        self.tree.column('file0', width=80, anchor='w')
        #
        self.tree.heading('#0', text='名称', anchor='w', command=tree_order_filename)
        self.tree.heading("index", text="序号", anchor='center')
        self.tree.heading("file", text="文件名", anchor='w', command=tree_order_filename)
        self.tree.heading("tags", text="标签", anchor='w', command=tree_order_tag)
        self.tree.heading("modify_time", text="修改时间", anchor='e', command=tree_order_modi_time)
        self.tree.heading("size", text="大小(kB)", anchor='e', command=tree_order_size)
        self.tree.heading("file0", text="完整路径", anchor='w', command=tree_order_path)
        #
        # 后续处理工作
        self.bind_func()  # 绑定功能

    def clear(self):
        """
        列表清空
        """
        pass

    def update(self):
        """
        刷新
        """
        pass

    def bind_func(self):
        """
        绑定快捷键或者行为
        """
        self.tree.bind('<Control-X>', exec_tree_file_cut_ctn)  # 拿起。
        self.tree.bind('<Control-x>', exec_tree_file_cut)  # 拿起。
        self.tree.bind('<Control-C>', exec_tree_file_copy_cnt)  # 拿起。
        self.tree.bind('<Control-c>', exec_tree_file_copy)  # 拿起。
        self.tree.bind('<Control-v>', exec_tree_file_put_down)  # 放下。
        self.tree.bind('<F2>', exec_tree_file_rename)  # 重命名
        self.tree.bind('<Delete>', exec_tree_file_delete)  # 删除
        self.tree.bind("<Motion>", exec_tree_mouse_highlight) # 指向对象高亮
        self.tree.bind('<Double-Button-1>', exec_tree_file_open)
        self.tree.bind('<Return>', exec_tree_file_open)
        self.tree.bind("<Button-3>", exec_tree_right_click)  # 绑定文件区域的右键功能
        self.tree.bind("<Button-1>", exec_tree_left_click)  # 绑定文件区域的左键功能
        self.tree.bind("<ButtonRelease-3>", show_popup_menu_file)  # 绑定文件夹区域的右键起功能
        self.tree.bind('<F5>', update_main_window)  # 刷新。
        self.tree.bind('<space>', self.call_space)  # 预览基本情况。
        #
        self.tree.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记

    def call_space(self, event=None):
        """
            {'fname_0': fname_0,  # 去掉标签之后的文件名
            'ftags': ftags,
            'ffname': ffname,  # 原始文件名，带标签的
            'filename_origional': ffname,  # 原始文件名，带标签、扩展名的
            'fpath': fpath,
            'f_path_only': fpath,
            'fname': fname,
            'filename_no_ext': fname,  # 去掉扩展名的文件名
            'fename': fename,  # 扩展名
            'file_ext': fename,  # 扩展名
            'full_path': tar, # 全路径
            'fsize': fsize_k, #
            'file_full_path': tar,  # 完整路径，和输入参数完全一样
            'file_mdf_time': file_modify_time,
            'file_crt_time': file_create_time
            }
        """

        if len(self.tree.selection()) == 1:
            try:
                t = self.tree.selection()[0]
                if is_tree_item_enable(t):
                    pth = self.tree.item(t, "values")[-1]
                    res = get_file_part(pth)

                    msg_lst = ["完整文件名：\n    ",
                               str(res['ffname']),
                               '\n\n',
                               "文件名（去标签）：\n    ",
                               str(res['fname_0']),
                               '\n\n',
                               '标签：\n    ',
                               res['ftags'],
                               '\n\n',
                               '修改日期：\n    ',
                               res['file_mdf_time'],
                               '\n\n',
                               '大小（kB）：\n    ',
                               res['fsize'],
                               '\n\n',
                               '完整路径：\n    ',
                               str(res['full_path']),
                               ]
                    msg = map(str, msg_lst)
                    TdSpaceWindow(app.window, '详情', ''.join(msg),ui_ratio=conf.ui_ratio,)
            except Exception as e:
                print(e)
                TdSpaceWindow(app.window, '错误', '文件加载异常',ui_ratio=conf.ui_ratio,)



###########################################################
###########################################################
# 主程序开始
###########################################################
###########################################################


"""
def check_single_instance():  # 检查是否已经运行；
    import win32gui
    import win32com.client
    import sys

    wd_name = cst.TAR + ' ' + cst.VER
    pr_name = 'tagdox'
    have_exe = 0
    try:
        # win32gui.GetWindow()
        shell = win32com.client.Dispatch("WScript.Shell")  # 未找到函数
        shell.AppActivate(wd_name)
        # print('\n已经存在打开的实例\n')
        have_exe = 1
        
        win = win32gui.FindWindow(None,wd_name)
        print(win)
        if win:
            have_exe = 1
            root = tk.Tk()
            t = tk.messagebox.showerror(title='ERROR',
                message='本程序已经在运行。')
            root.destroy()
            # win.ShowWindow(win32con.SW_SHOWNORMAL)
            print('\n已经存在打开的实例\n')
        else:
            print('\n不存在打开的实例\n')
    except Exception as e:
        print(e)
        have_exe = 0
    return have_exe
"""

# from tendo import singleton
# me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

# have_exe = check_single_instance()
# if __name__ == '__main__' and have_exe==0:


class td_flag:
    def __init__(self):
        self.flag_inited = 0  # 代表是否已经加载完成
        self.flag_break = 0  # 代表是否中断查询
        self.flag_running = 0  # 代表是否有正在运行的查询
        self.flag_root_folder = 0
        self.flag_sub_folders_changed = 0
        self.flag_file_changed = 0
        self.flag_folder_changed = 0


if __name__ == '__main__':
    # 变量 ###########################################################
    q = queue.Queue()
    #
    lst_files_to_go = []  # 所有文件的完整路径
    dT = []
    dicT = dict()
    #
    lst_tags = []  # 全部标签
    lst_tags_selected = []
    #
    lst_sub_path = []  # 子文件夹得到全局变量
    lst_sub_path_selected = []
    #
    lst_pick_up_files = []  # 程序内剪切板
    lst_pick_up_items = []  # 程序内剪切板
    state_pick_up = 'move'
    folder_to_move = ''  # 待移动的文件夹
    #
    # dict_path = dict()  # 用于列表简写和实际值
    # dict_folder_groups = dict()  # 文件夹对应分组
    #
    flag = td_flag()
    #
    # 加载设置参数。
    # conf.json_data = OPT_DEFAULT  # 用于后面处理的变量。
    conf.exec_json_file_load()
    ###########################################################
    #

    app = td_main_app()  # 主程序
    app.bind_funcs()
    #
    # readme 部分
    long_text = """
    用默认的 UTF-8 编码。如果你的文件使用了其他的编码，你需要在 open 函数中指定正确的编码，
    例如 open(filename, 'r', encoding='your-encoding')。 
    """
    default_readme = long_text + long_text + long_text
    app.update_readme()
    #
    # window = tk.Tk()  # 主窗口
    # window = app.window  # 主窗口
    # SCREEN_WIDTH = conf.SCREEN_WIDTH
    # SCREEN_HEIGHT = conf.SCREEN_HEIGHT
    # %%
    #
    # 样式
    # from ttkbootstrap import Style as TB_Style
    # style = TB_Style(theme='yeti')
    style = ttk.Style()

    set_style(style)

    # str_btm = tk.StringVar()  # 最下面显示状态用的
    # str_btm.set("加载中")
    # prog = tk.DoubleVar()  # 进度
    # prog_win = ''
    # 
    vPDX = 10
    vPDY = 5
    #
    # %%
    # ###########################################################
    #
    # 数据初始化
    '''if ALL_FOLDERS == 1:  # 对应是否带有“所有文件夹”这个功能的开关
        conf.lst_my_path_long_selected = conf.lst_my_path_long.copy()  # 用这个变量修复添加文件夹之后定位不准确的问题。
        lst_files_to_go = get_data(conf.lst_my_path_long_selected)
    else:
        try:
            conf.lst_my_path_long_selected = [conf.lst_my_path_long[0]] # 默认加载第一个文件夹的内容
            lst_files_to_go = get_data(conf.lst_my_path_long_selected)
        except:
            lst_files_to_go = get_data()  # 此处有隐患，还没条件测试
    #
    (dT, lst_tags) = get_dt()'''
    # 
    # 增加排序方向的可视化（三角形）
    show_tree_order()
    #
    PIC_LST = [tk.PhotoImage(file="./resources/imgs/龙猫.gif"),
               tk.PhotoImage(file="./resources/icons/folder_100_20.png")]
    PIC_DICT = {
        "龙猫": tk.PhotoImage(file="./resources/imgs/龙猫.gif"),
        "folder_100_20": tk.PhotoImage(file="./resources/icons/folder_100_20.png"),
        "folder_75_20": tk.PhotoImage(file="./resources/icons/folder_75_20.png"),
        "folder_50_20": tk.PhotoImage(file="./resources/icons/folder_50_20.png"),
        "folder_25_20": tk.PhotoImage(file="./resources/icons/folder_25_20.png")}
    IMAGE_FOLDER = tk.PhotoImage(file='./resources/imgs/gitee_homepage.png')
    #
    # 运行
    update_folder_list()  # 文件夹列表
    #
    try:
        tmp_itm_sel = app.tree_lst_folder.get_children()[0]
        tmp_itm_sel = app.tree_lst_folder.get_children(tmp_itm_sel)[0]
        tmp_path_long = app.tree_lst_folder.item(tmp_itm_sel, "values")[-1]
        conf.lst_my_path_long_selected = [tmp_path_long,]  # 默认加载第一个文件夹的内容
        lst_files_to_go = get_data(conf.lst_my_path_long_selected)
    except:
        lst_files_to_go = get_data()  # 此处有隐患，还没条件测试
    #
    (dT, lst_tags) = get_dt()
    #

    # update_sub_folder_list(lst_sub_path) # 填充子文件夹内容
    set_search_tag_values(lst_tags)  # 标签内容
    #
    try:
        exec_tree_add_items(app.tree, dT)  # 主要内容
    except Exception as e:
        print(e)
        print('初始化主列表发生错误')
        app.str_btm.set('已就绪')
        pass
    #
    #
    flag.flag_inited = 1  # 代表前面的部分已经运行过一次了
    set_prog_bar(0)
    #
    if True:
        sub_task = threading.Thread(target=process_update_data, args=(conf.lst_my_path_long,))
        sub_task.setDaemon(True)
        sub_task.start()
    #
    app.window.mainloop()
    print('主程序运行结束')
