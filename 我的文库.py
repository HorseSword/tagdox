# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""

import os
import tkinter as tk
from tkinter import ttk
import json

#常量
cALL_FILES='' # 标签为空的表达方式，默认是空字符串
LARGE_FONT=12 # 表头字号
MON_FONTSIZE=10 # 正文字号
ORDER_BY_N=1 # 排序列，1代表标签，以后可以自定义

URL_HELP='https://gitee.com/horse_sword/my-local-library' # 帮助的超链接，目前是 gitee 主页
TAR='我的文库' # 程序名称
VER='v0.6.4' # 版本号
EXP_FOLDERS=['_img'] # 排除文件夹规则，以后会加到自定义里面

#变量
lst_file=[] # 所有文件的完整路径
dT=[]
lst_tags=[] # 全部标签
lst_my_path0=[] # json里面，要扫描的文件夹列表
lst_my_path_s=[]
dict_path=dict() # 用于列表简写和实际值

# 准备基础数据

with open('data.json','r',encoding='utf8')as fp:
    json_data = json.load(fp)
    # tag_data=json_data['tags']      #标签
    opt_data=json_data['options']   #设置
    
def split_path(inp): # 通用函数：将完整路径拆分
    test_str=inp.replace('\\', '/',-1)
    test_str_res=test_str.split('/')
    return(test_str_res)

# lst_my_path=lst_my_path0.copy() #按文件夹筛选用

for i in opt_data['tar']: 
    # lst_my_path0.append(i)
    tmp_L=i['pth']
    lst_my_path0.append(tmp_L)
    try:
        tmp_S=i['short']
    except:
        tmp_S=split_path(i['pth'])[-1]
    lst_my_path_s.append(tmp_S)
    tmp={tmp_S:tmp_L}
    dict_path.update(tmp)
    
# print(lst_my_path_s)

lst_my_path=lst_my_path_s.copy()

V_SEP=opt_data['sep'] # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
V_FOLDERS=int(opt_data['vfolders']) # 目录最末层数名称检查，作为标签的检查层数

#%%



def get_data(vpath=lst_my_path0):
    lst_file=list() #获取所有文件的完整路径
    for vPath in vpath:
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

def get_file_part(tar):
    # 这里 tar 是完整路径
    [fpath,ffname]=os.path.split(tar) # fpath 所在文件夹、ffname 原始文件名
    [fname,fename]=os.path.splitext(ffname) # fname 文件名前半部分，fename 扩展名
    lst_sp=fname.split(V_SEP) #拆分为多个片段
    fname_0 = lst_sp[0]+fename # fname_0 去掉标签之后的文件名
    ftags=lst_sp[1:] # ftags 标签部分
    
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
    
    return {'fname_0':fname_0,'ftags':ftags,'ffname':ffname,'fpath':fpath,'fename':fename,'tar':tar}
    
def sort_by_tag(elem):
    global ORDER_BY_N
    return str(elem[ORDER_BY_N])

def get_dt():
    
    dT=list()
    for tar in lst_file:
        tmp=get_file_part(tar)
        dT.append([tmp['fname_0'],tmp['ftags'],tmp['fpath'],tmp['tar']])
    
    # 获取所有tag
    tmp=[]
    for i in dT:
        tmp+=i[1]
    
    lst_tags=list(set(tmp))
    lst_tags=sorted(lst_tags, key=lambda x: x.encode('gbk'))
    lst_tags=[cALL_FILES]+lst_tags
    # lst_tags.sort()
    
    
    dT.sort(key=sort_by_tag)
    
    return (dT, lst_tags)

lst_file = get_data()
(dT, lst_tags)=get_dt()

#%%


window = tk.Tk() # 主窗口

# 上面功能区
frame0=ttk.LabelFrame(window,text='',height=80)#,width=600)
# frame0.grid(row=0,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frame0.pack(side=tk.TOP,expand=1,fill=tk.X,padx=10,pady=5)
frame0.pack(expand=0,fill=tk.X,padx=10,pady=5)

