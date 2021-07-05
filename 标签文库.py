# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""

import os
import tkinter as tk
from tkinter import Text, ttk
import json
from tkinter import filedialog
from tkinter import simpledialog
from tkinter.constants import INSERT
import windnd
from os.path import isdir
from os.path import isfile
import time
# import threading # 多线程
# from docx import Document# 用于创建word文档
# import ctypes # 用于调整分辨率
from ctypes import windll
import shutil

URL_HELP='https://gitee.com/horse_sword/my-local-library' # 帮助的超链接，目前是 gitee 主页
URL_ADV='https://gitee.com/horse_sword/my-local-library/issues' # 提建议的位置
TAR='Tagdox / 标签文库' # 程序名称
VER='v0.9.5.4' # 版本号
# v0.9.5.0 增加进度条显示；优化加载效率；优化排序加载算法，缩短排序时间。
# v0.9.5.1 增加拖拽文件直接复制到文件夹内的功能，便于处理微信文件或其他需要复制的业务。
# v0.9.5.2 增加主菜单功能。
# v0.9.5.3 增加关于功能。
# v0.9.5.4 增加设置菜单；调整分隔符的潜在兼容性错误。

#%%
#常量，但以后可以做到设置里面
cALL_FILES=''                       # 标签为空的表达方式，默认是空字符串
LARGE_FONT=12                       # 表头字号
MON_FONTSIZE=10                     # 正文字号
ORDER_BY_N=1                        # 初始按哪一列排序，1代表标签，后面按顺序对应
ORDER_DESC=False                    # 是否逆序
CLEAR_AFTER_CHANGE_FOLDER=0         # 切换文件夹后，是否清除筛选。0 是保留，其他是清除。
EXP_FOLDERS=['_img']                # 排除文件夹规则，以后会加到自定义里面
ALL_FOLDERS=2                       # 是否有“所有文件夹”的功能,1 在前面，2在末尾，其余没有
PROG_STEP=500                       # 进度条刷新参数
NOTE_NAME='未命名'                  # 新建笔记的名称
NOTE_EXT='.docx'                    # 新建笔记的类型
NOTE_EXT_LIST=['.md','.txt','.docx','.rtf']
if isfile('D:/MyPython/开发数据/options_for_tagdox.json'):
    print('进入开发模式')
    OPTIONS_FILE='D:/MyPython/开发数据/options_for_tagdox.json'
else:
    print('正式模式')
    OPTIONS_FILE='options_for_tagdox.json'         # 配置文件的名称
V_SEP='#'
V_FOLDERS=2
OPT_DEFAULT={
	"options":{
		"sep":"#",
		"vfolders":"2",
		"note_ext":".docx",
		"tar":[
		]
	}
 }
json_data = OPT_DEFAULT # 用于后面处理的变量。
QUICK_TAGS=['@PIN','@TODO','@toRead','@Done'] #

#变量
lst_file=[] # 所有文件的完整路径
dT=[]
lst_tags=[] # 全部标签
lst_my_path0=[] # json里面，要扫描的文件夹列表
lst_my_path_s=[]
lst_my_path=[]
dict_path=dict() # 用于列表简写和实际值
run_flag=0 # 

window = tk.Tk() # 主窗口
str_btm=tk.StringVar() #最下面显示状态用的
str_btm.set("加载中")
#%%

# 通用函数
if True: # 调整清晰度
    #告诉操作系统使用程序自身的dpi适配
    windll.shcore.SetProcessDpiAwareness(1)
    #获取屏幕的缩放因子
    ScaleFactor=windll.shcore.GetScaleFactorForDevice(0)
    #设置程序缩放
    window.tk.call('tk', 'scaling', ScaleFactor/75)

def split_path(full_path): 
    '''
    通用函数：    
    将完整路径拆分，得到每个文件夹到文件名的列表。
    '''
    test_str=full_path.replace('\\', '/',-1)
    test_str_res=test_str.split('/')
    return(test_str_res)

def tree_clear(tree_obj): # 
    '''
    通用的 treeview 清除函数，因为是通用的，所以必须带参数。
    参数是 具体的 treeview 对象。
    '''
    x=tree_obj.get_children()
    for item in x:
        tree_obj.delete(item)
    if run_flag==1:
        window.update()

def safe_get_name(new_name):
    '''

    输入目标全路径，返回安全的新路径（可用于重命名、新建等）


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

def safe_rename(old_name,new_name):
    '''
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 是添加数字之后的最终文件名。
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

def safe_copy(old_name,new_name):
    '''
    安全复制
    '''
    old_name=old_name.replace('\\','/')
    new_name=new_name.replace('\\','/')
    tmp_new_full_name=safe_get_name(new_name)
    print('开始安全复制')
    print(old_name)
    print(tmp_new_full_name)
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

#%%
# 加载设置项 json 内容。保存到 opt_data 变量中，这是个 dict。


def update_json(tar=OPTIONS_FILE,data=json_data): 
    '''
    将 json_data变量的值，写入 json 文件。
    可以不带参数，随时调用就是写入json。
    '''
    with open(tar,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False)

def set_json_options(key1,value1):
    global json_data
    opt_data=json_data['options']   #设置
    opt_data[key1]=value1
    update_json(data=json_data)
    # load_json_data()
    pass

