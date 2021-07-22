# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""

import os
import tkinter as tk
from tkinter import ttk
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
import threading # 多线程
from multiprocessing import Pool
from multiprocessing import Process
# from docx import Document# 用于创建word文档
# import ctypes # 用于调整分辨率

import shutil
import queue
# import my_logger
# import send2trash # 回收站

URL_HELP='https://gitee.com/horse_sword/my-local-library' # 帮助的超链接，目前是 gitee 主页
URL_ADV='https://gitee.com/horse_sword/my-local-library/issues' # 提建议的位置
TAR='Tagdox / 标签文库' # 程序名称
VER='v0.14.1.0' # 版本号

'''
## 近期更新说明
#### v0.14.1.0 2021年7月22日
增加了文件夹拖动进来是移动还是复制的设置；优化设置文件的架构。
'''
#%%
#常量，但以后可以做到设置里面
DEVELOP_MODE=0 # 开启调试模式
LOGO_PATH='./src/LOGO.ico'
cALL_FILES=''                       # 标签为空的表达方式，默认是空字符串
LARGE_FONT=12                       # 表头字号
MON_FONTSIZE=10                     # 正文字号
ORDER_BY_N=2                        # 初始按哪一列排序，1代表标签，后面按顺序对应
ORDER_DESC=True                    # 是否逆序
CLEAR_AFTER_CHANGE_FOLDER=2         # 切换文件夹后，是否清除筛选。0 是保留，其他是清除。
EXP_FOLDERS=['_img']                # 排除文件夹规则，以后会加到自定义里面
ALL_FOLDERS=2                       # 是否有“所有文件夹”的功能,1 在前面，2在末尾，其余没有
PROG_STEP=500                       # 进度条刷新参数
NOTE_NAME='未命名'                  # 新建笔记的名称

#
try:
    if isfile('D:/MyPython/开发数据/options_for_tagdox.json'):
        print('进入开发模式')
        OPTIONS_FILE='D:/MyPython/开发数据/options_for_tagdox.json'
    else:
        print('正式模式')
        OPTIONS_FILE='options_for_tagdox.json'         # 配置文件的名称
except:
    print('正式模式')
    OPTIONS_FILE='options_for_tagdox.json'         # 配置文件的名称

V_SEP='^'     # 标签分隔符。可修改
V_FOLDERS=2   # 标签识别文件夹深度，可修改
NOTE_EXT='.docx'                    # 新建笔记的类型
NOTE_EXT_LIST=['.md','.txt','.docx','.rtf']
FILE_DRAG_MOVE='move'    # 文件拖动到列表的时候，是复制，还是移动。可修改。取值：'move' 'copy'。

OPT_DEFAULT={
	"options":{
		"sep":"#",
		"vfolders":"2",
		"note_ext":".docx",
        "file_drag_enter":"move",
		
	},
    "folders":[
	]
 }

QUICK_TAGS=['@PIN','@TODO','@toRead','@Done'] #
DIR_LST=['▲','▼'] # 列排序标题行
HEADING_LST=['file','tags','modify_time','size','file0']
HEADING_LST_TXT=['文件名','标签','修改时间','文件大小(kB)','完整路径']
# HEADING_LST=['file','tags','modify_time','file0']
# HEADING_LST_TXT=['文件名','标签','修改时间','完整路径']
MULTI_PROC=1 # 并发进程数，设置为1或更低就单独进程。
MULTI_FILE_COUNT=400



#%%
#######################################################################

def split_path(full_path): 
    '''
    通用函数：    
    将完整路径拆分，得到每个文件夹到文件名的列表。
    '''
    test_str=full_path.replace('\\', '/',-1)
    test_str_res=test_str.split('/')
    return(test_str_res)

def exec_tree_clear(tree_obj): # 
    '''
    通用函数。
    通用的 treeview 清除函数，因为是通用的，所以必须带参数。
    参数是 具体的 treeview 对象。
    '''
    x=tree_obj.get_children()
    for item in x:
        tree_obj.delete(item)
    if flag_inited==1:
        window.update()

def safe_get_name(new_name):
    '''

    输入目标全路径，返回安全的新路径（可用于重命名、新建等）
    输入和输出都是字符串。

    '''
    n=1
    [tmp_path,tmp_new_name]=os.path.split(new_name)

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
    # print(tmp_new_full_name)
    return(tmp_new_full_name)



def remove_to_trash(filename,remove=True):
    '''
    删除文件，
    尚未调试成功，没有启用。
    '''
    if remove:
        print('直接删除')
        os.remove(filename)
    else:
        print('删除到回收站')
        # send2trash.send2trash(filename) 

def exec_safe_rename(old_name,new_name):
    '''
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 如果重命名成功，返回添加数字之后的最终文件名；
    如果重命名失败，返回原始文件名。
    '''
    old_name=old_name.replace('\\','/')
    new_name=new_name.replace('\\','/')
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
    tmp_new_full_name=safe_get_name(new_name)
    try:
        os.rename(old_name,tmp_new_full_name)
        return(tmp_new_full_name)
    except:
        print('安全重命名失败！')
        return(old_name)
        pass

def safe_copy(old_name,new_name,opt_type='copy'):
    '''
    安全复制或移动文件。
    参数 opt_type 是 'copy' 或 'move'。
    '''
    old_name=old_name.replace('\\','/')
    new_name=new_name.replace('\\','/')
    tmp_new_full_name=safe_get_name(new_name)
    print('开始安全复制')
    print(old_name)
    print(tmp_new_full_name)
    if opt_type=='copy':
        try:
            shutil.copy(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name) 
            print('安全复制成功')
            # os.rename(old_name,tmp_new_full_name)
            return(tmp_new_full_name)
        except:
            print('对以下文件复制失败！')
            print(old_name)
            return(old_name)
            pass
    elif opt_type=='move':
        try:
            shutil.move(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name) 
            print('安全移动成功')
            # os.rename(old_name,tmp_new_full_name)
            return(tmp_new_full_name)
        except:
            print('对以下文件移动失败！')
            print(old_name)
            return(old_name)
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
#%%
# 加载设置项 json 内容。保存到 opt_data 变量中，这是个 dict。


def exec_update_json(tar=OPTIONS_FILE,data=None): 
    '''
    将 json_data变量的值，写入 json 文件。
    可以不带参数，随时调用就是写入json。
    '''
    global json_data
    if data is None:
        data=json_data
    with open(tar,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False)

def set_json_options(key1,value1):
    '''
    修改设置项。
    会自动触发 exec_update_json（写入json文件）.
    '''
    global json_data
    opt_data=json_data['options']   #设置
    opt_data[key1]=value1
    exec_update_json(data=json_data)
    # get_json_file_data()
    pass

def get_json_file_data(load_settings=True,load_folders=True):
    '''
    读取json文件，获取其中的参数，并存储到相应的变量中。

    如果json文件读取失败，则按照初始化标准重建这个文件。

    依赖函数：update_json。
    '''
    global json_data
    global V_SEP,V_FOLDERS
    global NOTE_EXT,FILE_DRAG_MOVE
    global lst_my_path_long
    global lst_my_path_short
    global lst_my_path_long_selected
    
    need_init_json=0
    try:
        with open(OPTIONS_FILE,'r',encoding='utf8')as fp:
            json_data = json.load(fp)
        
        if load_settings:
            try: opt_data=json_data['options']   #设置
            except: pass
            try: V_SEP=opt_data['sep'] # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
            except: pass
            try: V_FOLDERS=int(opt_data['vfolders']) # 目录最末层数名称检查，作为标签的检查层数
            except: pass
            try: NOTE_EXT=opt_data['note_ext'] # 默认笔记类型
            except: pass
            try: FILE_DRAG_MOVE=opt_data['file_drag_enter'] # 默认拖动操作
            except: pass
            print('加载基本参数成功')

        if load_folders:    
            # lst_my_path_long_selected=lst_my_path_long.copy() #按文件夹筛选用
            lst_my_path_long=[]
            lst_my_path_short=[]
        
        

            json_folders_lst=json_data['folders']

            for i in json_folders_lst: 
                # lst_my_path_long.append(i)
                tmp_L=i['pth']
                tmp_L=tmp_L.strip()
                try:
                    tmp_S=i['short']
                except:
                    tmp_S=split_path(i['pth'])[-1]
                tmp_S=tmp_S.replace(' ','_') # 修复路径空格bug的权宜之计，以后应该可以优化
                
                # 增加逻辑：避免短路径重名：
                j=1
                tmp_2=tmp_S
                while tmp_2 in lst_my_path_short:
                    j+=1
                    tmp_2=tmp_S+"("+str(j)+")"
                    print(tmp_2)
                tmp_S=tmp_2
                tmp_S=tmp_S.strip()
                
                if tmp_S=='' or tmp_L=='': # 出现空白文件夹
                    for j in range(len(json_folders_lst)-1,-1,-1):
                        if json_folders_lst[j]['pth'].strip()=='':    
                            json_folders_lst.pop(j)
                else:
                    lst_my_path_long.append(tmp_L)
                    lst_my_path_short.append(tmp_S)
                    tmp={tmp_S:tmp_L}
                    dict_path.update(tmp)
        
            lst_my_path_long_selected=lst_my_path_long.copy() # 此处有大量的可优化空间。
            print('加载关注文件夹列表成功')
    except:
        print('加载json异常，正在重置json文件')
        # need_init_json=1
        json_data = OPT_DEFAULT
        exec_update_json()
        

#######################################################################
#%% 线程处理



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


#%%

def set_prog_bar(inp,maxv=100):
    '''
    手动设置进度条。
    '''
    prog.set(inp)
    # progressbar_file.update() # 刷新进度条
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
        if inp<=1:
            prog_win=my_progress_window(window,inp)

        elif inp==100:
            prog_win.set(inp)
            del prog_win
        else:
            prog_win.set(inp)
    except:
        pass


def get_data(ipath=None,update_sub_path=1): 
    '''
    根据所选中的文件夹(列表)，
    返回 lst_file 列表。这个列表可以在 gen_dt 里面调用。
    此过程消耗时间较多。
    参数 ipath=lst_my_path_long
    '''
    print('调用 get_data 函数')

    global lst_sub_path,flag_running # 必须要有这句话，否则不能修改公共变量
    
    if ipath is None:
        ipath=lst_my_path_long

    # flag_running=1 # 标记为运行中。

    lst_sub_path_copy=lst_sub_path.copy()
    if flag_inited==1:
        exec_tree_clear(tree) # 
        set_prog_bar(1,30)
        str_btm.set("正在加载基础数据……")
        window.update()
        
    
    time0=time.time()
    lst_file=list() #获取所有文件的完整路径
    
    n=1
    n_max=len(ipath)
    lst_sub_path=[]
    
    PROG_STEP=2
    for vPath in ipath:
        n+=1
        if flag_inited==1 and n % PROG_STEP == 0:
            PROG_STEP*=2
            tmp_prog=1+29*n/n_max
            if tmp_prog>30:
                tmp_prog=30
            set_prog_bar(tmp_prog)
            
        for root, dirs, files in os.walk(vPath):
            
            tmp=[]
            vpass=0
            new_sub_path=root.replace('\\','/')
            new_sub_path=new_sub_path.replace(vPath+'/','')
            if (not new_sub_path in lst_sub_path) \
                and (str(new_sub_path).find('/')<0)  \
                and (str(new_sub_path) not in EXP_FOLDERS):
                lst_sub_path.append(new_sub_path)

            tmp_path=split_path(root)
            for tmp2 in tmp_path:
                if tmp2 in EXP_FOLDERS:
                    vpass=1
                    break
                elif tmp2[0]=='.': # 排除.开头的文件夹内容
                    vpass=1
                    break
            for name in files:
                tmp.append(os.path.join(root, name))
                if name=='_nomedia':
                    vpass=1
                    break # 之前居然没写break，难怪那么慢
                    
            if not vpass==1:
                lst_file+=tmp 
            
            if flag_break: # 强行中断
                break
        if flag_break:
            break

    print('加载 lst_file 消耗时间：')
    print(time.time()-time0)
    #
    # 更新子文件夹
    try:
        lst_sub_path.sort()
        lst_sub_path_copy.sort()
        if lst_sub_path == lst_sub_path_copy:
            update_sub_path=0
        else:
            print(lst_sub_path)
            print(lst_sub_path_copy)
    except:
        pass

    if update_sub_path:
        try:
            lst_sub_path.sort()
            v_sub_folders['value']=['']+lst_sub_path # 强制修改子文件夹列表，但这样写不太好
            v_sub_folders.current(0)
            #
            exec_update_sub_folder_list(lst_sub_path)
        except:
            pass
    else:
        lst_sub_path = lst_sub_path_copy
    # if flag_inited==1:
    #     set_prog_bar(30,30)
    
    return lst_file

