# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""

import multiprocessing
import os
import tkinter as tk
from tkinter import ttk
# import tkinter.tix as Tix 
# from tkinter import tix
from tkinter import Text, Variable
import json
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import font
from tkinter.constants import INSERT
import windnd
from os.path import isdir
from os.path import isfile
import time
import threading  # 多线程
from multiprocessing import Pool # 进程
from multiprocessing import Process
# from docx import Document# 用于创建word文档
# import ctypes # 用于调整分辨率 #

import shutil
import queue

# import my_logger
# import send2trash # 回收站（目前作废）

URL_HELP = 'https://gitee.com/horse_sword/my-local-library'  # 帮助的超链接，目前是 gitee 主页
URL_ADV = 'https://gitee.com/horse_sword/my-local-library/issues'  # 提建议的位置
TAR = 'Tagdox / 标签文库'  # 程序名称
VER = 'v0.16.1.1'  # 版本号

'''
## 近期更新说明
#### v0.16.1.1 2021年8月15日
更新了关于页面的二维码。
#### v0.16.1.0 2021年8月13日
设置项增加对最后目录的解析设置、对标签的解析设置。
#### v0.16.0.1 2021年8月13日
优化最后一级目录作为标签对空格的解析。
#### v0.16.0.0 2021年8月12日
启动时增加后台进程，显著提高数据加载速度。
'''
# %%
#
# 常量，开发用，不准备进入设置的
DEVELOP_MODE = 0  # 开启调试模式
LOGO_PATH = './src/LOGO.ico'
cALL_FILES = ''  # 标签为空的表达方式，默认是空字符串
PROG_STEP = 500  # 进度条刷新参数
CLEAR_AFTER_CHANGE_FOLDER = 2  # 切换文件夹后，是否清除筛选。0 是保留，其他是清除。
DIR_LST = ['▲', '▼']  # 列排序标题行
HEADING_LST = ['file', 'tags', 'modify_time', 'size', 'file0']
HEADING_LST_TXT = ['文件名', '标签', '修改时间', '文件大小(kB)', '完整路径']
MULTI_PROC = 1  # 并发进程数，设置为1或更低就单独进程。
MULTI_FILE_COUNT = 400
#
# 可以做到设置里面的常量
ORDER_BY_N = 2  # 初始按哪一列排序，1代表标签，后面按顺序对应
ORDER_DESC = True  # 是否逆序
LARGE_FONT = 10  # 表头字号
MON_FONTSIZE = 9  # 正文字号
FONT_TREE_HEADING=('微软雅黑', LARGE_FONT)
FONT_TREE_BODY=('微软雅黑', MON_FONTSIZE)
EXP_FOLDERS = ['_img']  # 排除文件夹名称，以后会加到自定义里面
ALL_FOLDERS = 2  # 文件夹列表是否带“（全部）”,1 在前面，2在末尾，其余没有
NOTE_NAME = '未命名笔记'  # 新建笔记的默认名称
DRAG_FILES_ADD_TAG = True # 为拖拽进来的新增文件统一添加当前选中的标签
TREE_SUB_SHOW = ['tag','sub_folder'][1] # 决定左侧布局是标签模式还是子文件夹模式。// 可修改
FOLDER_AS_TAG = 0 # 最后多少层文件夹名称，强制作为标签（即使不包括V_SEP） // 可修改
TAG_EASY = 1 # 标签筛选是严格模式还是简单模式，1是简单模式，名称有就行；0是严格模式。 // 可修改

V_SEP = '^'  # 标签分隔符。// 可修改
V_FOLDERS = 2  # 标签识别文件夹深度，// 可修改

NOTE_EXT_LIST = ['.md', '.txt', '.docx', '.rtf']
NOTE_EXT = '.docx'  # 新建笔记的类型 // 可修改
QUICK_TAGS = ['@PIN', '@TODO', '@toRead', '@Done']  # 快速添加标签
FILE_DRAG_MOVE = 'move'  # 文件拖动到列表的时候，是复制，还是移动。// 可修改。
# 取值：'move' 'copy'。// 可修改

#
try:
    if isfile('D:/MyPython/开发数据/options_for_tagdox.json'):
        print('读取开发模式的配置文件')
        OPTIONS_FILE = 'D:/MyPython/开发数据/options_for_tagdox.json'
    else:
        print('读取标准模式的配置文件')
        OPTIONS_FILE = 'options_for_tagdox.json'  # 配置文件的名称
except:
    print('读取标准模式的配置文件')
    OPTIONS_FILE = 'options_for_tagdox.json'  # 配置文件的名称

OPT_DEFAULT = {
    "options": {
        "sep": "^",
        "vfolders": "2",
        "note_ext": ".docx",
        "file_drag_enter": "copy",
        "TREE_SUB_SHOW":TREE_SUB_SHOW
    },
    "folders": [
    ]
}


# %%
#######################################################################

def get_split_path(full_path) -> list:
    '''
    通用函数：    
    将完整路径按照斜杠拆分，得到每个文件夹到文件名的列表。
    '''
    test_str = full_path.replace('\\', '/', -1)
    test_str_res = test_str.split('/')
    return (test_str_res)


def exec_tree_clear(tree_obj) -> None:  #
    '''
    通用函数。
    通用的 treeview 清除函数，因为是通用的，所以必须带参数。
    参数是 具体的 treeview 对象。
    '''
    x = tree_obj.get_children()
    for item in x:
        tree_obj.delete(item)
    if flag_inited == 1:
        window.update()


def safe_get_name(new_name) -> str:
    '''

    输入: 目标全路径; 
    返回: 安全的新路径（可用于重命名、新建等）
    输入和输出都是字符串。

    '''
    n = 1
    [tmp_path, tmp_new_name] = os.path.split(new_name)

    p = tmp_new_name.find(V_SEP)
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


def remove_to_trash(filename, remove=True):
    '''
    删除文件，remove=True就直接删除，否则移动到回收站。
    但是移动到回收站的功能尚未调试成功，所以没有启用。参数只能是 True。
    '''
    if remove:
        print('直接删除')
        os.remove(filename)
    else:
        print('删除到回收站')
        # send2trash.send2trash(filename) 


def exec_safe_rename(old_name, new_name):
    '''
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 如果重命名成功，返回添加数字之后的最终文件名；
    如果重命名失败，返回原始文件名。
    '''
    old_name = old_name.replace('\\', '/')
    new_name = new_name.replace('\\', '/')
    '''
    n=1
    [tmp_path,tmp_new_name]=os.path.split(new_name)
    # tmp_path=''
    # tmp_new_name=new_name
    p=tmp_new_name.find(V_SEP)
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


def safe_copy(old_name, new_name, opt_type='copy'):
    '''
    安全复制或移动文件。
    参数 opt_type 是 'copy' 或 'move'。
    '''
    old_name = old_name.replace('\\', '/')
    new_name = new_name.replace('\\', '/')
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
# 加载设置项 json 内容。保存到 opt_data 变量中，这是个 dict。


def write_json_file(tar=OPTIONS_FILE, data=None):
    '''
    将 json_data变量的值，写入 json 文件。
    可以不带参数，随时调用就是写入json。
    '''
    global json_data
    if data is None:
        data = json_data
    try:
        with open(tar, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        print('json文件写入异常')


def set_json_options(key1, value1, need_write=True):
    '''
    修改设置项，以键值对的方式修改。
    会自动触发 exec_update_json（写入json文件）.
    参数 need_write 代表了是否需要写入文件。默认是修改后立刻写入。
    '''
    global json_data
    opt_data = json_data['options']  # 设置
    opt_data[key1] = value1
    #
    if need_write:
        write_json_file(data=json_data)
    # load_json_file_data()
    pass


def load_json_file_data(load_settings=True, load_folders=True):
    '''
    读取json文件，获取其中的参数，并存储到相应的变量中。

    如果json文件读取失败，则按照初始化标准重建这个文件。

    依赖函数：update_json。
    '''
    global json_data
    global V_SEP, V_FOLDERS
    global NOTE_EXT, FILE_DRAG_MOVE
    global lst_my_path_long
    global lst_my_path_short
    global lst_my_path_long_selected
    global TREE_SUB_SHOW
    global FOLDER_AS_TAG
    global TAG_EASY

    need_init_json = 0
    try:
        with open(OPTIONS_FILE, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

        if load_settings:
            try:
                opt_data = json_data['options']  # 设置
            except Exception as e:
                print(e)
                pass
            try:
                V_SEP = opt_data['sep']  # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
            except Exception as e:
                print(e)
                pass
            try:
                V_FOLDERS = int(opt_data['vfolders'])  # 目录最末层数名称检查，作为标签的检查层数
            except:
                pass
            try:
                NOTE_EXT = opt_data['note_ext']  # 默认笔记类型
            except Exception as e:
                print(e)
                pass
            try:
                FILE_DRAG_MOVE = opt_data['file_drag_enter']  # 默认拖动操作
            except Exception as e:
                print(e)
                pass
            try:
                TREE_SUB_SHOW = opt_data['TREE_SUB_SHOW']  # 默认布局
            except Exception as e:
                print(e)
                pass
            #
            try:
                FOLDER_AS_TAG = opt_data['FOLDER_AS_TAG']  # 最后文件夹识别
            except Exception as e:
                print(e)
                pass
            #
            try:
                TAG_EASY = opt_data['TAG_EASY']  # 标签搜索方式
            except Exception as e:
                print(e)
                pass
            #
            print('加载基本参数成功')

        if load_folders:
            # lst_my_path_long_selected=lst_my_path_long.copy() #按文件夹筛选用
            lst_my_path_long = []
            lst_my_path_short = []

            json_folders_lst = json_data['folders']

            for i in json_folders_lst:
                # lst_my_path_long.append(i)
                tmp_L = i['pth']
                tmp_L = tmp_L.strip()
                try:
                    tmp_S = i['short'] # 如果有自定义名称，优先加载
                except:
                    tmp_S = get_split_path(i['pth'])[-1]
                tmp_S = tmp_S.replace(' ', '_')  # 修复路径空格bug的权宜之计，以后应该可以优化

                # 增加逻辑：避免短路径重名：
                j = 1
                tmp_2 = tmp_S
                while tmp_2 in lst_my_path_short:
                    j += 1
                    tmp_2 = tmp_S + "(" + str(j) + ")"
                    print(tmp_2)
                tmp_S = tmp_2
                tmp_S = tmp_S.strip()

                if tmp_S == '' or tmp_L == '':  # 出现空白文件夹
                    for j in range(len(json_folders_lst) - 1, -1, -1):
                        if json_folders_lst[j]['pth'].strip() == '':
                            json_folders_lst.pop(j)
                else:
                    lst_my_path_long.append(tmp_L)
                    lst_my_path_short.append(tmp_S)
                    tmp = {tmp_S: tmp_L}
                    dict_path.update(tmp)

            lst_my_path_long_selected = lst_my_path_long.copy()  # 此处有大量的可优化空间。
            print('加载关注文件夹列表成功')
    except:
        print('加载json异常，正在重置json文件')
        # need_init_json=1
        json_data = OPT_DEFAULT
        write_json_file()


#######################################################################
# %% 线程处理


# class thread_prog (threading.Thread):
#     '''
#     线程处理：

#     '''
#     def __init__(self,tar):
#         threading.Thread.__init__(self)
#         self.tar=tar

#     def prog_set(self,vnow):
#         self.tar.set(vnow)
#         # str_btm.set("加载中")
#         pass    


# %%

def set_prog_bar(inp, maxv=100):
    '''
    手动设置进度条。
    '''
    prog.set(inp)
    progressbar_file.update() # 刷新进度条
    if inp==0 or inp ==100:
        progressbar_file.pack_forget()
    else:
        progressbar_file.pack()
    #

    global prog_win
    try:
        prog_win
    except:
        var_exists = False
    else:
        var_exists = True
    print('进度条：')
    print(var_exists)
    try:
        if inp <= 1:
            # if var_exists == True:
            #     prog_win.set(100)
            #     del prog_win
            prog_win = my_progress_window(window, inp)

        elif inp == 100:
            prog_win.set(inp)
            # del prog_win
        else:
            prog_win.set(inp)
    except:
        pass


def get_data(ipath=None, update_sub_path=1,need_set_prog=True,is_global=True):
    '''
    根据所传入的文件夹列表 ipath，
    （1）刷新 子文件夹列表。
    （2）返回所有文件形成的 lst_files_to_go 列表。这个列表可以在 get_dt 里面调用。
    此过程消耗时间较多。
    参数 ipath 未指定时，自动取为全局变量 lst_my_path_long;
    update_sub_path 的作用是强制修改子文件夹列表【不完善】
    参数 need_set_prog 如果是 False，就不显示或更新进度条。
    '''
    print('调用 get_data 函数')

    if is_global:
        global lst_sub_path
    else:
        lst_sub_path=[]
        pass

    global flag_running  # 必须要有这句话，否则不能修改公共变量

    if ipath is None:
        ipath = lst_my_path_long

    # flag_running=1 # 标记为运行中。

    lst_sub_path_copy = lst_sub_path.copy()
    if flag_inited == 1:
        exec_tree_clear(tree)  #
        if need_set_prog :set_prog_bar(1, 30)
        str_btm.set("正在加载基础数据……")
        window.update()

    time0 = time.time()
    lst_files_to_go = []  # 获取所有文件的完整路径

    n = 1
    n_max = len(ipath)
    lst_sub_path = []

    PROG_STEP = 2
    print('\nget_data函数中获得的参数：')
    print(ipath)
    have_sub_folder=0
    #
    for vPath in ipath:
        n += 1 # 第一轮循环的时候n就是2
        #
        if flag_inited == 1 and n % PROG_STEP == 0:
            PROG_STEP *= 2
            tmp_prog = 1 + 29 * n / n_max
            if tmp_prog > 30:
                tmp_prog = 30
            if need_set_prog:set_prog_bar(tmp_prog)

        for root, dirs, files in os.walk(vPath):
            have_sub_folder+=1
            tmp = []
            vpass = 0
            #
            #
            # 文件
            if '_nomedia' in files:
                vpass=1
                continue
                # break # 这里可能不应该用break

            #
            tmp_path = get_split_path(root) # 对每个根文件夹，检查
            for tmp2 in tmp_path:
                if len(tmp2)<1:
                    continue
                if tmp2 in EXP_FOLDERS:
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
                #         and (str(new_sub_path) not in EXP_FOLDERS): # 只将一级子目录添加到列表中
                #     lst_sub_path.append(new_sub_path)
                # 子文件夹新方法：
                if have_sub_folder<=1:
                    lst_sub_path=dirs
                #
                lst_files_to_go += tmp

            if flag_break:  # 强行中断
                break
        if flag_break:
            break

    print('——————  加载 文件列表 消耗时间：——————\n')
    print(time.time() - time0)
    #
    # 更新子文件夹列表
    try:
        lst_sub_path.sort()
        lst_sub_path_copy.sort()
        if lst_sub_path == lst_sub_path_copy:
            update_sub_path = 0
        else:
            print(lst_sub_path)
            print(lst_sub_path_copy)
    except:
        pass

    if update_sub_path: # 如果参数为1的话，
        try:
            lst_sub_path.sort()
            v_sub_folders['value'] = [''] + lst_sub_path  # 强制修改子文件夹列表，但这样写【不太好】。
            v_sub_folders.current(0)
            #
            update_sub_folder_list(lst_sub_path)
        except:
            pass
    else:
        lst_sub_path = lst_sub_path_copy
    # if flag_inited==1:
    #     set_prog_bar(30,30)

    return lst_files_to_go