def load_json_data():
    '''
    读取json文件，获取其中的参数，并存储到相应的变量中。

    如果json文件读取失败，则按照初始化标准重建这个文件。

    依赖函数：update_json。
    '''
    global json_data
    global V_SEP
    global V_FOLDERS
    global NOTE_EXT
    global lst_my_path0
    global lst_my_path_s
    global lst_my_path
    
    need_init_json=0
    try:
        with open(OPTIONS_FILE,'r',encoding='utf8')as fp:
            json_data = json.load(fp)
            
        opt_data=json_data['options']   #设置
        V_SEP=opt_data['sep'] # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
        V_FOLDERS=int(opt_data['vfolders']) # 目录最末层数名称检查，作为标签的检查层数
        NOTE_EXT=opt_data['note_ext'] # 默认笔记类型
            
        # lst_my_path=lst_my_path0.copy() #按文件夹筛选用
        lst_my_path0=[]
        lst_my_path_s=[]
        
        print('加载基本参数成功')

        for i in opt_data['tar']: 
            # lst_my_path0.append(i)
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
            while tmp_2 in lst_my_path_s:
                j+=1
                tmp_2=tmp_S+"("+str(j)+")"
                print(tmp_2)
            tmp_S=tmp_2
            tmp_S=tmp_S.strip()
            
            if tmp_S=='' or tmp_L=='': # 出现空白文件夹
                for j in range(len(opt_data['tar'])-1,-1,-1):
                    if opt_data['tar'][j]['pth'].strip()=='':    
                        opt_data['tar'].pop(j)
            else:
                lst_my_path0.append(tmp_L)
                lst_my_path_s.append(tmp_S)
                tmp={tmp_S:tmp_L}
                dict_path.update(tmp)
        
        lst_my_path=lst_my_path0.copy() # 此处有大量的可优化空间。
    except:
        print('加载json异常，正在重置json文件')
        # need_init_json=1
        json_data = OPT_DEFAULT
        update_json()
        
load_json_data()

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
prog=tk.DoubleVar() # 进度
def set_prog_bar(inp,maxv=100):
    prog.set(inp)
    # progressbar_file.stop()
    # progressbar_file.start()
    # if maxv<=inp:
    #     progressbar_file.stop()
    progressbar_file.update()

def get_data(ipath=lst_my_path0): 
    '''
    根据所选中的文件夹，
    返回 lst_file 列表。
    这个参数可以在 get_dT 里面调用。
    此过程消耗时间较多。
    '''
    
    if run_flag==1:
        tree_clear(tree)
        set_prog_bar(0,30)
        str_btm.set("正在加载基础数据……")
        window.update()
        
    
    time0=time.time()
    lst_file=list() #获取所有文件的完整路径
    
    n=1
    n_max=len(ipath)
    
    for vPath in ipath:
        n+=1
        if run_flag==1 and n % PROG_STEP == 0:
            set_prog_bar(30*n/n_max)
            
        for root, dirs, files in os.walk(vPath):
            
            tmp=[]
            vpass=0
            
            tmp_path=split_path(root)
            for tmp2 in tmp_path:
                if tmp2 in EXP_FOLDERS:
                    vpass=1
                elif tmp2[0]=='.': # 排除.开头的文件夹内容
                    vpass=1
                
            for name in files:
                tmp.append(os.path.join(root, name))
                if name=='_nomedia':
                    vpass=1
                    
            if not vpass==1:
                lst_file+=tmp 
    print('加载 lst_file 消耗时间：')
    print(time.time()-time0)
    # if run_flag==1:
    #     set_prog_bar(30,30)
    return lst_file

def get_file_part(tar):     # 
    '''
    这里输入参数 tar 是完整路径。
    输入完整（文件）路径，以字典的形式，返回对应的所有文件信息。
    '''
    [fpath,ffname]=os.path.split(tar) # fpath 所在文件夹、ffname 原始文件名
    [fname,fename]=os.path.splitext(ffname) # fname 文件名前半部分，fename 扩展名
    lst_sp=fname.split(V_SEP) #拆分为多个片段
    fname_0 = lst_sp[0]+fename # fname_0 去掉标签之后的文件名
    ftags=lst_sp[1:] # ftags 标签部分
    
    mtime = os.stat(tar).st_mtime
    file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    
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
            'tar':tar,
            'file_full_path':tar, # 完整路径，和输入参数完全一样
            'file_mdf_time':file_modify_time}
    
def sort_by_tag(elem): # 主题表格排序
    global ORDER_BY_N
    return str(elem[ORDER_BY_N])

def get_dt():
    '''
    是最消耗时间的函数，也是获取数据的核心函数。
    数据来源的 lst_file 来自于 get_data() 函数，提供了所有文件。

    根据 lst_file 里面的文件列表，返回 (dT, lst_tags) .
    无需输入参数，自动找变量。
    '''
    if run_flag==1:
        str_btm.set("正在解析标签……")
        window.update()
        set_prog_bar(30)
        
    time0=time.time()
    
    n=1
    n_max=len(lst_file)
    
    dT=list()    
    
    for tar in lst_file:
        
        # 更新进度条
        n+=1
        if run_flag==1 and n % PROG_STEP ==0:
            set_prog_bar(30+70*n/n_max)
        
        tmp=get_file_part(tar)
        # dT.append([tmp['fname_0'],tmp['ftags'],tmp['fpath'],tmp['tar']])
        # 增加检查重复项的逻辑：
        # tmp_v=[tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['tar']]
        tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['tar'])
        
        # if not tmp_v in dT:
        #     dT.append(tmp_v) # 查重有点费时间
        dT.append(tmp_v)
    print('加载dT消耗时间：')
    print(time.time()-time0)
    
    # 去重
    dT2=[]
    for i in dT:
        if not i in dT2:
            dT2.append(i)
    dT=dT2
    # dT=list(set(dT))
    
    
    if run_flag==1:
        set_prog_bar(0)
        
    # 获取所有tag
    tmp=[]
    for i in dT:
        tmp+=i[1]
    
    lst_tags=list(set(tmp))
    lst_tags=sorted(lst_tags, key=lambda x: x.encode('gbk'))
    lst_tags=[cALL_FILES]+lst_tags
    # lst_tags.sort()
    
    
    dT.sort(key=sort_by_tag,reverse=ORDER_DESC)
    
    return (dT, lst_tags)

