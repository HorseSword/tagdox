# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""

import os
import tkinter as tk
from tkinter import ttk
import json
from tkinter import filedialog
from tkinter import simpledialog
import windnd
from os.path import isdir
from os.path import isfile
import time
# from docx import Document# 用于创建word文档

#常量
cALL_FILES='' # 标签为空的表达方式，默认是空字符串
LARGE_FONT=12 # 表头字号
MON_FONTSIZE=10 # 正文字号
ORDER_BY_N=1 # 排序列，1代表标签，后面按顺序对应
ORDER_DESC=False

URL_HELP='https://gitee.com/horse_sword/my-local-library' # 帮助的超链接，目前是 gitee 主页
TAR='Tagdox / 标签文库' # 程序名称
VER='v0.9.1' # 版本号
EXP_FOLDERS=['_img'] # 排除文件夹规则，以后会加到自定义里面
ALL_FOLDERS=1 # 是否有“显示所有文件夹”的功能，还没开发完，存在预加载的bug；
OPTIONS_FILE='options.json'
OPT_DEFAULT={
	"options":{
		"sep":"#",
		"vfolders":"2",
		"tar":[
		]
	}
 }

#变量
lst_file=[] # 所有文件的完整路径
dT=[]
lst_tags=[] # 全部标签
lst_my_path0=[] # json里面，要扫描的文件夹列表
lst_my_path_s=[]
lst_my_path=[]
dict_path=dict() # 用于列表简写和实际值
V_SEP='#'
V_FOLDERS=2

#%%
# 通用函数
def split_path(inp): # 通用函数：将完整路径拆分
    test_str=inp.replace('\\', '/',-1)
    test_str_res=test_str.split('/')
    return(test_str_res)

def tree_clear(tar): # treeview 清除，必须带参数
    x=tar.get_children()
    for item in x:
        tar.delete(item)
#%%
# 加载设置项 json 内容。保存到 opt_data 变量中，这是个 dict。

json_data = OPT_DEFAULT
def update_json(tar=OPTIONS_FILE,data=json_data): # 写入 json 文件
    with open(tar,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False)
        
def load_json_data():
    global json_data
    global V_SEP
    global V_FOLDERS
    global lst_my_path0
    global lst_my_path_s
    global lst_my_path
    
    need_init_json=0
    try:
        with open(OPTIONS_FILE,'r',encoding='utf8')as fp:
            json_data = json.load(fp)
    except:
        need_init_json=1
        json_data = OPT_DEFAULT
       
    opt_data=json_data['options']   #设置
    V_SEP=opt_data['sep'] # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
    V_FOLDERS=int(opt_data['vfolders']) # 目录最末层数名称检查，作为标签的检查层数
    
    # lst_my_path=lst_my_path0.copy() #按文件夹筛选用
    lst_my_path0=[]
    lst_my_path_s=[]
    
    for i in opt_data['tar']: 
        # lst_my_path0.append(i)
        tmp_L=i['pth']
        lst_my_path0.append(tmp_L)
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
        
        lst_my_path_s.append(tmp_S)
        tmp={tmp_S:tmp_L}
        dict_path.update(tmp)
    
    lst_my_path=lst_my_path0.copy() # 此处有大量的可优化空间。
    
    if need_init_json==1: # 如果没能正常读取 json 的话
        update_json()
        
load_json_data()


    
#%%

def get_data(ipath=lst_my_path0): # 返回 lst_file 列表
    lst_file=list() #获取所有文件的完整路径
    for vPath in ipath:
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
            
    return lst_file

def get_file_part(tar):     # 这里 tar 是完整路径
    [fpath,ffname]=os.path.split(tar) # fpath 所在文件夹、ffname 原始文件名
    [fname,fename]=os.path.splitext(ffname) # fname 文件名前半部分，fename 扩展名
    lst_sp=fname.split(V_SEP) #拆分为多个片段
    fname_0 = lst_sp[0]+fename # fname_0 去掉标签之后的文件名
    ftags=lst_sp[1:] # ftags 标签部分
    
    mtime = os.stat(tar).st_mtime
    file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    
    '''
    # 增加对文件目录带井号的解析（作废）
    tmp=fpath.split(V_SEP)
    if len(tmp)>1:
        for j in tmp[1:]:
            if j.find('\\')<0 and j.find('/')<0:
                ftags.append(j) # 只对最后的文件夹带井号的有反应
    '''
    
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
    
    return {'fname_0':fname_0,
            'ftags':ftags,
            'ffname':ffname,
            'fpath':fpath,
            'fename':fename,
            'tar':tar,
            'file_mdf_time':file_modify_time}
    