def get_file_part(tar):     # 【疑似bug】对带有空格的路径解析异常
    '''
    这里输入参数 tar 是完整文件路径。
    输入完整（文件）路径，以字典的形式，返回对应的所有文件信息。
    '''

    [fpath,ffname]=os.path.split(tar) # fpath 所在文件夹、ffname 原始文件名
    [fname,fename]=os.path.splitext(ffname) # fname 文件名前半部分，fename 扩展名
    lst_sp=fname.split(V_SEP) #拆分为多个片段
    fname_0 = lst_sp[0]+fename # fname_0 去掉标签之后的文件名
    ftags=lst_sp[1:] # ftags 标签部分
    
    mtime = os.stat(tar).st_mtime
    file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

    fsize=os.path.getsize(tar) # 文件大小，字节
    fsize=fsize/(1024) #换算到kB
    fsize=round(fsize,1)
    # fsize*=100
    # fsize=int(fsize)
    # fsize/=100


    # 对文件目录的解析算法2：
    tmp=split_path(fpath)
    tmp2=[]
    try: # 只要最后若干层的目录，取变量 V_FOLDERS
        for i in range(V_FOLDERS):
            tmp2.append(tmp[-i-1])
    except:
        pass
    
    for i in tmp2:
        i2=i.split(V_SEP)
        i3=i2[1:]
        ftags+=i3 
    
    # 对当前文件，进行标签整理、去重并排序
    ftags=list(set(ftags))
    ftags.sort()
    # print(ftags)
    
    # 统一斜杠方向
    fpath=fpath.replace('\\','/')
    tar=tar.replace('\\','/')
    
    return {'fname_0':fname_0, # 去掉标签之后的文件名
            'ftags':ftags,
            'ffname':ffname, # 原始文件名，带标签的
            'filename_origional':ffname, # 原始文件名，带标签、扩展名的
            'fpath':fpath,
            'f_path_only':fpath,
            'fname':fname,
            'filename_no_ext':fname, #去掉扩展名的文件名
            'fename':fename, # 扩展名
            'file_ext':fename, # 扩展名
            'full_path':tar,
            'fsize':fsize,
            'file_full_path':tar, # 完整路径，和输入参数完全一样
            'file_mdf_time':file_modify_time}
    
def dt_sort_by(elem): # 主题表格排序
    global ORDER_BY_N
    tmp=str(elem[ORDER_BY_N])
    if ORDER_BY_N==3:
        return float(tmp) # 数字
    else:
        tmp=tmp.replace('\xa0',' ') # GBK 不支持 'xa0' 的解码。这个是特殊空格。
        return tmp.encode('gbk') # 需要gbk才能中文正确排序

def sub_get_dt(lst_file_in):
    # 子循环
    tmp_dt=[]
    for tar in lst_file_in:
        tmp=get_file_part(tar)
        tmp_v=(str(tmp['fname_0']),tmp['ftags'],str(tmp['file_mdf_time']),tmp['fsize'],str(tmp['full_path']))
        tmp_dt.append(tmp_v)
    q.put(tmp_dt)
    print([V_FOLDERS,V_SEP,NOTE_EXT])
    return tmp_dt

def gen_dt(lst_file0=None):
    '''
    是最消耗时间的函数，也是获取数据的核心函数。
    输入参数是文件列表，缺省值是来自于 get_data() 函数的 lst_file ，提供了所有文件。

    根据 lst_file 里面的文件列表，返回 (dT, lst_tags) .
    无需输入参数，自动找变量。
    '''
    print('进入 gen_dt 函数')

    if flag_break:
        return (None,None)

    if lst_file0 is None:
        lst_file0=lst_file.copy()

    if flag_inited==1:
        str_btm.set("正在解析标签……")
        window.update()
        set_prog_bar(30)
        
    time0=time.time()
    
    n=1
    n_max=len(lst_file0)
    
    dT=list()    

    if MULTI_PROC>1 and len(lst_file0)>MULTI_FILE_COUNT: # 如果是并发状态：
        MAX_PROC=MULTI_PROC
        res_proc=[]
        tmp_len=int(len(lst_file0)/MAX_PROC)
        tmp_file_in=[]
        for i in range(MAX_PROC):
            if i<MAX_PROC-1:
                tmp_file_in.append(lst_file0[i*tmp_len:(i+1)*tmp_len])
            else:
                tmp_file_in.append(lst_file0[i*tmp_len:])
        #
        p=Pool(MAX_PROC) # 设置默认并发数。可以忽略
        # pl=[]
        res_tmp=[]
        t=[]
        for i in range(MAX_PROC):
            # res_tmp.append('')
            # res_tmp[i]=p.apply(sub_get_dt,args=(tmp_file_in[i],))
            # res_proc.append(res_tmp.get())
            # pl[-1].start()
            t.append(threading.Thread(target=sub_get_dt,args=(tmp_file_in[i],)))
            t[-1].start()

        # p.close()
        # p.join()
        set_prog_bar(50)
        for i in t:
            i.join()
        while not q.empty():
            tmp_get_dt=q.get()
            # print(tmp_get_dt)
            dT+=tmp_get_dt
        set_prog_bar(70)
        # tmp_part=[]
        # print('组合之前：——————')
        # print(time.time()-time0)
        # for i in res_tmp:
            # dT+=i
        print('组合之后：——————')
        print(time.time()-time0)
    else:
        for tar in lst_file0:
            
            # 更新进度条
            n+=1
            if flag_inited==1 and n % PROG_STEP ==0:
                set_prog_bar(30+69*n/n_max)
            
            tmp=get_file_part(tar)
            # dT.append([tmp['fname_0'],tmp['ftags'],tmp['fpath'],tmp['full_path']])
            # 增加检查重复项的逻辑：
            # tmp_v=[tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path']]
            # tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path'])
            tmp_v=(str(tmp['fname_0']),tmp['ftags'],str(tmp['file_mdf_time']),tmp['fsize'],str(tmp['full_path']))
            
            # if not tmp_v in dT:
            #     dT.append(tmp_v) # 查重有点费时间
            dT.append(tmp_v)
            #
            if flag_break: # 如果被中断的话
                break

    print('加载dT消耗时间：')
    print(time.time()-time0)
    
    # 去重
    dT2=[]
    for i in dT:
        if not i in dT2:
            dT2.append(i)
    dT=dT2
    # dT=list(set(dT))
    
    
    if flag_inited==1:
        set_prog_bar(99)
        
    # 获取所有tag
    tmp=[]
    for i in dT:
        tmp+=i[1]
    
    lst_tags=list(set(tmp))
    lst_tags=sorted(lst_tags, key=lambda x: x.replace('\xa0',' ').encode('gbk'))
    lst_tags=[cALL_FILES]+lst_tags
    # lst_tags.sort()
    
    try:
        dT.sort(key=dt_sort_by,reverse=ORDER_DESC)
    except:
        print('dT排序出现错误！') 
    
    return (dT, lst_tags)


#%%
#######################################################################
#%%
def show_info_window():
    '''
    显示关于窗口。
    不需要任何参数。
    '''
    screenwidth = SCREEN_WIDTH
    screenheight = SCREEN_HEIGHT
    w_width = 600
    w_height = 500
    info_window=tk.Toplevel(window)
    info_window.geometry('%dx%d+%d+%d'%(w_width, w_height, (screenwidth-w_width)/2, (screenheight-w_height)/2))
    info_window.title('关于标签文库')

    info_window.transient(window) # 避免在任务栏出现第二个窗口，而且可以实现置顶
    info_window.grab_set() # 模态

    info_window.deiconify()
    info_window.lift()
    info_window.focus_force()
    info_window.iconbitmap(LOGO_PATH) # 左上角图标

    info_frame=tk.Frame(info_window,padx=5,pady=5)
    info_frame.pack(expand=0,fill=tk.BOTH)
    

    tmp=tk.Label(info_frame,text='\n')
    tmp.pack()
    tmp=tk.Label(info_frame,text='标签文库 / Tagdox',fg='#2d7d9a',font=('微软雅黑',16))
    tmp.pack()
    tmp=tk.Label(info_frame,text='\n马剑 个人开发')
    tmp.pack()
    tmp=tk.Label(info_frame,text='版本：'+VER+'\n')
    tmp.pack()

    global p_logo
    p_logo = tk.PhotoImage(file='./src/在线帮助.png')
    logolbl= tk.Label(info_frame, text='A',image = p_logo)
    logolbl.pack()

    tmp=tk.Label(info_frame,text='（欢迎扫码访问产品动态）')
    tmp.pack()



# 自制输入窗体
class my_input_window:
    '''
    输入窗体类。
    实现了一个居中的模态窗体。
    '''
    input_value=''

    def __init__(self,parent,title='未命名',msg='未定义',default_value='',selection_range=None) -> None:
        '''
        自制输入窗体的初始化；
        参数：
        selection_range 是默认选中的范围。
        '''
        
        # 变量设置
        self.form0=parent # 父窗格
        #
        self.input_value=''
        self.title=title
        self.msg=msg
        self.default_value=default_value
        self.input_window=tk.Toplevel(self.form0)
        #
        self.input_window.transient(self.form0) # 避免在任务栏出现第二个窗口，而且可以实现置顶
        self.input_window.grab_set() #模态
        
        #
        # 窗口设置
        # self.input_window.overrideredirect(True) # 这句话可以去掉标题栏，同时也会没有阴影
        self.screenwidth = SCREEN_WIDTH
        self.screenheight = SCREEN_HEIGHT
        self.w_width = 800
        self.w_height = 160
        self.x_pos= (self.screenwidth-self.w_width)/2
        self.y_pos= (self.screenheight-self.w_height)/2
        self.input_window.geometry('%dx%d+%d+%d'%(self.w_width, self.w_height,self.x_pos,self.y_pos))
        self.input_window.title(self.title)
        #
        
        try:
            self.input_window.iconbitmap(LOGO_PATH) # 左上角图标
        except:
            pass

        self.iframe=tk.Frame(self.input_window,padx=20,pady=10)
        self.iframe.pack(expand=0,fill=tk.BOTH)
        
        # 文本框
        self.lb=tk.Label(self.iframe,text=self.msg,font="微软雅黑 "+str(MON_FONTSIZE))
        self.lb.pack(anchor='sw',pady=5)
        self.input_window.update()
        
        # 输入框
        self.et=tk.Entry(self.iframe,font="微软雅黑 "+str(MON_FONTSIZE))
        self.et.insert(0,self.default_value)
        self.et.pack(expand=0,fill=tk.X,pady=5)
        
        # self.et.selection_range(0, len(self.et.get()))
        if selection_range is None:
            self.et.selection_range(0, len(self.et.get()))
        else:
            self.et.selection_range(0, selection_range)
        self.et.focus() # 获得焦点

        # self.et.focus()
        # 键盘快捷键
        self.input_window.bind_all('<Return>',self.bt_yes_click)
        self.input_window.bind_all('<Escape>',self.bt_cancel_click)

        self.iframe_bt=tk.Frame(self.input_window,padx=10,pady=10)
        self.iframe_bt.pack()
        # self.iframe_bt.pack(expand=0,fill=tk.BOTH)
        # 按钮
        self.bty=ttk.Button(self.iframe_bt,text='确定',command=self.bt_yes_click)
        self.bty.pack(side=tk.LEFT,padx=20)
        self.btc=ttk.Button(self.iframe_bt,text='取消',command=self.bt_cancel_click)
        self.btc.pack(side=tk.LEFT,padx=20)

        self.input_window.deiconify()
        self.input_window.lift()
        self.input_window.focus_force()
        

        self.form0.wait_window(self.input_window) # 要用这句话拦截主窗体的代码运行
        
        

    def bt_cancel_click(self,event=None):
        self.input_window.destroy()
    
    def bt_yes_click(self,event=None) -> str:
        self.input_value=self.et.get()
        # print(self.input_value)
        self.input_window.destroy()
        return self.input_value

    def __str__(self) -> str:
        return self.input_value

    def __del__(self) -> str:
        self.input_value=''
        return ''