if ALL_FOLDERS==1: # 对应是否带有“所有文件夹”这个功能的开关
    lst_my_path=lst_my_path0.copy() # 用这个变量修复添加文件夹之后定位不准确的问题。
    lst_file = get_data(lst_my_path)
else:
    try:
        lst_my_path=[lst_my_path0[0]]
        lst_file = get_data(lst_my_path)
    except:
        lst_file = get_data() # 此处有隐患，还没条件测试
    
(dT, lst_tags)=get_dt()


#%%

# 窗体设计

window.title(TAR+' '+VER)
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
w_width = int(screenwidth*0.8)
w_height = int(screenheight*0.8)
x_pos=(screenwidth-w_width)/2
y_pos=(screenheight-w_height)/2
window.geometry('%dx%d+%d+%d'%(w_width, w_height, x_pos, y_pos))
# window.resizable(0,0) #限制尺寸

#%%
def show_info_window():
    '''
    关于窗口
    '''
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    w_width = 600
    w_height = 500
    info_window=tk.Toplevel(window)
    info_window.geometry('%dx%d+%d+%d'%(w_width, w_height, (screenwidth-w_width)/2, (screenheight-w_height)/2))
    info_window.title('关于标签文库')
    info_window.deiconify()
    info_window.lift()
    info_window.focus_force()

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
def my_input_window(title='未命名',msg='未定义'):
    '''
    想要做输入框，替代系统自带的，但是并没有启用。
    '''
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    w_width = 500
    w_height = 100
    input_window=tk.Toplevel(window)
    input_window.geometry('%dx%d+%d+%d'%(w_width, w_height, (screenwidth-w_width)/2, (screenheight-w_height)/2))
    input_window.title(title)
    # input_window.withdraw()
    input_window.deiconify()
    input_window.lift()
    input_window.focus_force()

    iframe=tk.Frame(input_window,padx=5,pady=5)
    iframe.pack(expand=0,fill=tk.BOTH)
    
    lb=tk.Label(iframe,text=msg)
    lb.pack(anchor='sw')
    
    et=tk.Entry(iframe)
    et.pack(expand=0,fill=tk.X)
    
# my_input_window()
    
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

# 框架设计

# 文件夹区
frameFolder=ttk.Frame(window,width=int(w_width*0.4))#,width=600)
frameFolder.pack(side=tk.LEFT,expand=0,fill=tk.Y,padx=10,pady=10)

frameFolderCtl=ttk.Frame(frameFolder,height=50,borderwidth=0,relief=tk.FLAT)
frameFolderCtl.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=10)

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
v_tag=ttk.Combobox(frame0) # 标签选择框
v_search=ttk.Entry(frame0) # 标签选择框
v_folders=ttk.Combobox(frameFolder) # 文件夹选择框
bar1=tk.Scrollbar(frameMain,width=20) #右侧滚动条
bar2=tk.Scrollbar(frameMain,orient=tk.HORIZONTAL)#,width=20) #底部滚动条

#%%
vPDX=10
vPDY=5

# bt_setting=ttk.Button(frameBtm,text='设置')#,command=show_form_setting)
# bt_setting.pack(side=tk.LEFT,expand=0,padx=5,pady=10)#,fill=tk.X) # 

bt_folder_add=ttk.Button(frameFolderCtl,text='添加文件夹') #state=tk.DISABLED,,command=setting_fun
bt_folder_add.pack(side=tk.LEFT,expand=0,padx=20,pady=10,fill=tk.X) # 

bt_folder_drop=ttk.Button(frameFolderCtl,text='移除文件夹') #state=tk.DISABLED,,command=setting_fun
bt_folder_drop.pack(side=tk.RIGHT,expand=0,padx=20,pady=10,fill=tk.X) # 

bar_folder=tk.Scrollbar(frameFolder,width=20)
bar_folder.pack(side=tk.RIGHT, expand=0,fill=tk.Y)

tree_lst_folder = ttk.Treeview(frameFolder, show = "headings", columns = ['folders'], 
                             selectmode = tk.BROWSE, 
                             # cursor='hand2',
                             yscrollcommand = bar_folder.set)#, height=18)
bar_folder.config( command = tree_lst_folder.yview )

tree_lst_folder.heading("folders", text = "关注的文件夹",anchor='w')
tree_lst_folder.column('folders', width=300, anchor='w')

# tree_lst_folder.insert(0,"（全部）")
def update_folder_list():
    '''
    根据 lst_my_path_s，将文件夹列表刷新一次。
    没有输入输出。
    '''
    global tree_lst_folder
    tree_clear(tree_lst_folder)
    tmp=0
    if ALL_FOLDERS==1:
        tree_lst_folder.insert('',tmp,values=("（全部）"))
    for i in lst_my_path_s:
        tmp+=1
        print(i)
        tree_lst_folder.insert('',tmp,values=(str(i))) # 此处有bug，对存在空格的不可用
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

update_folder_list()
tree_lst_folder.pack(side=tk.LEFT,expand=0,fill=tk.BOTH)

def tree_order_base(inp):
    '''
    主列表排序的入口程序。
    '''
    global ORDER_BY_N,ORDER_DESC,dT,lst_tags  
    if ORDER_BY_N==inp: # 如果同样位置点击，就切换排序方式
        ORDER_DESC=not ORDER_DESC
    else: # 如果不同位置点击，就预置排序方式
        ORDER_BY_N=inp
        if ORDER_BY_N==2: # 按修改时间排序的，第一次是最新的在前面。
            ORDER_DESC=True 
        else:
            ORDER_DESC=False # 其余排序方法，都是升序。
    # my_reload(0) # 这个方法虽然可以排序，但是效率太低
    
    # 新的排序方法
    dT.sort(key=sort_by_tag,reverse=ORDER_DESC)
    v_tag_choose()
    v_tag['value']=lst_tags
    v_inp['value']=lst_tags
    