def sort_by_tag(elem): # 主题表格排序
    global ORDER_BY_N
    return str(elem[ORDER_BY_N])

def get_dt():
    
    dT=list()
    for tar in lst_file:
        tmp=get_file_part(tar)
        # dT.append([tmp['fname_0'],tmp['ftags'],tmp['fpath'],tmp['tar']])
        # 增加检查重复项的逻辑：
        tmp_v=[tmp['fname_0'],tmp['ftags'],tmp['file_mdf_time'],tmp['tar']]
        if not tmp_v in dT:
            dT.append(tmp_v)
    
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

lst_file = get_data()
(dT, lst_tags)=get_dt()



#%%

# 窗体设计

window = tk.Tk() # 主窗口
window.title(TAR+' '+VER)
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
w_width = int(screenwidth*0.8)
w_height = int(screenheight*0.8)
window.geometry('%dx%d+%d+%d'%(w_width, w_height, (screenwidth-w_width)/2, (screenheight-w_height)/2))

# window.resizable(0,0) #限制尺寸

#%%

# 自制输入窗体
def my_input_window(title='未命名',msg='未定义'):
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
# 菜单

menu1=tk.Menu(window)

mFile=tk.Menu(menu1,tearoff=False)
menu1.add_cascade(label='文件', menu=mFile)

mFile.add_command(label='新建',accelerator='Ctrl+N')
mFile.add_command(label='打开', accelerator='Ctrl+O')
mFile.add_command(label='保存', accelerator='Ctrl+S')

mHelp=tk.Menu(menu1,tearoff=False)
menu1.add_cascade(label='帮助', menu=mHelp)

mHelp.add_command(label='使用说明',accelerator='Ctrl+N')

# window.configure(menu=menu1) # 菜单生效

#%%

# 框架设计

# 文件夹区
frameFolder=ttk.Frame(window,width=int(w_width*0.4))#,width=600)
# frame0.grid(row=0,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frame0.pack(side=tk.TOP,expand=1,fill=tk.X,padx=10,pady=5)
frameFolder.pack(side=tk.LEFT,expand=0,fill=tk.Y,padx=10,pady=10)

frameFolderCtl=ttk.Frame(frameFolder,height=50,borderwidth=0,relief=tk.FLAT)
frameFolderCtl.pack(side=tk.BOTTOM,expand=0,fill=tk.X,padx=10,pady=10)

# 上面功能区
frame0=ttk.LabelFrame(window,text='',height=80)#,width=600)
# frame0.grid(row=0,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frame0.pack(side=tk.TOP,expand=1,fill=tk.X,padx=10,pady=5)
frame0.pack(expand=0,fill=tk.X,padx=10,pady=5)

# 主功能区
frameMain=ttk.Frame(window)#,height=800)
# frameMain.grid(row=1,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frameMain.pack(side=tk.TOP,expand=1,fill=tk.BOTH,padx=10,pady=5)
frameMain.pack(expand=1,fill=tk.BOTH,padx=10,pady=0)

# 底部区
frameBtm=ttk.LabelFrame(window,height=80)
# frameBtm.grid(row=2,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frameBtm.pack(side=tk.BOTTOM,expand=1,fill=tk.X,padx=10,pady=5)
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

bt_setting=ttk.Button(frameFolderCtl,text='设置') #state=tk.DISABLED,,command=setting_fun
# bt_setting.pack(side=tk.LEFT,expand=0,padx=5,pady=10)#,fill=tk.X) # 

bt_folder_add=ttk.Button(frameFolderCtl,text='添加文件夹') #state=tk.DISABLED,,command=setting_fun
bt_folder_add.pack(side=tk.LEFT,expand=0,padx=20,pady=10,fill=tk.X) # 

bt_folder_drop=ttk.Button(frameFolderCtl,text='移除文件夹') #state=tk.DISABLED,,command=setting_fun
bt_folder_drop.pack(side=tk.RIGHT,expand=0,padx=20,pady=10,fill=tk.X) # 

bar_folder=tk.Scrollbar(frameFolder,width=20)
bar_folder.pack(side=tk.RIGHT, expand=0,fill=tk.Y)

