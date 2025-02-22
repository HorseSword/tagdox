# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian

## 近期更新说明
#### v0.28.1.1 2025年2月18日
fixed: 修正了无配置文件启动时（全新启动），因列表溢出导致无法启动的bug。

#### v0.28.1.0 2024年5月14日
左侧文件夹可以设置为常开模式了；
优化配置文件的显示格式。

#### v0.28.0.0 2024年5月10日
增加了通过配置文件调整界面尺寸的功能。

"""
import tkinter as tk

from tkinter import ttk
# import tkinter.tix as Tix 
# from tkinter import tix
# from tkinter import Text, Variable
import tkinter.messagebox
from tkinter import filedialog
# from tkinter import font
# from tkinter.constants import INSERT
import windnd  # 用于拖拽
#
import threading  # 多线程
# import multiprocessing
from multiprocessing import Pool  # 进程
# from docx import Document  # 用于创建word文档
# import ctypes # 用于调整分辨率 #
# from win32com.shell import shell, shellcon  # 此处报错是编辑器的问题，可以忽略
import queue
# 
import subprocess  # 用于打开文件所在位置并选中文件
import logging
logging.basicConfig(level=logging.ERROR) # logging.INFO DEBUG ERROR
#
# 自建库
from libs.common_funcs import *
from libs.my_filetools import *
from libs.markdown import MarkdownRel  # 对 markdown 的特殊处理
#
from codes.logic.conf import td_conf
from codes.logic.common import exec_list_sort
# 控件库
from codes.gui.windows import TdProgressWindow as TdProgressWindow
from codes.gui.windows import TdInputWindow as TdInputWindow
from codes.gui.windows import TdTextWindow
from codes.gui.window_settings import window_settings
from codes.gui.window_info import window_info
from codes.gui.tree_tag import tree_tag
from codes.gui.tree_folder import tree_folder
from codes.gui.tree_plus import tree_obj_find, tree_obj_scroll_to_selection, tree_obj_clear, tree_obj_mouse_highlight
from codes.gui.style import set_style as set_style_view
##
# import my_logger
# import send2trash # 回收站（目前作废）
###################################################################


class td_const():
    """
    用于存储常量
    """
    def __init__(self):
        self.URL_HELP = 'https://gitee.com/horse_sword/tagdox'  # 帮助的超链接，目前是 gitee 主页
        self.URL_ADV = 'https://gitee.com/horse_sword/tagdox/issues'  # 提建议的位置
        self.URL_CHK_UPDATE = 'https://gitee.com/horse_sword/tagdox/releases'  # 检查更新的位置
        self.TAR = 'Tagdox / 标签文库'  # 程序名称
        self.VER = 'v0.28.1.1'  # 版本号

conf = td_conf()  # 关键参数
cst = td_const()  # 常量

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

FOLDER_TYPE = 2
TAG_METHOD = 'FILE_STREAM'  # FILE_STREAM 或者 FILENAME
IS_MARKDOWN_MOVE_WITH_IMGS = True  # 是否移动markdown的时候，移动相应的相对路径文件；
#
# %%
#######################################################################

class td_data:
    """
    数据核心存储到这里。尽量不与其他变量过分耦合。
    """
    def __init__(self):
        self.dict_files = dict()  # 原名dicT，以完整路径为键，参数为值，用于加速程序显示
        #
        self.dt = []  # 用于存储临时值，加快运行速度。
        # self.lst_tags = []  # 存储当前列表的全部标签
        self.lst_tags_selected = []
        #
        self.lst_sub_path = []  #
        self.lst_sub_path_selected = []
        #
        self.lst_files_to_go = []  # 所有文件的完整路径，通过 get_data 获取
        #
        # 从 conf 迁移到 data 里面。但是并不成功。
        # self.dict_path = dict()  # 用于列表简写和实际值 #
        # self.dict_folder_groups = dict()  #
        # self.lst_my_path_long_selected = []  #
        # self.lst_my_path_short = []  #
        # self.lst_my_path_long = []  #

    def get_files_full_path(self, path_in):
        """
        根据
        """
        pass


# def exec_list_sort(lst):
#     """
#     通用函数，按我的规矩为列表排序的函数。
#
#     """
#     if not type(lst) is list:
#         return None
#     #
#     lst2 = lst.copy()
#     #
#     # 令@开头的标签在最前
#     lst_top = []
#     lst_en = []
#     lst_cn = []
#     for i in lst2:
#         if i == '':
#             continue
#         if str(i).startswith('@'):
#             lst_top.append(i)
#         else:
#             lst_en.append(i)
#     # 英文无论大小写都一起排序
#     # 如果是^开头，就忽略这个符号，直接正常排序
#     lst_en = sorted(lst_en, key=lambda x: str.lower(x.replace(conf.V_SEP, '').replace('\xa0', ' ')).encode('gbk'))
#     # 中文也排序
#     lst_cn = sorted(lst_cn, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
#     # 组合起来
#     lst2 = lst_top + lst_en + lst_cn
#     #
#     return lst2


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
    logging.debug('调用 get_data 函数')

    if is_global:
        lst_sub_path = app.lst_sub_path
    else:
        lst_sub_path = []

    if ipath is None:
        ipath = conf.lst_my_path_long

    # app.flag.flag_running=1 # 标记为运行中。

    lst_sub_path_copy = lst_sub_path.copy()
    if app.flag.flag_inited == 1:
        tree_obj_clear(app.tree_file)  #
        if need_set_prog: set_prog_bar(1, 30)
        app.str_btm.set("正在加载基础数据……")
        app.window.update()

    time0 = time.time()
    lst_files_to_go = []  # 获取所有文件的完整路径

    n = 1
    n_max = len(ipath)
    lst_sub_path = []

    PROG_STEP = 2
    logging.debug('\nget_data函数中获得的参数：')
    logging.debug(ipath)
    have_sub_folder = 0
    #
    for vPath in ipath:
        have_sub_folder = 0  # 应该在这
        n += 1  # 第一轮循环的时候n就是2
        #
        if app.flag.flag_inited == 1 and n % PROG_STEP == 0:
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

            if app.flag.flag_break:  # 强行中断
                break
        if app.flag.flag_break:
            break

    logging.debug('——————  加载 文件列表 消耗时间：——————\n')
    logging.debug(time.time() - time0)
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
            logging.debug(lst_sub_path)
            logging.debug(lst_sub_path_copy)
    except:
        pass

    if update_sub_path:  # 如果参数为1的话，
        try:
            logging.debug('即将刷新子文件夹')
            lst_sub_path.sort()
            app.v_sub_folders['value'] = [''] + lst_sub_path  # 强制修改子文件夹列表，但这样写【不太好】。
            app.v_sub_folders.current(0)
            #
            # update_sub_folder_list(lst_sub_path)
        except Exception as e:
            logging.error('error 374'+ str(e))
            pass
    else:
        lst_sub_path = lst_sub_path_copy
    # if app.flag.flag_inited==1:
    #     set_prog_bar(30,30)

    return lst_files_to_go


def get_file_part(file_path_full):  #
    """
    分拆。
    【疑似bug】对带有空格的路径解析异常

    :param file_path_full: 是完整文件路径。
    :returns: （文件）路径，以字典的形式，返回对应的所有文件信息。
    """

    [fpath, ffname] = os.path.split(file_path_full)  # fpath 所在文件夹、ffname 原始文件名
    [fname, fename] = os.path.splitext(ffname)  # fname 文件名前半部分，fename 扩展名
    lst_sp = fname.split(conf.V_SEP)  # 拆分为多个片段
    fname_0 = lst_sp[0] + fename  # fname_0 去掉标签之后的文件名
    ftags = lst_sp[1:]  # ftags 标签部分
    #
    if is_read_only(file_path_full):
        ftags.append('只读')
        # read_only_set(file_path_full, False)
    #
    # 增加NTFS流的标签解析
    if TAG_METHOD == 'FILE_STREAM':
        try:
            with open(file_path_full + ":tags", "r", encoding="utf8") as f:
                ftags += (set(list(map(lambda x: x.strip(), f.readlines()))))
        except FileNotFoundError:
            pass
        except Exception as e:
            # print(e)
            pass

    mtime = os.stat(file_path_full).st_mtime  # 修改时间
    file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    ctime = os.stat(file_path_full).st_ctime  # 创建时间
    file_create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))

    fsize = os.path.getsize(file_path_full)  # 文件大小，字节
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
            logging.error('error 449: '+ str(e))
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
    file_path_full = file_path_full.replace('\\', '/')

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
            'full_path': file_path_full,  # 全路径
            'fsize': fsize_k,  #
            'file_full_path': file_path_full,  # 完整路径，和输入参数完全一样
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
        # TODO 应该增加 errors = 'replace' 之类的处理方式


def sub_get_dt(lst_file_in):
    """
    dt 的作用是

    """
    # 子循环
    tmp_dt = []
    for tar in lst_file_in:
        tmp = get_file_part(tar)
        tmp_v = (str(tmp['fname_0']), tmp['ftags'], str(tmp['file_mdf_time']), tmp['fsize'], str(tmp['full_path']))
        tmp_dt.append(tmp_v)
    td_queue.put(tmp_dt)  # 存储到队列中
    logging.debug([conf.V_FOLDERS, conf.V_SEP, conf.NOTE_EXT])
    return tmp_dt


def process_update_data(lst1):
    """
    用于后台加载数据。

    :param lst1: 传入的是完整路径列表。
    """
    logging.info('———— 后台数据加载开始 ————')

    lst_files_to_go = []
    n = 0
    app.flag.flag_break = 0
    time0 = time.time()

    for vPath in lst1:
        n += 1  # 第一轮循环的时候n就是2
        #

        for root, dirs, files in os.walk(vPath):
            tmp = []
            vpass = 0
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

            if app.flag.flag_break:  # 强行中断
                break
        if app.flag.flag_break:
            break

    for one_file in lst_files_to_go:
        # 先查字典，这样可以显著加速查询
        one_file = one_file.replace('\\', '/')
        if one_file in core_data.dict_files.keys():
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
                core_data.dict_files[one_file] = tmp_v
            except Exception as e:
                print(e)
                pass
    #
    logging.info(f'时间消耗：{time.time() - time0}')
    logging.info('———— 后台数据加载完毕 ————')