def tree_order_filename(inp=None):
    tree_order_base(0)
    
def tree_order_tag(inp=None):
    tree_order_base(1)
    
def tree_order_modi_time(inp=None):
    tree_order_base(2)
    
def tree_order_path(inp=None):
    tree_order_base(3)

    

#%%
columns = ("index","file", "tags", "modify_time","file0")

tree = ttk.Treeview(frameMain, show = "headings", columns = columns, \
                    displaycolumns = ["file", "tags", "modify_time","file0"], \
                    selectmode = tk.BROWSE, \
                    yscrollcommand = bar1.set,xscrollcommand = bar2.set)#, height=18)

tree.column('index', width=30, anchor='center')
tree.column('file', width=400, anchor='w')
tree.column('tags', width=300, anchor='w')
tree.column('modify_time', width=100, anchor='w')
tree.column('file0', width=80, anchor='w')

tree.heading("index", text = "序号",anchor='center')
tree.heading("file", text = "文件名",anchor='w',command=tree_order_filename)
tree.heading("tags", text = "标签",anchor='w',command=tree_order_tag)
tree.heading("modify_time", text = "修改时间",anchor='w',command=tree_order_modi_time)
tree.heading("file0", text = "完整路径",anchor='w',command=tree_order_path)




def get_tag(tar=v_tag): 
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
    return res

def add_tree_item(tree,dT): 
    '''
    # 关键函数：增加主框架的内容
    # 先获得搜索项目以及 tag
    '''
    str_btm.set('正在刷新列表……')
    time0=time.time()
    tmp_search_items=get_tag() # 列表
    k=0
    print(tmp_search_items)
    for i in range(len(dT)):
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
        
        for tag in tmp_search_items:            
            tag=str.lower(tag)
            if tag=='' or tag==cALL_FILES or (tag in tag_lower):
                canadd=1
            elif str.lower(tmp[3]).find(tag)<0:
                canadd=0
        
        if canadd==1:
            k+=1
            if k%2==1:
                tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]),tags=['line1'])
            else:
                tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        if k % 1000==0:
            tree.update() # 提前刷新，优化用户体验
            
    str_btm.set("找到 "+str(k)+" 个结果")#"，用时"+str(time.time()-time0)+"秒")
    
    # tree.insert('',i,values=(d[0][i],d[1][i],d[2][i],d[3][i]))

add_tree_item(tree,dT)

def get_folder(): 
    '''
    获取文件夹名称 (简称)，需要用 folder_s2l(tmp) 转化为长路径。

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
    合并获取短路径和长路径的逻辑。返回值是代表长路径的字符串。
    '''
    short_folder=get_folder()
    if short_folder =='':
        return short_folder
    else:
        res=folder_s2l(short_folder)
        res=str(res).replace('\\','/')
        return res


style = ttk.Style()
# style.configure("Treeview.Heading", font=(None, 12),rowheight=60)
style.configure("Treeview.Heading", font=('微软雅黑', LARGE_FONT), \
                rowheight=int(LARGE_FONT*3.5),height=int(LARGE_FONT*4))

style.configure("Treeview", font=(None, MON_FONTSIZE), rowheight=int(MON_FONTSIZE*3.5))

# 行高
# style.configure("Treeview.Heading", font=(None, 12))

# 获取当前点击行的值
def treeOpen(event=None): #单击
    '''
    打开列表选中项目。

    '''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        print(item_text[-1])
        os.startfile(item_text[-1]) #打开这个文件

def file_rename(tar=None): # 对文件重命名
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_path = item_text[-1]
        tmp_file_name = split_path(tmp_full_path)[-1]
        print('正在重命名：')
        print(tmp_full_path)
        print(tmp_file_name)
        res = simpledialog.askstring('文件重命名',prompt='请输入新的文件名',initialvalue =tmp_file_name) # 有bug，不能输入#号
        tmp_new_name='/'.join(split_path(tmp_full_path)[0:-1]+[res])
        print(tmp_new_name)
        if res is not None:
            try:
                # os.rename(tmp_full_path,tmp_new_name)
                safe_rename(tmp_full_path,tmp_new_name)
                my_reload(0)
            except:
                t=tk.messagebox.showerror(title = 'ERROR',message='重命名失败！')
                # print(t)
                pass

def fun_test(event=None): # 
    ''' 
    用于调试一些测试性的功能，
    为了避免 event 输入，所以套了一层。

    '''
    show_form_setting()
    # print('进入测试功能')
    
    # full_path='D:/MaJian/Documents/NutNotes/_MY_NOTES/#Python_GUI/pyinstaller打包exe#@PIN.md'
    # # 
    # tree_find(full_path)

    pass

def tree_find(full_path=''): # 
    '''
    用于在 tree 里面找到项目，并加高亮。
    '''
    if full_path=='':
        return(-1)
        # full_path='D:/MaJian/Documents/NutNotes/_MY_NOTES/#Python_GUI/pyinstaller打包exe#@PIN.md'
    # 根据完整路径，找到对应的文件并高亮
    tc=tree.get_children()
    tc_cnt=len(tc)
    print('条目数量为：%s' % tc_cnt)
    n=0
    print('开始查找')
    for i in tc:
        tmp=tree.item(i,"values")
        # print(tmp[-1])
        if tmp[-1]==full_path:
            # tree.focus(i) #这个并不能高亮
            tree.selection_set(i)
            print('在第%d处检查到了相应结果' % n)
            (b1,b2)=bar1.get()
            b0=b2-b1

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
            # bar1.set(b1,b2)
            tree.yview_moveto(b1)
            return(n)
            break
        else:
            n+=1
    print('居然没找到：')
    print(full_path)
    return(-1)
    # for i in range()
    