tk_lst_folder = ttk.Treeview(frameFolder, show = "headings", columns = ['folders'], 
                             selectmode = tk.BROWSE, 
                             # rowheight=int(MON_FONTSIZE*3.5),
                             # font=(None, MON_FONTSIZE),
                             yscrollcommand = bar_folder.set)#, height=18)
bar_folder.config( command = tk_lst_folder.yview )
# tk_lst_folder=tk.Listbox(frameFolder,yscrollcommand=bar_folder.set,
#                          relief=tk.FLAT,
#                          # rowheight=int(MON_FONTSIZE*3.5),
#                          font=(None, MON_FONTSIZE))
tk_lst_folder.heading("folders", text = "关注的文件夹",anchor='w')
tk_lst_folder.column('folders', width=300, anchor='w')

# tk_lst_folder.insert(0,"（全部）")
def update_folder_list():
    global tk_lst_folder
    tree_clear(tk_lst_folder)
    tmp=0
    if ALL_FOLDERS==1:
        tk_lst_folder.insert('',tmp,values=("（全部）"))
    for i in lst_my_path_s:
        tmp+=1
        print(i)
        tk_lst_folder.insert('',tmp,values=(str(i))) # 此处有bug，对存在空格的不可用
    
        # tk_lst_folder.insert(tk.END,i)
    tmp=tk_lst_folder.get_children()[0]
    # tk_lst_folder.focus(tmp)
    tk_lst_folder.selection_set(tmp)
# tk_lst_folder.selection_set()

update_folder_list()
tk_lst_folder.pack(side=tk.LEFT,expand=0,fill=tk.BOTH)

def tree_order_base(inp):
    global ORDER_BY_N,ORDER_DESC  
    if ORDER_BY_N==inp:
        ORDER_DESC=not ORDER_DESC
    else:
        ORDER_BY_N=inp
        ORDER_DESC=False
    my_reload(0)
    
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

str_btm=tk.StringVar() #最下面显示状态用的
str_btm.set("加载中")


def get_tag(tar=v_tag): # 获取标签
    res=[]
    if len(v_tag.get())>0:
        res+=[v_tag.get()]
    if len(v_search.get())>0:
        res+=str(v_search.get()).split(' ')
    return res

def add_tree_item(tree,dT): # 关键函数：增加主框架的内容
    # 先获得搜索项目以及 tag
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
                tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]),tag='line1')
            else:
                tree.insert('',k,values=(k,tmp[0],tmp[1],tmp[2],tmp[3]))
        
    str_btm.set("找到 "+str(k)+" 个结果")
    # tree.insert('',i,values=(d[0][i],d[1][i],d[2][i],d[3][i]))

add_tree_item(tree,dT)

tree.tag_configure('line1', background='#cccccc') # 灰色底纹,然而无效

def get_folder(): # 获取文件夹名称
    # res= v_folders.get()
    # res='（全部）'
    for item in tk_lst_folder.selection():
        res = tk_lst_folder.item(item, "values")

    # res=tk_lst_folder.get(tk_lst_folder.curselection())
    try:
        res=res[0]
        if res=='（全部）':
            res=''
    except:
        res=''
    # print(res)
    return res

bar1.config( command = tree.yview )
bar2.config( command = tree.xview )
# tree.pack(expand = True, fill = tk.BOTH)

style = ttk.Style()

# style.configure("Treeview.Heading", font=(None, 12),rowheight=60)
style.configure("Treeview.Heading", font=(None, LARGE_FONT), \
                rowheight=int(LARGE_FONT*2.5),height=int(LARGE_FONT*3))

style.configure("Treeview", font=(None, MON_FONTSIZE), rowheight=int(MON_FONTSIZE*3.5))

# 行高
# style.configure("Treeview.Heading", font=(None, 12))

# 获取当前点击行的值
def treeOpen(event=None): #单击
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
                os.rename(tmp_full_path,tmp_new_name)
                my_reload(0)
            except:
                t=tk.messagebox.showerror(title = 'ERROR',message='重命名失败！')
                # print(t)
                pass
        
    

def tree_open_folder(event=None): #打开当前文件所在的目录
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
    # 增加标签
    tag_list=tag0.split(V_SEP)
    tag_old = get_file_part(filename)['ftags'] #已有标签
    file_old = get_file_part(filename)['ffname'] #原始的文件名
    path_old = get_file_part(filename)['fpath'] #路径
    [fname,fename]=os.path.splitext(file_old) #文件名前半部分，扩展名
    
    old_n=path_old+os.sep+fname+fename
    for i in tag_list:
        if not i in tag_old:
            new_n=path_old+os.sep+fname + V_SEP + i + fename
            print(old_n)
            print(new_n)
            os.rename(old_n,new_n)
            old_n=new_n #多标签时避免重命名错误
    my_reload(0) # 此处可以优化，避免完全重载