def get_file_part(tar):  # 
    '''
    这里输入参数 tar 是完整文件路径。
    输入完整（文件）路径，以字典的形式，返回对应的所有文件信息。
    【疑似bug】对带有空格的路径解析异常
    '''

    [fpath, ffname] = os.path.split(tar)  # fpath 所在文件夹、ffname 原始文件名
    [fname, fename] = os.path.splitext(ffname)  # fname 文件名前半部分，fename 扩展名
    lst_sp = fname.split(V_SEP)  # 拆分为多个片段
    fname_0 = lst_sp[0] + fename  # fname_0 去掉标签之后的文件名
    ftags = lst_sp[1:]  # ftags 标签部分

    mtime = os.stat(tar).st_mtime # 修改时间
    file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    ctime = os.stat(tar).st_ctime # 创建时间
    file_create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))

    fsize = os.path.getsize(tar)  # 文件大小，字节
    fsize_k = fsize / (1024)  # 换算到kB
    fsize_k = round(fsize_k, 1)

    # 对文件目录的解析算法2：
    tmp = get_split_path(fpath)
    tmp2 = []
    try:  # 只要最后若干层的目录，取变量 V_FOLDERS
        for i in range(V_FOLDERS):
            tmp2.append(tmp[-i - 1])
    except:
        pass

    for i in tmp2:
        i2 = i.split(V_SEP)
        try:
            i3 = i2[1:] # 取标签符号后面的
            # i3 = i2[0:] # 取整个子文件夹
        except:
            i3=[]
        ftags += i3
    #
    # 增加：最后若干层子文件夹作为标签的功能（默认1层）：
    for i in range(FOLDER_AS_TAG):
        try:
            if str(tmp[-1-i][0])==V_SEP:
                continue
            tags_from_folder=tmp[-1-i].split(V_SEP)
            for j in range(len(tags_from_folder)):
                tags_from_folder[j]=str(tags_from_folder[j]).replace(" ","_")
            ftags+=tags_from_folder
        except Exception as e:
            print(e)
            pass

    # 对当前文件，进行标签整理、去重并排序
    ftags = list(set(ftags))
    ftags.sort()
    #
    # 去掉空标签：
    i=0
    while i < len(ftags):
        if ftags[i]=='':
            ftags.pop(i)
        else:
            i+=1
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
            'full_path': tar, # 全路径
            'fsize': fsize_k, # 
            'file_full_path': tar,  # 完整路径，和输入参数完全一样
            'file_mdf_time': file_modify_time,
            'file_crt_time': file_create_time
            }


def dt_sort_by(elem):  
    '''
    主题表格排序
    '''
    # global ORDER_BY_N
    tmp = str(elem[ORDER_BY_N])
    if ORDER_BY_N == 3:
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
    print([V_FOLDERS, V_SEP, NOTE_EXT])
    return tmp_dt


def update_data(lst1):
    '''
    用于后台加载数据
    '''
    print('———— 后台数据加载开始 ————')

    lst_files_to_go=[]
    n=0
    flag_break=0

    global dicT

    for vPath in lst1:
        n += 1 # 第一轮循环的时候n就是2
        #

        for root, dirs, files in os.walk(vPath):
            tmp = []
            vpass = 0
            #
            #
            # 文件
            if '_nomedia' in files:
                vpass=1
                continue
                # break # 这里可能不应该用break

            #
            tmp_path = get_split_path(root) # 对每个根文件夹，检查
            for tmp2 in tmp_path:
                if len(tmp2)<1:
                    continue
                if tmp2 in EXP_FOLDERS:
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

            if flag_break:  # 强行中断
                break
        if flag_break:
            break

    for one_file in lst_files_to_go:
        # 先查字典，这样可以显著加速查询
        if one_file in dicT.keys():
            pass
        else:
            tmp = get_file_part(one_file)
            tmp_v = (str(tmp['fname_0']), tmp['ftags'], str(tmp['file_mdf_time']), tmp['fsize'], str(tmp['full_path']))
            try:
                dicT[one_file]=tmp_v
            except Exception as e:
                print(e)
                pass

    print('———— 后台数据加载完毕 ————')


def get_dt(lst_file0=None,need_set_prog=True,FAST_MODE=True):
    '''
    是最消耗时间的函数，也是获取数据的核心函数。
    输入参数是文件列表，lst_file0。
    这个参数的缺省值是来自于 get_data() 函数的 lst_files_to_go ，提供了所有文件。

    根据 lst_files_to_go 里面的文件列表，返回 (dT, lst_tags) .\n
    注意这里(dT, lst_tags)都不是全局变量，需要从返回值获得。
    
    只有 dicT 是全局变量，用于存储临时值，加快运行速度。
    '''
    print('进入 get_dt 函数')
    global dicT #

    if flag_break:
        return (None, None)

    if lst_file0 is None:
        lst_file0 = lst_files_to_go.copy()

    if flag_inited == 1:
        str_btm.set("正在解析标签……")
        window.update()
        if need_set_prog:set_prog_bar(30)

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
        if need_set_prog:set_prog_bar(50)
        for i in t:
            i.join()
        while not q.empty():
            tmp_get_dt = q.get()
            # print(tmp_get_dt)
            dT += tmp_get_dt
        if need_set_prog:set_prog_bar(70)
        # tmp_part=[]
        # print('组合之前：——————')
        # print(time.time()-time0)
        # for i in res_tmp:
        # dT+=i
        print('组合之后：——————')
        print(time.time() - time0)
        #
        #
    else:# 单线程
        
        for one_file in lst_file0:

            # 更新进度条
            n += 1
            if flag_inited == 1 and n % PROG_STEP == 0:
                if need_set_prog:set_prog_bar(30 + 69 * n / n_max)
            # 先查字典，这样可以显著加速查询
            if FAST_MODE and one_file in dicT.keys():
                tmp_v= list(dicT[one_file])

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
                tmp_v = (str(tmp['fname_0']), tmp['ftags'], str(tmp['file_mdf_time']), tmp['fsize'], str(tmp['full_path']))
                try:
                    dicT[one_file]=tmp_v
                except Exception as e:
                    print(e)
                    pass
            # if not tmp_v in dT:
            #     dT.append(tmp_v) # 查重有点费时间
            dT.append(tmp_v)
            #
            if flag_break:  # 如果被中断的话
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

    if flag_inited == 1:
        if need_set_prog:set_prog_bar(99)

    # 获取所有tag
    tmp = []
    for i in dT:
        tmp += i[1]

    lst_tags = list(set(tmp))
    lst_tags = sorted(lst_tags, key=lambda x: x.replace('\xa0', ' ').encode('gbk'))
    lst_tags = [cALL_FILES] + lst_tags
    # lst_tags.sort()

    try:
        dT.sort(key=dt_sort_by, reverse=ORDER_DESC)
    except:
        print('dT排序出现错误！')

    return (dT, lst_tags)