class my_progress_window:
    '''
    一个屏幕中间的进度条
    '''
    
    input_window=''#=tk.Toplevel(self.form0)

    def __init__(self,parent,prog_value=0,prog_text='') -> None:
        '''
        进度条，输入进度数值
        '''
        
        # 变量设置
        self.form0=parent

        self.input_value=''
        self.input_window=tk.Toplevel(self.form0)
        self.input_window.title('进度')
        self.my_prog=tk.DoubleVar() # 进度
        self.my_text=prog_text
        self.my_prog.set(prog_value)
        #
        # 窗口设置
        self.input_window.overrideredirect(True) # 这句话可以去掉标题栏，同时也会没有阴影
        self.screenwidth = SCREEN_WIDTH
        self.screenheight = SCREEN_HEIGHT
        self.w_width = 800
        self.w_height = 100
        self.x_pos= (self.screenwidth-self.w_width)/2
        self.y_pos= (self.screenheight-self.w_height)/2
        self.input_window.geometry('%dx%d+%d+%d'%(self.w_width, self.w_height,self.x_pos,self.y_pos))
        # self.input_window.title(self.title)
        self.input_window.transient(self.form0) # 避免在任务栏出现第二个窗口，而且可以实现置顶
        self.input_window.withdraw()

        try:
            self.input_window.iconbitmap(LOGO_PATH) # 左上角图标
        except:
            pass

        self.iframe=tk.Frame(self.input_window,padx=20,pady=20)
        self.iframe.pack(expand=0,fill=tk.BOTH)
        # 标签
        self.pct=tk.Label(self.iframe)
        self.pct.pack()
        # 进度条
        self.prog_bar=ttk.Progressbar(self.iframe,variable=self.my_prog)
        self.prog_bar.pack(expand=0,fill=tk.BOTH)

    def set(self,value):
        self.progress=value
        self.my_prog.set(self.progress)
        self.pct.configure(text=self.my_text+str(int(value))+'%')
        self.input_window.update()
        # self.pct.update()
        # self.prog_bar.update()
        if value==0:
            self.input_window.withdraw()
        elif value>0:
            self.input_window.deiconify() # 置顶
            # self.input_window.lift() # 置顶，但是会导致后面失去输入能力
            # self.input_window.focus_force()
            
            self.input_window.grab_set() #模态

        if value>=100:
            self.input_window.withdraw()
            # self.input_window.overrideredirect(False) 
            self.input_window.destroy()
            self.__destroy__()


def show_my_input_window(title='未命名',msg='未定义',default_value=''):
    '''
    想要做输入框，替代 tkinter 自带的，
    但是并没有启用。
    '''
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    w_width = 500
    w_height = 200
    x_pos= (screenwidth-w_width)/2
    y_pos= (screenheight-w_height)/2
    input_window=tk.Toplevel(window)
    input_window.geometry('%dx%d+%d+%d'%(w_width, w_height,x_pos,y_pos))
    input_window.title(title)
    #
    input_value=''
    #
    # input_window.withdraw()
    input_window.deiconify()
    input_window.lift()
    input_window.focus_force()
    input_window.transient(window) # 避免在任务栏出现第二个窗口，而且可以实现置顶
    input_window.grab_set() #模态

    iframe=tk.Frame(input_window,padx=10,pady=10)
    iframe.pack(expand=0,fill=tk.BOTH)
    
    lb=tk.Label(iframe,text=msg)
    lb.pack(anchor='sw')
    
    et=tk.Entry(iframe)
    et.pack(expand=0,fill=tk.X)

    def bt_cancel_click(event=None):
        input_window.destroy()
    
    def bt_yes_click(event=None):
        global input_value
        input_value=et.get()
        input_window.destroy()

    btc=ttk.Button(input_window,text='yes',command=bt_yes_click)
    btc.pack()

    return(input_value)
    
# my_input_window()

def show_input_window(title_value,body_value='',init_value='',is_file_name=True):
    '''
    接管输入框的过程，以后可以将自定义输入框替换到这里。
    目前的用法：输入参数 1 标题，2 正文，3 默认值；
    返回输入框的结果。如果输入内容为空，返回 None。
    参数 is_file_name 为 True 的时候，将文件名不能带的特殊字符自动去掉。
    '''
    # 获得输入值
    # res = simpledialog.askstring(title_value,prompt=body_value,initialvalue=init_value)
    res = str(my_input_window(window,title_value,body_value,init_value)).strip()
    if len(res)==0:
        print('没有得到输入内容')
        return None

    # 特殊处理
    if is_file_name:
        res=res.replace('\\','')
        res=res.replace('/','')
        res=res.replace('?','')
        res=res.replace('|','')
        res=res.replace('*','')
        res=res.replace('"','')
        res=res.replace('<','')
        res=res.replace('>','')
        res=res.replace(':','')
    return res
    pass

#%%
# 顶部菜单

if False:
    menu1=tk.Menu(window)
    mFile=tk.Menu(menu1,tearoff=False)
    menu1.add_cascade(label='文件', menu=mFile)

    mFile.add_command(label='新建',accelerator='Ctrl+N')
    mFile.add_command(label='打开', accelerator='Ctrl+O')
    mFile.add_command(label='保存', accelerator='Ctrl+S')

    mHelp=tk.Menu(menu1,tearoff=False)
    menu1.add_cascade(label='帮助', menu=mHelp)

    mHelp.add_command(label='使用说明',accelerator='Ctrl+H')

    # window.configure(menu=menu1) # 菜单生效

#%%

def exec_update_folder_list():
    '''
    根据 lst_my_path_s，将文件夹列表刷新一次。
    没有输入输出。
    '''
    global tree_lst_folder
    
    exec_tree_clear(tree_lst_folder)
    tmp=0
    if ALL_FOLDERS==1:
        tree_lst_folder.insert('',tmp,values=("（全部）"))
    for i in lst_my_path_short:
        tmp+=1
        print(i)
        tree_lst_folder.insert('',tmp,values=(str(i))) # 此处有bug，对存在空格的不可用
        # image=IMAGE_FOLDER,
    if ALL_FOLDERS==2:
        tree_lst_folder.insert('',tmp,values=("（全部）"))
        # tree_lst_folder.insert(tk.END,i)
    try:
        tmp=tree_lst_folder.get_children()[0]
        # tree_lst_folder.focus(tmp)
        tree_lst_folder.selection_set(tmp)
    except:
        pass
# tree_lst_folder.selection_set()

def exec_update_sub_folder_list(sf_list,refresh=True):
    '''
    根据 lst_my_path_s，将文件夹列表刷新一次。
    没有输入输出。
    '''
    exec_tree_clear(tree_lst_sub_folder)
    tmp_sub_folder=tree_lst_sub_folder.selection()

    if get_folder_short() in ["（全部）",""]:
        return
    
    tmp=0
    tree_lst_sub_folder.insert('',tmp,values=("（全部）"))
    for i in sf_list:
        tmp+=1
        print(i)
        tree_lst_sub_folder.insert('',tmp,values=(i,)) # 必须加逗号，否则对存在空格的不可用
        # image=IMAGE_FOLDER,
    try:
        if refresh:
            tmp=tree_lst_sub_folder.get_children()[0]
            # tree_lst_folder.focus(tmp)
            tree_lst_sub_folder.selection_set(tmp)
        else:
            tree_lst_sub_folder.selection_set(tmp_sub_folder)
            pass
    except Exception as e:
        print(e)
        pass
# tree_lst_folder.selection_set()



def tree_order_show():
    global ORDER_BY_N,ORDER_DESC
    DIR_VALUE=DIR_LST[1] if ORDER_DESC else DIR_LST[0]
    tree.heading(HEADING_LST[ORDER_BY_N], text=HEADING_LST_TXT[ORDER_BY_N]+DIR_VALUE)

def tree_order_base(inp):
    '''
    主列表排序的入口程序。
    '''

    global ORDER_BY_N,ORDER_DESC,dT,lst_tags  
    # 恢复标题
    tree.heading(HEADING_LST[ORDER_BY_N], text=HEADING_LST_TXT[ORDER_BY_N])
    #
    if ORDER_BY_N==inp: # 如果同样位置点击，就切换排序方式
        ORDER_DESC=not ORDER_DESC
    else: # 如果不同位置点击，就预置排序方式
        ORDER_BY_N=inp
        if ORDER_BY_N==2: # 按修改时间排序的，第一次是最新的在前面。
            ORDER_DESC=True 
        else:
            ORDER_DESC=False # 其余排序方法，都是升序。
    # exec_main_window_reload(0) # 这个方法虽然可以排序，但是效率太低
    #
    # 可视化
    tree_order_show()

    # 新的排序方法
    dT.sort(key=dt_sort_by,reverse=ORDER_DESC)
    exec_v_tag_choose()
    v_tag['value']=lst_tags
    v_inp['value']=lst_tags
    
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

    

#%%

def get_search_items(event=None): 
    '''
    获取标签下拉框里面的标签。
    不过，现在也兼职了对输入框的搜索。
    返回值是列表。
    '''
    res=[]
    if len(v_tag.get())>0:
        res+=[v_tag.get()]
    if len(v_search.get())>0:
        res+=str(v_search.get()).split(' ')
    if len(get_sub_folder())>0:
        tmp_path=lst_my_path_long_selected[0]+'/'+get_sub_folder()
        print('进入子文件夹：')
        print(tmp_path)
        res+=[tmp_path]
    else:
        # 还要考虑子文件夹从有到无时候的处理；
        pass
        '''
        # 还要刷新子文件夹的标签
        tmp_tag=v_tag.get() # 获取当前标签
        #刷新标签列表
        new_files = get_data(res,update_sub_path=0)
        (dt2,tags2)=gen_dt(new_files)
        print(tags2)
        v_tag['value']=['']+tags2
        if len(tmp_tag)>0:
            # 恢复标签
            v_tag.current(tags2.index(tmp_tag)+1)
            pass
        '''
    return res

def get_sub_folder():
    '''
    获取子文件夹名称（没有输入，返回字符串，或者空白）
    '''
    METHOD=2
    #
    if METHOD==1:
        return v_sub_folders.get()
    # 方法2：
    elif METHOD==2:
        res=''
        for item in tree_lst_sub_folder.selection():
            res = tree_lst_sub_folder.item(item, "values")[0]
        if res in ['（全部）']:
            res=''
        return res


def get_search_items_sub_folder(event=None): 
    '''
    获取子文件夹内的文件.
    在函数中，包括了对标签的刷新。
    '''
    if len(get_sub_folder())>0:
        tmp_path=lst_my_path_long_selected[0]+'/'+get_sub_folder()
        print('进入子文件夹：')
        print(tmp_path)
    else:
        tmp_path=lst_my_path_long_selected[0]
    tmp_path=str(tmp_path).replace('\\','/')

    # 这里，如果是子文件夹切换，还要刷新文件夹的标签【bug】
    #
    # if flag_root_folder:
    if not flag_sub_folders_changed:
        pass
    else:
        # 加载新标签列表
        tmp_tag=v_tag.get() # 获取当前标签
        # 刷新标签列表
        new_files = get_data([tmp_path],update_sub_path=0)
        (dt2,tags2)=gen_dt(new_files)
        # print(tags2)
        v_tag['value']=tags2
        if flag_inited:
            v_inp['value']=tags2
        if len(tmp_tag)>0:
            # 恢复标签
            try:
                v_tag.current(tags2.index(tmp_tag))
            except:
                v_tag.current(0)
        else:
            v_tag.current(0)
            pass
    res=get_search_items()
    return res