# 主功能区
frameMain=ttk.LabelFrame(window,text='')#,height=800)
# frameMain.grid(row=1,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frameMain.pack(side=tk.TOP,expand=1,fill=tk.BOTH,padx=10,pady=5)
frameMain.pack(expand=1,fill=tk.BOTH,padx=10,pady=0)

# 底部区
frameBtm=ttk.LabelFrame(window,text='',height=80)
# frameBtm.grid(row=2,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)
# frameBtm.pack(side=tk.BOTTOM,expand=1,fill=tk.X,padx=10,pady=5)
frameBtm.pack(expand=0,fill=tk.X,padx=10,pady=5)

columns = ("file", "tags", "path","file0")

bar1=tk.Scrollbar(frameMain,width=20) #右侧滚动条
bar2=tk.Scrollbar(frameMain,orient=tk.HORIZONTAL)#,width=20) #底部滚动条

str_btm=tk.StringVar() #最下面显示状态用的
str_btm.set("加载中")

tree = ttk.Treeview(frameMain, show = "headings", columns = columns, selectmode = tk.BROWSE, \
                    yscrollcommand = bar1.set,xscrollcommand = bar2.set)#, height=18)

tree.column('file', width=600, anchor='w')
tree.column('tags', width=400, anchor='w')
tree.column('path', width=20, anchor='w')
tree.column('file0', width=80, anchor='w')

tree.heading("file", text = "文件名",anchor='w')
tree.heading("tags", text = "标签",anchor='w')
tree.heading("path", text = "文件夹",anchor='w')
tree.heading("file0", text = "文件路径",anchor='w')


def add_tree_item(tree,dT,tag=''):
    k=0
    for i in range(len(dT)):
        tmp=dT[i]
        tag=str.lower(tag)
        tag_lower=[]
        for j in tmp[1]:
            tag_lower.append(str.lower(j))
            #搜索的时候转小写，避免找不到类似于MySQL这样的标签
            
        if tag=='' or tag==cALL_FILES or (tag in tag_lower) or str.lower(tmp[3]).find(tag)>0:
            k+=1
            if i%2==1:
                tree.insert('',i,values=(tmp[0],tmp[1],tmp[2],tmp[3]),tag='line1')
            else:
                tree.insert('',i,values=(tmp[0],tmp[1],tmp[2],tmp[3]))
    str_btm.set("找到 "+str(k)+" 个结果")
    # tree.insert('',i,values=(d[0][i],d[1][i],d[2][i],d[3][i]))

add_tree_item(tree,dT)

tree.tag_configure('line1', background='#cccccc') # 灰色底纹,然而无效



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

def input_new_tag(event=None):
    new_name=''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        tmp_file_name = get_file_part(tmp_full_name)['ffname']
        
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
    my_reload(0)

def my_reload(event=None):
    global lst_file,dT,lst_tags
    
    if not event==0:
        v_inp.delete(0,len(v_inp.get()))
    # v_inp.delete(0,len(v_inp.get()))
    
    lst_file = get_data(lst_my_path)
    (dT, lst_tags)=get_dt()
    # tree_clear(tree)

    v_tag_choose()
    v_tag['value']=lst_tags
    # tmp_tag=v_tag.get()
    # add_tree_item(tree,dT)

    pass

def my_help(event=None):
    os.startfile(URL_HELP)

#项目上，鼠标左键双击
tree.bind('<Double-Button-1>', treeOpen)
# 回车
tree.bind('<Return>', treeOpen)
# tree.bind('<ButtonPress-3>', input_newname) # 右键，此功能作废



# 搜索框
def tree_clear(tree):
    x=tree.get_children()
    for item in x:
        tree.delete(item)
        
def folder_s2l(inp):
    return dict_path[inp]
    pass