def clear_entry(tar):
    try:
        tar.delete(0,len(tar.get()))
    except:
        pass
    pass

def my_reload(event=None): # 刷新
    global lst_file,dT,lst_tags
    
    if not event==0:
        clear_entry(v_search)
        v_tag.current(0)
        # v_inp.delete(0,len(v_inp.get()))
    # v_inp.delete(0,len(v_inp.get()))
    
    # v_folder_choose(refresh=0)
    lst_file = get_data(lst_my_path) # 此处存在bug，导致刷新之后没有数据。尚未修复。
    # 原因是 lst_my_path 应该是长路径，不是短路径
    
    (dT, lst_tags)=get_dt()
    # tree_clear(tree)

    v_tag_choose()
    v_tag['value']=lst_tags
    v_inp['value']=lst_tags

def my_help(event=None):
    os.startfile(URL_HELP)

tree.bind('<Double-Button-1>', treeOpen)
tree.bind('<Return>', treeOpen)
# tree.bind('<ButtonPress-3>', input_newname) # 右键，此功能作废



# 搜索框

        
def folder_s2l(inp):
    return dict_path[inp]
    pass



def v_folder_choose(event=None,refresh=1): # 点击新的文件夹之后
    global lst_my_path
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
    if refresh==1:
        my_reload(lst_my_path)
    
    
def v_tag_choose(event=None):
    # tmp_tag=get_tag()
    tree_clear(tree)
    # add_tree_item(tree,dT,tag=tmp_tag)
    add_tree_item(tree,dT)



vPDX=10
vPDY=5
# lable_folders=tk.Label(frameFolder, text = '文件夹')
# lable_tag.grid(row=0,column=1,padx=10, pady=5,sticky=tk.W)
# lable_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_folders['value']=['']+lst_my_path
v_folders['state'] = 'readonly'
# v_folders.grid(row=0,column=2, padx=10, pady=5,sticky=tk.W)
# v_folders.pack(expand=0,padx=vPDX,pady=vPDY) # 
v_folders.bind('<<ComboboxSelected>>', v_folder_choose)
v_folders.bind('<Return>',v_folder_choose) #绑定回车键

# bt_folders=ttk.Button(frame0,text='跳转',command=v_folder_choose)
# bt_folders.grid(row=0,column=3,padx=10, pady=5,sticky=tk.EW)
# bt_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

lable_tag=tk.Label(frame0, text = '标签筛选')
# lable_tag.grid(row=0,column=11,padx=10, pady=5,sticky=tk.W)
lable_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_tag['value']=lst_tags
v_tag['state'] = 'readonly' # 只读
# v_tag.grid(row=0,column=12,padx=10, pady=5,sticky=tk.W)
v_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
v_tag.bind('<<ComboboxSelected>>', v_tag_choose)
v_tag.bind('<Return>',v_tag_choose) #绑定回车键


lable_search=tk.Label(frame0, text = '按名称')
# lable_tag.grid(row=0,column=11,padx=10, pady=5,sticky=tk.W)
lable_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

# v_tag['value']=lst_tags
# v_tag['state'] = 'readonly' # 只读
# v_tag.grid(row=0,column=12,padx=10, pady=5,sticky=tk.W)
v_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
# v_search.bind('<<ComboboxSelected>>', v_tag_choose)
v_search.bind('<Return>',v_tag_choose) #绑定回车键

bt_search=ttk.Button(frame0,text='搜索',command=v_tag_choose)
# bt_search.grid(row=0,column=13,padx=10, pady=5,sticky=tk.EW)
bt_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

bt_clear=ttk.Button(frame0,text='清空',command=my_reload)
# bt_search.grid(row=0,column=13,padx=10, pady=5,sticky=tk.EW)
bt_clear.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 





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
lable_sum=tk.Label(frameBtm, text = str_btm,textvariable=str_btm)
# lable_sum.grid(row=2,column=0,padx=10, pady=5,sticky=tk.W)
lable_sum.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