# %%
#######################################################################
# %%
def show_window_info():
    '''
    显示关于窗口。
    不需要任何参数。
    '''
    screenwidth = SCREEN_WIDTH
    screenheight = SCREEN_HEIGHT
    w_width = 660
    w_height = 560
    info_window = tk.Toplevel(window,background='white')
    info_window.geometry(
        '%dx%d+%d+%d' % (w_width, w_height, (screenwidth - w_width) / 2, (screenheight - w_height) / 2))
    info_window.title('关于标签文库')

    info_window.transient(window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
    info_window.grab_set()  # 模态

    info_window.deiconify()
    info_window.lift()
    info_window.focus_force()
    info_window.iconbitmap(LOGO_PATH)  # 左上角图标

    info_frame = tk.Frame(info_window, padx=5, pady=5,background='white')
    info_frame.pack(expand=0, fill=tk.BOTH)

    tmp = tk.Label(info_frame,background='white', text='\n')
    tmp.pack()
    tmp = tk.Label(info_frame,background='white', text='标签文库 / Tagdox', fg='#2d7d9a', font=('微软雅黑', 16))
    tmp.pack()
    tmp = tk.Label(info_frame,background='white', text='\n马剑 个人开发')
    tmp.pack()
    tmp = tk.Label(info_frame,background='white', text='版本：' + VER + '')
    tmp.pack()
    tmp = tk.Label(info_frame,background='white', text='Powered by Python and Tkinter\n')
    tmp.pack()

    global p_logo
    p_logo = tk.PhotoImage(file='./src/二维码设计.png')
    logolbl = tk.Label(info_frame,background='white', text='A', image=p_logo)
    logolbl.pack()

    # tmp = tk.Label(info_frame,background='white', text='（欢迎扫码访问产品动态）')
    # tmp.pack()


# 自制输入窗体
class my_input_window:
    '''
    输入窗体类。
    实现了一个居中的模态窗体。
    '''
    input_value = ''

    def __init__(self, parent, title='未命名', msg='未定义', default_value='', selection_range=None) -> None:
        '''
        自制输入窗体的初始化；
        参数：
        selection_range 是默认选中的范围。
        '''

        # 变量设置
        self.form0 = parent  # 父窗格
        #
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
        self.w_width = 800
        self.w_height = 160
        #
        # 屏幕中央：
        # self.screenwidth = SCREEN_WIDTH
        # self.screenheight = SCREEN_HEIGHT
        # self.x_pos = (self.screenwidth - self.w_width) / 2
        # self.y_pos = (self.screenheight - self.w_height) / 2
        #
        # 主窗口中央：
        self.x_pos=self.form0.winfo_x()+(self.form0.winfo_width()-self.w_width)/2
        self.y_pos=self.form0.winfo_y()+(self.form0.winfo_height()-self.w_height)/2

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
        self.et = tk.Entry(self.iframe, font="微软雅黑 " + str(MON_FONTSIZE))
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

        self.form0.wait_window(self.input_window)  # 要用这句话拦截主窗体的代码运行

    def bt_cancel_click(self, event=None):
        self.input_window.unbind_all('<Return>')
        self.input_window.unbind_all('<Escape>')
        self.input_window.destroy()

    def bt_yes_click(self, event=None) -> str:
        self.input_window.unbind_all('<Return>')
        self.input_window.unbind_all('<Escape>')
        try:
            self.input_value = self.et.get() # 
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


class my_progress_window:
    '''
    一个屏幕中间的进度条
    '''

    # input_window = ''  # =tk.Toplevel(self.form0)

    def __init__(self, parent, prog_value=0, prog_text='') -> None:
        '''
        进度条，输入进度数值
        '''

        # 变量设置
        self.form0 = parent

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
        self.w_width = 800
        self.w_height = 100
        #
        # 屏幕中央：
        # self.screenwidth = SCREEN_WIDTH
        # self.screenheight = SCREEN_HEIGHT
        # self.x_pos = (self.screenwidth - self.w_width) / 2
        # self.y_pos = (self.screenheight - self.w_height) / 2
        #
        # 主窗口中央：
        self.x_pos=self.form0.winfo_x()+(self.form0.winfo_width()-self.w_width)/2
        self.y_pos=self.form0.winfo_y()+(self.form0.winfo_height()-self.w_height)/2

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
        self.prog_bar.bind('<1>',self.force_close)

    def force_close(self,event=None):
        self.input_window.destroy()

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


def X_show_my_input_window(title='未命名', msg='未定义', default_value=''):
    '''
    想要做输入框，替代 tkinter 自带的，
    但是并没有启用。
    '''
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    w_width = 500
    w_height = 200
    x_pos = (screenwidth - w_width) / 2
    y_pos = (screenheight - w_height) / 2
    input_window = tk.Toplevel(window)
    input_window.geometry('%dx%d+%d+%d' % (w_width, w_height, x_pos, y_pos))
    input_window.title(title)
    #
    input_value = ''
    #
    # input_window.withdraw()
    input_window.deiconify()
    input_window.lift()
    input_window.focus_force()
    input_window.transient(window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
    input_window.grab_set()  # 模态

    iframe = tk.Frame(input_window, padx=10, pady=10)
    iframe.pack(expand=0, fill=tk.BOTH)

    lb = tk.Label(iframe, text=msg)
    lb.pack(anchor='sw')

    et = tk.Entry(iframe)
    et.pack(expand=0, fill=tk.X)

    def bt_cancel_click(event=None):
        input_window.destroy()

    def bt_yes_click(event=None):
        global input_value
        input_value = et.get()
        input_window.destroy()

    btc = ttk.Button(input_window, text='yes', command=bt_yes_click)
    btc.pack()

    return (input_value)


# my_input_window()

def show_window_input(title_value, body_value='', init_value='', is_file_name=True):
    '''
    接管输入框的过程，以后可以将自定义输入框替换到这里。
    目前的用法：输入参数 1 标题，2 正文，3 默认值；
    返回输入框的结果。如果输入内容为空，返回 None。
    参数 is_file_name 为 True 的时候，将文件名不能带的特殊字符自动去掉。
    '''
    # 获得输入值
    # res = simpledialog.askstring(title_value,prompt=body_value,initialvalue=init_value)
    res = str(my_input_window(window, title_value, body_value, init_value)).strip()
    if len(res) == 0:
        print('没有得到输入内容')
        return None

    # 特殊处理
    if is_file_name:
        res = res.replace('\\', '')
        res = res.replace('/', '')
        res = res.replace('?', '')
        res = res.replace('|', '')
        res = res.replace('*', '')
        res = res.replace('"', '')
        res = res.replace('<', '')
        res = res.replace('>', '')
        res = res.replace(':', '')
    return res
    pass


# %%
# 顶部菜单

if False:
    menu1 = tk.Menu(window)
    mFile = tk.Menu(menu1, tearoff=False)
    menu1.add_cascade(label='文件', menu=mFile)

    mFile.add_command(label='新建', accelerator='Ctrl+N')
    mFile.add_command(label='打开', accelerator='Ctrl+O')
    mFile.add_command(label='保存', accelerator='Ctrl+S')

    mHelp = tk.Menu(menu1, tearoff=False)
    menu1.add_cascade(label='帮助', menu=mHelp)

    mHelp.add_command(label='使用说明', accelerator='Ctrl+H')

    # window.configure(menu=menu1) # 菜单生效


# %%

def update_folder_list():
    '''
    根据 lst_my_path_s，将文件夹列表刷新一次。
    作用是：刷新主文件夹列表。暂不包括子文件夹刷新。
    没有输入输出。
    '''
    global tree_lst_folder

    exec_tree_clear(tree_lst_folder)
    tmp = 1
    if ALL_FOLDERS == 1:
        tree_lst_folder.insert('', tmp, values=("（全部）"),tags=['line1'] if tmp%2==0 else ['line2'])
    
    for i in lst_my_path_short:
        tmp += 1
        print(i)
        tree_lst_folder.insert('', tmp, values=(str(i)),tags=['line1'] if tmp%2==0 else ['line2'])  # 此处有bug，对存在空格的不可用
        # image=IMAGE_FOLDER,
    if ALL_FOLDERS == 2:
        tmp+=1
        tree_lst_folder.insert('', tmp, values=("（全部）"),tags=['line1'] if tmp%2==0 else ['line2'])
        # tree_lst_folder.insert(tk.END,i)
    try:
        to_selct = tree_lst_folder.get_children()[0]
        # tree_lst_folder.focus(tmp)
        tree_lst_folder.selection_set(to_selct)
    except:
        pass

def update_sub_folder_list_via_menu(event=None):
    update_sub_folder_list()
    update_main_window(0,fast_mode=True)#reload_setting=2)


def update_sub_folder_list(sub_folder_list=None, refresh=True):
    '''
    将子文件夹列表刷新一次。
    输入是要填充的子文件夹列表。
    参数 refresh =True 就选中全部子文件夹，=False 选中之前的。
    '''
    #
    tmp_sub_folder = tree_lst_sub_folder.selection() # 保存当前值
    #
    # 清空一次
    exec_tree_clear(tree_lst_sub_folder)
    #
    # 主文件夹为全部的时候，不返回任何子文件夹
    if get_folder_short() in ["（全部）", ""]:
        return
    #
    # 如果没有指定的话，
    if sub_folder_list is None:
        sub_folder_list=[]
        # 如果没有指定的话，就读取当前主文件夹的列表
        try:
            vPath=get_folder_long()
            for root, dirs, files in os.walk(vPath):
                sub_folder_list=dirs
                break
            pass
        except:
            pass
    #
    tmp = 0
    #
    # 先插入一个“全部”
    tree_lst_sub_folder.insert('', tmp, values=("（全部）"),tags=['line1'] if tmp%2==0 else ['line2'])
    # 排序
    sub_folder_list = sorted(sub_folder_list, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    #
    for i in sub_folder_list:
        if i in EXP_FOLDERS:
            continue
        tmp += 1
        print(i)
        tree_lst_sub_folder.insert('', tmp, values=(i,),tags=['line1'] if tmp%2==0 else ['line2'])  # 必须加逗号，否则对存在空格的不可用
        # image=IMAGE_FOLDER,
    # 
    # 恢复之前的选项；
    try:
        if refresh is None: 
            pass
        elif refresh: # refresh =True 代表重置当前选项，也就是选中最开始的。
            tmp = tree_lst_sub_folder.get_children()[0]
            # tree_lst_folder.focus(tmp)
            tree_lst_sub_folder.selection_set(tmp)
        else: # 否则选中之前的；
            try:
                tree_lst_sub_folder.selection_set(tmp_sub_folder)
            except:
                tmp = tree_lst_sub_folder.get_children()[0]
                tree_lst_sub_folder.selection_set(tmp)
        # 刷新一次；
        # update_main_window(0,fast_mode=True)#reload_setting=2)
    except Exception as e:
        print(e)
        pass
    

# tree_lst_folder.selection_set()


def show_tree_order():
    '''
    用来显示 tree 排序的视觉效果（也就是加三角）
    '''
    global ORDER_BY_N, ORDER_DESC
    DIR_VALUE = DIR_LST[1] if ORDER_DESC else DIR_LST[0]
    tree.heading(HEADING_LST[ORDER_BY_N], text=HEADING_LST_TXT[ORDER_BY_N] + DIR_VALUE)


def tree_order_base(inp):
    '''
    主列表排序的入口程序。
    '''

    global ORDER_BY_N, ORDER_DESC, dT, lst_tags
    # 恢复标题
    tree.heading(HEADING_LST[ORDER_BY_N], text=HEADING_LST_TXT[ORDER_BY_N])
    #
    if ORDER_BY_N == inp:  # 如果同样位置点击，就切换排序方式
        ORDER_DESC = not ORDER_DESC
    else:  # 如果不同位置点击，就预置排序方式
        ORDER_BY_N = inp
        if ORDER_BY_N == 2:  # 按修改时间排序的，第一次是最新的在前面。
            ORDER_DESC = True
        else:
            ORDER_DESC = False  # 其余排序方法，都是升序。
    # update_main_window(0) # 这个方法虽然可以排序，但是效率太低
    #
    # 可视化
    show_tree_order()

    # 新的排序方法
    dT.sort(key=dt_sort_by, reverse=ORDER_DESC)
    exec_search()
    set_search_tag_values(lst_tags)
    v_inp['value'] = lst_tags


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
    the_tag=''
    if TREE_SUB_SHOW=='tag':
        for item in tree_lst_sub_tag.selection():
            the_tag = tree_lst_sub_tag.item(item, "values")[0]
            break
    else:
        the_tag=v_tag.get()
    #
    if the_tag in ['（全部）']:
        the_tag=''
    print('标签里面是'+the_tag)
    return the_tag    


def tree_tag_search(event=None):
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
    lst_at=[]
    lst_en=[]
    lst_cn=[]
    for i in v_lst:
        if i =='':
            continue
        if str(i).startswith('@'):
            lst_at.append(i)
        else:
            lst_en.append(i)
    # 英文无论大小写都一起排序
    lst_en = sorted(lst_en, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    # 组合起来
    v_lst=lst_at+lst_en+lst_cn
    #
    #下拉框：
    v_tag['value']=['']+v_lst
    #
    # 列表：
    tmp_sub_tag = tree_lst_sub_tag.selection()
    exec_tree_clear(tree_lst_sub_tag)

    # if get_folder_short() in ["（全部）", ""]:
    #     return

    tmp = 0
    tree_lst_sub_tag.insert('', tmp, values=("（全部）"),tags=['line1'] if tmp%2==0 else ['line2'])
    
    for i in v_lst:
        tmp += 1
        # print(i)
        if str(i).strip()=='':
            continue
        tree_lst_sub_tag.insert('', tmp, values=(i,),tags=['line1'] if tmp%2==0 else ['line2'])  # 必须加逗号，否则对存在空格的不可用
        # image=IMAGE_FOLDER,
    tree_lst_sub_tag.update()
    try:
        if v_tag.get() != '':
            find_res=exec_tree_find(v_tag.get(),False,tree_lst_sub_tag,bar_sub_tag_v,0)
            if find_res==-1: # 如果没找到的话
                tmp = tree_lst_sub_tag.get_children()[0]
                tree_lst_sub_tag.selection_set(tmp)
        else:
            tmp = tree_lst_sub_tag.get_children()[0]
            tree_lst_sub_tag.selection_set(tmp)
        # else:
            # tree_lst_sub_tag.selection_set(tmp_sub_tag)
            pass
    except Exception as e:
        print(e)
        pass
    # if v_tag.get() != '':
    #     exec_tree_find(v_tag.get(),False,tree_lst_sub_tag,bar_sub_tag_v,0)


def set_sub_folder_selected(inp):
    if type(inp) is str:
        tmp_n = lst_sub_path.index(inp)
        v_sub_folders.current(tmp_n + 1)
    elif type(inp) is int:
        v_sub_folders.current(inp)


def set_search_tag_selected(ind):
    '''
    设置标签，选中指定的项目。
    如果输入的是字符串，则选中字符串。
    '''
    # 如果是字符串的话；
    if type(ind) is str:
        try:
            tags2=v_tag['values']
            set_search_tag_selected(tags2.index(ind))
        except:
            set_search_tag_selected(0)
    # 如果是数字的话
    elif type(ind) is int:
        #
        # 下拉框
        v_tag.current(ind)
        #
        # 列表：
        # exec_tree_find('（全部）',the_tree=tree_lst_sub_tag,the_bar=bar_sub_tag_v,the_col=0)
    else:
        v_tag.current(0)


def exec_after_sub_tag_choose(event=None):
    '''
    点击sub_tag之后
    '''
    res = ''
    for item in tree_lst_sub_tag.selection():
        res = tree_lst_sub_tag.item(item, "values")[0]
    if res in ['（全部）']:
        res = ''
    if res =='':
        set_search_tag_selected(0)
    else:
        set_search_tag_selected(res)
    exec_search()


def get_search_items(event=None,res_lst=False):
    '''
    获取标签下拉框里面的标签。
    不过，现在也兼职了对输入框的搜索。
    返回值是列表 res。
    或者参数 True的时候，返回 res_tag,res_keyword,res_path
    '''
    res = []
    res_tag = []
    res_keyword = []
    res_path = []
    #
    # 标签
    if len(get_search_tag_selected()) > 0:
        res_tag=[get_search_tag_selected()]
        res += res_tag
    #
    # 关键词
    if len(v_search.get()) > 0:
        res_keyword=str(v_search.get()).split(' ')
        res += res_keyword
    #
    # 子文件夹
    if len(get_sub_folder_selected()) > 0:
        tmp_path = lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
        print('进入子文件夹：')
        print(tmp_path)
        res_path = [tmp_path]
        res += res_path
    else:
        # 还要考虑子文件夹从有到无时候的处理；
        pass
        '''
        # 还要刷新子文件夹的标签
        tmp_tag=v_tag.get() # 获取当前标签
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
        return res_tag,res_keyword,res_path
    else:
        return res


def get_sub_folder_selected():
    '''
    获取子文件夹名称（没有输入，返回字符串，或者空白）
    '''
    if TREE_SUB_SHOW=='sub_folder': # sub_folder 模式，子文件夹是选项
        METHOD = 2
    elif TREE_SUB_SHOW=='tag' : # tag模式，子文件夹是下拉框
        METHOD = 1
    #
    if METHOD == 1:
        return v_sub_folders.get()
    # 方法2：
    elif METHOD == 2:
        res = ''
        for item in tree_lst_sub_folder.selection():
            res = tree_lst_sub_folder.item(item, "values")[0]
        if res in ['（全部）']:
            res = ''
        return res

def update_tags_in_sub_folder(tmp_path,must=0):
    '''
    切换子文件夹之后触发。刷新标签。
    输入参数是文件夹路径（str）。
    返回值是新的标签列表。
    参数 must 是强制刷新子文件夹标签的意思。
    '''
    # 这里，如果是子文件夹切换，还要刷新文件夹的标签【bug】
    #
    # if flag_root_folder:
    global dT
    print(f'正在加载该目录的标签：{tmp_path}')
    if must or flag_sub_folders_changed:
        # 加载新标签列表
        tmp_tag = get_search_tag_selected()  # 获取当前标签
        # 刷新标签列表 刷新期间不能操作进度条！
        new_files = get_data([tmp_path], update_sub_path=0,need_set_prog=False)
        (dt2, tags2) = get_dt(new_files,need_set_prog=False)
        
        # dT=dt2
        # print(f'\ndt2={dt2}')
        set_search_tag_values(tags2)
        if flag_inited:
            v_inp['value'] = tags2
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

def get_search_items_sub_folder(event=None,res_lst=False):
    '''
    获取子文件夹内的文件.
    在函数中，包括了【对标签的刷新】。
    '''
    try:
        if len(get_sub_folder_selected()) > 0:
            tmp_path = lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
            print('运行到 get_search_items_sub_folder, 进入子文件夹：')
            print(tmp_path)
        else:
            tmp_path = lst_my_path_long_selected[0]
    except:
        if res_lst:
            return [],[],[]
        else:
            return []
    tmp_path = str(tmp_path).replace('\\', '/')

    update_tags_in_sub_folder(tmp_path)
    '''
    # 这里，如果是子文件夹切换，还要刷新文件夹的标签【bug】
    #
    # if flag_root_folder:
    if not flag_sub_folders_changed:
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
        if flag_inited:
            v_inp['value'] = tags2
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
        res_tag,res_keyword,res_path = get_search_items(res_lst=True)
        return res_tag,res_keyword,res_path


def exec_add_tree_item(tree, dT) -> None:
    '''
    关键函数：增加主框架的内容
    先获得搜索项目以及 tag
    '''
    # global PIC_LST

    str_btm.set('正在刷新列表……')
    time0 = time.time()
    res_tag,res_keyword,res_path= get_search_items_sub_folder(res_lst=True)
    # tmp_search_items = get_search_items_sub_folder()  # 列表

    k = 0
    print('筛选条件：')
    # print(tmp_search_items)
    print(f'标签是 {res_tag}')
    print(f'关键词是 {res_keyword}')
    print(f'路径是{res_path}')
    n = 0
    n_max = len(dT)
    refresh_unit = 4
    print(f'检查的路径是{res_path}')

    for i in range(len(dT)): # 对每一条进行测试：
        n += 1

        tmp = dT[i]
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

        if canadd==1: # 路径
            
            for pth in res_path:
                if str.lower(tmp[-1]).find(str.lower(pth)) < 0: # 全路径搜索
                    # print(f'路径不符合，当前路径为{str.lower(tmp[-1])}')
                    canadd = 0
                    break # 有这句话就是 and 关系。
        
        if canadd==1: # 标签
            tag_lower = []
            for j in tmp[1]:
                tag_lower.append(str.lower(j))
            
            for tag in res_tag:  
                tag = str.lower(tag)
                if tag == '' or tag == cALL_FILES or (tag in tag_lower):
                    canadd = 1
                    # break
                elif TAG_EASY ==1 and str.lower(tmp[0]).find(tag)>=0: # 标签简单模式
                    canadd = 1
                else:
                    canadd = 0
                    break # 有这句话就是 and 关系。
        
        if canadd==1: # 关键词
            for keyw in res_keyword:
                #
                if True: # 文件名和标签搜索
                    if ';'.join(tag_lower).find(str.lower(keyw)) >= 0:
                        canadd=1
                    elif str.lower(tmp[0]).find(str.lower(keyw)) >= 0:
                        canadd=1
                    else:
                        canadd=0
                        break
                else: # 全路径搜索
                    if keyw == '' or str.lower(tmp[-1]).find(str.lower(keyw)) < 0: 
                        canadd = 0
                        break # 有这句话就是 and 关系。

        if canadd == 1:
            k += 1
            if k % 2 == 1:
                tree.insert('', k, values=(k, tmp[0], tmp[1], tmp[2], tmp[3], tmp[4]), tags=['line1'])
            else:
                tree.insert('', k, values=(k, tmp[0], tmp[1], tmp[2], tmp[3], tmp[4]), tags=['line2'])
    

        # if k % refresh_unit==0: # 刷新
        #     refresh_unit=refresh_unit*refresh_unit
        #     if flag_inited:
        #         set_prog_bar(99+1*n/n_max)
        #     tree.update() # 提前刷新，优化用户体验
        #     # str_btm.set('即将完成……')

    print('添加列表项消耗时间：')
    print(time.time() - time0)

    # str_btm.set("找到 " + str(k) + " 个结果，用时"+str(time.time()-time0)+"秒")
    str_btm.set("找到 " + str(k) + " 个结果")  # "，用时"+str(time.time()-time0)+"秒")
    if flag_inited:
        set_prog_bar(100)
        tree.focus()
    # flag_running=0

def get_folder_short():
    '''
    返回左侧列表文件夹名称 (简称)，需要用 get_folder_s2l(tmp) 转化为长路径。
    不考虑子文件夹。
    res= v_folders.get()
    res='（全部）'

    '''
    for item in tree_lst_folder.selection():
        res = tree_lst_folder.item(item, "values")

    # res=tree_lst_folder.get(tree_lst_folder.curselection())
    try:
        res = res[0]
        if res == '（全部）':
            res = ''
    except:
        res = ''
    # print(res)
    return res


def get_folder_long():
    '''
    合并获取短路径和长路径的逻辑。
    返回值是代表文件夹长路径的字符串。
    其中包括了对斜杠的处理。
    '''
    short_folder = get_folder_short()
    if short_folder == '':
        return short_folder
    else:
        res = get_folder_s2l(short_folder)
        res = str(res).replace('\\', '/')
        return res


def get_folder_long_v2():
    '''
    优化架构下的文件夹列表获取方法。
    这种架构下，文件夹列表的-1列就是长路径名。
    暂时没有启用。
    '''
    for item in tree_lst_folder.selection():
        path_long = tree_lst_folder.item(item, "values")[-1]
    return path_long


# 获取当前点击行的值
def exec_tree_file_open(event=None):  # 单击
    '''
    打开列表选中项目。
    按理说，兼容多文件。

    '''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        print('正在打开文件：')
        print(item_text[-1])
        try:
            os.startfile(item_text[-1])  # 打开这个文件
        except:
            print('打开文件失败')


def exec_file_rename(tar=None):  # 对文件重命名
    '''
    重命名tree选中的文件。需要有tree的选中项目。
    每个文件重命名一次，按理说兼容多文件，但是这个命令不应该给多文件执行。
    '''
    if len(tree.selection())>1:
        print('暂不支持多文件重命名')
        return
    for item in tree.selection():
        # 获得目标文件
        item_text = tree.item(item, "values")
        tmp_full_path = item_text[-1]
        tmp_file_name = get_split_path(tmp_full_path)[-1]
        #
        #
        print('正在重命名：')
        print(tmp_full_path)
        print(tmp_file_name)
        # res = simpledialog.askstring('文件重命名',prompt='请输入新的文件名',initialvalue =tmp_file_name) # 有bug，不能输入#号
        res = show_window_input('文件重命名', body_value='请输入新的文件名', init_value=tmp_file_name)  # 有bug，不能输入#号
        #
        if res is not None:
            try:
                tmp_new_name = '/'.join(get_split_path(tmp_full_path)[0:-1] + [res])
                print('tmp_new_name=')
                print(tmp_new_name)
                # os.rename(tmp_full_path,tmp_new_name)
                final_name = exec_safe_rename(tmp_full_path, tmp_new_name)
                update_main_window(0,fast_mode=True)
                exec_tree_find(final_name)
            except:
                t = tk.messagebox.showerror(title='ERROR', message='重命名失败！文件可能被占用，或者您没有操作权限。')
                # print(t)
                pass


def exec_tree_file_delete(tar=None):
    '''
    删除tree选中项对应的文件。
    兼容多文件，但是每个文件要确认一次，可能体验不太好。
    '''
    flag_deleted=0
    for item in tree.selection():
        # 获取文件全路径
        item_text = tree.item(item, "values")
        tmp_full_path = item_text[-1]
        # 再次确认
        if not isfile(tmp_full_path):
            print('并不存在文件：' + str(tmp_full_path))
        elif tk.messagebox.askokcancel("删除确认", "真的要【永久删除】以下文件吗？" + str(tmp_full_path)):
            flag_deleted=1
            try:
                # os.remove(tmp_full_path)
                remove_to_trash(tmp_full_path)
                if len(tree.selection())==1:
                    update_main_window(0)
            except:
                t = tk.messagebox.showerror(title='ERROR', message='删除失败，文件可能被占用！')
                print('删除失败，文件可能被占用')
            # 刷新

    if len(tree.selection())>1:
        if flag_deleted:
            update_main_window(0)


def exec_fun_test(event=None):  #
    ''' 
    用于调试一些测试性的功能，
    为了避免 event 输入，所以套了一层。

    '''
    res = my_input_window(window, '输入框', 'aaaa', '外部输入')
    print('自制输入框的返回值：')
    print(res)
    # print('进入测试功能')

    pass


def exec_tree_find(full_path='',need_update=True,the_tree=None,the_bar=None,the_col=None):  #
    '''
    用于在 任意 treeview（默认是tree） 里面找到项目，并加高亮。
    输入参数是查找值（完整路径）。
    need_update 代表是否要刷新列表。一般否是要刷新才能保证正确，
    如果是批量查询，可以自己提前刷新，然后取消函数刷新，可以增加速度。
    只支持单项目查找，多个查询需要重复运算。
    如果返回-1，代表没有找到。
    '''
    if full_path == '' or full_path is None:
        return (-1)
    #
    # 默认值
    if the_tree is None:
        the_tree=tree
    if the_bar is None:
        the_bar=bar_tree_v
    if the_col is None:
        the_col=-1
    #
    # 根据完整路径，找到对应的文件并高亮
    if need_update:
        the_tree.update()  # 必须在定位之前刷新列表，否则定位会错误
    tc = the_tree.get_children()
    tc_cnt = len(tc)
    print('条目数量为：%s' % tc_cnt)
    n = 0
    print('开始查找高亮的位置')
    try:
        (b1, b2) = the_bar.get()
    except:
        print(f'查询滚动条位置出现错误')
        print(the_bar.get())
        return(-1)
    b0 = b2 - b1
    # b0=0
    print('b0=')
    print(b0)
    for i in tc:
        tmp = the_tree.item(i, "values")
        # print(tmp[the_col])
        if tmp[the_col] == full_path:
            # the_tree.focus(i) #这个并不能高亮
            the_tree.selection_add(i)
            # the_tree.selection_add(tc[0])
            print('在第%d处检查到了相应结果' % n)
            print(1953)
            b1 = n / tc_cnt - 0.5 * b0
            b2 = n / tc_cnt + 0.5 * b0
            print((b0, b1, b2))
            if b1 < 0:
                b1 = 0
                b2 = b0
            elif b2 > 1:
                b2 = 1
                b1 = 1 - b0
            print((b1, b2))
            # the_bar.set(b1,b2)
            the_tree.yview_moveto(b1)
            return (n)
            break
        else:
            n += 1
    print('居然没找到：')
    print(full_path)
    return (-1)
    # for i in range()

def exec_tree_find_lst(inp_lst):
    '''
    传入一个列表。tree高亮。
    输入参数是要查询的内容，必须是列表。
    '''
    tree.update()
    if type(inp_lst) is not list:
        print('输入参数不是列表！')
        return

    for tmp_final_name in inp_lst:
        tmp_final_name = tmp_final_name.replace('\\', '/')
        print(f'正在定位 {tmp_final_name}')
        exec_tree_find(tmp_final_name,need_update=False)  # 为加标签之后的项目高亮

def tree_open_folder(event=None, VMETHOD=1):
    '''
    打开当前文件所在的目录.
    参数VMETHOD=1（默认）是打开文件夹，
    =2 是打开文件夹并选中文件（有点慢）。
    不需要传入路径参数，本函数会自动从tree里面读取。
    '''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_file = item_text[-1]
        tmp_file = tmp_file.replace('/', '\\')

        tmp_folder = '/'.join(get_split_path(tmp_file)[0:-1])
        # tmp_folder=item_text[-2]

        print(tmp_folder)
        if VMETHOD == 1:  # 打开文件夹
            os.startfile(tmp_folder)  # 打开这个文件
        elif VMETHOD == 2:  # 打开文件夹并选中文件。
            tmp = r'explorer /select, ' + tmp_file
            print(tmp)
            os.system(tmp)  # 性能极差，不知道哪的原因
            # os.system(r'explorer /select,d:\tmp\b.txt') # 这是打开文件夹并选中文件的方法

    pass


def tree_open_folder_select(event=None):
    tree_open_folder(VMETHOD=2)


def tree_open_current_folder(event=None):
    '''
    没有选中文件的时候，打开当前文件夹。
    支持打开子文件夹。
    '''
    if len(get_sub_folder_selected()) > 0:
        tmp_path = lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
    elif len(lst_my_path_long_selected)>1:
        print('输入多个文件夹，即将打开第一个')
        tmp_path = lst_my_path_long_selected[0]
    else:
        tmp_path = lst_my_path_long_selected[0]
    try:
        os.startfile(tmp_path)
    except:
        t = tk.messagebox.showerror(title='ERROR', message='打开文件夹失败！')


def exec_folder_add_from_sub(event=None):
    '''
    通过子文件夹的方式添加关注文件夹
    '''
    try:
        if len(get_sub_folder_selected()) > 0:
            tmp_path = lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
            exec_my_folder_add([tmp_path])
    except:
        print('请检查 exec_folder_add_from_sub 函数')

def exec_sub_folder_new(event=None):
    '''
    新建子文件夹
    '''
    # 
    # 获取名称
    path=show_window_input('新建文件夹','请输入文件夹名称')
    if path is None:
        return
    #
    # 补充完整路径
    if len(lst_my_path_long_selected)==1:
        tmp_path = lst_my_path_long_selected[0] + '/' + path
    else:
        t = tk.messagebox.showerror(title='ERROR', message='未选中唯一文件夹')
        return
    #
    # 新路径是否存在
    isExists=os.path.exists(tmp_path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        try:
            os.makedirs(tmp_path) 
 
            print (tmp_path+' 创建成功')
            #
            # 创建之后刷新一次
            update_sub_folder_list(refresh=False)
            update_main_window(0,fast_mode=True)
            # update_main_window(reload_setting=2)
            return True
        except:
            t = tk.messagebox.showerror(title='ERROR', message='文件夹创建失败')
    else:
        # 如果目录存在则不创建，并提示目录已存在
        t = tk.messagebox.showerror(title='ERROR', message=(tmp_path+' 目录已存在'))
        return False


def exec_sub_folder_rename(event=None):
    '''
    子文件夹重命名
    '''
    # 确定旧文件夹名称
    if len(get_sub_folder_selected()) > 0:
        old_folder=get_sub_folder_selected()
        old_path = lst_my_path_long_selected[0] + '/' + old_folder
    #
    # 新文件夹名称
    new_folder=show_window_input('重命名文件夹','请输入文件夹名称',old_folder)
    if new_folder is None:
        return
    new_path=lst_my_path_long_selected[0] + '/' + new_folder
    #
    # 新文件夹名称是否存在
    isExists=os.path.exists(new_path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        try:
            os.rename(old_path,new_path) 
            print (new_path+' 创建成功')
            # 刷新一次
            update_sub_folder_list(refresh=None)
            exec_tree_find(new_folder,True,tree_lst_sub_folder,bar_sub_folder_v,0)
            update_main_window(0,fast_mode=True)
            return True
        except:
            t = tk.messagebox.showerror(title='ERROR', 
            message='文件夹重命名失败，可能是有内部文件正在被访问，或没有操作权限。')
    else:
        # 如果目录存在则不创建，并提示目录已存在
        t = tk.messagebox.showerror(title='ERROR', message=(new_path+' 目录已存在，请输入另外的名称。'))
        return False

def input_new_tag(event=None, tag_name=None):
    '''
    输入新的标签，为选中项添加标签。
    tag_name 是输入的标签。
    '''
    # new_name=''
    if tag_name is None: # 默认从输入框获取
        new_tag = v_inp.get()
        new_tag = str(new_tag).strip()
    else:
        new_tag = tag_name

    if new_tag is None or new_tag == '':
        print("取消新标签")
        return

    taged_files=[]
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        # tmp_file_name = get_file_part(tmp_full_name)['ffname'] # 没有用到

        # new_tag = tk.simpledialog.askstring(title="添加标签", prompt="请输入新的标签")#, initialvalue=tmp)

        if new_tag == None or new_tag == '':
            print("取消新标签")
        else:
            taged_files.append(exec_file_add_tag(tmp_full_name, new_tag))
            # print(new_name)
    if len(tree.selection())>1: # 多文件的只在最后刷新。
        # (b1, b2) = bar_tree_v.get()
        update_main_window(0)
        exec_tree_find_lst(taged_files)
        # for i in taged_files:
            # exec_tree_find(i)
        
        # exec_tree_find(taged_files[-1]) 
        # tree.yview_moveto(b1)

def exec_input_new_tag_via_dialog(event=None):
    '''
    以输入框的方式添加标签。

    '''
    # 没有选中项的时候，直接跳过
    if len(tree.selection()) ==0:
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


def exec_file_add_tag(filename, tag0):
    '''
    增加标签
    '''
    tmp_final_name=filename

    tag_list = tag0.split(V_SEP)
    tag_old = get_file_part(filename)['ftags']  # 已有标签
    file_old = get_file_part(filename)['ffname']  # 原始的文件名
    path_old = get_file_part(filename)['fpath']  # 路径
    [fname, fename] = os.path.splitext(file_old)  # 文件名前半部分，扩展名

    old_n = path_old + '/' + fname + fename
    new_n = old_n
    for i in tag_list:
        if not i in tag_old:
            new_n = path_old + os.sep + fname + V_SEP + i + fename
            print(old_n)
            print(new_n)
            try:
                # os.rename(old_n,new_n)
                tmp_final_name = exec_safe_rename(old_n, new_n)
                old_n = new_n  # 多标签时避免重命名错误
            except:
                t = tk.messagebox.showerror(title='ERROR', message='为文件添加标签失败！')
                print('为文件添加标签失败')
                pass
    
    if len(tree.selection())==1:
        update_main_window(0,fast_mode=True)  # 此处可以优化，避免完全重载
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
#     for item in tree.selection():
#         item_text = tree.item(item, "values")
#         tmp_full_name = item_text[-1]
#     exec_file_add_tag(tmp_full_name,TAG_STAR)

def exec_fast_add_tag(tag):
    '''
    以右键的方式快速为文件加收藏。
    目前是为文件增加 TAG_STAR 对应的值。
    '''
    TAG_STAR = tag
    taged_files=[]
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        taged_files.append(exec_file_add_tag(tmp_full_name, TAG_STAR))
    if len(tree.selection())>1:
        # (b1, b2) = bar_tree_v.get()
        update_main_window(0)
        # tree.yview_moveto(b1)
        for file_1 in taged_files:
            exec_tree_find(file_1)
        # exec_tree_find(taged_files[-1])


def exec_clear_entry(tar):
    '''
    将输入框清空。
    必须要指定要清空的输入框对象。
    '''
    try:
        tar.delete(0, len(tar.get()))
    except:
        pass
    pass

def exec_clear_search_items(event=None):
    update_main_window(666,fast_mode=True)

def update_main_window(event=None, reload_setting=False,fast_mode=False):
    '''
    刷新。
    切换目录之后自动执行此功能。
    
    输入参数0的话，保留子文件夹、搜索框、标签框。
    输入参数1，保留子文件夹、标签框，(清除搜索框)。推荐使用参数1；
    其余参数，(清空子文件夹、标签框、搜索框)。

    '''
    global lst_files_to_go, dT
    global lst_tags, lst_sub_path

    # if TREE_SUB_SHOW =='tag' and event is None:
    #     event=1

    # 原始值
    old_tag=get_search_tag_selected()
    old_sub_folder=get_sub_folder_selected()

    if reload_setting == True:
        # 按需加载设置参数
        load_json_file_data(load_folders=False)

    tmp_sub_folder = get_sub_folder_selected()
    if len(tmp_sub_folder)>0:
        path_lst=[lst_my_path_long_selected[0]+'/'+ tmp_sub_folder]
    else:
        path_lst=lst_my_path_long_selected.copy()

    if event == 0:
        # 什么都不做
        pass
    elif event == 1:
        '''
        保留子文件夹；保留标签；
        清空搜索框
        '''
        # tmp_sub_folder=get_sub_folder_selected()
        exec_clear_entry(v_search)
    else:
        '''
        清空搜索框；
        标签留空；
        '''
        exec_clear_entry(v_search)
        set_search_tag_selected(0)
        if TREE_SUB_SHOW =='tag': # 在 tag 模式，需要连子文件夹也刷新
            set_sub_folder_selected(0)
        print('已经全部清空')

        # v_inp.delete(0,len(v_inp.get()))
    # v_inp.delete(0,len(v_inp.get()))

    # exec_after_folder_choose(refresh=0)
    print('—— 刷新核心过程 start ———')
    #
    if TREE_SUB_SHOW =='tag':
        path_lst=lst_my_path_long_selected
    elif TREE_SUB_SHOW == 'sub_folder':
        path_lst=lst_my_path_long_selected

    if len(tmp_sub_folder)>0: # 如果子文件夹选中，则不刷新子文件夹
        # 注意，这里修改了 lst_files_to_go 所以会导致全局的文件列表出现错乱。
        lst_files_to_go = get_data(path_lst,0)
    else:
        lst_files_to_go = get_data(path_lst)
    print(f'\n ———— 当前的数据来自文件夹：{path_lst}\n')
    # lst_files_to_go = get_data(lst_my_path_long_selected)
    #
    (dT, lst_tags) = get_dt(FAST_MODE=fast_mode)
    # if event in [0]: 
    #     (dT, lst_tags) = get_dt(FAST_MODE=fast_mode)
    # else:
    #     (dT, lst_tags) = get_dt() # 此处有待商榷
    #
    print('—— 刷新核心过程 end ———')
    # exec_tree_clear(tree)
    #
    # 恢复子文件夹选项（即将作废）
    if event in [0,1] and TREE_SUB_SHOW=='sub_folder':
        try:  # 用一种【不太优雅】，但是暴力有效的方法修复了bug……
            if len(tmp_sub_folder) > 0:
                tmp_n = lst_sub_path.index(tmp_sub_folder)
                set_sub_folder_selected(tmp_n + 1)
                print('子文件夹修复完毕')
        except:
            print('进入这个分支')
            v_sub_folders.current(0)
    #
    # 恢复标签
    window.update()
    if TREE_SUB_SHOW =='tag':
        if event in [0,1]: # 【此处从逻辑上好像有bug】
            tags_=update_tags_in_sub_folder(lst_my_path_long_selected[0]+'/'+ old_sub_folder,1)
    elif TREE_SUB_SHOW =='sub_folder':
        if len(lst_my_path_long_selected)>1:
            # tags_=update_tags_in_sub_folder(lst_my_path_long_selected)
            pass
        else:
            tags_=update_tags_in_sub_folder(lst_my_path_long_selected[0]+'/'+ old_sub_folder,1)
        if event in [0,1]:
            set_search_tag_selected(old_tag)
    exec_search()  # 目的是按照刷新后的筛选条件对内容进行筛选
    #
    
    try:
        if event in [0,1] and TREE_SUB_SHOW =='tag':
            '''
            if old_sub_folder =='':
                tags_=update_tags_in_sub_folder(lst_my_path_long_selected[0],1)
            else:
                tags_=update_tags_in_sub_folder(lst_my_path_long_selected[0]+'/'+ tmp_sub_folder,1)
            '''       
            pass
        else:
            set_search_tag_values(lst_tags) # 这个导致总是刷新全部标签
    except Exception as e:
        print(e)
    
    # if not (event  in [0,1] and TREE_SUB_SHOW =='tag'):
    #     set_search_tag_values(lst_tags) # 这个导致总是刷新全部标签

    v_inp['value'] = lst_tags # 这句没啥用吧

    try:
        set_prog_bar(100)
    except:
        pass
    #
    # 刷新之后，令文件列表获得焦点(貌似无效)
    # tree.focus()


def show_online_help(event=None):
    '''
    提供帮助文件。
    目前的方式主要是跳转到在线帮助文件。以后考虑到内网打不开网页，需要增加一个离线的方面。
    '''
    os.startfile(URL_HELP)


def show_online_advice(event=None):
    '''
    在线反馈
    '''
    os.startfile(URL_ADV)


def show_window_closing(need_asking=True):
    '''
    退出程序。
    '''
    if need_asking:
        if tk.messagebox.askokcancel("退出", "真的要退出吗"):
            window.destroy()
    else:
        window.destroy()


# 搜索框

def get_folder_s2l(folder_short_name):
    '''
    文件夹短路径转长路径。
    '''
    return dict_path[folder_short_name]
    pass


def exec_after_folder_choose(event=None, refresh=1, sub_folder=None):  # 点击新的文件夹之后
    '''
    选择左侧文件夹后启动。\n
    参数：refresh：默认是1，代表了运行之后是否刷新列表。\n
    sub_folder：输入完整路径，但是没有被任何函数调用过
    '''
    # 
    # if TREE_SUB_SHOW=='tag':
    #     pass
    # elif TREE_SUB_SHOW=='sub_folder': # 如果是子文件夹模式，先清空子文件夹；
    #     exec_tree_clear(tree_lst_sub_folder) # 新增语句
    #     pass

    global lst_my_path_long_selected # 
    global flag_running 
    global flag_root_folder
    #
    flag_root_folder = 1
    # if flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
    # return
    print('调用 exec_after_folder_choose 函数')
    #
    # 缓存之前选中的文件夹；
    #
    if sub_folder is None: # 如果没有指定输入参数
        lst_path_ori = lst_my_path_long_selected.copy()
    else:
        lst_path_ori = []
    #
    # 
    #
    folder_short = get_folder_short() # 获取当前选中的文件夹；
    need_disabled=0
    #
    if folder_short == '': # 如果主文件夹是全部；
        lst_my_path_long_selected = lst_my_path_long.copy()
        # 设置按钮为无效
        need_disabled=1
    #
    # 如果有参数指定的子文件夹：（未开放）
    elif sub_folder is not None:
        folder_short = sub_folder
        lst_my_path_long_selected = [folder_short] # 将传入的文件夹路径保存起来
        # 设置按钮有效
        need_disabled=0
        pass
    # 如果是其他文件夹，获取新选中的完整路径；
    else:
        folder_long = get_folder_s2l(folder_short)  # 将显示值转换为实际值
        lst_my_path_long_selected = [folder_long]
        # 设置按钮有效
        need_disabled=0
    # 
    # 调整按钮和控件的可用性：
    if need_disabled:
        bt_new.configure(state=tk.DISABLED)
        bt_folder_drop.configure(state=tk.DISABLED)
        v_sub_folders.current(0)
        v_sub_folders.configure(state=tk.DISABLED)
    else:
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')
    #
    # 如果前后的选项没有变化的话，就不刷新文件夹列表
    #
    if lst_path_ori == lst_my_path_long_selected: # 如果选项没变化
        pass
    else:  # 选项发生变化：
        if TREE_SUB_SHOW=='sub_folder':
            exec_tree_clear(tree_lst_sub_folder) # 新增语句
        if refresh:
            # update_main_window(lst_my_path_long_selected)
            update_main_window(CLEAR_AFTER_CHANGE_FOLDER,fast_mode=True)
        tree.yview_moveto(0)

    # flag_running=0 # 标记为没有任务
    flag_root_folder = 0
    print('exec_after_folder_choose 函数结束')


def exec_after_folder_choose_v2(event=None, refresh=1, sub_folder=None):  # 点击新的文件夹之后
    '''
    选择左侧文件夹后启动。
    '''
    global lst_my_path_long_selected, flag_running, flag_root_folder
    #
    flag_root_folder = 1
    # if flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
    # return
    print('调用 exec_after_folder_choose 函数')
    if sub_folder is None:
        lst_path_ori = lst_my_path_long_selected.copy()
    else:
        lst_path_ori = []

    tmp = get_folder_short()
    if tmp == '':
        lst_my_path_long_selected = lst_my_path_long.copy()
        # 设置按钮为无效
        bt_new.configure(state=tk.DISABLED)
        bt_folder_drop.configure(state=tk.DISABLED)
        v_sub_folders.current(0)
        v_sub_folders.configure(state=tk.DISABLED)

    elif sub_folder is not None:
        tmp = sub_folder
        lst_my_path_long_selected = [tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')
        pass
    else:
        tmp = get_folder_s2l(tmp)  # 将显示值转换为实际值
        lst_my_path_long_selected = [tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')

    if not lst_path_ori == lst_my_path_long_selected:  # 如果前后的选项没有变化的话，就不刷新文件夹列表
        if refresh == 1:
            # update_main_window(lst_my_path_long_selected)
            update_main_window(CLEAR_AFTER_CHANGE_FOLDER)
        tree.yview_moveto(0)

    # flag_running=0 # 标记为没有任务
    flag_root_folder = 0
    print('exec_after_folder_choose 函数结束')


def X_sub_folder_choose_not_used(event=None):
    '''
    还没弄完。功能没有被启用。
    '''
    global lst_sub_path, lst_my_path_long_selected
    if get_sub_folder_selected() == '':
        exec_after_folder_choose()

    print('sub处理前')
    print(lst_sub_path)
    print(lst_my_path_long_selected)
    tmp_lst_sub_path = lst_sub_path.copy()
    tmp_lst_my_path = lst_my_path_long_selected.copy()

    tmp_path = lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
    tmp_folder = tmp_path

    exec_after_folder_choose(sub_folder=tmp_folder)
    lst_my_path_long_selected = tmp_lst_my_path.copy()
    tmp_lst_sub_path.sort()
    v_sub_folders['value'] = [''] + tmp_lst_sub_path  # 强制修改子文件夹列表，但这样写不太好
    lst_sub_path = tmp_lst_sub_path.copy()
    print('sub处理后')
    print(lst_sub_path)
    print(lst_my_path_long_selected)
    # v_sub_folders.current(0)


def exec_search(event=None):
    '''
    选择标签之后、选择子文件夹后、输入搜索词按回车后触发。
    清空tree，并按照dT为tree增加行。
    '''
    if TREE_SUB_SHOW =='sub_folder':
        v_tag.configure(state=tk.DISABLED)
    exec_tree_clear(tree)
    # exec_add_tree_item(tree,dT,tag=tmp_tag)
    # if flag_sub_folders_changed == 1:
        # get_data(get_sub_folder_selected())
        # (dT, lst_tags) =get_dt()
    exec_add_tree_item(tree, dT)
    tree.update()
    if TREE_SUB_SHOW =='sub_folder':
        v_tag.configure(state='readonly')


def exec_after_sub_folders_choose(event=None):
    '''
    切换子文件夹后执行
    '''
    global flag_sub_folders_changed
    # 如果正在加载中就直接停止
    if TREE_SUB_SHOW=='tag': # 运行期间，不允许切换子文件夹
        v_sub_folders.configure(state=tk.DISABLED)
    flag_sub_folders_changed = 1
    # 这里需要刷新DT之后再进入
    exec_search()
    
    flag_sub_folders_changed = 0
    if TREE_SUB_SHOW=='tag':
        v_sub_folders.configure(state='readonly') # 此方法有效
        # update_main_window(CLEAR_AFTER_CHANGE_FOLDER)
    elif TREE_SUB_SHOW=='sub_folder': # 子文件夹模式切换的时候，清空标签
        set_search_tag_selected(0)


# %%


def show_window_setting():  #
    '''
    设置窗口
    '''
    global V_SEP, V_FOLDERS, NOTE_EXT, FILE_DRAG_MOVE
    global FOLDER_AS_TAG
    global TAG_EASY
    global json_data
    #
    dict_file_drag={"复制":"copy", "移动":"move"}
    dict_window_mode={"标签":"tag", "子文件夹":"sub_folder"}
    dict_tag_mode={"包含匹配":1, "严格全字匹配":0}
    dict_yes_no={"是":1, "否":0}

    def setting_yes(event=None):
        '''
        还没有功能
        '''
        # 获得新参数
        global V_SEP, V_FOLDERS, NOTE_EXT, FILE_DRAG_MOVE
        global FOLDER_AS_TAG
        global TAG_EASY
        global TREE_SUB_SHOW
        need_reboot=False
        # 先处理要重启的：
        #
        if dict_window_mode[v_inp_mode.get()] != TREE_SUB_SHOW \
            or dict_yes_no[v_last_folder_as_tag.get()] != FOLDER_AS_TAG:
            if tk.messagebox.askokcancel("请确认", "部分设置需要重启才能生效。确定要保存设置并【关闭程序】吗？"):
                need_reboot=True
            else:
                return
        NOTE_EXT = v_inp_note_type.get()
        V_FOLDERS = v_inp_folder_depth.get()
        V_SEP = v_inp_sep.get()
        FILE_DRAG_MOVE = dict_file_drag[v_inp_drag_type.get()]
        TREE_SUB_SHOW = dict_window_mode[v_inp_mode.get()]
        FOLDER_AS_TAG = dict_yes_no[v_last_folder_as_tag.get()]
        TAG_EASY = dict_tag_mode[v_tag_easy.get()]
        #
        # 保存到设置文件中
        set_json_options('sep', V_SEP,need_write=False)
        set_json_options('vfolders', V_FOLDERS,need_write=False)
        set_json_options('note_ext', NOTE_EXT,need_write=False)
        set_json_options('file_drag_enter', FILE_DRAG_MOVE,need_write=False)
        set_json_options('TREE_SUB_SHOW', TREE_SUB_SHOW)
        set_json_options('FOLDER_AS_TAG', FOLDER_AS_TAG)
        set_json_options('TAG_EASY', TAG_EASY)
        #
        # 关闭窗口
        form_setting.destroy()
        # 然后刷新文件列表
        if need_reboot:
            window.destroy()
        else:
            update_main_window(None, reload_setting=True)
        pass
    
    def add_combo():
        pass

    form_setting = tk.Toplevel(window)
    form_setting.title('设置')
    form_setting.resizable(0, 0)  # 限制尺寸
    form_setting.transient(window)  # 避免在任务栏出现第二个窗口，而且可以实现置顶
    form_setting.grab_set()
    screenwidth = SCREEN_WIDTH
    screenheight = SCREEN_HEIGHT
    w_width = 500  # int(screenwidth*0.8)
    w_height = 400  # int(screenheight*0.8)
    # 主窗口中央：
    x_pos=window.winfo_x()+(window.winfo_width()-w_width)/2
    y_pos=window.winfo_y()+(window.winfo_height()-w_height)/2
    # x_pos = (screenwidth - w_width) / 2
    # y_pos = (screenheight - w_height) / 2
    form_setting.geometry('%dx%d+%d+%d' % (w_width, w_height, x_pos, y_pos))
    form_setting.deiconify()
    form_setting.lift()
    form_setting.focus_force()
    form_setting.iconbitmap(LOGO_PATH)  # 左上角图标
    # v2sep=tk.StringVar()
    # v2sep.set(V_SEP)

    # v2sep=V_SEP
    frame_setting2 = ttk.Frame(form_setting, width=800)
    frame_setting2.pack(side=tk.BOTTOM, expand=0, fill=tk.X)
    frame_setting2.columnconfigure(0, weight=1)
    frame_setting2.columnconfigure(1, weight=1)

    frame_setting1 = ttk.Frame(form_setting, height=800, width=800)
    frame_setting1.pack(expand=0, fill=tk.BOTH)
    frame_setting1.columnconfigure(0, weight=1)
    frame_setting1.columnconfigure(1, weight=1)

    # frame_setting2.grid_configure()

    lable_set_sep = tk.Label(frame_setting1, text='标签分隔符')
    lable_set_sep.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

    v_inp_sep = ttk.Entry(frame_setting1, width=16, text=V_SEP)
    exec_clear_entry(v_inp_sep)
    v_inp_sep.insert(0, V_SEP)
    v_inp_sep.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

    lable_set_folder_depth = tk.Label(frame_setting1, text='识别为标签的文件夹层数')
    lable_set_folder_depth.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

    v_inp_folder_depth = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    lst_folder_depth = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
    v_inp_folder_depth['values'] = lst_folder_depth
    v_inp_folder_depth['state'] = 'readonly'
    tmp_n = lst_folder_depth.index(str(V_FOLDERS))
    v_inp_folder_depth.current(tmp_n)
    v_inp_folder_depth.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

    nr = 2
    #
    # 是否将最后的目录视为标签
    nr += 1
    lable_ = tk.Label(frame_setting1, text='将最后一层文件夹作为标签 *')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_last_folder_as_tag = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    v_last_folder_as_tag['values'] = list(dict_yes_no.keys())
    v_last_folder_as_tag['state'] = 'readonly'
    v_last_folder_as_tag.current(0)
    tmp_list=list(dict_yes_no.values())
    print(tmp_list)
    tmp_n = tmp_list.index(FOLDER_AS_TAG)
    v_last_folder_as_tag.current(tmp_n)
    v_last_folder_as_tag.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 笔记类型
    
    nr += 1
    lable_set_note_type = tk.Label(frame_setting1, text='笔记类型')
    lable_set_note_type.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)

    v_inp_note_type = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    v_inp_note_type['values'] = NOTE_EXT_LIST
    v_inp_note_type['state'] = 'readonly'
    v_inp_note_type.current(0)
    tmp_n = NOTE_EXT_LIST.index(NOTE_EXT)
    v_inp_note_type.current(tmp_n)
    v_inp_note_type.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 拖动是移动还是复制
    nr += 1
    # lable_drag_type
    lable_ = tk.Label(frame_setting1, text='拖拽添加文件的操作')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_inp_drag_type = ttk.Combobox(frame_setting1, width=16)  
    the_combo=v_inp_drag_type
    the_dict=dict_file_drag
    the_val=FILE_DRAG_MOVE
    #
    the_combo['values'] = list(the_dict.keys()) 
    the_combo['state'] = 'readonly'
    the_combo.current(0)
    tmp_list=list(the_dict.values())
    tmp_n = tmp_list.index(the_val)
    the_combo.current(tmp_n)
    the_combo.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)
    
    # 拖动是移动还是复制
    nr += 1
    # lable_drag_type
    lable_ = tk.Label(frame_setting1, text='标签搜索模式')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_tag_easy = ttk.Combobox(frame_setting1, width=16)  
    the_combo=v_tag_easy
    the_dict=dict_tag_mode
    the_val=TAG_EASY
    #
    the_combo['values'] = list(the_dict.keys()) 
    the_combo['state'] = 'readonly'
    the_combo.current(0)
    tmp_list=list(the_dict.values())
    tmp_n = tmp_list.index(the_val)
    the_combo.current(tmp_n)
    the_combo.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 布局是标签模式还是子文件夹模式
    nr += 1
    lable_ = tk.Label(frame_setting1, text='显示模式 *')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)
    #
    v_inp_mode = ttk.Combobox(frame_setting1, width=16)  # ,textvariable=v2fdepth)
    v_inp_mode['values'] = list(dict_window_mode.keys())
    v_inp_mode['state'] = 'readonly'
    v_inp_mode.current(0)
    tmp_list=list(dict_window_mode.values())
    print(tmp_list)
    tmp_n = tmp_list.index(TREE_SUB_SHOW)
    v_inp_mode.current(tmp_n)
    v_inp_mode.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)

    # 布局是标签模式还是子文件夹模式
    nr += 1
    lable_ = tk.Label(frame_setting1, text='（注意：标*的项目需要重启生效）')
    lable_.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.W)

    # 下面的设置区域
    nr = 100
    bt_setting_yes = ttk.Button(frame_setting2, text='确定', command=setting_yes)
    bt_setting_yes.grid(row=nr, column=0, padx=10, pady=5, sticky=tk.EW)
    # bt_setting_yes.pack(side=tk.LEFT,expand=0,fill=tk.X)

    bt_setting_cancel = ttk.Button(frame_setting2, text='取消', command=form_setting.destroy)
    bt_setting_cancel.grid(row=nr, column=1, padx=10, pady=5, sticky=tk.EW)
    # bt_setting_cancel.pack(side=tk.LEFT,expand=0,fill=tk.X)

    # window.wait_window(form_setting)


def exec_folder_add_click(event=None):  #
    '''
    通过点击的方式，添加新的目录
    '''
    res = filedialog.askdirectory()  # 选择目录，返回目录名
    res_lst = [res]
    print(res)
    if res == '':
        print('取消添加文件夹')
    else:
        exec_my_folder_add(res_lst)


def exec_folder_add_drag(files):  #
    '''
    通过拖拽的方式，添加目录。
    '''
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
        exec_my_folder_add(folders)

def exec_tree_drag_enter_popupmenu(files):
    '''
    ###########################################
    弹出菜单，判断是移动还是复制。
    （存在逻辑问题，还没有启用）
    #######################################
    '''
    global FILE_DRAG_MOVE
    menu_move_or_copy = tk.Menu(window, tearoff=0)
    menu_move_or_copy.add_command(label="复制", command=lambda x=files: exec_tree_drag_enter(x,'copy'))
    menu_move_or_copy.add_command(label="移动", command=lambda x=files: exec_tree_drag_enter(x,'move'))
    # menu_move_or_copy.post(event.x_root, event.y_root)
    menu_move_or_copy.post(0,0)
    # exec_tree_drag_enter(files)

def exec_tree_drag_enter(files,drag_type=None):
    '''
    以拖拽的方式将文件拖动到tree范围内，将执行复制命令。
    注意，不是移动，只是复制。
    safe_copy 的参数 opt_type = copy 是复制， = move 是移动。
    '''
    global flag_file_changed

    if drag_type is not None:
        global FILE_DRAG_MOVE
        FILE_DRAG_MOVE=drag_type

    # 确定目录
    short_name = get_folder_short()
    print(short_name)
    if short_name == '':
        # print('未指定目标目录，取消复制')
        str_btm.set('未指定目标目录，取消复制')
        return
    else:
        if len(get_sub_folder_selected()) > 0:
            long_name = lst_my_path_long_selected[0] + '/' + get_sub_folder_selected()
        else:
            long_name = lst_my_path_long_selected[0]
        # long_name=get_folder_s2l(short_name) #将文件夹的显示值转换为实际值
        print('long_name=')
        print(long_name)
    #
    # 获取对象（k已经没什么用）
    k = len(tree.get_children())
    #
    #获取标签
    res_tag,res_keyword,res_path= get_search_items_sub_folder(res_lst=True)
    #
    new_file_lst=[]
    for item in files:
        item = item.decode('gbk')
        if not isfile(item):
            continue

        print(item)
        # 先安全复制
        old_name = item
        [fpath, ffname] = os.path.split(old_name)  # fpath 所在文件夹、ffname 原始文件名
        [fname, fename] = os.path.splitext(ffname)  # fname 文件名前半部分，fename 扩展名
        #
        if DRAG_FILES_ADD_TAG: # 为拖拽进来的新增文件统一添加当前选中的标签
            if len(str(fname).split(V_SEP))>0:
                tag_orig=str(fname).split(V_SEP)[1:]
            for tag in res_tag:
                if not tag in tag_orig:
                    fname = fname + V_SEP + tag
            ffname=fname+fename
        #
        new_name = long_name + '/' + ffname
        if FILE_DRAG_MOVE in ['copy', 'move']:
            res = safe_copy(old_name, new_name, opt_type=FILE_DRAG_MOVE)
            str_btm.set('拖动添加文件成功')
        #     res=safe_move(old_name, new_name, opt_type='copy')
        #     str_btm.set('文件拖拽成功')
        print('res=')
        print(res)
        new_file_lst.append(res)
        # 再显示到列表中
        k += 1
        # tmp=get_file_part(res)
        # tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path'])
        # tmp=tmp_v
        # tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        flag_file_changed = 1

    # 刷新：
    if flag_file_changed:
        update_main_window(0)  # 这里不刷新的话，后面排序或者筛选都会出错。
        # 高亮文件
        try:
            exec_tree_find_lst(new_file_lst)
            # exec_tree_find(res)
            # tree.yview_moveto(1)
        except:
            pass


def update_folder_and_json_file(ind=None):  # 刷新左侧的文件夹列表
    '''
    刷新 json 文件，并根据文件内容刷新文件夹列表。
    输入参数是要选中的文件夹。
    '''
    # 更新json文件
    write_json_file(data=json_data)
    load_json_file_data()
    #
    # 更新左侧列表
    update_folder_list()
    #
    # 选中指定的文件夹
    tree_lst_folder.update()
    if ind is not None:
        # tree_lst_folder.selection_set(ind)
        tmp_lst_folder = tree_lst_folder.get_children()
        tree_lst_folder.selection_set(tmp_lst_folder[ind])
        pass
    # 更新正文
    exec_after_folder_choose()


def exec_my_folder_add(tar_list):
    '''
    添加关注的目录,输入必须是列表。
    '''
    global json_data
    for tar in tar_list:
        if len(tar) > 0:  # 用于避免空白项目，虽然不知道哪里来的
            tar = str(tar).replace("\\", '/')
            tmp = {"pth": tar}
            if not tmp in json_data['folders']:  # 此处判断条件有漏洞，因为加入short参数之后就不对了
                json_data['folders'].append(tmp)
    # 刷新目录
    update_folder_and_json_file()


def exec_folder_drop():  # 删除关注的目录
    '''
    取消关注选中的文件夹。
    没有输入输出。
    '''
    global json_data
    # 获取当前选中的文件夹
    short_name = get_folder_short()
    print(short_name)
    if short_name == '':
        pass
    else:
        long_name = get_folder_s2l(short_name)  # 将显示值转换为实际值
        print(long_name)
    # 增加确认
    if tk.messagebox.askokcancel("操作确认", "真的要取消关注选中的文件夹吗？\n该文件夹将从关注列表中移除，但其本身数据并不会受到影响。"):
        pass
    else:
        return
    # 在 json 里面找到对应项目并删除
    n = 0
    for i in json_data['folders']:
        if i['pth'] == long_name:
            json_data['folders'].pop(n)
            break
        n += 1
    # 刷新目录
    update_folder_and_json_file()


def exec_folder_move_up(event=None, d='up'):
    '''
    文件夹列表上下移动，默认上移，参数可以为 'up' 、 'down'、'top'。
    json_data['folders']是列表，
    每一项的'pth'是长路径。
    '''
    # 
    global json_data
    # 获取当前选中的文件夹
    short_name = get_folder_short()
    print(short_name)
    if short_name == '':
        pass
    else:
        long_name = get_folder_s2l(short_name)  # 将显示值转换为实际值
        print(long_name)
    # 在 json 里面找到对应项目，并交换顺序
    tar_lst = json_data['folders']  # 这个列表只包括文件夹，不包括“所有”。
    n = 0
    min_pos = 0
    max_pos = len(tar_lst) - 1
    #
    if d=='top':
        n2=0
        for i in tar_lst:
            if i['pth'] == long_name:
                if n==0:
                    return
                part_0=tar_lst[0:n]
                part_1=tar_lst[n]
                if n+1<=max_pos:
                    part_2=tar_lst[n+1:]
                else:
                    part_2=[]
                json_data['folders']=[part_1]+part_0+part_2
                print('文件夹置顶成功')
                break
            n+=1
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
    update_folder_and_json_file(n2)  # 还需要选中目标文件夹
    pass


def exec_folder_move_down(event=None):
    '''
    向下移动
    '''
    exec_folder_move_up(d='down')


def exec_folder_move_top(event=None):
    '''
    置顶
    '''
    exec_folder_move_up(d='top')


def exec_folder_open(tar=None):  # 打开目录
    # 获得当前选中的长目录
    if len(lst_my_path_long_selected) != 1:
        pass
    else:
        try:
            os.startfile(lst_my_path_long_selected[0])
        except:
            pass


def exec_create_note(event=None):  # 添加笔记
    global lst_my_path_long_selected, NOTE_NAME, NOTE_EXT
    tags = ['笔记']
    if not get_search_tag_selected() == '': # 新笔记自动增加选中的标签
        tags+=[get_search_tag_selected()]

    if len(lst_my_path_long_selected) != 1:
        t = tk.messagebox.showerror(title='ERROR', message='未选中文件夹，新建笔记功能暂不可用')
        print('新建笔记功能锁定，暂不可用')
        return
    #
    # res = simpledialog.askstring('新建 Tagdox 笔记',prompt='请输入文件名',initialvalue =NOTE_NAME)
    res = show_window_input('新建 Tagdox 笔记', body_value='请输入文件名', init_value=NOTE_NAME)
    if res is not None:
        print('获得新笔记标题：')
        print(res)
        NOTE_NAME = res
        if len(tags) > 0:
            stags = V_SEP + V_SEP.join(tags)
        else:
            stags = ''

        if len(lst_my_path_long_selected) > 1:
            pass

        if len(lst_my_path_long_selected) == 1:
            pth = lst_my_path_long_selected[0]

            if not event == 'exec_create_note_here':
                # 增加对子文件夹的判断逻辑。
                # 新建的位置正确，但是刷新之后找不到新笔记，而且子文件夹自动消失，体验不好。
                psub = get_sub_folder_selected()
                if len(psub) > 0:
                    pth = pth + '/' + psub

            print('即将在此新建笔记：')
            print(pth)
            if True:  # pth in lst_my_path_long: # 后面这个判断有点多余
                fpth = pth + '/' + NOTE_NAME + stags + NOTE_EXT

                # 检查是否有这个文件
                i = 0
                while isfile(fpth):
                    i += 1
                    fpth = pth + '/' + NOTE_NAME + '(' + str(i) + ')' + stags + NOTE_EXT

                # 创建文件
                print('创建文件：')
                print(fpth)
                try:
                    if NOTE_EXT in NOTE_EXT_LIST:
                        with open(fpth, 'w') as _:
                            pass
                    elif NOTE_EXT in ['.docxXXXXX']:
                        # d=Document()
                        # d.save(fpth)
                        pass
                    # 打开
                    os.startfile(fpth)  # 打开这个文件
                    # 刷新
                    if event == 'exec_create_note_here':  # 【这里有bug，刷新之后不能显示内容】
                        update_main_window(1,fast_mode=True)
                        exec_tree_find(fpth)
                        # return fpth
                    else:
                        update_main_window(1,fast_mode=True)  # 没有这句话会搜不到
                        exec_tree_find(fpth)
                    # else:
                    #     return fpth
                except:
                    t = tk.messagebox.showerror(title='ERROR', message='新建笔记失败')

    else:
        pass
    #


def exec_create_note_here(event=None):
    '''
    树状图里面，可以右击直接在选中文件的相同位置新建笔记。
    '''
    global lst_my_path_long_selected
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
    tmp_path = '/'.join(get_split_path(tmp_full_name)[0:-1])
    print('当前路径')
    print(tmp_path)
    lst_tmp = lst_my_path_long_selected.copy()
    lst_my_path_long_selected = [tmp_path]

    fpth = exec_create_note('exec_create_note_here')
    lst_my_path_long_selected = lst_tmp.copy()

    if fpth is not None:
        update_main_window(1)
        exec_tree_find(fpth)
    pass


# %%
def jump_to_search(event=None):
    '''
    输入快捷键快速搜索的功能。
    '''
    tmp_search_value=v_search.get()
    res = show_window_input('快速搜索', body_value='请输入搜索关键词，多个关键词之间用空格隔开。',
     init_value=tmp_search_value)
    if res is not None:
        exec_clear_entry(v_search)
        res=res.strip()
        v_search.insert(0, res)
        exec_search()
        v_search.focus()



def jump_to_tag(event=None):
    v_inp.focus()


# %%
# 弹出菜单

def show_popup_menu_main(event):
    '''
    主菜单，点击设置按钮可以弹出。
    设置菜单的弹出
    '''
    menu_main = tk.Menu(window, tearoff=0)
    menu_main.add_command(label='参数设置…', command=show_window_setting)
    menu_main.add_separator()
    # menu_main.add_command(label='使用说明')#,command=show_online_help)
    menu_main.add_command(label='访问主页（联网）', command=show_online_help)
    menu_main.add_command(label='建议和反馈（联网）', command=show_online_advice)
    menu_main.add_command(label='关于…', command=show_window_info)
    menu_main.add_separator()
    menu_main.add_command(label='退出', command=show_window_closing)
    #
    menu_main.post(event.x_root, event.y_root)


def show_popup_menu_folder(event):
    '''
    文件夹区域的右键菜单
    '''
    if len(lst_my_path_long_selected) != 1:  # 如果没有选中项目的话
        menu_folder_no = tk.Menu(window, tearoff=0)
        menu_folder_no.add_command(label="打开所选文件夹", state=tk.DISABLED, command=exec_folder_open)
        menu_folder_no.add_separator()
        menu_folder_no.add_command(label="添加关注文件夹…", command=exec_folder_add_click)
        menu_folder_no.add_command(label="取消关注所选文件夹", state=tk.DISABLED, command=exec_folder_drop)
        menu_folder_no.post(event.x_root, event.y_root)
    else:
        menu_folder = tk.Menu(window, tearoff=0)
        menu_folder.add_command(label="打开所选文件夹", command=exec_folder_open)
        menu_folder.add_separator()
        menu_folder.add_command(label="置顶", command=exec_folder_move_top)
        menu_folder.add_command(label="向上移动", command=exec_folder_move_up)
        menu_folder.add_command(label="向下移动", command=exec_folder_move_down)
        menu_folder.add_separator()
        menu_folder.add_command(label="添加关注文件夹…", command=exec_folder_add_click)
        menu_folder.add_command(label="取消关注所选文件夹", command=exec_folder_drop)
        menu_folder.post(event.x_root, event.y_root)


def show_popup_menu_sub_folder(event):
    '''
    子文件夹区域的右键菜单
    '''
    if True:
        menu_sub_folder = tk.Menu(window, tearoff=0)
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


def exec_file_drop_tag(event=None):
    '''
    删除标签
    '''
    if event is None:
        return
    tag_value = event
    res_lst=[]
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        #
        res = get_file_part(tmp_full_name)
        file_path = res['f_path_only']
        file_name_ori = res['filename_origional']
        file_ext = res['fename']
        if file_ext == '':
            print(file_name_ori)
            tmp_rv = list(file_name_ori)
            tmp_rv.reverse()
            tmp_rv = ''.join(tmp_rv)
            print(tmp_rv)
            #
            tmp_r_tag = list(V_SEP + tag_value)
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
        new_name = file_name_ori.replace(V_SEP + tag_value + V_SEP, V_SEP)
        new_name = new_name.replace(V_SEP + tag_value + '.', ".")

        new_full_name = file_path + '/' + new_name
        print('原始文件名：')
        print(tmp_full_name)
        print('去掉标签后：')
        print(new_full_name)
        print('被去掉的标签：')
        print(tag_value)
        # os.rename(tmp_full_name,new_full_name)
        if tmp_full_name!=new_full_name:
            tmp_final_name = exec_safe_rename(tmp_full_name, new_full_name)
        res_lst.append(new_full_name)
    
    update_main_window(0,fast_mode=True)  # 此处可以优化，避免完全重载
    exec_tree_find_lst(res_lst)
    # for tmp_final_name in res_lst:
    #     tmp_final_name = tmp_final_name.replace('\\', '/')
    #     print('删除标签完成，正在定位%s' % (tmp_final_name))
    #     exec_tree_find(tmp_final_name)  # 为加标签之后的项目高亮

def show_popup_menu_file(event):
    '''
    文件区域的右键菜单
    '''
    n_selection = len(tree.selection())
    # for item in tree.selection():
    #     item_text = tree.item(item, "values")
    #     tmp_full_name = item_text[-1]
    #     n_selection += 1
    #
    menu_tags_to_drop = tk.Menu(window, tearoff=0)
    menu_tags_to_add = tk.Menu(window, tearoff=0)
    if len(QUICK_TAGS) > 0:
        for i in QUICK_TAGS:
            menu_tags_to_add.add_command(label=i, command=lambda x=i: exec_fast_add_tag(x))
        menu_tags_to_add.add_separator()
    menu_tags_to_add.add_command(label='自定义标签…', command=exec_input_new_tag_via_dialog)
    #
    menu_file = tk.Menu(window, tearoff=0)
    menu_file.add_command(label="打开文件", command=exec_tree_file_open, accelerator='Enter')
    # menu_file.add_command(label="在相同位置创建笔记",command=exec_create_note_here)
    menu_file.add_separator()
    if len(lst_my_path_long_selected) == 1:
        menu_file.add_command(label="新建笔记", command=exec_create_note, accelerator='Ctrl+N')
    else:
        menu_file.add_command(label="新建笔记", state=tk.DISABLED, command=exec_create_note, accelerator='Ctrl+N')
    menu_file.add_separator()
    if n_selection==1:
        menu_file.add_command(label="打开选中项所在文件夹", command=tree_open_folder)
    elif n_selection>1:
        menu_file.add_command(label="打开选中项所在文件夹", state=tk.DISABLED, command=tree_open_folder)
    # menu_file.add_command(label="打开选中项所在文件夹并选中文件（有点慢）",command=tree_open_folder_select)
    menu_file.add_command(label="打开当前文件夹", command=tree_open_current_folder)
    menu_file.add_separator()
    menu_file.add_command(label='添加标签 ', command=exec_input_new_tag_via_dialog, accelerator='Ctrl+T')
    menu_file.add_cascade(label="快速添加标签", menu=menu_tags_to_add)
    if n_selection==1:
        menu_file.add_cascade(label="移除标签", menu=menu_tags_to_drop)
    elif n_selection>1:
        menu_file.add_cascade(label="移除标签", menu=menu_tags_to_drop)
    menu_file.add_separator()
    # menu_file.add_command(label="发送无标签副本到桌面（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    # menu_file.add_command(label="复制到剪切板（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    # menu_file.add_command(label="移动到文件夹（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    # menu_file.add_command(label="粘贴（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    if n_selection==1:
        menu_file.add_command(label="重命名", command=exec_file_rename, accelerator='F2')
    elif n_selection>1:
        menu_file.add_command(label="重命名", state=tk.DISABLED, command=exec_file_rename, accelerator='F2')
    menu_file.add_command(label="删除", command=exec_tree_file_delete)
    menu_file.add_separator()
    menu_file.add_command(label="刷新", command=update_main_window)

    menu_file_no_selection = tk.Menu(window, tearoff=0)
    # menu_file_no_selection.add_command(label="打开文件",state=tk.DISABLED,command=exec_tree_file_open)
    menu_file_no_selection.add_command(label="打开当前文件夹", command=tree_open_current_folder)
    menu_file_no_selection.add_separator()
    if len(lst_my_path_long_selected) == 1:
        menu_file_no_selection.add_command(label="新建笔记", command=exec_create_note, accelerator='Ctrl+N')
    else:
        menu_file_no_selection.add_command(label="新建笔记", state=tk.DISABLED, command=exec_create_note,
                                           accelerator='Ctrl+N')
    # menu_file_no_selection.add_command(label="重命名",state=tk.DISABLED)#,command=exec_folder_add_click)
    # menu_file_no_selection.add_command(label="添加收藏",state=tk.DISABLED)#,command=exec_folder_add_click)
    menu_file_no_selection.add_separator()
    menu_file_no_selection.add_command(label="刷新", command=update_main_window)

    
    if n_selection ==1:  # 如果有选中项目的话，
        
        # tmp_file_name=get_split_path(tmp_full_name)[-1]
        for item in tree.selection():
            item_text = tree.item(item, "values")
            tmp_full_name = item_text[-1]
        tmp_file_name = get_file_part(tmp_full_name)['fname']
        tmp_tags_all = get_file_part(tmp_full_name)['ftags']
        tmp_tags = tmp_file_name.split(V_SEP)
        # print(tmp_res)
        tmp_tags.pop(0)
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
                    menu_tags_to_drop.add_command(label=i, command=lambda x=i: exec_file_drop_tag(x))

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
    
    elif n_selection>1:
        try:
            for i in range(10000):  # 删除已有标签
                menu_tags_to_drop.delete(0)
        except:
            pass
        
        tmp_tags_from_files=[]
        file_checked=0
        for item in tree.selection():
            
            item_text = tree.item(item, "values")
            tmp_full_name = item_text[-1]
            tmp_file_name = get_file_part(tmp_full_name)['fname']
            tmp_tags_all = get_file_part(tmp_full_name)['ftags'] # 自带标签+路径标签
            tmp_tags = tmp_file_name.split(V_SEP) # 选中项自带标签
            # print(tmp_res)
            tmp_tags.pop(0)
            if file_checked==0:
                tmp_tags_from_files+=tmp_tags
            else:
                # 取交集
                tmp_tags_from_files=list(set(tmp_tags_from_files).intersection(set(tmp_tags)))
                #
                # 方法2
                # for i in range(len(tmp_tags_from_files)):
                #     if tmp_tags_from_files[-1-i] not in tmp_tags:
                #         tmp_tags_from_files.pop(-1-i)
                #
                # 如果是取并集：
                # tmp_tags_from_files+=tmp_tags

            file_checked+=1
        
        if len(tmp_tags_from_files) > 0:
            tmp_tags_from_files=list(set(tmp_tags_from_files))
            for i in tmp_tags_from_files:
                menu_tags_to_drop.add_command(label=i, command=lambda x=i: exec_file_drop_tag(x))
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

def fixed_map_v2(tar,option):
    return [elm for elm in style.map(tar, query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]

def set_style(style):
    # style = ttk.Style()
    # 修复 treeview 背景色的bug；
    style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
    style.map('TFrame', foreground=fixed_map_v2('Frame','foreground'), background=fixed_map_v2('Frame','background'))
    
    MY_THEME=False
    if MY_THEME:
        style.theme_use('alt') #  winnative
        #
        # treeview
        style.configure("Treeview.Heading", font=FONT_TREE_HEADING, \
                        rowheight=int(LARGE_FONT * 4), height=int(LARGE_FONT * 4), \
                        relief='flat',borderwidth=0)

        style.configure("Treeview", font=FONT_TREE_BODY, \
                        rowheight=int(MON_FONTSIZE * 3.5), \
                        fieldbackground='white',background='#666666', \
                        relief='flat',borderwidth=0)
        # style.configure("Treeview.Item",font=5)
        style.configure("Dark.Treeview", fieldbackground='#333333',background='black')
        style.configure("Dark.Treeview.Heading", fieldbackground='blue', \
            background='black',foreground='white')
        #
        # 框架
        style.configure("TFrame",fieldbackground='white',background='#EEEEEE', \
            borderwidth=0, relief='flat')
        # 
        # 按钮
        style.configure("TButton",fieldbackground='#666666',background='#999900', \
            activeforeground=" #ff0000",activebackground="#00ff00",
            height=20,
            borderwidth=1,relief='flat')
        #
        style.configure("TEntry",fieldbackground='#FFFFFF',background='#EEEEEE', \
            borderwidth=1,relief='solid')
        

    else:
        style.configure("Treeview.Heading", font=FONT_TREE_HEADING, \
                        rowheight=int(LARGE_FONT * 4), height=int(LARGE_FONT * 4))
        style.configure("Treeview", font=FONT_TREE_BODY, \
                        rowheight=int(MON_FONTSIZE * 3.5),relief='flat',borderwidth=0)
        # style.configure("Dark.TFrame", fieldbackground='#333333',background='#666666',
        #     foreground='white')
        # style.configure("Dark.Treeview", fieldbackground='#333333',background='#666666',
        #     foreground='white')
        # style.configure("Dark.Treeview.Heading", fieldbackground='blue', \
        #     background='#888800',foreground='#999999')
        style.configure("Dark.TFrame")
        style.configure("Dark.Treeview")
        style.configure("Dark.Treeview.Heading")

    pass
    
    # style.tag_configure('line1',background="#EEEEEE")


# %%
class main_app:
    def __init__(self) -> None:
        pass


if __name__ == '__main__':
    # if True:
    # 变量 ###########################################################
    q = queue.Queue()
    #
    #
    lst_files_to_go = []  # 所有文件的完整路径
    dT = []
    dicT=dict()
    #
    lst_tags = []  # 全部标签
    lst_tags_selected=[] 
    #
    lst_my_path_long = []  # json里面，要扫描的文件夹列表
    lst_my_path_short = []
    lst_my_path_long_selected = []
    #
    lst_sub_path = [] # 子文件夹得到全局变量
    lst_sub_path_selected = []
    #
    dict_path = dict()  # 用于列表简写和实际值
    #
    flag_inited = 0  # 代表是否已经加载完成
    flag_break = 0  # 代表是否中断查询
    flag_running = 0  # 代表是否有正在运行的查询
    flag_root_folder = 0
    flag_sub_folders_changed = 0
    flag_file_changed = 0
    ###########################################################
    #
    window = tk.Tk()  # 主窗口
    # %%
    PIC_LST = [tk.PhotoImage(file="./src/龙猫.gif")]
    IMAGE_FOLDER = tk.PhotoImage(file='./src/在线帮助.png')
    #
    # 样式
    style = ttk.Style()
    set_style(style)

    # MY_THEME=True
    # if MY_THEME:
    #     style.theme_use('winnative')
    #     style.configure("Treeview.Heading", font=FONT_TREE_HEADING, \
    #                     rowheight=int(LARGE_FONT * 4), height=int(LARGE_FONT * 4))
    #     style.configure("Treeview", font=FONT_TREE_BODY, \
    #                     rowheight=int(MON_FONTSIZE * 3.5),fieldbackground='#333333',background='#666666')
    #     style.configure("Dark.Treeview", fieldbackground='#333333',background='black')
    #     style.configure("Dark.Treeview.Heading", fieldbackground='blue', \
    #         background='black',foreground='white')
    #     style.configure("Frame",fieldbackground='white',background='white')
    #     # 
    #     # 按钮
    #     style.configure("TButton",fieldbackground='blue',background='blue', \
    #         )
        

    # else:
    #     style.configure("Treeview.Heading", font=FONT_TREE_HEADING, \
    #                     rowheight=int(LARGE_FONT * 4), height=int(LARGE_FONT * 4))
    #     style.configure("Treeview", font=FONT_TREE_BODY, \
    #                     rowheight=int(MON_FONTSIZE * 3.5))
    #
    # 通用函数
    try:  # 调整清晰度
        # 放在这里，是为了兼容不能打开ctypes的计算机。
        from ctypes import windll

        # 告诉操作系统使用程序自身的dpi适配
        windll.shcore.SetProcessDpiAwareness(1)
        # 获取屏幕的缩放因子
        ScaleFactor = windll.shcore.GetScaleFactorForDevice(0)  # 当前屏幕放大百分数（125）
        # 设置程序缩放
        window.tk.call('tk', 'scaling', ScaleFactor / 75)
        #
        SCREEN_WIDTH = window.winfo_screenwidth() * ScaleFactor / 100  # 必须考虑分辨率导致的偏移
        SCREEN_HEIGHT = window.winfo_screenheight() * ScaleFactor / 100  #
    except:
        SCREEN_WIDTH = window.winfo_screenwidth()
        SCREEN_HEIGHT = window.winfo_screenheight()
    #
    # 加载设置参数。
    json_data = OPT_DEFAULT  # 用于后面处理的变量。
    load_json_file_data()

    str_btm = tk.StringVar()  # 最下面显示状态用的
    str_btm.set("加载中")
    prog = tk.DoubleVar()  # 进度
    prog_win = ''

    if ALL_FOLDERS == 1:  # 对应是否带有“所有文件夹”这个功能的开关
        lst_my_path_long_selected = lst_my_path_long.copy()  # 用这个变量修复添加文件夹之后定位不准确的问题。
        lst_files_to_go = get_data(lst_my_path_long_selected)
    else:
        try:
            lst_my_path_long_selected = [lst_my_path_long[0]]
            lst_files_to_go = get_data(lst_my_path_long_selected)
        except:
            lst_files_to_go = get_data()  # 此处有隐患，还没条件测试

    (dT, lst_tags) = get_dt()

    # 窗体设计
    window.title(TAR + ' ' + VER)
    screenwidth = SCREEN_WIDTH
    screenheight = SCREEN_HEIGHT
    w_width = int(screenwidth * 0.8)
    w_height = int(screenheight * 0.8)
    x_pos = (screenwidth - w_width) / 2
    y_pos = (screenheight - w_height) / 2
    window.geometry('%dx%d+%d+%d' % (w_width, w_height, x_pos, y_pos))
    # window.resizable(0,0) #限制尺寸
    window.state('zoomed')  # 最大化

    ####################################################################
    # 框架设计
    frame_window=ttk.Frame(window,padding=(1,1,1,1),relief='flat',borderwidth=0) 
    frame_window.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=3, pady=3)
    # 文件夹区
    frameLeft = ttk.Frame(frame_window, 
        # style="Dark.Treeview",
        width=int(w_width * 0.4),
        padding=(0,0,0,0),
        borderwidth=0,
        relief='flat')  # ,width=600)
    frameLeft.pack(side=tk.LEFT, expand=0, fill=tk.Y, padx=0, pady=0)  # padx=10,pady=5)
    # for i in range(2):
    # frameLeft.rowconfigure(i,weight=1)

    frameFolder = ttk.Frame(frameLeft,relief='flat', borderwidth=0,
        height=SCREEN_HEIGHT * 0.8)  # ,width=600),width=int(w_width*0.4)
    frameFolder.pack(side=tk.TOP, expand=1, fill=tk.Y, padx=0, pady=2)  # padx=10,pady=5)
    # frameFolder.grid(column=0,row=0)

    # 子文件夹区
    frameSubFolder = ttk.Frame(frameLeft,relief='flat')  # ,width=600)
    frameSubFolder.pack(side=tk.BOTTOM, expand=1, fill=tk.Y, padx=0, pady=2)  # padx=10,pady=5)
    # 同位置的标签区
    # frameSubTags = ttk.Frame(frameLeft)  # ,width=600)
    # frameSubTags.pack(side=tk.BOTTOM, expand=1, fill=tk.Y, padx=10, pady=5)  # padx=10,pady=5)
    #
    # 文件夹下面的控制区
    frameFolderCtl = ttk.Frame(frameLeft, height=10, borderwidth=0, relief=tk.SOLID)
    # frameFolderCtl.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=5)

    # 上面功能区
    frame0 = ttk.Frame(frame_window, relief='flat', height=120)#, borderwidth=1 ,relief='solid')  # ,width=600) LabelFrame
    frame0.pack(expand=0, fill=tk.X, padx=0, pady=0)# padx=10, pady=5)

    # 主功能区
    frameMain = ttk.Frame(frame_window)  # ,height=800)
    frameMain.pack(expand=1, fill=tk.BOTH, padx=0, pady=0)# padx=10, pady=0)

    # 底部区
    frameBtm = ttk.Frame(frame_window, height=120,padding=(0,0,0,0),relief='flat')
    frameBtm.pack(side=tk.BOTTOM, expand=0, fill=tk.X, padx=0, pady=0)

    # %%
    v_sub_folders = ttk.Combobox(frame0)  # 子文件夹选择框
    v_tag = ttk.Combobox(frame0)  # 标签选择框
    v_search = ttk.Entry(frame0)  # 搜索框
    v_folders = ttk.Combobox(frameFolder)  # 文件夹选择框

    bar_tree_v = tk.Scrollbar(frameMain, width=16)  # 右侧滚动条
    bar_tree_h = tk.Scrollbar(frameMain, orient=tk.HORIZONTAL, width=16)  # 底部滚动条

    # ---

    # %%
    vPDX = 10
    vPDY = 5

    # bt_setting=ttk.Button(frameBtm,text='设置')#,command=show_window_setting)
    # bt_setting.pack(side=tk.LEFT,expand=0,padx=5,pady=10)#,fill=tk.X) # 

    bt_folder_add = ttk.Button(frameFolderCtl, text='添加文件夹')  # state=tk.DISABLED,,command=setting_fun
    bt_folder_add.pack(side=tk.LEFT, expand=0, padx=20, pady=10, fill=tk.X)  #

    bt_folder_drop = ttk.Button(frameFolderCtl, text='移除文件夹')  # state=tk.DISABLED,,command=setting_fun
    bt_folder_drop.pack(side=tk.RIGHT, expand=0, padx=20, pady=10, fill=tk.X)  #

    bar_folder_v = tk.Scrollbar(frameFolder, width=16)
    bar_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)

    # 文件夹列表
    if True:
        tree_lst_folder = ttk.Treeview(frameFolder,
                                    columns=['folders'],
                                    # columns = ['index','type','folders','folder_path'],
                                    displaycolumns=['folders'],
                                    selectmode=tk.BROWSE,
                                    show="headings",
                                    # show="tree",
                                    # cursor='hand2',
                                    # pady=0,padx=0,
                                    yscrollcommand=bar_folder_v.set)  # , height=18)
        bar_folder_v.config(command=tree_lst_folder.yview)

        tree_lst_folder.heading("folders", text="关注的文件夹", anchor='w')
        tree_lst_folder.column('folders', width=300, anchor='w')
        #
        tree_lst_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
        update_folder_list()

    # 子文件夹列表
    if True:
        bar_sub_folder_v = tk.Scrollbar(frameSubFolder, width=16)
        if TREE_SUB_SHOW=='sub_folder':
            bar_sub_folder_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)

        tree_lst_sub_folder = ttk.Treeview(frameSubFolder,
                                        columns=['folders'],
                                        # columns = ['index','type','folders','folder_path'],
                                        displaycolumns=['folders'],
                                        selectmode=tk.BROWSE,
                                        show="headings",
                                        # show="tree",
                                        # cursor='hand2',
                                        style="Dark.Treeview",
                                        yscrollcommand=bar_sub_folder_v.set)  # , height=18)

        tree_lst_sub_folder.heading("folders", text="子文件夹", anchor='w')
        tree_lst_sub_folder.column('folders', width=300, anchor='w')
        bar_sub_folder_v.config(command=tree_lst_sub_folder.yview)
        #
        update_sub_folder_list(lst_sub_path) # 填充内容
        if TREE_SUB_SHOW=='sub_folder':
            tree_lst_sub_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
    #
    # 标签列表：
    if True:
        v_tag_search=tk.Entry(frameSubFolder)
        bar_sub_tag_v = tk.Scrollbar(frameSubFolder, width=16)
        if TREE_SUB_SHOW=='tag':
            # v_tag_search.pack(side=tk.TOP,expand=0,fill=tk.X)
            bar_sub_tag_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)

        tree_lst_sub_tag = ttk.Treeview(frameSubFolder,
                                        columns=['tags'],
                                        # columns = ['index','type','folders','folder_path'],
                                        displaycolumns=['tags'],
                                        selectmode=tk.BROWSE,
                                        show="headings",
                                        # show="tree",
                                        # cursor='hand2',
                                        
                                        yscrollcommand=bar_sub_tag_v.set)  # , height=18)

        tree_lst_sub_tag.heading("tags", text="标签", anchor='w',command=tree_tag_search)
        tree_lst_sub_tag.column('tags', width=300, anchor='w')
        bar_sub_tag_v.config(command=tree_lst_sub_tag.yview)
        #
        if TREE_SUB_SHOW=='tag':
            tree_lst_sub_tag.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
    #
    # tree_lst_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=10)
    # tree_lst_sub_folder.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=10)
    #
    # 主文件列表
    columns = ("index", "file", "tags", "modify_time", "size", "file0")
    column_text = ("序号", "文件名", "标签", "修改时间", "文件大小(kB)", "完整路径")
    tree_displaycolumns = ["file", "tags", "modify_time", "size"]
    col_dic={
        "序号":{
            "name":"index",
            "text":"序号",
            "visb":False,
            "head_anch":"center",
            "body_anch":"center",
            "width":30,
            "head_command":None
        },
        "文件名":{
            "name":"file",
            "text":"文件名",
            "visb":True,
            "head_anch":"w",
            "body_anch":"w",
            "width":400,
            "head_command":tree_order_filename
        }
    }
    #
    tree = ttk.Treeview(frameMain, show="headings", columns=columns, \
                        displaycolumns=tree_displaycolumns, \
                        # selectmode=tk.BROWSE, \
                        selectmode='extended', \
                        yscrollcommand=bar_tree_v.set, xscrollcommand=bar_tree_h.set)  # , height=18)

    tree.column('index', width=30, anchor='center')
    tree.column('file', width=400, anchor='w')
    tree.column('tags', width=300, anchor='w')
    tree.column('modify_time', width=100, anchor='w')
    tree.column('size', width=80, anchor='w')
    tree.column('file0', width=80, anchor='w')

    tree.heading("index", text="序号", anchor='center')
    tree.heading("file", text="文件名", anchor='w', command=tree_order_filename)
    tree.heading("tags", text="标签", anchor='w', command=tree_order_tag)
    tree.heading("modify_time", text="修改时间", anchor='w', command=tree_order_modi_time)
    tree.heading("size", text="文件大小(kB)", anchor='w', command=tree_order_size)
    tree.heading("file0", text="完整路径", anchor='w', command=tree_order_path)
    # 
    # 增加排序方向的可视化（三角形）
    show_tree_order()

    try:
        exec_add_tree_item(tree, dT)
    except Exception as e:
        print(e)
        print('初始化主列表发生错误')
        str_btm.set('已就绪')
        pass

    # 样式
    # style = ttk.Style()
    # style.configure("Treeview.Heading", font=FONT_TREE_HEADING, \
    #                 rowheight=int(LARGE_FONT * 4), height=int(LARGE_FONT * 4))
    # style.configure("Treeview", font=FONT_TREE_BODY, \
    #                 rowheight=int(MON_FONTSIZE * 3.5))
    # style.configure("Dark.Treeview", background='blue')
    # style.configure("Button",font=('微软雅黑', 12))

    # style.configure("Treeview.Heading", font=(None, 12),rowheight=60)
    # 行高
    # style.configure("Treeview.Heading", font=(None, 12))

    vPDX = 10#10
    vPDY = 5#5

    if True:  # 子文件夹搜索
        lable_sub_folders = tk.Label(frame0, text='子文件夹')
        if TREE_SUB_SHOW=='tag':
            lable_sub_folders.pack(side=tk.LEFT,expand=0,padx=0,pady=vPDY) # 

        v_sub_folders['value'] = [''] + lst_sub_path
        v_sub_folders['state'] = 'readonly'
        if TREE_SUB_SHOW=='tag':
            v_sub_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
        v_sub_folders.bind('<<ComboboxSelected>>', exec_after_sub_folders_choose)

    if TREE_SUB_SHOW=='sub_folder':
        lable_tag = tk.Label(frame0, text='标签')
        lable_tag.pack(side=tk.LEFT, expand=0, padx=2, pady=vPDY)  #

    set_search_tag_values(lst_tags)
    v_tag['state'] = 'readonly'  # 只读
    if TREE_SUB_SHOW=='sub_folder':
        v_tag.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #
    v_tag.bind('<<ComboboxSelected>>', exec_search)
    v_tag.bind('<Return>', exec_search)  # 绑定回车键

    lable_search = tk.Label(frame0, text='关键词')
    lable_search.pack(side=tk.LEFT, expand=0, padx=0, pady=vPDY)  #

    v_search.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #
    v_search.bind('<Return>', exec_search)  # 绑定回车键

    # bt_search=tk.Button(frame0,text='搜索', command=exec_search,bd=0,activebackground='red')
    bt_search = ttk.Button(frame0, text='搜索', command=exec_search)  # ,bd=0,activebackground='red')
    bt_search.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #

    bt_clear = ttk.Button(frame0, text='清空', command=exec_clear_search_items)
    bt_clear.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #

    bt_test = ttk.Button(frame0, text='测试功能', command=exec_fun_test)
    if DEVELOP_MODE:
        bt_test.pack(side=tk.LEFT, expand=0, padx=vPDX, pady=vPDY)  #

    # 布局
    bar_tree_h.pack(side=tk.BOTTOM, expand=0, fill=tk.X, padx=2, pady=1)  # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

    tree.pack(side=tk.LEFT, expand=1, fill=tk.BOTH, padx=2, pady=1)

    bar_tree_v.pack(side=tk.LEFT, expand=0, fill=tk.Y, padx=2, pady=1)  # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

    vPDX = 10
    vPDY = 5

    # 进度条
    frame_prog=ttk.Frame(frameBtm)
    # frame_prog.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY)
    progressbar_file = ttk.Progressbar(frame_prog, variable=prog, mode='determinate')
    progressbar_file.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY)

    lable_sum = tk.Label(frameBtm, text=str_btm, textvariable=str_btm)
    lable_sum.pack(side=tk.LEFT, expand=0, padx=2, pady=vPDY)  #

    bt_settings = ttk.Button(frameBtm, text='菜单')  # ,command=show_online_help)
    bt_settings.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

    bt_reload = ttk.Button(frameBtm, text='刷新', command=update_main_window)
    bt_reload.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

    bt_new = ttk.Button(frameBtm, text='新建笔记')  # ,state=tk.DISABLED)#,command=update_main_window)
    bt_new.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

    bt_add_tag = ttk.Button(frameBtm, text='添加标签',command=exec_input_new_tag_via_dialog)#, command=input_new_tag
    bt_add_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

    # 新标签的输入框
    v_inp = ttk.Combobox(frameBtm, width=16)
    # v_inp.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
    v_inp.bind('<Return>', input_new_tag)
    v_inp['value'] = lst_tags

    lable_tag = tk.Label(frameBtm, text='添加新标签')
    # lable_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

    # 设置拖拽反映函数
    windnd.hook_dropfiles(tree_lst_folder, func=exec_folder_add_drag)
    # windnd.hook_dropfiles(tree, func=exec_tree_drag_enter_popupmenu)
    windnd.hook_dropfiles(tree, func=exec_tree_drag_enter)

    

    # 其他初始化设定
    if ALL_FOLDERS == 1:
        bt_folder_drop.configure(state=tk.DISABLED)

    # 各种功能的绑定
    # tree_lst_folder.bind('<<ListboxSelect>>',exec_after_folder_choose)
    # tree_lst_folder.bind('<Button-1>',exec_after_folder_choose)
    tree_lst_folder.bind('<ButtonRelease-1>', exec_after_folder_choose)
    tree_lst_folder.bind('<KeyRelease-Up>', exec_after_folder_choose)
    tree_lst_folder.bind('<KeyRelease-Down>', exec_after_folder_choose)
    #
    # tree_lst_sub_folder.bind('<<TreeviewSelect>>', exec_after_sub_folders_choose) # 会导致重复加载
    tree_lst_sub_folder.bind('<ButtonRelease-1>', exec_after_sub_folders_choose)
    tree_lst_sub_folder.bind('<KeyRelease-Up>', exec_after_sub_folders_choose)
    tree_lst_sub_folder.bind('<KeyRelease-Down>', exec_after_sub_folders_choose)
    #
    tree_lst_sub_tag.bind('<ButtonRelease-1>', exec_after_sub_tag_choose)
    tree_lst_sub_tag.bind('<KeyRelease-Up>', exec_after_sub_tag_choose)
    tree_lst_sub_tag.bind('<KeyRelease-Down>', exec_after_sub_tag_choose)

    # tree.tag_configure('line1', background='#EEEEEE')  # 灰色底纹
    #
    tree.bind('<Double-Button-1>', exec_tree_file_open)
    tree.bind('<Return>', exec_tree_file_open)
    tree.bind("<Button-3>", show_popup_menu_file)  # 绑定文件夹区域的功能
    tree.bind('<F5>', update_main_window)  # 刷新。
    #
    tree_lst_folder.bind("<Button-3>", show_popup_menu_folder)  # 绑定文件夹区域的右键功能
    tree_lst_sub_folder.bind("<Button-3>", show_popup_menu_sub_folder)  # 绑定文件夹区域的右键功能
    
    

    # 程序内快捷键
    window.bind_all('<Control-n>', exec_create_note)  # 绑定添加笔记的功能。
    window.bind_all('<Control-f>', jump_to_search)  # 跳转到搜索框。
    window.bind_all('<F2>', exec_file_rename)  # 跳转到搜索框。
    
    # window.bind_all('<Control-t>',jump_to_tag) # 跳转到标签框。
    window.bind_all('<Control-t>', exec_input_new_tag_via_dialog)  # 快速输入标签。

    # 按钮功能绑定
    # bt_setting.configure(command=show_window_setting) # 
    bt_folder_add.configure(command=exec_folder_add_click)  # 增加文件夹
    bt_folder_drop.configure(command=exec_folder_drop)  # 减少文件夹
    # bt_folder_drop.configure(command=exec_input_new_tag_via_dialog)  # 加标签
    # bt_settings.configure(command=show_popup_menu_main)  # 菜单按钮
    bt_settings.bind("<ButtonRelease-1>", show_popup_menu_main)  # 菜单按钮
    bt_new.configure(command=exec_create_note)

    bar_tree_v.config(command=tree.yview)
    bar_tree_h.config(command=tree.xview)
    # tree.pack(expand = True, fill = tk.BOTH)
    #
    # 测试气泡
    # b = tix.Balloon(window, statusbar=None)
    # b.bind_widget(bt_clear,balloonmsg='test',statusmsg=None)
    #
    # 样式
    for tar in [tree_lst_folder,tree_lst_sub_folder,tree_lst_sub_tag,tree]:
        tar.tag_configure('line1',background="#F2F2F2")

    # 运行

    window.iconbitmap(LOGO_PATH)  # 左上角图标
    flag_inited = 1  # 代表前面的部分已经运行过一次了
    set_prog_bar(0)
    # update_sub_folder_list(lst_sub_path)
    # bt_add_tag.pack_forget()

    if True:
        sub_task=threading.Thread(target=update_data,args=(lst_my_path_long,))
        sub_task.start()

    window.mainloop()