def exec_add_tree_item(tree,dT) -> None: 
    '''
    关键函数：增加主框架的内容
    先获得搜索项目以及 tag
    '''
    global PIC_LST

    str_btm.set('正在刷新列表……')
    time0=time.time()
    # tmp_search_items=get_search_items() # 列表
    tmp_search_items=get_search_items_sub_folder() # 列表
    
    k=0
    print('筛选条件：')
    print(tmp_search_items)
    n=0
    n_max=len(dT)
    refresh_unit=4
    for i in range(len(dT)):
        n+=1

        tmp=dT[i]
        try:
            if tmp[0][0:2]=='~$': # 排除word临时文件
                continue
        except:
            pass
        tag_lower=[]
        for j in tmp[1]:
            tag_lower.append(str.lower(j))
            #搜索的时候转小写，避免找不到类似于MySQL这样的标签
        
        canadd=1
        
        for tag in tmp_search_items:  # 这里感觉好像逻辑有问题
            tag=str.lower(tag)
            if tag=='' or tag==cALL_FILES or (tag in tag_lower):
                canadd=1
                # break
            elif str.lower(tmp[-1]).find(tag)<0:
                canadd=0
        
        if canadd==1:
            k+=1
            if k%2==1:
                tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3],tmp[4]),tags=['line1'])
            else:
                tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3],tmp[4]))
        # if k % refresh_unit==0: # 刷新
        #     refresh_unit=refresh_unit*refresh_unit
        #     if flag_inited:
        #         set_prog_bar(99+1*n/n_max)
        #     tree.update() # 提前刷新，优化用户体验
        #     # str_btm.set('即将完成……')
    print('添加列表项消耗时间：')
    print(time.time()-time0)    
    
    str_btm.set("找到 "+str(k)+" 个结果")#"，用时"+str(time.time()-time0)+"秒")
    if flag_inited:    
        set_prog_bar(100)
    # flag_running=0
    # 设置文件夹

    # tree.insert('',i,values=(d[0][i],d[1][i],d[2][i],d[3][i]))



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
        res=res[0]
        if res=='（全部）':
            res=''
    except:
        res=''
    # print(res)
    return res

def get_folder_long():
    '''
    合并获取短路径和长路径的逻辑。
    返回值是代表文件夹长路径的字符串。
    '''
    short_folder=get_folder_short()
    if short_folder =='':
        return short_folder
    else:
        res=get_folder_s2l(short_folder)
        res=str(res).replace('\\','/')
        return res

def get_folder_long_v2():
    '''
    优化架构下的文件夹列表获取方法。
    这种架构下，文件夹列表的-1列就是长路径名。
    '''
    for item in tree_lst_folder.selection():
        path_long=tree_lst_folder.item(item,"values")[-1]
    return path_long


# 获取当前点击行的值
def exec_tree_file_open(event=None): #单击
    '''
    打开列表选中项目。
    按理说，兼容多文件。

    '''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        print('正在打开文件：')
        print(item_text[-1])
        try:
            os.startfile(item_text[-1]) #打开这个文件
        except:
            print('打开文件失败')

def exec_file_rename(tar=None): # 对文件重命名
    '''
    重命名tree选中的文件。需要有tree的选中项目。
    每个文件重命名一次，按理说兼容多文件，但是这个命令不应该给多文件执行。
    '''
    for item in tree.selection():
        # 获得目标文件
        item_text = tree.item(item, "values")
        tmp_full_path = item_text[-1]
        tmp_file_name = split_path(tmp_full_path)[-1]
        #
        #
        print('正在重命名：')
        print(tmp_full_path)
        print(tmp_file_name)
        # res = simpledialog.askstring('文件重命名',prompt='请输入新的文件名',initialvalue =tmp_file_name) # 有bug，不能输入#号
        res = show_input_window('文件重命名',body_value='请输入新的文件名',init_value=tmp_file_name) # 有bug，不能输入#号
        #
        if res is not None:
            try:
                tmp_new_name='/'.join(split_path(tmp_full_path)[0:-1]+[res])
                print('tmp_new_name=')
                print(tmp_new_name)
                # os.rename(tmp_full_path,tmp_new_name)
                final_name = exec_safe_rename(tmp_full_path,tmp_new_name)
                exec_main_window_reload(1)
                exec_tree_find(final_name)
            except:
                t=tk.messagebox.showerror(title = 'ERROR',message='重命名失败！文件可能被占用，或者您没有操作权限。')
                # print(t)
                pass

def exec_tree_file_delete(tar=None):
    '''
    删除tree选中项对应的文件。
    兼容多文件，但是每个文件要确认一次，可能体验不太好。
    '''
    for item in tree.selection():
        # 获取文件全路径
        item_text = tree.item(item, "values")
        tmp_full_path = item_text[-1]
        # 再次确认
        if not isfile(tmp_full_path):
            print('并不存在文件：'+str(tmp_full_path))  
        elif tk.messagebox.askokcancel("删除确认", "真的要删除以下文件吗（不放进回收站）？"+str(tmp_full_path)):
            try:
                # os.remove(tmp_full_path)
                remove_to_trash(tmp_full_path)
                exec_main_window_reload(1)
            except:
                t=tk.messagebox.showerror(title = 'ERROR',message='删除失败，文件可能被占用！')
                print('删除失败，文件可能被占用')
            # 刷新
    
    pass

def exec_fun_test(event=None): # 
    ''' 
    用于调试一些测试性的功能，
    为了避免 event 输入，所以套了一层。

    '''
    res=my_input_window(window,'输入框','aaaa','外部输入')
    print('自制输入框的返回值：')
    print(res)
    # print('进入测试功能')

    pass

def exec_tree_find(full_path=''): # 
    '''
    用于在 tree 里面找到项目，并加高亮。
    输入参数是完整路径。
    只支持单文件查找。
    '''
    if full_path=='':
        return(-1)
        
    # 根据完整路径，找到对应的文件并高亮
    tree.update() # 必须在定位之前刷新列表，否则定位会错误
    tc=tree.get_children()
    tc_cnt=len(tc)
    print('条目数量为：%s' % tc_cnt)
    n=0
    print('开始查找')
    (b1,b2)=bar_tree_v.get()
    b0=b2-b1
    # b0=0
    print('b0=')
    print(b0)
    for i in tc:
        tmp=tree.item(i,"values")
        # print(tmp[-1])
        if tmp[-1]==full_path:
            # tree.focus(i) #这个并不能高亮
            tree.selection_set(i)
            print('在第%d处检查到了相应结果' % n)

            b1=n/tc_cnt-0.5*b0
            b2=n/tc_cnt+0.5*b0
            print((b0,b1,b2))
            if b1<0:
                b1=0
                b2=b0
            elif b2>1:
                b2=1
                b1=1-b0
            print((b1,b2))
            # bar_tree_v.set(b1,b2)
            tree.yview_moveto(b1)
            return(n)
            break
        else:
            n+=1
    print('居然没找到：')
    print(full_path)
    return(-1)
    # for i in range()
    

def tree_open_folder(event=None,VMETHOD=1): 
    '''
    打开当前文件所在的目录.
    参数VMETHOD=1（默认）是打开文件夹，
    =2 是打开文件夹并选中文件（有点慢）。
    不需要传入路径参数，本函数会自动从tree里面读取。
    '''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_file=item_text[-1]
        tmp_file=tmp_file.replace('/','\\')
        
        tmp_folder='/'.join(split_path(tmp_file)[0:-1])
        # tmp_folder=item_text[-2]
        
        print(tmp_folder)
        if VMETHOD==1: # 打开文件夹
            os.startfile(tmp_folder) #打开这个文件
        elif VMETHOD==2:  # 打开文件夹并选中文件。
            tmp=r'explorer /select, '+tmp_file
            print(tmp)
            os.system(tmp) # 性能极差，不知道哪的原因
            # os.system(r'explorer /select,d:\tmp\b.txt') # 这是打开文件夹并选中文件的方法
        
    pass
def tree_open_folder_select(event=None):
    tree_open_folder(VMETHOD=2)

def tree_open_current_folder(event=None):
    '''
    没有选中文件的时候，打开当前文件夹。
    支持打开子文件夹。
    '''
    if len(get_sub_folder())>0:
        tmp_path=lst_my_path_long_selected[0]+'/'+get_sub_folder()
    else:
        tmp_path=lst_my_path_long_selected[0]
    os.startfile(tmp_path)

def exec_folder_add_from_sub(event=None):
    '''
    通过子文件夹的方式添加关注文件夹
    '''
    try:
        if len(get_sub_folder())>0:
            tmp_path=lst_my_path_long_selected[0]+'/'+get_sub_folder()
            exec_my_folder_add([tmp_path])
    except:
        print('请检查1536')


def input_new_tag(event=None,tag_name=None):
    '''
    输入新的标签
    '''
    # new_name=''
    if tag_name is None:
        new_tag=v_inp.get()
        new_tag=str(new_tag).strip()
    else:
        new_tag=tag_name

    if new_tag is None or new_tag == '':
        print("取消新标签")
        return

    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        # tmp_file_name = get_file_part(tmp_full_name)['ffname'] # 没有用到
        
        # new_tag = tk.simpledialog.askstring(title="添加标签", prompt="请输入新的标签")#, initialvalue=tmp)
        
        if new_tag == None or new_tag == '':
            print("取消新标签")
        else:
            exec_file_add_tag(tmp_full_name,new_tag)
            # print(new_name)

def exec_input_new_tag_via_dialog(event=None):
    '''
    以输入框的方式添加标签。

    '''
    # 没有选中项的时候，直接跳过
    if len(tree.selection())!=1:
        return

    new_tag=show_input_window('添加标签','请输入标签','')
    if new_tag is None:
        return
    try:
        new_tag=str(new_tag).strip()
    except:
        pass
    input_new_tag(tag_name=new_tag)

def exec_file_add_tag(filename,tag0):    
    '''
    增加标签
    '''
    tag_list=tag0.split(V_SEP)
    tag_old = get_file_part(filename)['ftags'] #已有标签
    file_old = get_file_part(filename)['ffname'] #原始的文件名
    path_old = get_file_part(filename)['fpath'] #路径
    [fname,fename]=os.path.splitext(file_old) #文件名前半部分，扩展名
    
    old_n=path_old+ '/' +fname+fename
    new_n=old_n
    for i in tag_list:
        if not i in tag_old:
            new_n=path_old+os.sep+fname + V_SEP + i + fename
            print(old_n)
            print(new_n)
            try:
                # os.rename(old_n,new_n)
                tmp_final_name=exec_safe_rename(old_n,new_n)
                old_n=new_n #多标签时避免重命名错误
            except:
                t=tk.messagebox.showerror(title = 'ERROR',message='为文件添加标签失败！')
                print('为文件添加标签失败')
                pass
    exec_main_window_reload(1) # 此处可以优化，避免完全重载
    try:
        tmp_final_name=tmp_final_name.replace('\\','/')
        print('添加标签完成，正在定位%s' %(tmp_final_name))
        exec_tree_find(tmp_final_name) # 为加标签之后的项目高亮
    except:
        pass

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
    TAG_STAR=tag
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
    exec_file_add_tag(tmp_full_name,TAG_STAR)

def exec_clear_entry(tar):
    '''
    将输入框清空。
    必须要指定要清空的输入框对象。
    '''
    try:
        tar.delete(0,len(tar.get()))
    except:
        pass
    pass