bt_help=ttk.Button(frameBtm,text='使用说明',command=my_help)
# bt_help.grid(row=2,column=99,padx=10, pady=5,sticky=tk.EW)
bt_help.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_clear=ttk.Button(frameBtm,text='刷新',command=my_reload)
# bt_clear.grid(row=0,column=20,padx=10, pady=5,sticky=tk.EW)
bt_clear.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_new=ttk.Button(frameBtm,text='新建笔记(Ctrl+N)',state=tk.DISABLED)#,command=my_reload)
# bt_clear.grid(row=0,column=20,padx=10, pady=5,sticky=tk.EW)
bt_new.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_add_tag=ttk.Button(frameBtm,text='点此添加标签',command=input_new_tag)
# bt_clear.grid(row=2,column=22,padx=10, pady=5,sticky=tk.EW)
bt_add_tag.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

v_inp=ttk.Combobox(frameBtm,width=16) # 新标签的输入框
# v_inp.grid(row=2,column=21 ,padx=10, pady=5)
v_inp.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 
v_inp.bind('<Return>',input_new_tag)
v_inp['value']=lst_tags

lable_tag=tk.Label(frameBtm, text = '添加新标签')
# lable_tag.grid(row=2,column=20,padx=10, pady=5,sticky=tk.W)
lable_tag.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 
#%% 