def tree_open_folder(event=None): 
    '''#打开当前文件所在的目录
    '''
    VMETHOD=1
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_file=item_text[-1]
        tmp_file=tmp_file.replace('/','\\')
        
        tmp_folder='/'.join(split_path(tmp_file)[0:-1])
        # tmp_folder=item_text[-2]
        
        print(tmp_folder)
        if VMETHOD==1:
            os.startfile(tmp_folder) #打开这个文件
        elif VMETHOD==2: 
            tmp=r'explorer /select,'+tmp_file
            print(tmp)
            os.system(tmp) # 性能极差，不知道哪的原因
            # os.system(r'explorer /select,d:\tmp\b.txt') # 这是打开文件夹并选中文件的方法
        
    pass


def input_new_tag(event=None):
    new_name=''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        # tmp_file_name = get_file_part(tmp_full_name)['ffname'] # 没有用到
        
        # new_tag = tk.simpledialog.askstring(title="添加标签", prompt="请输入新的标签")#, initialvalue=tmp)
        new_tag=v_inp.get()
        new_tag=str(new_tag).strip()
        
        if new_tag == None or new_tag == '':
            pass
            print("取消")
        else:
            file_add_tag(tmp_full_name,new_tag)
            print(new_name)

def file_add_tag(filename,tag0):    
    '''
    # 增加标签
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
                tmp_final_name=safe_rename(old_n,new_n)
                old_n=new_n #多标签时避免重命名错误
            except:
                print('为文件添加标签失败')
                pass
    my_reload(0) # 此处可以优化，避免完全重载
    try:
        tmp_final_name=tmp_final_name.replace('\\','/')
        print('添加标签完成，正在定位%s' %(tmp_final_name))
        tree_find(tmp_final_name) # 为加标签之后的项目高亮
    except:
        pass

def file_add_star(event=None): 
    '''
    加收藏。
    目前是为文件增加 TAG_STAR 对应的值。
    通常是 @PIN。
    '''
    TAG_STAR='@PIN'
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
    file_add_tag(tmp_full_name,TAG_STAR)
    
def fast_add_tag(tag): 
    '''
    加收藏。
    目前是为文件增加 TAG_STAR 对应的值。
    通常是 @PIN。
    '''
    TAG_STAR=tag
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
    file_add_tag(tmp_full_name,TAG_STAR)

def clear_entry(tar):
    '''
    将输入框清空。
    必须要指定要清空的输入框对象。
    '''
    try:
        tar.delete(0,len(tar.get()))
    except:
        pass
    pass

def my_reload(event=None): 
    '''
    刷新。
    切换目录之后自动执行此功能。
    
    输入参数0的话，清空搜索框、标签框。

    如果输入参数为空或者不是0，就保留。

    '''
    global lst_file,dT,lst_tags
    
    if not event==0:
        clear_entry(v_search)
        v_tag.current(0)
        
        # v_inp.delete(0,len(v_inp.get()))
    # v_inp.delete(0,len(v_inp.get()))
    
    # v_folder_choose(refresh=0)
    lst_file = get_data(lst_my_path) # 原因是 lst_my_path 应该是长路径，不是短路径
    
    (dT, lst_tags)=get_dt()
    # tree_clear(tree)

    v_tag_choose()
    v_tag['value']=lst_tags
    v_inp['value']=lst_tags

def my_help(event=None):
    '''
    提供帮助文件。
    目前的方式主要是跳转到在线帮助文件。以后考虑到内网打不开网页，需要增加一个离线的方面。
    '''
    os.startfile(URL_HELP)
    
def my_advice(event=None):
    '''
    在线反馈
    '''
    os.startfile(URL_ADV)
    
def my_closing():
    if tk.messagebox.askokcancel("退出", "真的要退出吗"):
        window.destroy()
        
tree.bind('<Double-Button-1>', treeOpen)
tree.bind('<Return>', treeOpen)
# tree.bind('<ButtonPress-3>', input_newname) # 右键，此功能作废



# 搜索框

        
def folder_s2l(inp):
    return dict_path[inp]
    pass



def v_folder_choose(event=None,refresh=1): # 点击新的文件夹之后
    global lst_my_path
    
    lst_path_ori=lst_my_path.copy()
    
    tmp=get_folder()
    if tmp=='':
        lst_my_path=lst_my_path0.copy()
        # 设置按钮为无效
        bt_new.configure(state=tk.DISABLED)
        bt_folder_drop.configure(state=tk.DISABLED)
    else:
        tmp=folder_s2l(tmp) #将显示值转换为实际值
        lst_my_path=[tmp]
        # 设置按钮有效
        bt_new.configure(state=tk.NORMAL)
        bt_folder_drop.configure(state=tk.NORMAL)
    
    if not lst_path_ori==lst_my_path: # 如果前后的选项没有变化的话，就不刷新文件夹列表
        if refresh==1:
            # my_reload(lst_my_path)
            my_reload(CLEAR_AFTER_CHANGE_FOLDER)
        tree.yview_moveto(0)
    
    
def v_tag_choose(event=None):
    '''
    选择标签之后触发。
    清空tree，并按照dT为tree增加行。
    '''
    # tmp_tag=get_tag()
    tree_clear(tree)
    # add_tree_item(tree,dT,tag=tmp_tag)
    add_tree_item(tree,dT)

vPDX=10
vPDY=5
# lable_folders=tk.Label(frameFolder, text = '子文件夹')
# lable_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

# v_sub_folders['value']=['']+lst_my_path
# v_sub_folders['state'] = 'readonly'
# v_sub_folders.grid(row=0,column=2, padx=10, pady=5,sticky=tk.W)
# v_sub_folders.pack(expand=0,padx=vPDX,pady=vPDY) # 
# v_sub_folders.bind('<<ComboboxSelected>>', v_folder_choose)
# v_sub_folders.bind('<Return>',v_folder_choose) #绑定回车键

lable_tag=tk.Label(frame0, text = '标签筛选')
lable_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_tag['value']=lst_tags
v_tag['state'] = 'readonly' # 只读
v_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
v_tag.bind('<<ComboboxSelected>>', v_tag_choose)
v_tag.bind('<Return>',v_tag_choose) #绑定回车键


lable_search=tk.Label(frame0, text = '按名称')
lable_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
v_search.bind('<Return>',v_tag_choose) #绑定回车键

bt_search=ttk.Button(frame0,text='搜索',command=v_tag_choose)
bt_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

bt_clear=ttk.Button(frame0,text='清空',command=my_reload)
bt_clear.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

bt_test=ttk.Button(frame0,text='测试功能',command=fun_test)
# bt_test.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 





# 布局
bar2.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=2,pady=1) # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

# tree.grid(row=1,column=0,padx=10, pady=5,sticky=tk.NSEW)
# tree.place(anchor=tk.W,relheight=1)
tree.pack(side=tk.LEFT,expand=1,fill=tk.BOTH,padx=2,pady=1)

# bar1.grid(row=1,column=1,sticky=tk.NS)
# bar1.place(x=0,y=0,anchor=tk.NE)
bar1.pack(side=tk.LEFT,expand=0,fill=tk.Y,padx=2,pady=1) # 用pack 可以实现自适应side=tk.LEFTanchor=tk.E

vPDX=10
vPDY=5

# 进度条
progressbar_file=ttk.Progressbar(frameBtm,variable=prog,mode='determinate')
progressbar_file.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY)

lable_sum=tk.Label(frameBtm, text = str_btm,textvariable=str_btm)
lable_sum.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 



bt_settings=ttk.Button(frameBtm,text='菜单')#,command=my_help)
bt_settings.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_clear=ttk.Button(frameBtm,text='刷新',command=my_reload)
bt_clear.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_new=ttk.Button(frameBtm,text='新建笔记')#,state=tk.DISABLED)#,command=my_reload)
bt_new.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_add_tag=ttk.Button(frameBtm,text='添加标签',command=input_new_tag)
bt_add_tag.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

v_inp=ttk.Combobox(frameBtm,width=16) # 新标签的输入框
v_inp.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 
v_inp.bind('<Return>',input_new_tag)
v_inp['value']=lst_tags

lable_tag=tk.Label(frameBtm, text = '添加新标签')
lable_tag.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

#%% 


def show_form_setting(): # 
    '''
    设置窗口
    （但是并没有启用）
    ''' 
    global V_SEP,V_FOLDERS,NOTE_EXT
    global json_data

    def setting_yes(event=None):
        '''
        还没有功能
        '''
        # 获得新参数
        global V_SEP,V_FOLDERS,NOTE_EXT
        NOTE_EXT=v_inp_note_type.get()
        V_FOLDERS=v_inp_folder_depth.get()
        V_SEP=v_inp_sep.get()
        # 保存到设置文件中
        set_json_options('sep',V_SEP)
        set_json_options('vfolders',V_FOLDERS)
        set_json_options('note_ext',NOTE_EXT)
        # 关闭窗口
        form_setting.destroy()
        # 然后刷新文件列表
        my_reload()
        pass

    form_setting=tk.Toplevel(window)
    form_setting.title('设置')
    form_setting.resizable(0,0) #限制尺寸
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    w_width = 400#int(screenwidth*0.8)
    w_height = 200#int(screenheight*0.8)
    x_pos=(screenwidth-w_width)/2
    y_pos=(screenheight-w_height)/2
    form_setting.geometry('%dx%d+%d+%d'%(w_width, w_height, x_pos, y_pos))

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
    clear_entry(v_inp_sep)
    v_inp_sep.insert(0, V_SEP)
    v_inp_sep.grid(row=0,column=1 ,padx=10, pady=5,sticky=tk.EW)
    
    lable_set_folder_depth=tk.Label(frame_setting1, text = '识别为标签的文件夹层数')
    lable_set_folder_depth.grid(row=1,column=0,padx=10, pady=5,sticky=tk.W)
    
    v_inp_folder_depth=ttk.Combobox(frame_setting1,width=16)#,textvariable=v2fdepth)
    lst_folder_depth=['0','1','2','3','4','5']
    v_inp_folder_depth['values']=lst_folder_depth
    v_inp_folder_depth['state']='readonly'
    tmp_n=lst_folder_depth.index(str(V_FOLDERS))
    v_inp_folder_depth.current(tmp_n)
    v_inp_folder_depth.grid(row=1,column=1 ,padx=10, pady=5,sticky=tk.EW)

    # 笔记类型
    lable_set_note_type=tk.Label(frame_setting1, text = '笔记类型')
    lable_set_note_type.grid(row=2,column=0,padx=10, pady=5,sticky=tk.W)

    v_inp_note_type=ttk.Combobox(frame_setting1,width=16)#,textvariable=v2fdepth)
    v_inp_note_type['values']=NOTE_EXT_LIST
    v_inp_note_type['state']='readonly'
    v_inp_note_type.current(0)
    tmp_n=NOTE_EXT_LIST.index(NOTE_EXT)
    v_inp_note_type.current(tmp_n)
    v_inp_note_type.grid(row=2,column=1 ,padx=10, pady=5,sticky=tk.EW)
    # v_inp.bind('<Return>',input_new_tag)

    # 下面的设置区域
    bt_setting_yes=ttk.Button(frame_setting2,text='确定',command=setting_yes)
    bt_setting_yes.grid(row=10,column=0,padx=10, pady=5,sticky=tk.EW)
    # bt_setting_yes.pack(side=tk.LEFT,expand=0,fill=tk.X)
    
    bt_setting_cancel=ttk.Button(frame_setting2,text='取消',command=form_setting.destroy)
    bt_setting_cancel.grid(row=10,column=1,padx=10, pady=5,sticky=tk.EW)
    # bt_setting_cancel.pack(side=tk.LEFT,expand=0,fill=tk.X)
    


def my_folder_add_click(): # 
    '''
    通过点击的方式，添加新的目录
    '''
    res=filedialog.askdirectory()#选择目录，返回目录名
    res=[res]
    print(res)
    if res=='':
        print('取消添加文件夹')
    else:
        my_folder_add(res)


def my_folder_add_drag(files): # 
    '''
    通过拖拽的方式，添加目录。
    '''
    filenames=list() #可以得到文件路径编码, 可以看到实际上就是个列表。
    folders=list()
    # print(files)
    for item in files:
        item=item.decode('gbk')
        if isdir(item):
            folders.append(item)
        elif isfile(item):
            filenames.append(item)
    if len(folders)>0:
        my_folder_add(folders)

# 设置拖拽反映函数
windnd.hook_dropfiles(tree_lst_folder, func=my_folder_add_drag)

def tree_drag_enter(files):
    '''
    以拖拽的方式将文件拖动到tree范围内，将执行复制命令

    '''
    short_name=get_folder()
    print(short_name)
    if short_name=='':
        # print('未指定目标目录，取消复制')
        str_btm.set('未指定目标目录，取消复制')
        return
    else:
        long_name=folder_s2l(short_name) #将显示值转换为实际值
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
        res=safe_copy(old_name, new_name)
        print('res=')
        print(res)
        
        #再显示到列表中
        k+=1
        tmp=get_file_part(res)
        tmp_v=(tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['tar'])
        tmp=tmp_v
        tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        
    # 高亮文件
    tree_find(res)
    tree.yview_moveto(1)
    
windnd.hook_dropfiles(tree, func=tree_drag_enter)

def my_folder_refresh(): # 刷新左侧的文件夹列表
    # 更新json文件
    update_json(data=json_data)
    load_json_data()
    # 更新左侧列表
    update_folder_list()
    # 更新正文
    v_folder_choose()

def my_folder_add(tar_list): # 添加关注的目录
    global json_data
    for tar in tar_list:
        if len(tar)>0: # 用于避免空白项目，虽然不知道哪里来的
            tar=str(tar).replace("\\",'/')
            tmp={"pth":tar}
            if not tmp in json_data['options']['tar']: # 此处判断条件有漏洞，因为加入short参数之后就不对了
                json_data['options']['tar'].append(tmp)
    # 刷新目录
    my_folder_refresh()
    

def my_folder_drop(): # 删除关注的目录
    global json_data
    # 获取当前选中的文件夹
    short_name=get_folder()
    print(short_name)
    if short_name=='':
        pass
    else:
        long_name=folder_s2l(short_name) #将显示值转换为实际值
        print(long_name)
    
    # 在 json 里面找到对应项目并删除
    n=0
    for i in json_data['options']['tar']:
        if i['pth']==long_name:
            json_data['options']['tar'].pop(n)
            break
        n+=1
    # 刷新目录
    my_folder_refresh()
    
    
def my_folder_open(tar=None): # 打开目录
    # 获得当前选中的长目录
    if len(lst_my_path)!=1:
        pass
    else:
        try:
            os.startfile(lst_my_path[0])
        except:
            pass

def set_local_data(): # 修改 json
    pass




def create_note(event=None): # 添加笔记
    global lst_my_path,NOTE_NAME,NOTE_EXT
    tags=['Tagdox笔记']
    
    if len(lst_my_path)!=1:
        print('新建功能锁定，暂不可用')
        return
    #
    res = simpledialog.askstring('新建 Tagdox 笔记',prompt='请输入文件名',initialvalue =NOTE_NAME)
    if res is not None:
        print(res)
        NOTE_NAME=res
        if len(tags)>0:
            stags=V_SEP+V_SEP.join(tags)
        else:
            stags=''
            
        if len(lst_my_path)>1:
            pass
        
        if len(lst_my_path)==1:
            pth=lst_my_path[0]
            print(pth)
            if True:#pth in lst_my_path0: # 后面这个判断有点多余
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
                if not event=='create_note_here':
                    my_reload()
                    tree_find(fpth)
                else:
                    return fpth
    else:
        pass
    #

def create_note_here(event=None):
    '''
    树状图里面，可以右击直接在选中文件的相同位置新建笔记。
    '''
    global lst_my_path
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
    tmp_path = '/'.join(split_path(tmp_full_name)[0:-1])
    print('当前路径')
    print(tmp_path)
    lst_tmp=lst_my_path.copy()
    lst_my_path=[tmp_path]
    
    fpth=create_note('create_note_here')
    lst_my_path=lst_tmp.copy()
    
    if fpth is not None:
        my_reload()
        tree_find(fpth)
    pass

            
bt_new.configure(command=create_note)
bt_folder_drop.configure(state=tk.DISABLED)

#%%
def jump_to_search(event=None):
    v_search.focus()
    
def jump_to_tag(event=None):
    v_inp.focus()

#%%
# 弹出菜单
'''
主菜单，点击设置按钮可以弹出
'''
menu_main = tk.Menu(window,tearoff=0)
menu_main.add_command(label='参数设置',command=show_form_setting)
menu_main.add_separator()
# menu_main.add_command(label='使用说明')#,command=my_help)
menu_main.add_command(label='在线帮助',command=my_help)
menu_main.add_command(label='建议和反馈',command=my_advice)
menu_main.add_command(label='关于',command=show_info_window)
menu_main.add_separator()
menu_main.add_command(label='退出',command=my_closing)

def popup_menu_main(event):
    '''
    程序核心设置菜单的弹出
    '''
    menu_main.post(event.x_root,event.y_root)

'''
文件夹区域的右键菜单
'''
menu_folder = tk.Menu(window,tearoff=0)
menu_folder.add_command(label="添加文件夹",command=my_folder_add_click)
menu_folder.add_separator()
menu_folder.add_command(label="向上移动（开发中）",state=tk.DISABLED,command=my_folder_open)
menu_folder.add_command(label="向下移动（开发中）",state=tk.DISABLED,command=my_folder_open)
menu_folder.add_separator()
menu_folder.add_command(label="打开所选文件夹",command=my_folder_open)
menu_folder.add_command(label="取消关注所选文件夹",command=my_folder_drop)

menu_folder_no = tk.Menu(window,tearoff=0)
menu_folder_no.add_command(label="添加文件夹",command=my_folder_add_click)
menu_folder_no.add_separator()
menu_folder_no.add_command(label="打开所选文件夹",state=tk.DISABLED,command=my_folder_open)
menu_folder_no.add_command(label="取消关注所选文件夹",state=tk.DISABLED,command=my_folder_drop)

def popup_menu_folder(event):
    if len(lst_my_path)!=1: # 如果没有选中项目的话
        menu_folder_no.post(event.x_root,event.y_root)
    else:
        menu_folder.post(event.x_root,event.y_root)

menu_tags_to_drop = tk.Menu(window,tearoff=0)
menu_tags_to_add = tk.Menu(window,tearoff=0)

'''
文件区域的右键菜单
'''
menu_file = tk.Menu(window,tearoff=0)
menu_file.add_command(label="打开文件",command=treeOpen)
menu_file.add_command(label="在相同位置创建笔记",command=create_note_here)
menu_file.add_command(label="打开所在文件夹",command=tree_open_folder)
menu_file.add_separator()
# menu_file.add_command(label="添加收藏 @PIN",command=file_add_star)
menu_file.add_cascade(label="快速添加标签",menu=menu_tags_to_add)#,command=file_add_star)
menu_file.add_cascade(label="移除标签",menu=menu_tags_to_drop)
menu_file.add_separator()
menu_file.add_command(label="发送无标签副本到桌面（开发中）",state=tk.DISABLED)#,command=file_rename)
menu_file.add_command(label="复制到剪切板（开发中）",state=tk.DISABLED)#,command=file_rename)
menu_file.add_command(label="移动到文件夹（开发中）",state=tk.DISABLED)#,command=file_rename)
menu_file.add_command(label="粘贴（开发中）",state=tk.DISABLED)#,command=file_rename)
menu_file.add_command(label="删除（开发中）",state=tk.DISABLED)#,command=file_rename)
menu_file.add_command(label="重命名（开发中）",state=tk.DISABLED,command=file_rename)
menu_file.add_separator()
menu_file.add_command(label="刷新",command=my_reload)

if len(QUICK_TAGS)>0:
    for i in QUICK_TAGS:
        menu_tags_to_add.add_command(label=i,command=lambda x=i:fast_add_tag(x))
    menu_tags_to_add.add_separator()
menu_tags_to_add.add_command(label='自定义标签…',command=jump_to_tag)

menu_file_no_selection = tk.Menu(window,tearoff=0)
menu_file_no_selection.add_command(label="打开文件",state=tk.DISABLED,command=treeOpen)
menu_file_no_selection.add_command(label="转到所在文件夹",state=tk.DISABLED,command=tree_open_folder)
menu_file_no_selection.add_command(label="重命名",state=tk.DISABLED)#,command=my_folder_add_click)
menu_file_no_selection.add_command(label="添加收藏",state=tk.DISABLED)#,command=my_folder_add_click)
menu_file_no_selection.add_separator()
menu_file_no_selection.add_command(label="刷新",command=my_reload)

def drop_tag(event=None): # 删除标签，以后将#号换成SEP
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
    tmp_final_name=safe_rename(tmp_full_name,new_full_name)
    my_reload(0) # 此处可以优化，避免完全重载
    try:
        tmp_final_name=tmp_final_name.replace('\\','/')
        print('删除标签完成，正在定位%s' %(tmp_final_name))
        tree_find(tmp_final_name) # 为加标签之后的项目高亮
    except:
        pass

def popup_menu_file(event):
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
                    menu_tags_to_drop.add_command(label=i,command=lambda x=i:drop_tag(x))
                    
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
# 各种功能的绑定
# tree_lst_folder.bind('<<ListboxSelect>>',v_folder_choose)
# tree_lst_folder.bind('<Button-1>',v_folder_choose)
tree_lst_folder.bind('<ButtonRelease-1>',v_folder_choose)
tree.tag_configure('line1', background='#cccccc') # 灰色底纹,然而无效

tree_lst_folder.bind("<Button-3>",popup_menu_folder) # 绑定文件夹区域的右键功能
bt_settings.bind("<Button-1>",popup_menu_main) # 菜单按钮
tree.bind("<Button-3>",popup_menu_file) # 绑定文件夹区域的功能

# bt_setting.configure(command=show_form_setting) # 功能绑定
bt_folder_add.configure(command=my_folder_add_click) # 功能绑定
bt_folder_drop.configure(command=my_folder_drop) # 功能绑定

bar1.config( command = tree.yview )
bar2.config( command = tree.xview )
# tree.pack(expand = True, fill = tk.BOTH)
window.bind_all('<Control-n>',create_note) # 绑定添加笔记的功能。
window.bind_all('<Control-f>',jump_to_search) # 跳转到搜索框。
window.bind_all('<Control-t>',jump_to_tag) # 跳转到标签框。

#%%
# 运行
window.state('zoomed') # 最大化
run_flag=1
set_prog_bar(0)
# bt_add_tag.pack_forget()
window.mainloop() 