def get_dt(lst_file0=None, need_set_prog=True, FAST_MODE=True):
    """
    是最消耗时间的函数，也是获取数据的核心函数。
    输入参数是文件列表，lst_file0。
    这个参数的缺省值是来自于 get_data() 函数的 lst_files_to_go ，提供了所有文件。

    根据 lst_files_to_go 里面的文件列表，返回 (dT, lst_tags) .\n
    注意这里(dT, lst_tags)都不是全局变量，需要从返回值获得。

    只有 core_data.dict_files 是全局变量，用于存储临时值，加快运行速度。
    """
    logging.debug('进入 get_dt 函数')

    if app.flag.flag_break:
        return (None, None)

    if lst_file0 is None:
        lst_file0 = app.lst_files_to_go.copy()

    if app.flag.flag_inited == 1:
        app.str_btm.set("正在解析标签……")
        app.window.update()
        if need_set_prog:
            set_prog_bar(30)

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
        while not td_queue.empty():
            tmp_get_dt = td_queue.get()
            # print(tmp_get_dt)
            dT += tmp_get_dt
        if need_set_prog: set_prog_bar(70)
        # tmp_part=[]
        # print('组合之前：——————')
        # print(time.time()-time0)
        # for i in res_tmp:
        # dT+=i
        logging.debug('组合之后：——————')
        logging.debug(time.time() - time0)
        #
    else:  # 单线程

        for one_file in lst_file0:
            one_file = one_file.replace('\\', '/')
            # 更新进度条
            n += 1
            if app.flag.flag_inited == 1 and n % PROG_STEP == 0:
                if need_set_prog: set_prog_bar(30 + 60 * n / n_max)
            # 先查字典，这样可以显著加速查询
            if FAST_MODE and one_file in core_data.dict_files.keys():
                tmp_v = list(core_data.dict_files[one_file])

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

                    core_data.dict_files[one_file] = tmp_v
                except Exception as e:
                    logging.error('ERROR 708 ' + str(e))
                    pass
            # if not tmp_v in dT:
            #     dT.append(tmp_v) # 查重有点费时间
            dT.append(tmp_v)
            #
            if app.flag.flag_break:  # 如果被中断的话
                break

    logging.debug('加载dT消耗时间：' + str(time.time() - time0))

    # 去重
    dT2 = []
    for i in dT:
        if not i in dT2:
            dT2.append(i)
    dT = dT2
    # dT=list(set(dT))

    if app.flag.flag_inited == 1:
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
        logging.error('ERROR 743: dT排序出现错误！')

    return (dT, lst_tags)


# %%
#######################################################################
# %%
class window_manager:
    """
    弹窗管理员
    """
    def show_window_info(self, event=None):
        """
        打开关于窗口
        """
        win_info_obj = window_info(conf, app, cst.VER)
        win_info_obj.show()

    def show_window_settings(self, event=None):
        """
        显示设置窗口，但只有在调用的时候才会初始化。
        """
        win_settings_obj = window_settings(conf=conf, app=app, update_func=app_refresh)
        win_settings_obj.show()

    def show_window_closing(self, event=None, need_asking=False):
        """
        退出程序。
        """
        if need_asking:
            if tk.messagebox.askokcancel("退出", "真的要退出吗"):
                app.window.destroy()
        else:
            app.window.destroy()

def show_window_input(title_value, body_value='', init_value='', is_file_name=True, app=None):
    """
    接管输入框的过程，以后可以将自定义输入框替换到这里。

    目前的用法：输入参数 1 标题，2 正文，3 默认值；

    返回输入框的结果。如果输入内容为空，返回 None。

    参数 is_file_name 为 True 的时候，将文件名不能带的特殊字符自动去掉。

    """
    if app is None:
        return ''

    # 获得输入值
    res = str(TdInputWindow(app.window, title=title_value, msg=body_value,
                            default_value=init_value, ui_ratio=conf.ui_ratio,)).strip()
    if len(res) == 0:
        logging.warning('没有得到输入内容')
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