def exec_main_window_reload(event=None,reload_setting=False): 
    '''
    刷新。
    切换目录之后自动执行此功能。
    
    输入参数0的话，保留子文件夹、搜索框、标签框。
    输入参数1，保留子文件夹、标签框，清除搜索框。推荐使用参数1；
    其余参数，清空子文件夹、标签框、搜索框。

    '''
    global lst_file,dT,lst_tags,lst_sub_path

    if reload_setting==True:
        # 按需加载设置参数
        get_json_file_data(load_folders=False)

    tmp_sub_folder=get_sub_folder()

    if event==0:
        pass
    elif event==1:
        '''
        保留子文件夹；
        保留标签；
        清空搜索框
        '''
        # tmp_sub_folder=get_sub_folder()
        exec_clear_entry(v_search)
    else:
        '''
        清空搜索框；
        标签留空；
        '''
        exec_clear_entry(v_search)
        v_tag.current(0)
        
        # v_inp.delete(0,len(v_inp.get()))
    # v_inp.delete(0,len(v_inp.get()))
    
    # exec_v_folder_choose(refresh=0)
    print('—— 刷新核心过程 start ———')
    #
    lst_file = get_data(lst_my_path_long_selected) 
    (dT, lst_tags)=gen_dt()
    #
    print('—— 刷新核心过程 end ———')
    # exec_tree_clear(tree)
    #
    # 恢复子文件夹选项（即将作废）
    if event==0 or event==1:
        try: # 用一种不太优雅，但是有效的方法修复了bug……
            if len(tmp_sub_folder)>0:
                tmp_n=lst_sub_path.index(tmp_sub_folder)
                v_sub_folders.current(tmp_n+1)
                print('子文件夹修复完毕')
        except:
            print('进入这个分支')
            v_sub_folders.current(0)
    
    exec_v_tag_choose() # 目的是？
    #
    v_tag['value']=lst_tags
    v_inp['value']=lst_tags

def show_my_help(event=None):
    '''
    提供帮助文件。
    目前的方式主要是跳转到在线帮助文件。以后考虑到内网打不开网页，需要增加一个离线的方面。
    '''
    os.startfile(URL_HELP)
    
def show_my_advice(event=None):
    '''
    在线反馈
    '''
    os.startfile(URL_ADV)
    
def show_main_closing():
    '''
    退出程序。
    '''
    if tk.messagebox.askokcancel("退出", "真的要退出吗"):
        window.destroy()
        

# 搜索框

def get_folder_s2l(folder_short_name):
    '''
    文件夹短路径转长路径。
    '''
    return dict_path[folder_short_name]
    pass