def init_form_setting(): # 设置窗口
        
    form_setting=tk.Toplevel(window)
    v2sep=tk.StringVar(value=V_SEP)
    v2fdepth=tk.StringVar(value=V_FOLDERS)
    v2mypath=list()
    for i in range(5):
        if i<len(lst_my_path):
            v2mypath.append(tk.StringVar(value=lst_my_path[i]))
        else:
            v2mypath.append(tk.StringVar(value=''))
    # v2sep=V_SEP
    frame_setting1=ttk.LabelFrame(form_setting,text='参数设置',height=80,width=800)
    frame_setting1.grid(row=0,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
    frame_setting1.columnconfigure(1, weight=1)
    
    frame_setting2=ttk.LabelFrame(form_setting,text='待扫描文件夹',width=800)
    frame_setting2.grid(row=1,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
    frame_setting2.columnconfigure(1, weight=1)
    
    lable_set_sep=tk.Label(frame_setting1, text = '标签分隔符')
    lable_set_sep.grid(row=0,column=0,padx=10, pady=5,sticky=tk.W)
    
    v_inp_sep=ttk.Entry(frame_setting1,width=16,textvariable=v2sep)
    v_inp_sep.grid(row=0,column=1 ,padx=10, pady=5)
    # v_inp_sep.set(V_SEP)
    # v_inp.bind('<Return>',input_new_tag)
    
    lable_set_folder_depth=tk.Label(frame_setting1, text = '识别为标签的文件夹层数')
    lable_set_folder_depth.grid(row=1,column=0,padx=10, pady=5,sticky=tk.W)
    
    v_inp_folder_depth=ttk.Entry(frame_setting1,width=16,textvariable=v2fdepth)
    v_inp_folder_depth.grid(row=1,column=1 ,padx=10, pady=5)
    # v_inp.bind('<Return>',input_new_tag)
    
    lst_folder_togo_label=[]
    lst_folder_togo_value=[]
    for i in range(5):
        lst_folder_togo_label.append(tk.Label(frame_setting2, text = '文件夹'+str(i+1)))
        lst_folder_togo_label[-1].grid(row=i+2,column=0,padx=10, pady=5,sticky=tk.W)
        
        lst_folder_togo_value.append(ttk.Entry(frame_setting2,width=16,textvariable=v2mypath[i]))
        lst_folder_togo_value[-1].grid(row=i+2,column=1 ,padx=10, pady=5,sticky=tk.EW)
    bt_setting_yes=ttk.Button(form_setting,text='确定',command=setting_yes)
    bt_setting_yes.grid(row=10,column=0,padx=10, pady=5,sticky=tk.EW)
    
    bt_setting_cancel=ttk.Button(form_setting,text='取消',command=form_setting.destroy)
    bt_setting_cancel.grid(row=10,column=1,padx=10, pady=5,sticky=tk.EW)
    
    form_setting.title('设置')
    form_setting.resizable(0,0) #限制尺寸

def my_folder_add_click(): # 获取要添加的目录
    
    res=filedialog.askdirectory()#选择目录，返回目录名
    res=[res]
    print(res)
    if res=='':
        print('取消添加文件夹')
    else:
        my_folder_add(res)


def my_folder_add_drag(files):
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
windnd.hook_dropfiles(tk_lst_folder, func=my_folder_add_drag)

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

def setting_yes(event=None):
    # 获得新参数
    
    pass

bt_setting.configure(command=init_form_setting) # 功能绑定
bt_folder_add.configure(command=my_folder_add_click) # 功能绑定
bt_folder_drop.configure(command=my_folder_drop) # 功能绑定

def create_note(event=None):
    global lst_my_path
    NOTE_NAME='未命名'
    NOTE_EXT='.docx'
    tags=['Tagdox笔记']
    
    if len(lst_my_path)!=1:
        print('新建功能锁定，暂不可用')
        return
    #
    print('新建功能跳过')
    res = simpledialog.askstring('新建 Tagdox 笔记',prompt='请输入文件名',initialvalue =NOTE_NAME)
    if res is not None:
        print(res)
        NOTE_NAME=res
        if len(tags)>0:
            stags='#'+'#'.join(tags)
        else:
            stags=''
            
        if len(lst_my_path)>1:
            pass
        
        if len(lst_my_path)==1:
            pth=lst_my_path[0]
            print(pth)
            if pth in lst_my_path0:
                fpth=pth+'/'+ NOTE_NAME + stags + NOTE_EXT 
                
                # 检查是否有这个文件
                i=0
                while isfile(fpth):
                    i+=1
                    fpth=pth+'/'+ NOTE_NAME +'('+str(i)+')'+ stags+ NOTE_EXT
                
                #创建文件
                print(fpth)
                if NOTE_EXT in ['.md','.txt','.docx']:
                    with open(fpth,'w') as _:
                        pass
                elif NOTE_EXT in ['.docxXXXXX']:
                    # d=Document()
                    # d.save(fpth)
                    pass
                # 打开
                os.startfile(fpth) #打开这个文件
                #刷新
                my_reload()
    else:
        pass
    #
    
            
bt_new.configure(command=create_note)
bt_folder_drop.configure(state=tk.DISABLED)

#%%
# 弹出菜单
menu_folder = tk.Menu(window,tearoff=0)
menu_folder.add_command(label="添加文件夹",command=my_folder_add_click)
menu_folder.add_command(label="转到所选文件夹",command=my_folder_open)
menu_folder.add_separator()
menu_folder.add_command(label="取消关注所选文件夹",command=my_folder_drop)

menu_folder_no = tk.Menu(window,tearoff=0)
menu_folder_no.add_command(label="添加文件夹",command=my_folder_add_click)
menu_folder_no.add_command(label="转到所选文件夹",state=tk.DISABLED,command=my_folder_open)
menu_folder_no.add_separator()
menu_folder_no.add_command(label="取消关注所选文件夹",state=tk.DISABLED,command=my_folder_drop)

def popup_menu_folder(event):
    if len(lst_my_path)!=1:
        menu_folder_no.post(event.x_root,event.y_root)
    else:
        menu_folder.post(event.x_root,event.y_root)

menu_file = tk.Menu(window,tearoff=0)
menu_file.add_command(label="打开文件",command=treeOpen)
menu_file.add_command(label="转到所在文件夹",command=tree_open_folder)
menu_file.add_command(label="重命名（尚未开发完成）",state=tk.DISABLED,command=file_rename)
menu_file.add_separator()
menu_file.add_command(label="刷新",command=my_reload)

menu_file_no_selection = tk.Menu(window,tearoff=0)
menu_file_no_selection.add_command(label="打开文件",state=tk.DISABLED,command=treeOpen)
menu_file_no_selection.add_command(label="转到所在文件夹",state=tk.DISABLED,command=tree_open_folder)
menu_file_no_selection.add_command(label="重命名",state=tk.DISABLED)#,command=my_folder_add_click)
menu_file_no_selection.add_separator()
menu_file_no_selection.add_command(label="刷新",command=my_reload)

def popup_menu_file(event):
    tmp=0
    for item in tree.selection():
        tmp+=1
    if tmp>0:
        menu_file.post(event.x_root,event.y_root)
    else:
        menu_file_no_selection.post(event.x_root,event.y_root)

tk_lst_folder.bind("<Button-3>",popup_menu_folder) # 绑定文件夹区域的功能
tree.bind("<Button-3>",popup_menu_file) # 绑定文件夹区域的功能

#%%
# 运行
# tk_lst_folder.bind('<<ListboxSelect>>',v_folder_choose)
# tk_lst_folder.bind('<Button-1>',v_folder_choose)
tk_lst_folder.bind('<ButtonRelease-1>',v_folder_choose)
window.bind_all('<Control-n>',create_note)
window.state('zoomed')
window.mainloop() 