def update_sub_folder_list_USELESS(sub_folder_list=None, refresh=True):  # TODO 似乎没用，准备删掉
    """
    将子文件夹列表刷新一次。
    输入是要填充的子文件夹列表。
    参数 refresh =True 就选中全部子文件夹，=False 选中之前的。
    """
    #
    tmp_sub_folder = app.XX_tree_lst_sub_folder.selection()  # 保存当前值
    #
    # 清空一次
    tree_obj_clear(app.XX_tree_lst_sub_folder)
    #
    # 主文件夹为全部的时候，不返回任何子文件夹
    if get_folder_short() in ["（全部）", ""]:
        print('主文件夹为全部，所以不更新子文件夹')
        return
    #
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
                res = conf.dict_path[short_folder]
                res = str(res).replace('\\', '/')
        #
        elif FOLDER_TYPE == 2:
            res = get_folder_short()
            res = str(res).replace('\\', '/')
        #
        return res

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
    app.XX_tree_lst_sub_folder.insert('', tmp, values=("（全部）"), tags=['line1'] if tmp % 2 == 0 else ['line2'])
    # 排序
    sub_folder_list = sorted(sub_folder_list, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    #
    for i in sub_folder_list:
        if i in conf.EXP_FOLDERS:
            continue
        tmp += 1
        logging.debug(i)
        app.XX_tree_lst_sub_folder.insert('', tmp, values=(i,),
                                   tags=['line1'] if tmp % 2 == 0 else ['line2'])  # 必须加逗号，否则对存在空格的不可用
        # image=IMAGE_FOLDER,
    # 
    # 恢复之前的选项；
    try:
        if refresh is None:
            pass
        elif refresh:  # refresh =True 代表重置当前选项，也就是选中最开始的。
            tmp = app.XX_tree_lst_sub_folder.get_children()[0]
            # app.tree_lst_folder.focus(tmp)
            app.XX_tree_lst_sub_folder.selection_set(tmp)
        else:  # 否则选中之前的；
            try:
                app.XX_tree_lst_sub_folder.selection_set(tmp_sub_folder)
            except:
                tmp = app.XX_tree_lst_sub_folder.get_children()[0]
                app.XX_tree_lst_sub_folder.selection_set(tmp)
        # 刷新一次；
        # app_refresh(0,fast_mode=True)#reload_setting=2)
    except Exception as e:
        print(e)
        app.tree_folder.refresh()
        pass


def tree_file_order_show():
    """
    用来显示 tree_file 排序的视觉效果（也就是加三角）
    """
    DIR_VALUE = DIR_LST[1] if conf.ORDER_DESC else DIR_LST[0]
    app.tree_file.heading(HEADING_LST[conf.ORDER_BY_N], text=HEADING_LST_TXT[conf.ORDER_BY_N] + DIR_VALUE)


def tree_file_order_by(inp):
    """
    主列表排序的入口程序。
    """

    # global dT#, lst_tags
    # 恢复标题
    app.tree_file.heading(HEADING_LST[conf.ORDER_BY_N], text=HEADING_LST_TXT[conf.ORDER_BY_N])
    #
    if conf.ORDER_BY_N == inp:  # 如果同样位置点击，就切换排序方式
        conf.ORDER_DESC = not conf.ORDER_DESC  # 正序 / 倒序
    else:  # 如果不同位置点击，就预置排序方式
        conf.ORDER_BY_N = inp
        if conf.ORDER_BY_N == 2:  # 按修改时间排序的，第一次是最新的在前面。
            conf.ORDER_DESC = True
        else:
            conf.ORDER_DESC = False  # 其余排序方法，都是升序。
    # app_refresh(0) # 这个方法虽然可以排序，但是效率太低
    #
    # 可视化
    tree_file_order_show()
    # 新的排序方法
    app.DT.sort(key=dt_sort_by, reverse=conf.ORDER_DESC)
    tree_file_search()
    app.tree_tag.set_lst_tag(app.lst_tags)
    app.combobox_tag['value'] = app.lst_tags


def tree_order_filename(inp=None):
    tree_file_order_by(0)


def tree_order_tag(inp=None):
    tree_file_order_by(1)


def tree_order_modi_time(inp=None):
    tree_file_order_by(2)


def tree_order_size(inp=None):
    tree_file_order_by(3)


def tree_order_path(inp=None):
    tree_file_order_by(4)

def set_sub_folder_selected(inp):
    if type(inp) is str:
        tmp_n = app.lst_sub_path.index(inp)
        app.v_sub_folders.current(tmp_n + 1)
    elif type(inp) is int:
        app.v_sub_folders.current(inp)


# def set_search_tag_selected(ind):
#     """
#     设置标签，选中指定的项目。
#     如果输入的是字符串，则选中字符串。
#     """
#     # 如果是字符串的话；
#     if type(ind) is str:
#         try:
#             tags2 = app.v_tag['values']
#             set_search_tag_selected(tags2.index(ind))
#         except:
#             set_search_tag_selected(0)
#     # 如果是数字的话
#     elif type(ind) is int:
#         #
#         # 下拉框
#         app.v_tag.current(ind)
#         #
#         # 列表：
#         # tree_obj_find('（全部）',the_tree=app.tree_lst_sub_tag,the_bar=app.bar_sub_tag_v,the_col=0)
#     else:
#         app.v_tag.current(0)

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
    if len(app.tree_tag.get_tag()) > 0:
        res_tag = [app.tree_tag.get_tag()]
        res += res_tag
    #
    # 关键词
    if len(app.entry_search_files.get()) > 0:
        res_keyword = str(app.entry_search_files.get()).split(' ')
        res += res_keyword
    #
    # 子文件夹
    if len(get_sub_folder_selected()) > 0:
        tmp_path = conf.get_current_path() + '/' + get_sub_folder_selected()
        print('进入子文件夹：')
        print(tmp_path)
        res_path = [tmp_path]
        res += res_path
    else:
        # 还要考虑子文件夹从有到无时候的处理；
        pass

    if res_lst:
        return res_tag, res_keyword, res_path
    else:
        return res


def get_sub_folder_selected():
    """
    获取子文件夹名称（没有输入，返回字符串，或者空白）
    【还不完善】
    """
    res = ''
    for item in app.XX_tree_lst_sub_folder.selection():
        res = app.XX_tree_lst_sub_folder.item(item, "values")[0]
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
    # if app.flag.flag_root_folder:
    # global dT
    logging.debug(f'正在加载该目录的标签：{tmp_path}')
    if must or app.flag.flag_sub_folders_changed:
        # 加载新标签列表
        tmp_tag = app.tree_tag.get_tag()  # 获取当前标签
        # 刷新标签列表 刷新期间不能操作进度条！
        new_files = get_data([tmp_path], update_sub_path=0, need_set_prog=False)
        (dt2, tags2) = get_dt(new_files, need_set_prog=False)

        # app.DT=dt2
        # print(f'\ndt2={dt2}')
        app.tree_tag.set_lst_tag(tags2)
        if app.flag.flag_inited:
            app.combobox_tag['value'] = tags2
        if len(tmp_tag) > 0:
            # 恢复标签
            try:
                app.tree_tag.set_search_tag_selected(tags2.index(tmp_tag))
            except:
                app.tree_tag.set_search_tag_selected(0)
        else:
            app.tree_tag.set_search_tag_selected(0)
            pass
        logging.debug(f'获取的标签是：{tags2}')
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
            tmp_path = conf.get_current_path() + '/' + get_sub_folder_selected()
            print('运行到 get_search_items_sub_folder, 进入子文件夹：')
            print(tmp_path)
        else:
            tmp_path = conf.get_current_path()
    except:
        if res_lst:
            return [], [], []
        else:
            return []
    tmp_path = str(tmp_path).replace('\\', '/')

    update_tags_in_sub_folder(tmp_path)

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


def tree_file_add_items(tree_obj, dT, search_items=None) -> None:
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
    logging.debug(f'get_search_items_sub_folder 用时 = {time.time()-time0}')
    # 上面这一步其实不太花时间
    #
    logging.debug('筛选条件：')
    # print(tmp_search_items)
    logging.debug(f'标签是 {res_tag}')
    logging.debug(f'关键词是 {res_keyword}')
    logging.debug(f'路径是{res_path}')
    n = 0
    n_max = len(dT)
    refresh_unit = 4
    logging.debug(f'检查的路径是{res_path}')
    #
    # print('app.v_this_folder = ', app.v_this_folder.get())
    logging.debug('主路径是 = ' + str(conf.lst_my_path_long_selected))
    #
    # 前置条件检查：
    var_note_only = app.v_note_only.get()  # 只看笔记
    var_this_folder = app.v_this_folder.get()  # 只看当前文件夹
    var_group_by_folder = app.v_folder_layers.get()  # 按文件夹分组
    is_this_folder = 1  # 是否是当前文件夹
    item_sub_folder = None
    tmp_current_path = conf.get_current_path().replace('\\', '/')  # 当前路径
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
        for _dir in exec_list_sort(lst_sub_folders, char_sep=conf.V_SEP):
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
            logging.error('error 1703' + str(e))
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
                # print(str.lower(conf.get_current_path()))
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
                if app.flag.flag_inited:
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

    logging.debug('添加列表项消耗时间：')
    logging.debug(time.time() - time0)

    # app.str_btm.set("找到 " + str(k) + " 个结果，用时"+str(time.time()-time0)+"秒")
    # "在"+str(len(dT))+"个项目中找到 " + str(k) + " 个文件，"
    app.str_btm.set("找到 " + str(k_all) + " 个文件")  # "，用时"+str(time.time()-time0)+"秒")
    if app.flag.flag_inited:
        set_prog_bar(100)
        tree_obj.focus()
    # app.flag.flag_running=0


def exec_run(filepath):
    """
    运行文件或路径
    """
    filepath_fixed = '"'+filepath+'"'
    os.startfile(filepath)  # TODO 这个方法好像不太合适，会导致占用。
    # subprocess.Popen(filepath_fixed, shell=True)

# 获取当前点击行的值
def tree_file_open(event=None):  # 单击
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

    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        item_text = app.tree_file.item(item, "values")
        logging.debug('正在打开文件：')
        tmp_tar = item_text[-1]
        logging.debug(tmp_tar)
        try:
            if tree_file_item_is_enabled(item):
                exec_run(tmp_tar)  # 打开这个文件
        except:
            logging.warning(f'打开 {tmp_tar} 失败')


def tree_file_item_is_enabled(itm):
    """
    用于检查选中项目是否可用（如果是分组，就不可用）
    """
    item_text = app.tree_file.item(itm, 'values')
    tmp_tar = item_text[-1]
    if tmp_tar == '':
        return 0
    else:
        return 1


def tree_file_duplicate(tar=None):  # 文件原地建立副本
    """
    为文件建立副本
    """
    pass


def tree_file_rename(tar=None):  # 对文件重命名
    """
    重命名tree选中的文件。需要有tree的选中项目。
    每个文件重命名一次，按理说兼容多文件，但是这个命令不应该给多文件执行。
    """
    if len(app.tree_file.selection()) > 1:
        logging.warning('暂不支持多文件重命名')
        return
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        # 获得目标文件
        item_text = app.tree_file.item(item, "values")
        tmp_full_path = item_text[-1]
        tmp_file_name = get_split_path(tmp_full_path)[-1]  # 文件名
        #
        #
        logging.debug('正在重命名：')
        logging.debug(f'路径 = { tmp_full_path}')
        logging.debug(f'文件名 = {tmp_file_name}')
        # res = simpledialog.askstring('文件重命名',prompt='请输入新的文件名',initialvalue =tmp_file_name) # 有bug，不能输入#号
        [fname, fename] = os.path.splitext(tmp_file_name)  # 文件名，扩展名，其中扩展名包括点号。
        logging.debug(f'fname = {fname}, fename = {fename}')
        res = app.show_window_input('文件重命名', body_value='请输入新的文件名', init_value=fname)  # 有bug，不能输入#号
        #
        if res is not None:
            try:
                tmp_new_name = '/'.join(get_split_path(tmp_full_path)[0:-1] + [res + fename])
                logging.debug(f'tmp_new_name = {tmp_new_name}')
                # os.rename(tmp_full_path,tmp_new_name)
                final_name = safe_rename(tmp_full_path, tmp_new_name, sep = conf.V_SEP)
                app_refresh(0, fast_mode=True)
                tree_obj_find(final_name)
            except:
                t = tk.messagebox.showerror(title='ERROR', message='重命名失败！文件可能被占用，或者您没有操作权限。')


def tree_file_delete(tar=None):
    """
    删除tree选中项对应的文件。
    兼容多文件，但是每个文件要确认一次，可能体验不太好。
    """
    flag_deleted = 0
    if tk.messagebox.askokcancel("删除确认", "要将选中项删除到回收站吗？"):
        #
        for item in app.tree_file.selection():
            if not tree_file_item_is_enabled(item):
                continue
            # 获取文件全路径
            item_text = app.tree_file.item(item, "values")
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
                    if len(app.tree_file.selection()) == 1:
                        app_refresh(0)
                except:
                    t = tk.messagebox.showerror(title='ERROR', message='删除失败，文件可能被占用！' + str(tmp_full_path))
                    print('删除失败，文件可能被占用')
                # 刷新

        if len(app.tree_file.selection()) > 1:
            if flag_deleted:
                app_refresh(0)

def function_for_testing(event=None):  #
    """
    用于调试一些测试性的功能，
    为了避免 event 输入，所以套了一层。

    """
    res = TdInputWindow(app.window, '输入框', 'aaaa', '外部输入')
    logging.debug(f'自制输入框的返回值：{res}')

def tree_file_find_by_lst(inp_lst):
    """
    传入一个列表。tree高亮。
    输入参数是要查询的内容，必须是列表。
    """
    app.tree_file.update()
    if type(inp_lst) is not list:
        logging.error('输入参数不是列表！')
        return

    for tmp_final_name in inp_lst:
        tmp_final_name = tmp_final_name.replace('\\', '/')
        logging.debug(f'正在定位 {tmp_final_name}')
        tree_obj_find(tmp_final_name, need_update=False)  # 为加标签之后的项目高亮


def tree_file_open_folder(event=None, VMETHOD=1):
    """
    打开当前文件所在的目录.
    参数VMETHOD=1（默认）是打开文件夹，
    =2 是打开文件夹并选中文件（有点慢）。
    不需要传入路径参数，本函数会自动从tree里面读取。
    """
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        item_text = app.tree_file.item(item, "values")
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
    tree_file_open_folder(VMETHOD=2)


def tree_open_current_folder(event=None):
    """
    没有选中文件的时候，打开当前文件夹。
    支持打开子文件夹。
    """
    if len(get_sub_folder_selected()) > 0:
        tmp_path = conf.get_current_path() + '/' + get_sub_folder_selected()
    elif len(conf.lst_my_path_long_selected) > 1:
        logging.debug('输入多个文件夹，即将打开第一个')
        tmp_path = conf.get_current_path()
    else:
        tmp_path = conf.get_current_path()
    try:
        exec_run(tmp_path)
    except:
        t = tk.messagebox.showerror(title='ERROR', message='打开文件夹失败！')

def input_new_tag(event=None, tag_name=None):
    """
    输入新的标签，为选中项添加标签。
    tag_name 是输入的标签。
    """
    # new_name=''
    if tag_name is None:  # 默认从输入框获取
        new_tag = app.combobox_tag.get()
        new_tag = str(new_tag).strip()
    else:
        new_tag = tag_name

    if new_tag is None or new_tag == '':
        logging.debug("取消新标签")
        return

    taged_files = []
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        item_text = app.tree_file.item(item, "values")
        tmp_full_name = item_text[-1]
        # tmp_file_name = get_file_part(tmp_full_name)['ffname'] # 没有用到

        # new_tag = tk.simpledialog.askstring(title="添加标签", prompt="请输入新的标签")#, initialvalue=tmp)

        if new_tag == None or new_tag == '':
            logging.debug("取消新标签")
        else:
            taged_files.append(tree_file_tag_add(tmp_full_name, new_tag))
            # print(new_name)
    if len(app.tree_file.selection()) > 1:  # 多文件的只在最后刷新。
        # (b1, b2) = bar_tree_v.get()
        app_refresh(0)
        tree_file_find_by_lst(taged_files)
        # for i in taged_files:
        # tree_obj_find(i)

        # tree_obj_find(taged_files[-1]) 
        # app.tree_file.yview_moveto(b1)


def tree_file_tag_add_via_dialog(event=None):
    """
    以输入框的方式添加标签。

    """
    # 没有选中项的时候，直接跳过
    if len(app.tree_file.selection()) == 0:
        t = tk.messagebox.showerror(title='错误', message='添加标签之前，请先选中至少一个文件。')
        logging.debug('没有选中任何项目')
        return
    #
    new_tag = app.show_window_input('添加标签', '请输入标签', '')
    if new_tag is None:
        return
    try:
        new_tag = str(new_tag).strip()
    except:
        pass
    input_new_tag(tag_name=new_tag)


def update_one_of_dicT(file_path_full):
    """
    更新dicT中的一项，
    包括对文件名斜杠的处理。


    :return:
    """
    file_path_full = file_path_full.replace('\\', '/')
    tmp = get_file_part(file_path_full)
    tmp_v = (str(tmp['fname_0']),
             tmp['ftags'],
             str(tmp['file_mdf_time']),
             tmp['fsize'],
             tmp['fename'],
             str(tmp['full_path']))
    core_data.dict_files[file_path_full] = tmp_v


def tree_file_tag_add_readonly(file_path_full):
    pass


def tree_file_tag_add(file_path_full, new_tag, need_update=True):
    """
    增加标签
    """
    file_path_full = file_path_full.replace('\\', '/')
    tmp_final_name = file_path_full
    ntfs_error = False
    #
    if new_tag == '只读':
        read_only_set(file_path_full, True)
        update_one_of_dicT(file_path_full)
    #
    else:
        # 增加NTFS流的标签解析
        if TAG_METHOD == 'FILE_STREAM' and not os.path.splitext(file_path_full)[1] in conf.EXP_EXTS:
            # 先看有没有这个标签
            tmp = get_file_part(file_path_full)
            tags_old = tmp['ftags']
            if new_tag in tags_old:  # 如果已经有的话，直接忽略
                pass
            else:
                # 增加标签
                tags_old.append(new_tag)
                tags_old.sort()
                try:
                    # 只读文件不能直接修改标签，需要先去掉只读状态
                    if read_only_get(file_path_full):
                        tmp_read_only = True
                        read_only_set(file_path_full,False)
                    with open(file_path_full + ":tags", "w", encoding="utf8") as f:
                        f.writelines(list(map(lambda x: x + "\n", tags_old)))
                    if tmp_read_only:
                        read_only_set(file_path_full,True)
                except Exception as e:
                    logging.error('error2671: '+str(e))
                    ntfs_error = True
                #
                # 更新缓存
                update_one_of_dicT(file_path_full)
                # tmp_v = (str(tmp['fname_0']),
                #          tags_old,
                #          str(tmp['file_mdf_time']),
                #          tmp['fsize'],
                #          tmp['fename'],
                #          str(tmp['full_path']))
                # core_data.dict_files[file_path_full] = tmp_v
            # return tmp_final_name
        #
        # 如果不采用 file_stream 模式：
        if TAG_METHOD != 'FILE_STREAM' or ntfs_error or os.path.splitext(file_path_full)[1] in conf.EXP_EXTS:
            tag_list = new_tag.split(conf.V_SEP)
            tag_old = get_file_part(file_path_full)['ftags']  # 已有标签
            file_old = get_file_part(file_path_full)['ffname']  # 原始的文件名
            path_old = get_file_part(file_path_full)['fpath']  # 路径
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
                        tmp_final_name = safe_rename(old_n, new_n, sep = conf.V_SEP)
                        old_n = new_n  # 多标签时避免重命名错误
                    except Exception as e:
                        tk.messagebox.showerror(title='ERROR', message='为文件添加标签失败！')
                        logging.error(f'为文件添加标签失败,e={e}')
    # 刷新并选中
    if len(app.tree_file.selection()) == 1 and need_update:
        app_refresh(0, fast_mode=True)  # 此处可以优化，避免完全重载
        try:
            tmp_final_name = tmp_final_name.replace('\\', '/')
            logging.debug(f'添加标签完成，正在定位 {tmp_final_name}')
            tree_obj_find(tmp_final_name)  # 为加标签之后的项目高亮
        except:
            pass
    return tmp_final_name


def tree_file_tag_add_fast(tag):
    """
    以右键的方式快速为文件加收藏。
    目前是为文件增加 TAG_STAR 对应的值。
    """
    TAG_STAR = tag
    taged_files = []
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        item_text = app.tree_file.item(item, "values")
        tmp_full_name = item_text[-1]
        taged_files.append(tree_file_tag_add(tmp_full_name, TAG_STAR))
    if len(app.tree_file.selection()) > 1:
        # (b1, b2) = bar_tree_v.get()
        app_refresh(0)
        # app.tree_file.yview_moveto(b1)
        for file_1 in taged_files:
            tree_obj_find(file_1)
        # tree_obj_find(taged_files[-1])


def exec_clear_search_items(event=None):
    app_refresh(666, fast_mode=True)


def app_refresh(event=None, reload_setting=False, fast_mode=False):
    """
    刷新。
    切换目录之后自动执行此功能。

    输入参数0的话，保留子文件夹、搜索框、标签框。
    输入参数1，保留子文件夹、标签框，(清除搜索框)。推荐使用参数1；
    其余参数，(清空子文件夹、标签框、搜索框)。

    """
    app.update_readme()
    # 原始值
    old_tag = app.tree_tag.get_tag()
    old_sub_folder = get_sub_folder_selected()

    if reload_setting == True:
        # 按需加载设置参数
        conf.exec_json_file_load(load_folders=False)

    tmp_sub_folder = get_sub_folder_selected()
    #
    if len(tmp_sub_folder) > 0:
        path_lst = [conf.get_current_path() + '/' + tmp_sub_folder]
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
        app.entry_search_files.delete(0,'end')
    else:
        '''
        清空搜索框；
        标签留空；
        '''
        app.entry_search_files.delete(0,'end')
        app.tree_tag.set_search_tag_selected(0)
        logging.debug('已经全部清空')

        # app.combobox_tag.delete(0,len(app.combobox_tag.get()))
    # app.combobox_tag.delete(0,len(app.combobox_tag.get()))

    # tree_folder_on_choose(refresh=0)
    logging.debug('—— 刷新核心过程 start ———')
    #
    path_lst = conf.lst_my_path_long_selected

    if len(tmp_sub_folder) > 0:  # 如果子文件夹选中，则不刷新子文件夹
        # 注意，这里修改了 app.lst_files_to_go 所以会导致全局的文件列表出现错乱。
        app.lst_files_to_go = get_data(path_lst, 0)
    else:
        app.lst_files_to_go = get_data(path_lst)
    logging.debug(f'\n ———— 当前的数据来自文件夹：{path_lst}\n')
    # app.lst_files_to_go = get_data(conf.lst_my_path_long_selected)
    #
    (app.DT, app.lst_tags) = get_dt(FAST_MODE=fast_mode)
    # if event in [0]: 
    #     (app.DT, app.lst_tags) = get_dt(FAST_MODE=fast_mode)
    # else:
    #     (app.DT, app.lst_tags) = get_dt() # 此处有待商榷
    #
    logging.debug('—— 刷新核心过程 end ———')
    # tree_obj_clear(app.tree_file)
    #
    # 恢复子文件夹选项 TODO 即将作废
    if event in [0, 1]:
        try:  # 用一种【不太优雅】，但是暴力有效的方法修复了bug……
            if len(tmp_sub_folder) > 0:
                tmp_n = app.lst_sub_path.index(tmp_sub_folder)
                set_sub_folder_selected(tmp_n + 1)
                logging.debug('子文件夹修复完毕')
        except:
            logging.debug('进入这个分支')
            app.v_sub_folders.current(0)
    #
    # 恢复标签
    app.window.update()
    #
    if len(conf.lst_my_path_long_selected) > 1:
        # tags_=update_tags_in_sub_folder(conf.lst_my_path_long_selected)
        pass
    else:
        tags_ = update_tags_in_sub_folder(conf.get_current_path() + '/' + old_sub_folder, 1)
    if event in [0, 1]:
        app.tree_tag.set_search_tag_selected(old_tag)
    #
    tree_file_search()  # 目的是按照刷新后的筛选条件对内容进行筛选
    #
    try:
        app.tree_tag.set_lst_tag(app.lst_tags)  # 这个导致总是刷新全部标签
    except Exception as e:
        logging.error(f'error 2828:{e}')

    app.combobox_tag['value'] = app.lst_tags  # 这句没啥用吧

    try:
        set_prog_bar(100)
    except:
        pass
    #
    # 刷新之后，令文件列表获得焦点(貌似无效)
    # app.tree_file.focus()


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


def tree_file_search(event=None):
    '''
    选择标签之后、选择子文件夹后、输入搜索词按回车后触发。
    纯前端函数。
    清空tree，并按照dT为tree增加行。
    '''
    app.v_tag.configure(state=tk.DISABLED)
    tree_obj_clear(app.tree_file)
    tree_file_add_items(app.tree_file, app.DT)
    app.tree_file.update()
    app.v_tag.configure(state='readonly')


def tree_folder_star_add_by_dialog(event=None):  #
    """
    通过点击的方式，添加新的目录
    """
    res = filedialog.askdirectory()  # 选择目录，返回目录名
    res_lst = [res]
    logging.debug(res)
    if res == '':
        logging.debug('取消添加文件夹')
    else:
        tree_folder_star_add(res_lst)


def tree_file_drag_enter_popupmenu(files, method=None):
    """
    ###########################################
    弹出菜单，判断是移动还是复制。
    #######################################
    """
    # 弹出对话框
    if conf.FILE_DRAG_MOVE in ['copy', 'move']:
        tree_file_drag_enter(files)
    elif conf.FILE_DRAG_MOVE == 'area':
        tree_file_drag_enter(files, method)
    else:  # 如果是弹窗选择的话：
        res = tk.messagebox.askyesno(title='拖拽文件到指定位置', message='是否保留原文件？\n点击“是”保留，点击“否”删除。')
        logging.debug(res)
        if res:
            tree_file_drag_enter(files, "copy")
        else:
            tree_file_drag_enter(files, "move")


def tree_file_drag_enter_move(files):
    tree_file_drag_enter(files, "move")


def tree_file_drag_enter(files, drag_type=None, target_path=None):
    """
    以拖拽的方式将文件拖动到tree范围内，将执行复制命令。
    注意，不是移动，只是复制。
    exec_safe_copy 的参数可以强制指定，也可以读取系统值。
    drag_type = copy 是复制， = move 是移动。
    target_path 是目标路径。为空则从左侧获取。
    """
    # 变量定义
    app.flag.flag_folder_changed = 0
    # v_method = 2  # 树形架构下，采用方案2 # 这句没用了
    #
    logging.debug(f'files={files}')
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
    if target_path is not None:
        pass
    else:
        if len(app.tree_lst_folder.selection()) == 0:
            tk.messagebox.showerror(title='错误',
                                    message='必须在左侧选定文件夹后，才能执行拖拽操作。')
            # 如果没有任何文件夹被选中
            return
        #
        if app.tree_folder.get_depth() == 0:  # 选中的是文件夹分组。而不是文件夹
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
        elif app.tree_folder.current_folder.depth >= 1:
            long_name = app.tree_folder.current_folder.path_full
        pass
        target_path = long_name

    #
    # 获取对象（k已经没什么用）
    k = len(app.tree_file.get_children())
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
            logging.error(f'转码失败，{item} 不能被转码为gbk')
        if not isfile(item):
            logging.error(f'{item}不是文件')
            if isdir(item):
                tree_folder_clipboard_paste(tar_folder_from=item, tar_folder_to=target_path, need_update=False)
                app.flag.flag_folder_changed = 1
                app.flag.flag_file_changed = 1
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
        new_name = target_path + '/' + ffname
        if drag_type in ['copy', 'move']:
            #
            # 2021年10月30日新增：markdown特殊处理
            if IS_MARKDOWN_MOVE_WITH_IMGS is True and len(old_name) > 3 and old_name[-3:] in conf.EXP_EXTS:
                MarkdownRel.copy_md_linked_files(old_name, target_path)
            #
            res = safe_copy(old_name, new_name, opt_type=drag_type, sep = conf.V_SEP)
            app.str_btm.set('拖动添加文件成功')
        #     res=safe_move(old_name, new_name, opt_type='copy')
        #     app.str_btm.set('文件拖拽成功')
        logging.debug(f'res={res}')
        new_file_lst.append(res)
        # 再显示到列表中
        k += 1
        # tmp=get_file_part(res)
        # tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path'])
        # tmp=tmp_v
        # app.tree_file.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        app.flag.flag_file_changed = 1

    # 刷新：
    if app.flag.flag_folder_changed:
        app.tree_folder.refresh()
        # app_refresh(fast_mode=True)
        pass

    if app.flag.flag_file_changed:
        app_refresh(0, fast_mode=True)  # 这里不刷新的话，后面排序或者筛选都会出错。
        # 高亮文件
        try:
            tree_file_find_by_lst(new_file_lst)
            # tree_obj_find(res)
            # app.tree_file.yview_moveto(1)
        except:
            pass


def exec_create_txt_note(event=None):
    exec_create_note(my_ext='.txt')

def tree_file_create_readme(event=None):
    pth = conf.get_current_path()
    file_path = pth + '/readme.md'
    try:
        if os.path.isfile(file_path):
            os.startfile(file_path)  # 打开这个文件
        else:
            with open(file_path,'w+') as f:
                pass
            os.startfile(file_path)  # 打开这个文件
    except Exception as e:
        logging.error(e)

def exec_create_note(event=None, my_ext=None):  # 添加笔记
    if my_ext is None:
        pass
    else:
        old_ext = conf.NOTE_EXT
        conf.NOTE_EXT = my_ext

    tags = ['笔记']
    if not app.tree_tag.get_tag() == '':  # 新笔记自动增加选中的标签
        tags += [app.tree_tag.get_tag()]

    if len(conf.lst_my_path_long_selected) != 1:
        t = tk.messagebox.showerror(title='ERROR', message='未选中文件夹，新建笔记功能暂不可用')
        logging.warning('新建笔记功能锁定，暂不可用')
        return
    #
    the_note_name = conf.NOTE_NAME_DEFAULT
    # res = simpledialog.askstring('新建 Tagdox 笔记',prompt='请输入文件名',initialvalue =the_note_name)
    res = app.show_window_input('新建 Tagdox 笔记（' + conf.NOTE_EXT + "）", body_value='请输入文件名', init_value=the_note_name)
    if res is not None:
        logging.debug(f'获得新笔记标题：{res}')
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
            pth = conf.get_current_path()

            if not event == 'exec_create_note_here':
                # 增加对子文件夹的判断逻辑。
                # 新建的位置正确，但是刷新之后找不到新笔记，而且子文件夹自动消失，体验不好。
                psub = get_sub_folder_selected()
                if len(psub) > 0:
                    pth = pth + '/' + psub

            logging.debug(f'即将在此新建笔记：{pth}')
            if True:  # pth in conf.lst_my_path_long: # 后面这个判断有点多余
                fpth = pth + '/' + the_note_name + stags + conf.NOTE_EXT

                # 检查是否有这个文件
                i = 0
                while isfile(fpth):
                    i += 1
                    fpth = pth + '/' + the_note_name + '(' + str(i) + ')' + stags + conf.NOTE_EXT

                # 创建文件
                logging.debug(f'创建文件：{fpth}')
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
                            tree_file_tag_add(fpth, tg, need_update=False)

                    # 刷新
                    if event == 'exec_create_note_here':  # 【这里有bug，刷新之后不能显示内容】
                        app_refresh(1, fast_mode=True)
                        tree_obj_find(fpth)
                        # return fpth
                    else:
                        app_refresh(1, fast_mode=True)  # 没有这句话会搜不到
                        tree_obj_find(fpth)
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
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        item_text = app.tree_file.item(item, "values")
        tmp_full_name = item_text[-1]
    tmp_path = '/'.join(get_split_path(tmp_full_name)[0:-1])
    logging.debug(f'当前路径 = {tmp_path}')
    lst_tmp = conf.lst_my_path_long_selected.copy()
    conf.lst_my_path_long_selected = [tmp_path]

    fpth = exec_create_note('exec_create_note_here')
    conf.lst_my_path_long_selected = lst_tmp.copy()
    if fpth is not None:
        app_refresh(1)
        tree_obj_find(fpth)


# %%
def jump_to_search(event=None):
    """
    输入快捷键快速搜索的功能。
    """
    tmp_search_value = app.entry_search_files.get()
    res = app.show_window_input('快速搜索', body_value='请输入搜索关键词，多个关键词之间用空格隔开。',
                            init_value=tmp_search_value)
    if res is not None:
        app.entry_search_files.delete(0,'end')
        res = res.strip()
        app.entry_search_files.insert(0, res)
        tree_file_search()
        app.entry_search_files.focus()


def X_jump_to_tag(event=None):
    app.combobox_tag.focus()


# %%
# 弹出菜单

def show_popup_menu_main(event):
    """
    主菜单，点击设置按钮可以弹出。
    设置菜单的弹出
    """
    menu_main = tk.Menu(app.window, tearoff=0)
    menu_main.add_command(label='设置…', command=win_manager.show_window_settings)
    menu_main.add_separator()
    menu_main.add_command(label="添加文件夹到关注列表…", command=tree_folder_star_add_by_dialog)
    menu_main.add_separator()
    # menu_main.add_command(label='使用说明')#,command=show_online_help)
    menu_main.add_command(label='访问主页（联网）', command=show_online_help)
    menu_main.add_command(label='建议和反馈（联网）', command=show_online_advice)
    menu_main.add_command(label='检查更新（联网）', command=show_online_check_update)
    menu_main.add_command(label='关于…', command=win_manager.show_window_info)
    menu_main.add_separator()
    menu_main.add_command(label='退出', command=win_manager.show_window_closing)
    #
    menu_main.post(event.x_root, event.y_root)


def tree_file_tag_remove(event=None):
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
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        item_text = app.tree_file.item(item, "values")
        tmp_full_name = item_text[-1]  # 完整文件名
        # 判断只读
        if tag_value == '只读':
            read_only_set(tmp_full_name, False)
            update_one_of_dicT(tmp_full_name)
        if True:
            if read_only_get(tmp_full_name):
                tmp_is_read_only = True
                read_only_set(tmp_full_name, False)
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
                        # 恢复只读属性
                        if tmp_is_read_only:
                            read_only_set(tmp_full_name, True)
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
                logging.debug(file_name_ori)
                tmp_rv = list(file_name_ori)
                tmp_rv.reverse()
                tmp_rv = ''.join(tmp_rv)
                logging.debug(tmp_rv)
                #
                tmp_r_tag = list(conf.V_SEP + tag_value)
                tmp_r_tag.reverse()
                tmp_r_tag = ''.join(tmp_r_tag)
                logging.debug(tmp_r_tag)
                #
                tmp_rv = tmp_rv.replace(tmp_r_tag, '', 1)
                #
                tmp_rv = list(tmp_rv)
                tmp_rv.reverse()
                tmp_rv = ''.join(tmp_rv)
                #
                file_name_ori = tmp_rv
                logging.debug('从右向左替换')
                logging.debug(file_name_ori)
            new_name = file_name_ori.replace(conf.V_SEP + tag_value + conf.V_SEP, conf.V_SEP)
            new_name = new_name.replace(conf.V_SEP + tag_value + '.', ".")

            new_full_name = file_path + '/' + new_name
            logging.debug(f'原始文件名 = {tmp_full_name}')
            logging.debug(f'去掉标签后 = {new_full_name}')
            logging.debug(f'被去掉的标签 = {tag_value}')
            # os.rename(tmp_full_name,new_full_name)
            if tmp_full_name != new_full_name:
                tmp_final_name = safe_rename(tmp_full_name, new_full_name, sep = conf.V_SEP)
            res_lst.append(new_full_name)

    app_refresh(0, fast_mode=True)  # 此处可以优化，避免完全重载
    tree_file_find_by_lst(res_lst)
    # for tmp_final_name in res_lst:
    #     tmp_final_name = tmp_final_name.replace('\\', '/')
    #     print('删除标签完成，正在定位%s' % (tmp_final_name))
    #     tree_obj_find(tmp_final_name)  # 为加标签之后的项目高亮


def tree_file_right_click(event):
    """
    右键点击 app.tree_file 区域

    :param event:
    :return:
    """
    tmp = app.tree_file.identify_row(event.y)
    if tmp not in app.tree_file.selection():
        app.tree_file.selection_set(tmp)
    tree_obj_mouse_highlight(event, app=app, clear_only=True)


def tree_file_left_click(event):
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
    tmp = app.tree_file.identify_row(event.y)
    logging.debug(len(tmp))
    # if tmp not in app.tree_file.get_children():
    if len(tmp) == 0:  # not in app.tree_file.get_children():
        app.tree_file.selection_set(tmp)


def show_popup_menu_file(event):
    """
    文件区域的右键菜单
    """
    n_selection = len(app.tree_file.selection())
    # for item in app.tree_file.selection():
    #     item_text = app.tree_file.item(item, "values")
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
            menu_tags_to_add.add_command(label=i, command=lambda x=i: tree_file_tag_add_fast(x))
        menu_tags_to_add.add_separator()
    menu_tags_to_add.add_command(label='自定义标签…', command=tree_file_tag_add_via_dialog)
    #
    menu_file = tk.Menu(app.window, tearoff=0)
    menu_file.add_command(label="打开文件", command=tree_file_open, accelerator='Enter')
    # menu_file.add_command(label="在相同位置创建笔记",command=exec_create_note_here)
    menu_file.add_separator()
    if len(conf.lst_my_path_long_selected) == 1:
        menu_file.add_command(label="新建笔记（" + conf.NOTE_EXT + "）", command=exec_create_note, accelerator='Ctrl+N')
        menu_file.add_cascade(label="新建更多格式的笔记", menu=menu_create_note)
    else:
        menu_file.add_command(label="新建笔记", state=tk.DISABLED, command=exec_create_note, accelerator='Ctrl+N')
    menu_file.add_separator()
    if n_selection == 1:
        # menu_file.add_command(label="打开选中项所在文件夹（使用资源管理器）", command=tree_file_open_folder)
        menu_file.add_command(label="打开所在文件夹（使用资源管理器）", command=tree_open_folder_select)
    elif n_selection > 1:
        menu_file.add_command(label="打开选中项所在文件夹（使用资源管理器）", state=tk.DISABLED, command=tree_file_open_folder)
    # menu_file.add_command(label="打开当前文件夹", command=tree_open_current_folder)
    menu_file.add_separator()
    menu_file.add_command(label='添加标签 ', command=tree_file_tag_add_via_dialog, accelerator='Ctrl+T')
    menu_file.add_cascade(label="快速添加标签", menu=menu_tags_to_add)
    if n_selection == 1:
        menu_file.add_cascade(label="移除标签", menu=menu_tags_to_drop)
    elif n_selection > 1:
        menu_file.add_cascade(label="移除标签", menu=menu_tags_to_drop)
    menu_file.add_separator()
    # menu_file.add_command(label="发送无标签副本到桌面（开发中）",state=tk.DISABLED)#,command=tree_file_rename)
    # menu_file.add_command(label="复制到剪切板（开发中）",state=tk.DISABLED)#,command=tree_file_rename)
    # menu_file.add_command(label="移动到文件夹（开发中）",state=tk.DISABLED)#,command=tree_file_rename)
    # menu_file.add_command(label="粘贴（开发中）",state=tk.DISABLED)#,command=tree_file_rename)
    if n_selection == 1:
        menu_file.add_command(label="重命名", command=tree_file_rename, accelerator='F2')
    elif n_selection > 1:
        menu_file.add_command(label="重命名", state=tk.DISABLED, command=tree_file_rename, accelerator='F2')
    menu_file.add_command(label="删除", command=tree_file_delete, accelerator='Del')
    menu_file.add_separator()
    menu_file.add_command(label="剪切（程序内）", command=tree_file_cut, accelerator='Ctrl+X')
    menu_file.add_command(label="复制（程序内）", command=tree_file_copy, accelerator='Ctrl+C')
    menu_file.add_command(label="粘贴（程序内）", state=tk.DISABLED if len(app.clipboard_files) == 0 else tk.NORMAL,
                          command=tree_file_put_down, accelerator='Ctrl+V')
    # menu_file.add_command(label="取消", state=tk.DISABLED if len(app.clipboard_files) == 0 else tk.NORMAL,
    #                       command=tree_file_pick_nothing)

    menu_file.add_separator()
    menu_file.add_command(label="刷新", command=app_refresh, accelerator='F5')
    #
    # 没有选中项目的时候
    #
    menu_file_no_selection = tk.Menu(app.window, tearoff=0)
    # menu_file_no_selection.add_command(label="打开文件",state=tk.DISABLED,command=tree_file_open)
    menu_file_no_selection.add_command(label="打开当前文件夹（使用资源管理器）", command=tree_open_current_folder)
    menu_file_no_selection.add_separator()
    if len(conf.lst_my_path_long_selected) == 1:
        menu_file_no_selection.add_command(label="新建笔记（" + conf.NOTE_EXT + "）", command=exec_create_note,
                                           accelerator='Ctrl+N')
        menu_file_no_selection.add_cascade(label="新建更多格式的笔记", menu=menu_create_note)
    else:
        menu_file_no_selection.add_command(label="新建笔记", state=tk.DISABLED, command=exec_create_note,
                                           accelerator='Ctrl+N')
    # menu_file_no_selection.add_command(label="重命名",state=tk.DISABLED)#,command=tree_folder_star_add_by_dialog)
    # menu_file_no_selection.add_command(label="添加收藏",state=tk.DISABLED)#,command=tree_folder_star_add_by_dialog)
    menu_file_no_selection.add_separator()
    menu_file_no_selection.add_command(label="剪切（程序内）", state=tk.DISABLED, command=tree_file_cut, accelerator='Ctrl+X')
    menu_file_no_selection.add_command(label="复制（程序内）", state=tk.DISABLED, command=tree_file_copy, accelerator='Ctrl+C')
    menu_file_no_selection.add_command(label="粘贴（程序内）", state=tk.DISABLED if len(app.clipboard_files) == 0 else tk.NORMAL,
                                       command=tree_file_put_down, accelerator='Ctrl+V')
    # menu_file_no_selection.add_command(label="取消", state=tk.DISABLED if len(app.clipboard_files) == 0 else tk.NORMAL,
    #                                    command=tree_file_pick_nothing)
    menu_file_no_selection.add_separator()
    menu_file_no_selection.add_command(label="刷新", command=app_refresh, accelerator='F5')
    #
    menu_file_one_folder = tk.Menu(app.window, tearoff=0)
    menu_file_one_folder.add_command(label="粘贴到此（程序内）", state=tk.DISABLED if len(app.clipboard_files) == 0 else tk.NORMAL,
                          command=tree_file_paste_here, accelerator='Ctrl+V')
    menu_file_one_folder.add_command(label="刷新", command=app_refresh, accelerator='F5')
    #
    # 开始判断显示什么菜单
    #
    if n_selection == 1: # 如果有1个选中项目，而且是文件。
        item = app.tree_file.selection()[0]
        if tree_file_item_is_enabled(item):
            # tmp_file_name=get_split_path(tmp_full_name)[-1]
            # for item in app.tree_file.selection():
            item_text = app.tree_file.item(item, "values")
            tmp_full_name = item_text[-1]
            tmp_file_name = get_file_part(tmp_full_name)['fname']
            tmp_tags_all = get_file_part(tmp_full_name)['ftags']
            tmp_tags = tmp_file_name.split(conf.V_SEP)
            # print(tmp_res)
            tmp_tags.pop(0)  # 分隔符前面的是文件名，不是标签
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
            #
            # 新增：只读
            if read_only_get(tmp_full_name):
                tmp_tags.append('只读')
            try:
                for i in range(10000):  # 删除已有标签
                    menu_tags_to_drop.delete(0)
            except:
                pass
            # 去重
            tmp_tags = list(set(tmp_tags))
            tmp_tags_all = list(set(tmp_tags_all))
            #
            if len(tmp_tags_all) > 0:
                if len(tmp_tags) == 0:
                    pass
                else:
                    # menu_tags_to_drop.add_separator()
                    for i in tmp_tags:
                        menu_tags_to_drop.add_command(label=i, command=lambda x=i: tree_file_tag_remove(x))

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
            #
        else: # 如果有1个选中项目，而且是子分组。
            menu_file_one_folder.post(event.x_root, event.y_root)
    #
    elif n_selection > 1:  # 选中很多项目的时候
        try:
            for i in range(10000):  # 删除已有标签
                menu_tags_to_drop.delete(0)
        except:
            pass
        tmp_tags_from_files = []
        file_checked = 0
        for item in app.tree_file.selection():
            if not tree_file_item_is_enabled(item):  # 直接跳过分组
                continue
            item_text = app.tree_file.item(item, "values")
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
                menu_tags_to_drop.add_command(label=i, command=lambda x=i: tree_file_tag_remove(x))
        else:
            menu_tags_to_drop.add_command(label='无可移除的共有标签', state=tk.DISABLED)
            pass
        menu_file.post(event.x_root, event.y_root)
    #
    else: # 没有选中项的时候
        menu_file_no_selection.post(event.x_root, event.y_root)

def tree_file_pick_up(event=None, need_clear=False):
    """
    将选中的文件拿起来
    """
    #
    # 每次复制或剪切的时候，文件夹的清理总是需要的
    tree_folder_clipoard_clear()
    #
    if need_clear:
        tree_file_pick_nothing()
        # lst_pick_up_files = []
        # lst_pick_up_items = []
    #
    # 添加到列表中：
    for item in app.tree_file.selection():
        if not tree_file_item_is_enabled(item):
            continue
        #
        item_text = app.tree_file.item(item, "values")
        tmp_full_name = item_text[-1]
        #
        item_tags = app.tree_file.item(item, 'tags')
        #
        if app.clipboard_state == 'move':
            new_tag = 'pick_up'
        elif app.clipboard_state == 'copy':
            new_tag = 'pick_copy'
        if not new_tag in list(item_tags):
            new_item_tags = list(item_tags) + [new_tag]
        else:
            new_item_tags = list(item_tags)
        #
        app.tree_file.item(item, tags=new_item_tags)
        #
        if not tmp_full_name in app.clipboard_files:
            app.clipboard_files.append(tmp_full_name)
        if not item in app.clipboard_items:
            app.clipboard_items.append(item)


def tree_file_cut_ctn(event=None):
    """
    连续剪切
    """
    if app.clipboard_state == 'copy':
        app.clipboard_state = 'move'
        tree_file_pick_up(need_clear=True)
    else:
        tree_file_pick_up(need_clear=False)


def tree_file_cut(event=None):
    """
    剪切（程序内）
    """
    app.clipboard_state = 'move'
    tree_file_pick_up(need_clear=True)


def tree_file_copy_cnt(event=None):
    """
    连续复制
    """
    # global state_pick_up
    if app.clipboard_state == 'move':
        app.clipboard_state = 'copy'
        tree_file_pick_up(need_clear=True)
    else:
        tree_file_pick_up(need_clear=False)


def tree_file_copy(event=None):
    """
    选中的文件复制
    """
    app.clipboard_state = 'copy'
    tree_file_pick_up(need_clear=True)


def tree_file_pick_nothing(event=None, fastmode=False):
    """
    清空pick列表
    """
    if not fastmode:
        for item in app.clipboard_items: # lst_pick_up_items:
            try:
                new_item_tags = list(app.tree_file.item(item, 'tags'))
                if 'pick_up' in new_item_tags:
                    new_item_tags.remove('pick_up')
                if 'pick_copy' in new_item_tags:
                    new_item_tags.remove('pick_copy')
                app.tree_file.item(item, tags=new_item_tags)
            except:
                pass
    # lst_pick_up_files = []
    # lst_pick_up_items = []
    app.clipboard_files = []
    app.clipboard_items = []


def tree_file_put_down(event=None):
    """
    将选中的文件放下
    """
    tree_file_drag_enter(app.clipboard_files, drag_type=app.clipboard_state)  # 调用的是拖动函数
    tree_file_pick_nothing(fastmode=True)


def tree_file_paste_here(event=None, target_path=None):
    """
    粘贴到指定位置
    """
    # 获取当前选中项目的路径
    item_folder = app.tree_file.selection()[0]
    target_path_tail = app.tree_file.item(item_folder, "text") # 这个是/开头的文件夹名称，是不完整的
    target_path_head = app.tree_folder.current_folder.path_full
    target_path = target_path_head + '/' + target_path_tail
    logging.debug(f"target_path = {target_path}")
    tree_file_drag_enter(app.clipboard_files, #lst_pick_up_files,
                         drag_type = app.clipboard_state, # =state_pick_up
                         target_path=target_path)  # 调用的是拖动函数
    tree_file_pick_nothing(fastmode=True)


def tree_file_group(event=None):
    """
    快速打包，并放在新的文件夹里面
    TODO: 还没完成
    """
    file_lst = []  # 文件列表
    tar_folder = ''  # 目标位置
    #
    # 判断是否满足条件；
    if len(app.tree_file.selection()) <= 0:  # 没有选中文件
        return -1
    elif app.tree_folder.get_depth() == 0:  # 选中的是文件夹分组。而不是文件夹
        return -1
    elif app.tree_folder.get_depth() >= 1:
        current_folder = app.tree_folder.current_folder.path_full
    #
    # 获得文件列表：
    group_name = app.show_window_input('快速打包','请输入分组文件夹名称')
    if group_name is not None:
        tar_folder = current_folder + '/' + group_name

    for i in app.tree_file.selection():
        file_full_path = app.tree_file.item(i)  # 获得路径

    app.tree_folder.refresh()  # 刷新文件夹列表
    # 刷新树

def tree_file_mouse_highlight(event=None, **kwargs):
    """
    兼容的临时方法，之后再删除
    """
    tree_obj_mouse_highlight(event, app=app, **kwargs)

# %%
class td_main_app:
    """
    主窗口类
    """
    def __init__(self) -> None:
        """
        界面部分。
        也就是UI的设计。
        """
        self.last_focus = None
        self.the_tree = None
        self.keyword_folder = ''  # 用于搜索文件夹的
        self.file_open_time = time.time()  # 最近一次tree_file_open 的时间；
        self.window = tk.Tk()
        self.flag = td_flag()
        self.conf = conf
        self.conf.ui_ratio = 1.5  # 界面的放大倍率，之后会提供前端修改的功能
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
            "龙猫": tk.PhotoImage(file=".//resources/imgs/龙猫.gif"),  # 这行没用，是纯测试的
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
        self.lst_tags = []
        self.lst_files_to_go = []
        self.lst_sub_path = []
        self.DT = []
        self.folder_to_move = ''

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
            #
            self.tree_folder = tree_folder(self,
                                           frame_obj=self.frame_folder,
                                           bar_v_obj=self.bar_folder_v,
                                           bar_h_obj=self.bar_folder_h
                                           )
            self.tree_lst_folder = self.tree_folder.tree_body
            # self.tree_lst_folder = ttk.Treeview(self.frame_folder,
            #                                     selectmode=tk.BROWSE,
            #                                     style='Dark.Treeview',
            #                                     show="tree",
            #                                     yscrollcommand=self.bar_folder_v.set,
            #                                     xscrollcommand=self.bar_folder_h.set,
            #                                     )  # , height=18)
            # self.bar_folder_v.config(command=self.tree_lst_folder.yview)
            # self.bar_folder_h.config(command=self.tree_lst_folder.xview)
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
            self.tree_tag = tree_tag(self, frame_tags=self.frame_tags,
                                     bar_v=self.bar_sub_tag_v,
                                     tree_file_search=tree_file_search)
            self.tree_lst_sub_tag = self.tree_tag.tree_body
            # self.tree_lst_sub_tag = ttk.Treeview(self.frame_tags,
            #                                      columns=['tags'],
            #                                      # columns = ['index','type','folders','folder_path'],
            #                                      displaycolumns=['tags'],
            #                                      selectmode=tk.BROWSE,
            #                                      show="headings",
            #                                      style='Taglist.Treeview',
            #                                      # show="tree",
            #                                      # cursor='hand2',
            #
            #                                      yscrollcommand=self.bar_sub_tag_v.set)  # , height=18)

            # self.tree_lst_sub_tag.heading("tags", text="全部标签", anchor='w', command=tree_tag_search)
            # self.tree_lst_sub_tag.column('tags', width=int(conf.ui_ratio * conf.ui_conf['FRAME_RIGHT_WIDTH']), anchor='w')
            # self.bar_sub_tag_v.config(command=self.tree_lst_sub_tag.yview)
            #
            self.bar_sub_tag_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
            self.tree_tag.tree_body.pack(side=tk.LEFT, expand=0, fill=tk.BOTH, padx=0, pady=0)
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

            self.v_sub_folders['value'] = [''] + self.lst_sub_path
            self.v_sub_folders['state'] = 'readonly'

            # self.v_sub_folders.bind('<<ComboboxSelected>>', on_sub_folders_choose)

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
                                   command=self.tree_folder.search_clear,
                                   )
        self.bt_clear_folder_search.pack(side=tk.RIGHT, expand=0, fill=tk.Y, padx=5, pady=2)
        #
        # self.lable_search_folder = ttk.Label(self.frame_folder_top, text='文件夹')
        self.entry_search_folder = ttk.Entry(self.frame_folder_top,)
        self.entry_search_folder.pack(side=tk.RIGHT, expand=1, fill=tk.BOTH, padx=5, pady=2)
        self.entry_search_folder.bind('<Return>', self.tree_folder.search_folder_by_name)  # 绑定回车键
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
        # self.bt_new_note = ttk.Button(self.frame_top, text='新建笔记')  # ,state=tk.DISABLED)#,command=app_refresh)
        # self.bt_new_note.pack(side=tk.LEFT, expand=0, padx=0, pady=vPDY)  #
        #
        self.bt_reload = ttk.Button(self.frame_bottom,
                                    text='刷新',
                                    command=app_refresh,
                                    )
        self.bt_reload.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        self.bt_add_tag = ttk.Button(self.frame_bottom, text='添加标签',
                                     command=tree_file_tag_add_via_dialog)  # , command=input_new_tag
        self.bt_add_tag.pack(side=tk.RIGHT, expand=0, padx=0, pady=vPDY)  #

        self.bt_new_note = ttk.Button(self.frame_bottom, text='新建笔记')  # ,state=tk.DISABLED)#,command=app_refresh)
        self.bt_new_note.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #

        self.bt_readme = ttk.Button(self.frame_bottom, text='readme')  # ,state=tk.DISABLED)#,command=app_refresh)
        self.bt_readme.pack(side=tk.RIGHT, expand=0, padx=0, pady=vPDY)  #

        # 新标签的输入框（不再使用）
        self.combobox_tag = ttk.Combobox(self.frame_bottom, width=int(16*conf.ui_ratio))
        # combobox_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        self.combobox_tag.bind('<Return>', input_new_tag)
        self.combobox_tag['value'] = self.lst_tags
        #
        # self.lable_tag = tk.Label(self.frame_bottom, text='添加新标签')
        # lable_tag.pack(side=tk.RIGHT, expand=0, padx=vPDX, pady=vPDY)  #
        #            
        # 其他初始化设定
        if ALL_FOLDERS == 1:
            self.bt_folder_drop.configure(state=tk.DISABLED)
        self.refresh = app_refresh
        #
        # 测试气泡
        # b = tix.Balloon(window, statusbar=None)
        # b.bind_widget(bt_clear,balloonmsg='test',statusmsg=None)
        #
        self.bar_tree_v.config(command=self.tree_file.yview)
        self.bar_tree_h.config(command=self.tree_file.xview)
        # 样式
        self.window.iconbitmap(LOGO_PATH)  # 左上角图标 #

    def show_window_input(self, title_value, body_value='', init_value='', is_file_name=True):
        return show_window_input(title_value=title_value, body_value=body_value,
                                 init_value=init_value, is_file_name=is_file_name, app=self)

    def run(self, filepath):
        """
        运行文件或路径
        """
        filepath_fixed = '"' + filepath + '"'
        os.startfile(filepath)  # TODO 这个方法好像不太合适，会导致占用。
        # subprocess.Popen(filepath_fixed, shell=True)

    def update_readme(self, text_in = None):
        """
        用于更新 readme 里面的内容
        """
        README_MAX_LENGTH= 5000
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
                            text_to_show = f.read(README_MAX_LENGTH).decode('utf-8')
                    except Exception as e:
                        with open(current_path+ '/readme.md', 'rb') as f:
                            text_to_show = f.read(README_MAX_LENGTH).decode('gbk','ignore')
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
        self.bt_folder_drop.configure(command=self.tree_folder.star_remove)  # 减少文件夹
        #
        # 设置拖拽反映函数
        windnd.hook_dropfiles(self.tree_lst_folder, func=self.tree_folder.star_add_drag)
        windnd.hook_dropfiles(self.tree_file, func=tree_file_drag_enter_popupmenu)
        windnd.hook_dropfiles(self.tree_lst_sub_tag, func=tree_file_drag_enter_move)
        #
        # 各种功能的绑定
        # tree_lst_folder.bind('<<ListboxSelect>>',tree_folder_on_choose)
        # tree_lst_folder.bind('<Button-1>',tree_folder_on_choose)
        # self.tree_lst_folder.bind('<ButtonRelease-1>', tree_folder_on_choose)
        # self.tree_lst_folder.bind('<KeyRelease-Up>', tree_folder_on_choose)
        # self.tree_lst_folder.bind('<KeyRelease-Down>', tree_folder_on_choose)
        # self.tree_lst_folder.bind("<Motion>", tree_folder_mouse_highlight_add)
        # self.tree_lst_folder.bind("<Button-3>", tree_folder_right_click)  # 绑定文件夹区域的右键功能
        #
        # self.XX_tree_lst_sub_folder.bind('<ButtonRelease-1>', on_sub_folders_choose)
        # self.XX_tree_lst_sub_folder.bind('<KeyRelease-Up>', on_sub_folders_choose)
        # self.XX_tree_lst_sub_folder.bind('<KeyRelease-Down>', on_sub_folders_choose)
        # self.XX_tree_lst_sub_folder.bind("<Button-3>", XX_show_popup_menu_sub_folder)  # 绑定文件夹区域的右键功能
        #
        # self.tree_lst_sub_tag.bind('<ButtonRelease-1>', tree_tag_on_choose)
        # self.tree_lst_sub_tag.bind('<KeyRelease-Up>', tree_tag_on_choose)
        # self.tree_lst_sub_tag.bind('<KeyRelease-Down>', tree_tag_on_choose)
        # self.tree_lst_sub_tag.bind("<Motion>", tree_tag_mouse_highlight)
        #
        # 程序内快捷键
        self.window.bind_all('<Control-r>', tree_file_create_readme)  # 绑定添加笔记的功能。
        self.window.bind_all('<Control-n>', exec_create_note)  # 绑定添加笔记的功能。
        self.window.bind_all('<Control-f>', jump_to_search)  # 跳转到搜索框。
        self.window.bind_all('<Control-t>', tree_file_tag_add_via_dialog)  # 快速输入标签。
        self.window.bind_all('<Control-p>', self.tree_folder.search_folder_by_name)
        #
        # self.tree_file.bind('<Control-X>', tree_file_cut_ctn)  # 拿起。
        # self.tree_file.bind('<Control-x>', tree_file_cut)  # 拿起。
        # self.tree_file.bind('<Control-C>', tree_file_copy_cnt)  # 拿起。
        # self.tree_file.bind('<Control-c>', tree_file_copy)  # 拿起。
        # self.tree_file.bind('<Control-v>', tree_file_put_down)  # 放下。
        # self.tree_lst_folder.bind('<Control-v>', tree_file_put_down)  # 放下，点选文件夹之后仍然可以操作，可以提高用户体验。
        # self.tree_file.bind('<F2>', tree_file_rename)  # 重命名
        # self.tree_file.bind('<Delete>', tree_file_delete)  # 重命名
        # self.tree_file.bind("<Motion>", tree_obj_mouse_highlight)

        self.frame_folder_top.bind("<Motion>", self.tree_folder.mouse_highlight_remove)

        # self.tree_file.bind('<Double-Button-1>', tree_file_open)
        # self.tree_file.bind('<Return>', tree_file_open)
        # self.tree_file.bind("<Button-3>", tree_file_right_click)  # 绑定文件区域的右键功能
        # self.tree_file.bind("<Button-1>", tree_file_left_click)  # 绑定文件区域的右键功能
        # self.tree_file.bind("<ButtonRelease-3>", show_popup_menu_file)  # 绑定文件夹区域的右键起功能
        # self.tree_file.bind('<F5>', app_refresh)  # 刷新。
        # self.tree_file.bind('<space>', self.call_space)  # 刷新。
        # #
        # self.tree_file.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记
        # self.tree_lst_folder.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记
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