def v_folder_choose(event=None): # 获取文件夹名称
    global lst_my_path
    tmp=v_folders.get()
    if tmp=='':
        lst_my_path=lst_my_path0.copy()
    else:
        tmp=folder_s2l(tmp) #将显示值转换为实际值
        lst_my_path=[tmp]

    my_reload(lst_my_path)
    
def v_tag_choose(event=None):
    tmp_tag=v_tag.get()
    tree_clear(tree)
    add_tree_item(tree,dT,tag=tmp_tag)

def v_tag_key(event):
    print(event.char)

v_tag=ttk.Combobox(frame0)
v_folders=ttk.Combobox(frame0)

vPDX=10
vPDY=5
lable_folders=tk.Label(frame0, text = '文件夹')
# lable_tag.grid(row=0,column=1,padx=10, pady=5,sticky=tk.W)
lable_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_folders['value']=['']+lst_my_path
v_folders['state'] = 'readonly'
# v_folders.grid(row=0,column=2, padx=10, pady=5,sticky=tk.W)
v_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
v_folders.bind('<<ComboboxSelected>>', v_folder_choose)
v_folders.bind('<Return>',v_folder_choose) #绑定回车键

# bt_folders=ttk.Button(frame0,text='跳转',command=v_folder_choose)
# bt_folders.grid(row=0,column=3,padx=10, pady=5,sticky=tk.EW)
# bt_folders.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

lable_tag=tk.Label(frame0, text = '按标签或名称搜索')
# lable_tag.grid(row=0,column=11,padx=10, pady=5,sticky=tk.W)
lable_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_tag['value']=lst_tags
# v_tag['state'] = 'readonly'
# v_tag.grid(row=0,column=12,padx=10, pady=5,sticky=tk.W)
v_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
v_tag.bind('<<ComboboxSelected>>', v_tag_choose)
v_tag.bind('<Return>',v_tag_choose) #绑定回车键

bt_search=ttk.Button(frame0,text='搜索',command=v_tag_choose)
# bt_search.grid(row=0,column=13,padx=10, pady=5,sticky=tk.EW)
bt_search.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

lable_tag=tk.Label(frame0, text = '添加新标签')
# lable_tag.grid(row=2,column=20,padx=10, pady=5,sticky=tk.W)
lable_tag.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 

v_inp=ttk.Entry(frame0,width=16) # 新标签的输入框
# v_inp.grid(row=2,column=21 ,padx=10, pady=5)
v_inp.pack(side=tk.LEFT,expand=0,padx=vPDX,pady=vPDY) # 
v_inp.bind('<Return>',input_new_tag)

bt_clear=ttk.Button(frame0,text='点此添加标签',command=input_new_tag)
# bt_clear.grid(row=2,column=22,padx=10, pady=5,sticky=tk.EW)
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

bt_setting=ttk.Button(frameBtm,text='设置（开发中）',state=tk.DISABLED)#,command=my_reload)
# bt_setting.grid(row=2,column=50,padx=10, pady=5,sticky=tk.EW)
bt_setting.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

bt_clear=ttk.Button(frameBtm,text='刷新',command=my_reload)
# bt_clear.grid(row=0,column=20,padx=10, pady=5,sticky=tk.EW)
bt_clear.pack(side=tk.RIGHT,expand=0,padx=vPDX,pady=vPDY) # 

#%%

#%%
# 运行

window.title(TAR+' '+VER)
# 用于 grid 布局，已取消
# window.rowconfigure(2, weight=1)
# window.columnconfigure(1, weight=1)

# window.geometry("1600x800+100+50")


screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
w_width = int(screenwidth*0.85)
w_height = int(screenheight*0.8)
window.geometry('%dx%d+%d+%d'%(w_width, w_height, (screenwidth-w_width)/2, (screenheight-w_height)/2))

# window.resizable(0,0) #限制尺寸

window.mainloop() 