def exec_v_folder_choose(event=None,refresh=1,sub_folder=None): # 点击新的文件夹之后
    '''
    选择左侧文件夹后启动。
    '''
    global lst_my_path_long_selected,flag_running,flag_root_folder
    #
    flag_root_folder=1
    # if flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
        # return
    print('调用 exec_v_folder_choose 函数')
    if sub_folder is None:
        lst_path_ori=lst_my_path_long_selected.copy()
    else:
        lst_path_ori=[]
    
    tmp=get_folder_short()
    if tmp=='':
        lst_my_path_long_selected=lst_my_path_long.copy()
        # 设置按钮为无效
        bt_new.configure(state=tk.DISABLED)
        bt_folder_drop.configure(state=tk.DISABLED)
        v_sub_folders.current(0)
        v_sub_folders.configure(state=tk.DISABLED)

    elif sub_folder is not None:
        tmp=sub_folder
        lst_my_path_long_selected=[tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')
        pass
    else:
        tmp=get_folder_s2l(tmp) #将显示值转换为实际值
        lst_my_path_long_selected=[tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')
    
    if not lst_path_ori==lst_my_path_long_selected: # 如果前后的选项没有变化的话，就不刷新文件夹列表
        if refresh==1:
            # exec_main_window_reload(lst_my_path_long_selected)
            exec_main_window_reload(CLEAR_AFTER_CHANGE_FOLDER)
        tree.yview_moveto(0)
    
    # flag_running=0 # 标记为没有任务
    flag_root_folder=0
    print('exec_v_folder_choose 函数结束')

def exec_v_folder_choose_v2(event=None,refresh=1,sub_folder=None): # 点击新的文件夹之后
    '''
    选择左侧文件夹后启动。
    '''
    global lst_my_path_long_selected,flag_running,flag_root_folder
    #
    flag_root_folder=1
    # if flag_running: # 如果正在查，就先不启动新任务。这样处理还不理想。
        # return
    print('调用 exec_v_folder_choose 函数')
    if sub_folder is None:
        lst_path_ori=lst_my_path_long_selected.copy()
    else:
        lst_path_ori=[]
    
    tmp=get_folder_short()
    if tmp=='':
        lst_my_path_long_selected=lst_my_path_long.copy()
        # 设置按钮为无效
        bt_new.configure(state=tk.DISABLED)
        bt_folder_drop.configure(state=tk.DISABLED)
        v_sub_folders.current(0)
        v_sub_folders.configure(state=tk.DISABLED)

    elif sub_folder is not None:
        tmp=sub_folder
        lst_my_path_long_selected=[tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')
        pass
    else:
        tmp=get_folder_s2l(tmp) #将显示值转换为实际值
        lst_my_path_long_selected=[tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
        v_sub_folders.configure(state='readonly')
    
    if not lst_path_ori==lst_my_path_long_selected: # 如果前后的选项没有变化的话，就不刷新文件夹列表
        if refresh==1:
            # exec_main_window_reload(lst_my_path_long_selected)
            exec_main_window_reload(CLEAR_AFTER_CHANGE_FOLDER)
        tree.yview_moveto(0)
    
    # flag_running=0 # 标记为没有任务
    flag_root_folder=0
    print('exec_v_folder_choose 函数结束')

def v_sub_folder_choose(event=None):
    '''
    还没弄完。功能没有被启用。
    '''
    global lst_sub_path,lst_my_path_long_selected
    if get_sub_folder()=='':
        exec_v_folder_choose()

    print('sub处理前')
    print(lst_sub_path)
    print(lst_my_path_long_selected)
    tmp_lst_sub_path=lst_sub_path.copy()
    tmp_lst_my_path=lst_my_path_long_selected.copy()

    tmp_path=lst_my_path_long_selected[0]+'/'+get_sub_folder()
    tmp_folder=tmp_path
    
    exec_v_folder_choose(sub_folder=tmp_folder)
    lst_my_path_long_selected=tmp_lst_my_path.copy()
    tmp_lst_sub_path.sort()
    v_sub_folders['value']=['']+tmp_lst_sub_path # 强制修改子文件夹列表，但这样写不太好
    lst_sub_path=tmp_lst_sub_path.copy()
    print('sub处理后')
    print(lst_sub_path)
    print(lst_my_path_long_selected)
    # v_sub_folders.current(0)
    
def exec_v_tag_choose(event=None):
    '''
    选择标签之后、选择子文件夹后、输入搜索词按回车后触发。
    清空tree，并按照dT为tree增加行。
    '''
    # tmp_tag=get_search_items()
    exec_tree_clear(tree)
    # exec_add_tree_item(tree,dT,tag=tmp_tag)
    exec_add_tree_item(tree,dT)
    tree.update()

def v_sub_folders_choose(event=None):
    global flag_sub_folders_changed
    flag_sub_folders_changed=1
    exec_v_tag_choose()
    flag_sub_folders_changed=0


#%% 
def show_from_progres():
    #
    pass

def show_form_setting(): # 
    '''
    设置窗口
    ''' 
    global V_SEP,V_FOLDERS,NOTE_EXT,FILE_DRAG_MOVE
    global json_data

    def setting_yes(event=None):
        '''
        还没有功能
        '''
        # 获得新参数
        global V_SEP,V_FOLDERS,NOTE_EXT,FILE_DRAG_MOVE
        NOTE_EXT=v_inp_note_type.get()
        V_FOLDERS=v_inp_folder_depth.get()
        V_SEP=v_inp_sep.get()
        FILE_DRAG_MOVE=v_inp_drag_type.get()
        #
        # 保存到设置文件中
        set_json_options('sep',V_SEP)
        set_json_options('vfolders',V_FOLDERS)
        set_json_options('note_ext',NOTE_EXT)
        set_json_options('file_drag_enter',FILE_DRAG_MOVE)
        #
        # 关闭窗口
        form_setting.destroy()
        # 然后刷新文件列表
        exec_main_window_reload(None, reload_setting=True)
        pass

    form_setting=tk.Toplevel(window)
    form_setting.title('设置')
    form_setting.resizable(0,0) #限制尺寸
    form_setting.transient(window) # 避免在任务栏出现第二个窗口，而且可以实现置顶
    form_setting.grab_set()
    screenwidth = SCREEN_WIDTH
    screenheight = SCREEN_HEIGHT
    w_width = 400 #int(screenwidth*0.8)
    w_height = 260 #int(screenheight*0.8)
    x_pos=(screenwidth-w_width)/2
    y_pos=(screenheight-w_height)/2
    form_setting.geometry('%dx%d+%d+%d'%(w_width, w_height, x_pos, y_pos))
    form_setting.deiconify()
    form_setting.lift()
    form_setting.focus_force()
    form_setting.iconbitmap(LOGO_PATH) # 左上角图标
    # v2sep=tk.StringVar()
    # v2sep.set(V_SEP)

    # v2sep=V_SEP
    frame_setting2=ttk.Frame(form_setting,width=800)
    frame_setting2.pack(side=tk.BOTTOM,expand=0,fill=tk.X)
    frame_setting2.columnconfigure(0,weight=1)
    frame_setting2.columnconfigure(1,weight=1)

    frame_setting1=ttk.Frame(form_setting,height=800,width=800)
    frame_setting1.pack(expand=0,fill=tk.BOTH)
    
    
    # frame_setting2.grid_configure()
    
    lable_set_sep=tk.Label(frame_setting1, text = '标签分隔符')
    lable_set_sep.grid(row=0,column=0,padx=10, pady=5,sticky=tk.W)
    
    v_inp_sep=ttk.Entry(frame_setting1,width=16,text=V_SEP)
    exec_clear_entry(v_inp_sep)
    v_inp_sep.insert(0, V_SEP)
    v_inp_sep.grid(row=0,column=1 ,padx=10, pady=5,sticky=tk.EW)
    
    lable_set_folder_depth=tk.Label(frame_setting1, text = '识别为标签的文件夹层数')
    lable_set_folder_depth.grid(row=1,column=0,padx=10, pady=5,sticky=tk.W)
    
    v_inp_folder_depth=ttk.Combobox(frame_setting1,width=16)#,textvariable=v2fdepth)
    lst_folder_depth=['0','1','2','3','4','5','6','7','8']
    v_inp_folder_depth['values']=lst_folder_depth
    v_inp_folder_depth['state']='readonly'
    tmp_n=lst_folder_depth.index(str(V_FOLDERS))
    v_inp_folder_depth.current(tmp_n)
    v_inp_folder_depth.grid(row=1,column=1 ,padx=10, pady=5,sticky=tk.EW)

    # 笔记类型
    nr=2
    nr+=1
    lable_set_note_type=tk.Label(frame_setting1, text = '笔记类型')
    lable_set_note_type.grid(row=nr,column=0,padx=10, pady=5,sticky=tk.W)

    v_inp_note_type=ttk.Combobox(frame_setting1,width=16)#,textvariable=v2fdepth)
    v_inp_note_type['values']=NOTE_EXT_LIST
    v_inp_note_type['state']='readonly'
    v_inp_note_type.current(0)
    tmp_n=NOTE_EXT_LIST.index(NOTE_EXT)
    v_inp_note_type.current(tmp_n)
    v_inp_note_type.grid(row=nr,column=1 ,padx=10, pady=5,sticky=tk.EW)

    # 拖动是移动还是复制
    nr+=1
    lable_drag_type=tk.Label(frame_setting1, text = '拖拽添加文件的操作')
    lable_drag_type.grid(row=nr,column=0,padx=10, pady=5,sticky=tk.W)

    v_inp_drag_type=ttk.Combobox(frame_setting1,width=16)#,textvariable=v2fdepth)
    tmp_list=['move','copy']
    v_inp_drag_type['values']=tmp_list
    v_inp_drag_type['state']='readonly'
    v_inp_drag_type.current(0)
    tmp_n=tmp_list.index(FILE_DRAG_MOVE)
    v_inp_drag_type.current(tmp_n)
    v_inp_drag_type.grid(row=nr,column=1 ,padx=10, pady=5,sticky=tk.EW)

    # 下面的设置区域
    nr=10
    bt_setting_yes=ttk.Button(frame_setting2,text='确定',command=setting_yes)
    bt_setting_yes.grid(row=nr,column=0,padx=10, pady=5,sticky=tk.EW)
    # bt_setting_yes.pack(side=tk.LEFT,expand=0,fill=tk.X)
    
    bt_setting_cancel=ttk.Button(frame_setting2,text='取消',command=form_setting.destroy)
    bt_setting_cancel.grid(row=nr,column=1,padx=10, pady=5,sticky=tk.EW)
    # bt_setting_cancel.pack(side=tk.LEFT,expand=0,fill=tk.X)
    
    # window.wait_window(form_setting)


def exec_folder_add_click(event=None): # 
    '''
    通过点击的方式，添加新的目录
    '''
    res=filedialog.askdirectory()#选择目录，返回目录名
    res_lst=[res]
    print(res)
    if res=='':
        print('取消添加文件夹')
    else:
        exec_my_folder_add(res_lst)


def exec_folder_add_drag(files): # 
    '''
    通过拖拽的方式，添加目录。
    '''
    filenames=list() #可以得到文件路径编码, 可以看到实际上就是个列表。
    folders=[]
    # print(files)
    for item in files:
        item=item.decode('gbk') # 此处可能存在编码错误，而且，为啥要编码？？
        # item=item.replace('\xa0',' ').decode('gbk')
        if isdir(item):
            folders.append(item)
        elif isfile(item):
            filenames.append(item)
    if len(folders)>0:
        exec_my_folder_add(folders)



def exec_tree_drag_enter(files):
    '''
    以拖拽的方式将文件拖动到tree范围内，将执行复制命令。
    注意，不是移动，只是复制。
    safe_copy 的参数 opt_type = copy 是复制， = move 是移动。
    '''
    global flag_file_changed

    short_name=get_folder_short()
    print(short_name)
    if short_name=='':
        # print('未指定目标目录，取消复制')
        str_btm.set('未指定目标目录，取消复制')
        return
    else:
        if len(get_sub_folder())>0:
            long_name=lst_my_path_long_selected[0]+'/'+get_sub_folder()
        else:
            long_name=lst_my_path_long_selected[0]
        # long_name=get_folder_s2l(short_name) #将文件夹的显示值转换为实际值
        print('long_name=')
        print(long_name)
    
    tc=tree.get_children()
    k=len(tc)
    
    for item in files:
        item=item.decode('gbk')
        if not isfile(item):
            continue
        
        print(item)    
        # 先安全复制
        old_name = item
        [fpath,ffname]=os.path.split(old_name) # fpath 所在文件夹、ffname 原始文件名
        new_name = long_name + '/' + ffname
        if FILE_DRAG_MOVE in ['copy','move']:
            res=safe_copy(old_name, new_name, opt_type=FILE_DRAG_MOVE)
            str_btm.set('拖动添加文件成功')
        #     res=safe_move(old_name, new_name, opt_type='copy')
        #     str_btm.set('文件拖拽成功')
        print('res=')
        print(res)
        
        #再显示到列表中
        k+=1
        # tmp=get_file_part(res)
        # tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['full_path'])
        # tmp=tmp_v
        # tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        flag_file_changed=1
        
    # 刷新：
    if flag_file_changed:
        exec_main_window_reload(0) # 这里不刷新的话，后面排序或者筛选都会出错。
        # 高亮文件
        try:
            exec_tree_find(res)
            # tree.yview_moveto(1)
        except:
            pass
    


def exec_folder_refresh(ind=None): # 刷新左侧的文件夹列表
    # 更新json文件
    exec_update_json(data=json_data)
    get_json_file_data()
    # 更新左侧列表
    exec_update_folder_list()
    # 选中指定的文件夹
    tree_lst_folder.update()
    if ind is not None:
        # tree_lst_folder.selection_set(ind)
        tmp_lst_folder = tree_lst_folder.get_children()
        tree_lst_folder.selection_set(tmp_lst_folder[ind])
        pass
    # 更新正文
    exec_v_folder_choose()

def exec_my_folder_add(tar_list): 
    '''
    添加关注的目录,输入必须是列表。
    '''
    global json_data
    for tar in tar_list:
        if len(tar)>0: # 用于避免空白项目，虽然不知道哪里来的
            tar=str(tar).replace("\\",'/')
            tmp={"pth":tar}
            if not tmp in json_data['folders']: # 此处判断条件有漏洞，因为加入short参数之后就不对了
                json_data['folders'].append(tmp)
    # 刷新目录
    exec_folder_refresh()
    

def exec_folder_not_follow(): # 删除关注的目录
    '''
    取消关注选中的文件夹。
    没有输入输出。
    '''
    global json_data
    # 获取当前选中的文件夹
    short_name=get_folder_short()
    print(short_name)
    if short_name=='':
        pass
    else:
        long_name=get_folder_s2l(short_name) #将显示值转换为实际值
        print(long_name)
    # 增加确认
    if tk.messagebox.askokcancel("操作确认", "真的要取消关注选中的文件夹吗？\n该文件夹将从关注列表中移除，但其本身数据并不会受到影响。"):
        pass
    else:
        return
    # 在 json 里面找到对应项目并删除
    n=0
    for i in json_data['folders']:
        if i['pth']==long_name:
            json_data['folders'].pop(n)
            break
        n+=1
    # 刷新目录
    exec_folder_refresh()

def exec_folder_move_up(event=None,d='up'):
    '''
    文件夹列表上下移动，默认上移，参数可以为 'up' 或者 'down'。
    json_data['folders']是列表，
    每一项的'pth'是长路径。
    '''
    # 
    global json_data
    # 获取当前选中的文件夹
    short_name=get_folder_short()
    print(short_name)
    if short_name=='':
        pass
    else:
        long_name=get_folder_s2l(short_name) #将显示值转换为实际值
        print(long_name)
    # 在 json 里面找到对应项目，并交换顺序
    tar_lst=json_data['folders'] # 这个列表只包括文件夹，不包括“所有”。
    n=0
    min_pos=0 
    max_pos=len(tar_lst)-1
    #
    for i in tar_lst:
        n2=n-1 if d=='up' else n+1

        if i['pth']==long_name:
            # print('文件夹位置参数=')
            # print((n,n2,min_pos,max_pos))
            if n2<min_pos or n2>max_pos: # 目标序号超出
                print('不能按要求交换顺序')
                # t=tk.messagebox.showerror(title = 'ERROR',message='不能按要求交换顺序。')
                return
            else:
                tar_lst[n],tar_lst[n2]=tar_lst[n2],tar_lst[n]
                print('文件夹交换顺序成功')
                break
        n+=1
    # 刷新目录，测试逻辑正确
    if ALL_FOLDERS==1: # “所有文件夹” 在最前
        n2+=1
    else:
        pass
    exec_folder_refresh(n2) # 还需要选中目标文件夹
    pass

def exec_folder_move_down(event=None):
    '''
    向下移动
    '''
    exec_folder_move_up(d='down')

def exec_folder_open(tar=None): # 打开目录
    # 获得当前选中的长目录
    if len(lst_my_path_long_selected)!=1:
        pass
    else:
        try:
            os.startfile(lst_my_path_long_selected[0])
        except:
            pass

def set_local_data(): # 修改 json
    pass




def exec_create_note(event=None): # 添加笔记
    global lst_my_path_long_selected,NOTE_NAME,NOTE_EXT
    tags=['Tagdox笔记']
    
    if len(lst_my_path_long_selected)!=1:
        print('新建笔记功能锁定，暂不可用')
        return
    #
    # res = simpledialog.askstring('新建 Tagdox 笔记',prompt='请输入文件名',initialvalue =NOTE_NAME)
    res = show_input_window('新建 Tagdox 笔记',body_value='请输入文件名',init_value=NOTE_NAME)
    if res is not None:
        print('获得新笔记标题：')
        print(res)
        NOTE_NAME=res
        if len(tags)>0:
            stags=V_SEP+V_SEP.join(tags)
        else:
            stags=''
            
        if len(lst_my_path_long_selected)>1:
            pass
        
        if len(lst_my_path_long_selected)==1:
            pth=lst_my_path_long_selected[0]

            if not event=='exec_create_note_here':
                # 增加对子文件夹的判断逻辑。
                # 新建的位置正确，但是刷新之后找不到新笔记，而且子文件夹自动消失，体验不好。
                psub=get_sub_folder()
                if len(psub)>0:
                    pth=pth+'/'+psub

            print('即将在此新建笔记：')
            print(pth)
            if True:#pth in lst_my_path_long: # 后面这个判断有点多余
                fpth=pth+'/'+ NOTE_NAME + stags + NOTE_EXT 
                
                # 检查是否有这个文件
                i=0
                while isfile(fpth):
                    i+=1
                    fpth=pth+'/'+ NOTE_NAME +'('+str(i)+')'+ stags+ NOTE_EXT
                
                #创建文件
                print('创建文件：')
                print(fpth)
                if NOTE_EXT in NOTE_EXT_LIST:
                    with open(fpth,'w') as _:
                        pass
                elif NOTE_EXT in ['.docxXXXXX']:
                    # d=Document()
                    # d.save(fpth)
                    pass
                # 打开
                os.startfile(fpth) #打开这个文件
                #刷新
                if event=='exec_create_note_here': #【这里有bug，刷新之后不能显示内容】
                    exec_main_window_reload(1)
                    exec_tree_find(fpth)
                    # return fpth
                else:
                    exec_main_window_reload(1) # 没有这句话会搜不到
                    exec_tree_find(fpth)
                # else:
                #     return fpth
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
    tmp_path = '/'.join(split_path(tmp_full_name)[0:-1])
    print('当前路径')
    print(tmp_path)
    lst_tmp=lst_my_path_long_selected.copy()
    lst_my_path_long_selected=[tmp_path]
    
    fpth=exec_create_note('exec_create_note_here')
    lst_my_path_long_selected=lst_tmp.copy()
    
    if fpth is not None:
        exec_main_window_reload(1)
        exec_tree_find(fpth)
    pass



#%%
def jump_to_search(event=None):
    v_search.focus()
    
def jump_to_tag(event=None):
    v_inp.focus()

#%%
# 弹出菜单

def show_popup_menu_main(event):
    '''
    主菜单，点击设置按钮可以弹出。
    设置菜单的弹出
    '''
    menu_main = tk.Menu(window,tearoff=0)
    menu_main.add_command(label='参数设置',command=show_form_setting)
    menu_main.add_separator()
    # menu_main.add_command(label='使用说明')#,command=show_my_help)
    menu_main.add_command(label='在线帮助',command=show_my_help)
    menu_main.add_command(label='建议和反馈',command=show_my_advice)
    menu_main.add_command(label='关于',command=show_info_window)
    menu_main.add_separator()
    menu_main.add_command(label='退出',command=show_main_closing)
    #
    menu_main.post(event.x_root,event.y_root)


def show_popup_menu_folder(event):
    '''
    文件夹区域的右键菜单
    '''
    if len(lst_my_path_long_selected)!=1: # 如果没有选中项目的话
        menu_folder_no = tk.Menu(window,tearoff=0)
        menu_folder_no.add_command(label="打开所选文件夹",state=tk.DISABLED,command=exec_folder_open)
        menu_folder_no.add_separator()
        menu_folder_no.add_command(label="添加关注文件夹…",command=exec_folder_add_click)
        menu_folder_no.add_command(label="取消关注所选文件夹",state=tk.DISABLED,command=exec_folder_not_follow)
        menu_folder_no.post(event.x_root,event.y_root)
    else:
        menu_folder = tk.Menu(window,tearoff=0)
        menu_folder.add_command(label="打开所选文件夹",command=exec_folder_open)
        menu_folder.add_separator()
        menu_folder.add_command(label="向上移动",command=exec_folder_move_up)
        menu_folder.add_command(label="向下移动",command=exec_folder_move_down)
        menu_folder.add_separator()
        menu_folder.add_command(label="添加关注文件夹…",command=exec_folder_add_click)
        menu_folder.add_command(label="取消关注所选文件夹",command=exec_folder_not_follow)
        menu_folder.post(event.x_root,event.y_root)

def show_popup_menu_sub_folder(event):
    '''
    子文件夹区域的右键菜单
    '''
    if True:
        menu_sub_folder = tk.Menu(window,tearoff=0)
        menu_sub_folder.add_command(label='打开当前文件夹',command=tree_open_current_folder)
        if len(get_sub_folder())>0:
            menu_sub_folder.add_command(label='将当前文件夹添加到关注',command=exec_folder_add_from_sub)
        else:
            menu_sub_folder.add_command(label='将当前文件夹添加到关注',state=tk.DISABLED)
        menu_sub_folder.add_separator()
        menu_sub_folder.add_command(label='新建文件夹',state=tk.DISABLED,command=tree_open_current_folder)
        if len(get_sub_folder())>0:
            menu_sub_folder.add_command(label='重命名文件夹',state=tk.DISABLED,command=tree_open_current_folder)
        else:
            menu_sub_folder.add_command(label='重命名文件夹',state=tk.DISABLED)
        menu_sub_folder.add_separator()
        menu_sub_folder.add_command(label='刷新',command=exec_main_window_reload)
        #
        menu_sub_folder.post(event.x_root,event.y_root)

def exec_file_drop_tag(event=None): 
    '''
    删除标签，以后将#号换成SEP
    '''
    if event is None:
        return
    tag_value=event
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
    #
    res=get_file_part(tmp_full_name)
    file_path=res['f_path_only']
    file_name_ori=res['filename_origional']
    file_ext=res['fename']
    if file_ext=='':
        print(file_name_ori)
        tmp_rv=list(file_name_ori)
        tmp_rv.reverse()
        tmp_rv=''.join(tmp_rv)
        print(tmp_rv)
        #
        tmp_r_tag=list(V_SEP + tag_value)
        tmp_r_tag.reverse()
        tmp_r_tag=''.join(tmp_r_tag)
        print(tmp_r_tag)
        #
        tmp_rv=tmp_rv.replace(tmp_r_tag,'',1)
        #
        tmp_rv=list(tmp_rv)
        tmp_rv.reverse()
        tmp_rv=''.join(tmp_rv)
        #
        file_name_ori=tmp_rv
        print('从右向左替换')
        print(file_name_ori)
    new_name=file_name_ori.replace(V_SEP + tag_value + V_SEP,V_SEP)
    new_name=new_name.replace(V_SEP + tag_value+'.',".")

    new_full_name=file_path+'/'+new_name
    print('原始文件名：')
    print(tmp_full_name)
    print('去掉标签后：')
    print(new_full_name)
    print('被去掉的标签：')
    print(tag_value)
    # os.rename(tmp_full_name,new_full_name)
    tmp_final_name=exec_safe_rename(tmp_full_name,new_full_name)
    exec_main_window_reload(1) # 此处可以优化，避免完全重载
    try:
        tmp_final_name=tmp_final_name.replace('\\','/')
        print('删除标签完成，正在定位%s' %(tmp_final_name))
        exec_tree_find(tmp_final_name) # 为加标签之后的项目高亮
    except:
        pass

def show_popup_menu_file(event):

    '''
    文件区域的右键菜单
    '''
    menu_tags_to_drop = tk.Menu(window,tearoff=0)
    menu_tags_to_add = tk.Menu(window,tearoff=0)
    if len(QUICK_TAGS)>0:
        for i in QUICK_TAGS:
            menu_tags_to_add.add_command(label=i,command=lambda x=i:exec_fast_add_tag(x))
        menu_tags_to_add.add_separator()
    menu_tags_to_add.add_command(label='自定义标签…',command=exec_input_new_tag_via_dialog)
    #
    menu_file = tk.Menu(window,tearoff=0)
    menu_file.add_command(label="打开文件",command=exec_tree_file_open,accelerator='Enter')
    # menu_file.add_command(label="在相同位置创建笔记",command=exec_create_note_here)
    menu_file.add_separator()
    if len(lst_my_path_long_selected)==1:
        menu_file.add_command(label="新建笔记",command=exec_create_note,accelerator='Ctrl+N')
    else:
        menu_file.add_command(label="新建笔记",state=tk.DISABLED,command=exec_create_note,accelerator='Ctrl+N')
    menu_file.add_separator()
    menu_file.add_command(label="打开选中项所在文件夹",command=tree_open_folder)
    # menu_file.add_command(label="打开选中项所在文件夹并选中文件（有点慢）",command=tree_open_folder_select)
    menu_file.add_command(label="打开当前文件夹",command=tree_open_current_folder)
    menu_file.add_separator()
    menu_file.add_command(label='添加标签 ',command=exec_input_new_tag_via_dialog,accelerator='Ctrl+T')
    menu_file.add_cascade(label="快速添加标签",menu=menu_tags_to_add)
    menu_file.add_cascade(label="移除标签",menu=menu_tags_to_drop)
    menu_file.add_separator()
    # menu_file.add_command(label="发送无标签副本到桌面（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    # menu_file.add_command(label="复制到剪切板（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    # menu_file.add_command(label="移动到文件夹（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    # menu_file.add_command(label="粘贴（开发中）",state=tk.DISABLED)#,command=exec_file_rename)
    menu_file.add_command(label="重命名",command=exec_file_rename,accelerator='F2')
    menu_file.add_command(label="删除",command=exec_tree_file_delete)
    menu_file.add_separator()
    menu_file.add_command(label="刷新",command=exec_main_window_reload)



    menu_file_no_selection = tk.Menu(window,tearoff=0)
    # menu_file_no_selection.add_command(label="打开文件",state=tk.DISABLED,command=exec_tree_file_open)
    menu_file_no_selection.add_command(label="打开当前文件夹",command=tree_open_current_folder)
    menu_file_no_selection.add_separator()
    if len(lst_my_path_long_selected)==1:
        menu_file_no_selection.add_command(label="新建笔记",command=exec_create_note,accelerator='Ctrl+N')
    else:
        menu_file_no_selection.add_command(label="新建笔记",state=tk.DISABLED,command=exec_create_note,accelerator='Ctrl+N')
    # menu_file_no_selection.add_command(label="重命名",state=tk.DISABLED)#,command=exec_folder_add_click)
    # menu_file_no_selection.add_command(label="添加收藏",state=tk.DISABLED)#,command=exec_folder_add_click)
    menu_file_no_selection.add_separator()
    menu_file_no_selection.add_command(label="刷新",command=exec_main_window_reload)


    tmp=0
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        tmp+=1
    if tmp>0: # 如果有选中项目的话，
        # tmp_file_name=split_path(tmp_full_name)[-1]
        tmp_file_name=get_file_part(tmp_full_name)['fname']
        tmp_tags_all=get_file_part(tmp_full_name)['ftags']
        tmp_tags=tmp_file_name.split(V_SEP)
        # print(tmp_res)
        tmp_tags.pop(0)
        try:
            for i in range(10000): #删除已有标签
                menu_tags_to_drop.delete(0)
        except:
            pass

        if len(tmp_tags_all)>0:
            if len(tmp_tags)==0:
                pass
            else:
                # menu_tags_to_drop.add_separator()
                for i in tmp_tags:
                    menu_tags_to_drop.add_command(label=i,command=lambda x=i:exec_file_drop_tag(x))
                    
            if len(tmp_tags_all)>len(tmp_tags):
                if len(tmp_tags)>0:
                    menu_tags_to_drop.add_separator()
                menu_tags_to_drop.add_command(label='以下标签来自文件路径，不可直接删除',state=tk.DISABLED)
                
            for i in tmp_tags_all:
                if not i in tmp_tags:
                    menu_tags_to_drop.add_command(label=i,state=tk.DISABLED)

        else:    
            menu_tags_to_drop.add_command(label='无可操作项目',state=tk.DISABLED)
            pass
        
        menu_file.post(event.x_root,event.y_root)
    else:
        menu_file_no_selection.post(event.x_root,event.y_root)

#%%
class main_app:
    def __init__(self) -> None:
        pass

if __name__=='__main__':
# if True:
    q=queue.Queue()
    #变量
    
    lst_file=[] # 所有文件的完整路径
    dT=[]
    lst_tags=[] # 全部标签
    lst_my_path_long=[] # json里面，要扫描的文件夹列表
    lst_my_path_short=[]
    lst_my_path_long_selected=[]
    lst_sub_path=[]
    dict_path=dict() # 用于列表简写和实际值
    #
    flag_inited=0 # 代表是否已经加载完成
    flag_break=0 # 代表是否中断查询
    flag_running=0 # 代表是否有正在运行的查询
    flag_root_folder=0
    flag_sub_folders_changed=0
    flag_file_changed=0

    #
    window = tk.Tk() # 主窗口
    #%%
    PIC_LST=[tk.PhotoImage(file="./src/龙猫.gif")]
    IMAGE_FOLDER= tk.PhotoImage(file='./src/在线帮助.png')
    # 通用函数
    try: # 调整清晰度
        # 放在这里，是为了兼容不能打开ctypes的计算机。
        from ctypes import windll
        #告诉操作系统使用程序自身的dpi适配
        windll.shcore.SetProcessDpiAwareness(1)
        #获取屏幕的缩放因子
        ScaleFactor=windll.shcore.GetScaleFactorForDevice(0) # 当前屏幕放大百分数（125）
        #设置程序缩放
        window.tk.call('tk', 'scaling', ScaleFactor/75)
        #
        SCREEN_WIDTH=window.winfo_screenwidth()*ScaleFactor/100 # 必须考虑分辨率导致的偏移
        SCREEN_HEIGHT=window.winfo_screenheight()*ScaleFactor/100 #
    except:
        SCREEN_WIDTH=window.winfo_screenwidth()
        SCREEN_HEIGHT=window.winfo_screenheight()
    #
    # 加载设置参数。
    json_data = OPT_DEFAULT # 用于后面处理的变量。
    get_json_file_data()

    str_btm=tk.StringVar() #最下面显示状态用的
    str_btm.set("加载中")
    prog=tk.DoubleVar() # 进度
    prog_win=''


    if ALL_FOLDERS==1: # 对应是否带有“所有文件夹”这个功能的开关
        lst_my_path_long_selected=lst_my_path_long.copy() # 用这个变量修复添加文件夹之后定位不准确的问题。
        lst_file = get_data(lst_my_path_long_selected)
    else:
        try:
            lst_my_path_long_selected=[lst_my_path_long[0]]
            lst_file = get_data(lst_my_path_long_selected)
        except:
            lst_file = get_data() # 此处有隐患，还没条件测试
        
    (dT, lst_tags)=gen_dt()


    # 窗体设计
    window.title(TAR+' '+VER)
    screenwidth = SCREEN_WIDTH
    screenheight = SCREEN_HEIGHT
    w_width = int(screenwidth*0.8)
    w_height = int(screenheight*0.8)
    x_pos=(screenwidth-w_width)/2
    y_pos=(screenheight-w_height)/2
    window.geometry('%dx%d+%d+%d'%(w_width, w_height, x_pos, y_pos))
    # window.resizable(0,0) #限制尺寸
    window.state('zoomed') # 最大化

    ####################################################################
    # 框架设计


    # 文件夹区
    frameLeft=ttk.Frame(window,width=int(w_width*0.4))#,width=600)
    frameLeft.pack(side=tk.LEFT,expand=0,fill=tk.Y,padx=0,pady=0)#padx=10,pady=5)
    # for i in range(2):
        # frameLeft.rowconfigure(i,weight=1)

    frameFolder=ttk.Frame(frameLeft,height=SCREEN_HEIGHT*0.8)#,width=600),width=int(w_width*0.4)
    frameFolder.pack(side=tk.TOP,expand=1,fill=tk.Y,padx=10,pady=5)#padx=10,pady=5)
    # frameFolder.grid(column=0,row=0)
    
    frameSubFolder=ttk.Frame(frameLeft)#,width=600)
    # frameSubFolder.grid(column=0,row=1)
    frameSubFolder.pack(side=tk.BOTTOM,expand=1,fill=tk.Y,padx=10,pady=5)#padx=10,pady=5)
    # 文件夹下面的控制区
    frameFolderCtl=ttk.Frame(frameLeft,height=10,borderwidth=0,relief=tk.FLAT)
    # frameFolderCtl.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=5)

    # 上面功能区
    frame0=ttk.LabelFrame(window,text='',height=80)#,width=600)
    frame0.pack(expand=0,fill=tk.X,padx=10,pady=5)

    # 主功能区
    frameMain=ttk.Frame(window)#,height=800)
    frameMain.pack(expand=1,fill=tk.BOTH,padx=10,pady=0)

    # 底部区
    frameBtm=ttk.LabelFrame(window,height=80)
    frameBtm.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=5)

    #%%
    v_sub_folders=ttk.Combobox(frame0) # 子文件夹选择框
    v_tag=ttk.Combobox(frame0) # 标签选择框
    v_search=ttk.Entry(frame0) # 搜索框
    v_folders=ttk.Combobox(frameFolder) # 文件夹选择框

    bar_tree_v=tk.Scrollbar(frameMain,width=16) #右侧滚动条
    bar_tree_h=tk.Scrollbar(frameMain,orient=tk.HORIZONTAL,width=16) #底部滚动条
    
    # ---

    #%%
    vPDX=10
    vPDY=5

    # bt_setting=ttk.Button(frameBtm,text='设置')#,command=show_form_setting)
    # bt_setting.pack(side=tk.LEFT,expand=0,padx=5,pady=10)#,fill=tk.X) # 

    bt_folder_add=ttk.Button(frameFolderCtl,text='添加文件夹') #state=tk.DISABLED,,command=setting_fun
    bt_folder_add.pack(side=tk.LEFT,expand=0,padx=20,pady=10,fill=tk.X) # 

    bt_folder_drop=ttk.Button(frameFolderCtl,text='移除文件夹') #state=tk.DISABLED,,command=setting_fun
    bt_folder_drop.pack(side=tk.RIGHT,expand=0,padx=20,pady=10,fill=tk.X) # 

    bar_folder_v=tk.Scrollbar(frameFolder,width=16)
    bar_folder_v.pack(side=tk.RIGHT, expand=0,fill=tk.Y)

    # 文件夹列表
    tree_lst_folder = ttk.Treeview(frameFolder,  
                                columns = ['folders'], 
                                # columns = ['index','type','folders','folder_path'], 
                                displaycolumns = ['folders'],
                                selectmode = tk.BROWSE, 
                                show = "headings",
                                # show="tree",
                                # cursor='hand2',
                                yscrollcommand = bar_folder_v.set)#, height=18)
    bar_folder_v.config( command = tree_lst_folder.yview )

    tree_lst_folder.heading("folders", text = "关注的文件夹",anchor='w')
    tree_lst_folder.column('folders', width=300, anchor='w')
    
    # 子文件夹列表
    bar_sub_folder_v=tk.Scrollbar(frameSubFolder,width=16)
    bar_sub_folder_v.pack(side=tk.RIGHT, expand=0,fill=tk.Y)

    tree_lst_sub_folder = ttk.Treeview(frameSubFolder,  
                                columns = ['folders'], 
                                # columns = ['index','type','folders','folder_path'], 
                                displaycolumns = ['folders'],
                                selectmode = tk.BROWSE, 
                                show = "headings",
                                # show="tree",
                                # cursor='hand2',
                                yscrollcommand = bar_sub_folder_v.set)#, height=18)
    

    tree_lst_sub_folder.heading("folders", text = "子文件夹",anchor='w')
    tree_lst_sub_folder.column('folders', width=300, anchor='w')
    bar_sub_folder_v.config( command = tree_lst_sub_folder.yview )

    # tree_lst_folder.insert(0,"（全部）")


    exec_update_folder_list()
    tree_lst_folder.pack(side=tk.LEFT,expand=0,fill=tk.BOTH,padx=0,pady=10)
    tree_lst_sub_folder.pack(side=tk.LEFT,expand=0,fill=tk.BOTH,padx=0,pady=10)


    columns = ("index","file", "tags", "modify_time","size","file0")

    tree = ttk.Treeview(frameMain, show = "headings", columns = columns, \
                        displaycolumns = ["file", "tags", "modify_time","size"], \
                        selectmode = tk.BROWSE, \
                        yscrollcommand = bar_tree_v.set,xscrollcommand = bar_tree_h.set)#, height=18)

    tree.column('index', width=30, anchor='center')
    tree.column('file', width=400, anchor='w')
    tree.column('tags', width=300, anchor='w')
    tree.column('modify_time', width=100, anchor='w')
    tree.column('size', width=80, anchor='w')
    tree.column('file0', width=80, anchor='w')

    tree.heading("index", text = "序号",anchor='center')
    tree.heading("file", text = "文件名",anchor='w',command=tree_order_filename)
    tree.heading("tags", text = "标签",anchor='w',command=tree_order_tag)
    tree.heading("modify_time", text = "修改时间",anchor='w',command=tree_order_modi_time)
    tree.heading("size", text = "文件大小(kB)",anchor='w',command=tree_order_size)
    tree.heading("file0", text = "完整路径",anchor='w',command=tree_order_path)
    # 增加排序方向的可视化
    tree_order_show()

    try:
        exec_add_tree_item(tree,dT)
    except:
        str_btm.set('已就绪')
        pass

    # 样式
    style = ttk.Style()
    style.configure("Treeview.Heading", font=('微软雅黑', MON_FONTSIZE), \
                    rowheight=int(MON_FONTSIZE*4),height=int(MON_FONTSIZE*4))
    # style.configure("Treeview.Heading", font=('Courier New', MON_FONTSIZE), \
                    # rowheight=int(MON_FONTSIZE*4),height=int(MON_FONTSIZE*4))
    style.configure("Treeview", font=(None, MON_FONTSIZE), rowheight=int(MON_FONTSIZE*3.5))

    # style.configure("Treeview.Heading", font=(None, 12),rowheight=60)
    # 行高
    # style.configure("Treeview.Heading", font=(None, 12))
    
    vPDX=10
    vPDY=5

    if True: # 子文件夹搜索
        lable_sub_folders=tk.Label(frame0, text = '子文件夹')
        # lable_sub_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

        v_sub_folders['value']=['']+lst_sub_path
        v_sub_folders['state'] = 'readonly'
        # v_sub_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
        v_sub_folders.bind('<<ComboboxSelected>>', v_sub_folders_choose)

    lable_tag=tk.Label(frame0, text = '标签')
    lable_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

    v_tag['value']=lst_tags
    v_tag['state'] = 'readonly' # 只读
    v_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
    v_tag.bind('<<ComboboxSelected>>', exec_v_tag_choose)
    v_tag.bind('<Return>',exec_v_tag_choose) #绑定回车键


    lable_search=tk.Label(frame0, text = '文件名')
    lable_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

    v_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
    v_search.bind('<Return>',exec_v_tag_choose) #绑定回车键

    bt_search=ttk.Button(frame0,text='搜索',command=exec_v_tag_choose)
    bt_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

    bt_clear=ttk.Button(frame0,text='清空',command=exec_main_window_reload)
    bt_clear.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

    bt_test=ttk.Button(frame0,text='测试功能',command=exec_fun_test)
    if DEVELOP_MODE:
        bt_test.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 



    # 布局
    bar_tree_h.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=2,pady=1) # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

    tree.pack(side=tk.LEFT,expand=1,fill=tk.BOTH,padx=2,pady=1)

    bar_tree_v.pack(side=tk.LEFT,expand=0,fill=tk.Y,padx=2,pady=1) # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

    vPDX=10
    vPDY=5

    # 进度条
    progressbar_file=ttk.Progressbar(frameBtm,variable=prog,mode='determinate')
    # progressbar_file.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY)

    lable_sum=tk.Label(frameBtm, text = str_btm,textvariable=str_btm)
    lable_sum.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 



    bt_settings=ttk.Button(frameBtm,text='菜单')#,command=show_my_help)
    bt_settings.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

    bt_reload=ttk.Button(frameBtm,text='刷新',command=exec_main_window_reload)
    bt_reload.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

    bt_new=ttk.Button(frameBtm,text='新建笔记')#,state=tk.DISABLED)#,command=exec_main_window_reload)
    bt_new.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

    bt_add_tag=ttk.Button(frameBtm,text='添加标签',command=input_new_tag)
    bt_add_tag.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

    # 新标签的输入框
    v_inp=ttk.Combobox(frameBtm,width=16) 
    v_inp.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 
    v_inp.bind('<Return>',input_new_tag)
    v_inp['value']=lst_tags

    lable_tag=tk.Label(frameBtm, text = '添加新标签')
    lable_tag.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

    # 设置拖拽反映函数
    windnd.hook_dropfiles(tree_lst_folder, func=exec_folder_add_drag)
    windnd.hook_dropfiles(tree, func=exec_tree_drag_enter)
                
    bt_new.configure(command=exec_create_note)

    # 其他初始化设定
    if ALL_FOLDERS==1:
        bt_folder_drop.configure(state=tk.DISABLED)

    # 各种功能的绑定
    # tree_lst_folder.bind('<<ListboxSelect>>',exec_v_folder_choose)
    # tree_lst_folder.bind('<Button-1>',exec_v_folder_choose)
    tree_lst_folder.bind('<ButtonRelease-1>',exec_v_folder_choose)
    # tree_lst_sub_folder.bind('<<TreeviewSelect>>', v_sub_folders_choose)
    tree_lst_sub_folder.bind('<ButtonRelease-1>', v_sub_folders_choose)
    tree.tag_configure('line1', background='#cccccc') # 灰色底纹,然而无效
    tree.bind('<Double-Button-1>', exec_tree_file_open)
    tree.bind('<Return>', exec_tree_file_open)
    # tree.bind('<ButtonPress-3>', input_newname) # 右键，此功能作废
    tree_lst_folder.bind("<Button-3>",show_popup_menu_folder) # 绑定文件夹区域的右键功能
    tree_lst_sub_folder.bind("<Button-3>",show_popup_menu_sub_folder) # 绑定文件夹区域的右键功能
    bt_settings.bind("<Button-1>",show_popup_menu_main) # 菜单按钮
    tree.bind("<Button-3>",show_popup_menu_file) # 绑定文件夹区域的功能

    # 程序内快捷键
    window.bind_all('<Control-n>',exec_create_note) # 绑定添加笔记的功能。
    window.bind_all('<Control-f>',jump_to_search) # 跳转到搜索框。
    window.bind_all('<F2>',exec_file_rename) # 跳转到搜索框。
    # window.bind_all('<Control-t>',jump_to_tag) # 跳转到标签框。
    window.bind_all('<Control-t>',exec_input_new_tag_via_dialog) # 快速输入标签。

    # 功能绑定
    # bt_setting.configure(command=show_form_setting) # 功能绑定
    bt_folder_add.configure(command=exec_folder_add_click) # 功能绑定
    bt_folder_drop.configure(command=exec_folder_not_follow) # 功能绑定

    bar_tree_v.config( command = tree.yview )
    bar_tree_h.config( command = tree.xview )
    # tree.pack(expand = True, fill = tk.BOTH)

    # 运行

    window.iconbitmap(LOGO_PATH) # 左上角图标
    flag_inited=1 # 代表前面的部分已经运行过一次了
    set_prog_bar(0)
    exec_update_sub_folder_list(lst_sub_path)
    # bt_add_tag.pack_forget()
    window.mainloop() 