class td_tree_file():
    """
    文件树，也是面积最大的树。
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
        self.bar_tree_v = tk.Scrollbar(frame_root,
                                       width=int(16 * conf.ui_ratio))  # 右侧滚动条
        self.bar_tree_h = tk.Scrollbar(frame_bottom,
                                       orient=tk.HORIZONTAL,
                                       width=int(16 * conf.ui_ratio))  # 底部滚动条
        self.body = ttk.Treeview(frame_root,
                                 # show="headings",  # 如果有这句话，就不能显示图标
                                 columns=columns,
                                 displaycolumns=tree_displaycolumns, \
                                 # selectmode=tk.BROWSE, \
                                 selectmode='extended', \
                                 yscrollcommand=self.bar_tree_v.set,
                                 xscrollcommand=self.bar_tree_h.set,
                                 )  # , height=18)
        self.tree_body = self.body  # 别称
        #
        self.tree_body.column('#0', width=700, anchor='w')  # ,stretch=tk.NO)
        self.tree_body.column('index', width=30, anchor='center')
        self.tree_body.column('file', width= conf.ui_conf['TREE_WIDTH_FILENAME'], minwidth=100, anchor='w') # 600
        self.tree_body.column('tags', width= conf.ui_conf['TREE_WIDTH_TAGS'], minwidth=100, anchor='w')  # 200
        self.tree_body.column('modify_time', width=conf.ui_conf['TREE_WIDTH_MODIFY_TIME'], minwidth=80, anchor='e')  # ,stretch=tk.NO)  # 120
        self.tree_body.column('size', width=conf.ui_conf['TREE_WIDTH_SIZE'], minwidth=40, anchor='e')  # ,stretch=tk.NO)  # 60
        self.tree_body.column('file0', width=80, anchor='w')
        #
        self.tree_body.heading('#0', text='名称', anchor='w', command=tree_order_filename)
        self.tree_body.heading("index", text="序号", anchor='center')
        self.tree_body.heading("file", text="文件名", anchor='w', command=tree_order_filename)
        self.tree_body.heading("tags", text="标签", anchor='w', command=tree_order_tag)
        self.tree_body.heading("modify_time", text="修改时间", anchor='e', command=tree_order_modi_time)
        self.tree_body.heading("size", text="大小(kB)", anchor='e', command=tree_order_size)
        self.tree_body.heading("file0", text="完整路径", anchor='w', command=tree_order_path)
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

    def mouse_highlight(self):
        """
        鼠标指向的条目，增加高亮。
        """
        pass

    def bind_func(self):
        """
        绑定快捷键或者行为
        """
        self.tree_body.bind('<Control-X>', tree_file_cut_ctn)  # 拿起。
        self.tree_body.bind('<Control-x>', tree_file_cut)  # 拿起。
        self.tree_body.bind('<Control-C>', tree_file_copy_cnt)  # 拿起。
        self.tree_body.bind('<Control-c>', tree_file_copy)  # 拿起。
        self.tree_body.bind('<Control-v>', tree_file_put_down)  # 放下。
        self.tree_body.bind('<F2>', tree_file_rename)  # 重命名
        self.tree_body.bind('<Delete>', tree_file_delete)  # 删除
        self.tree_body.bind("<Motion>", tree_file_mouse_highlight) # 指向对象高亮
        self.tree_body.bind('<Double-Button-1>', tree_file_open)
        self.tree_body.bind('<Return>', tree_file_open)
        self.tree_body.bind("<Button-3>", tree_file_right_click)  # 绑定文件区域的右键功能
        self.tree_body.bind("<Button-1>", tree_file_left_click)  # 绑定文件区域的左键功能
        self.tree_body.bind("<ButtonRelease-3>", show_popup_menu_file)  # 绑定文件夹区域的右键起功能
        self.tree_body.bind('<F5>', app_refresh)  # 刷新。
        self.tree_body.bind('<space>', self.call_space)  # 预览基本情况。
        #
        self.tree_body.bind('<Insert>', exec_create_txt_note)  # 快速新建txt笔记

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

        if len(self.tree_body.selection()) == 1:
            try:
                t = self.tree_body.selection()[0]
                if tree_file_item_is_enabled(t):
                    pth = self.tree_body.item(t, "values")[-1]
                    res = get_file_part(pth)

                    msg_lst = ["完整文件名：\n    ", str(res['ffname']), '\n\n',
                               "文件名（去标签）：\n    ", str(res['fname_0']), '\n\n',
                               '标签：\n    ', res['ftags'],  '\n\n',
                               '修改日期：\n    ', res['file_mdf_time'], '\n\n',
                               '大小（kB）：\n    ', res['fsize'], '\n\n',
                               '完整路径：\n    ', str(res['full_path']),
                               ]
                    try:
                        if str(res['fename']) in ['.md','.txt']:
                            try:
                                with open(res['full_path'],'r',encoding='utf8') as f:
                                    file_content = f.read(100000)
                            except:
                                with open(res['full_path'],'r',encoding='gbk') as f:
                                    file_content = f.read(100000)
                            msg_lst.append('\n\n————————————————————\n\n')
                            msg_lst.append(file_content)
                    except Exception as e:  # utf8 和 gbk 都无法解码的话
                        logging.error(e)
                    msg = map(str, msg_lst)
                    TdTextWindow(app.window, '详情', ''.join(msg),ui_ratio=conf.ui_ratio,)
            except Exception as e:
                logging.error(e)
                TdTextWindow(app.window, '错误', '文件加载异常',ui_ratio=conf.ui_ratio,)
        else: # 选择多个项目的话
            logging.debug(f"选择了多条项目，不能执行预览。")


###########################################################
###########################################################
# 主程序开始
###########################################################
###########################################################

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
    td_queue = queue.Queue()

    core_data = td_data()

    #
    # lst_files_to_go = []  # 所有文件的完整路径
    # dT = []
    #
    # lst_tags = []  # 全部标签
    lst_tags_selected = []
    #
    # lst_sub_path = []  # 子文件夹得到全局变量
    lst_sub_path_selected = []
    #
    # lst_pick_up_files = []  # 程序内剪切板
    # lst_pick_up_items = []  # 程序内剪切板
    # state_pick_up = 'move'
    # folder_to_move = ''  # 待移动的文件夹
    #
    # dict_path = dict()  # 用于列表简写和实际值
    # dict_folder_groups = dict()  # 文件夹对应分组
    #
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
    set_style_view(style,app,conf)
    #
    win_manager = window_manager()
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
    tree_file_order_show()

    # 运行
    # app.tree_folder.refresh()  # 文件夹列表
    app.tree_folder.refresh()

    IMAGE_FOLDER = tk.PhotoImage(file='./resources/imgs/gitee_homepage.png')

    try:
        tmp_itm_sel = app.tree_lst_folder.get_children()[0]
        tmp_itm_sel = app.tree_lst_folder.get_children(tmp_itm_sel)[0]
        tmp_path_long = app.tree_lst_folder.item(tmp_itm_sel, "values")[-1]
        conf.lst_my_path_long_selected = [tmp_path_long,]  # 默认加载第一个文件夹的内容
        app.lst_files_to_go = get_data(conf.lst_my_path_long_selected)
    except:
        app.lst_files_to_go = get_data()  # 此处有隐患，还没条件测试
    #
    (app.DT, app.lst_tags) = get_dt()
    #
    app.tree_tag.set_lst_tag(app.lst_tags)  # 标签内容
    #
    try:
        tree_file_add_items(app.tree_file, app.DT)  # 主要内容
    except Exception as e:
        logging.warning(e)
        logging.warning('初始化主列表发生错误')
        app.str_btm.set('已就绪')
    #
    app.flag.flag_inited = 1  # 代表前面的部分已经运行过一次了
    set_prog_bar(0)
    #
    USE_THREAD = False
    if USE_THREAD:
        sub_task = threading.Thread(target=process_update_data, args=(conf.lst_my_path_long,))
        sub_task.setDaemon(True)
        sub_task.start()
    #
    app.window.mainloop()
    logging.info('主程序运行结束')
