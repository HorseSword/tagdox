# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 09:28:24 2021

@author: MaJian
"""


import os
# 用tk的表格处理
import tkinter as tk
from tkinter import ttk
import json

cALL_FILES='( 全部 )'
lst_file=[] # 所有文件的完整路径
dT=[]
lst_tags=[] # 全部标签
URL_HELP='https://gitee.com/horse_sword/my-local-library'
TAR='我的文库'
VER='v0.5.1'

#%%

# 准备基础数据

with open('data.json','r',encoding='utf8')as fp:
    json_data = json.load(fp)
    # tag_data=json_data['tags']      #标签
    opt_data=json_data['options']   #设置
    
lst_my_path=[]
for i in opt_data['tar']:
    lst_my_path.append(i)

V_SEP=opt_data['sep'] # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。

#%%
def get_data():
    lst_file=list() #获取所有文件的完整路径
    for vPath in lst_my_path:
        for root, dirs, files in os.walk(vPath):
            for name in files:
                lst_file.append(os.path.join(root, name)) 
    return lst_file

def get_file_part(tar):
    # 这里 tar 是完整路径
    [fpath,ffname]=os.path.split(tar) #所在文件夹、原始文件名
    [fname,fename]=os.path.splitext(ffname) #文件名前半部分，扩展名
    lst_sp=fname.split(V_SEP) #拆分为多个片段
    fname_0 = lst_sp[0]+fename #fname_0 去掉标签之后的文件名
    ftags=lst_sp[1:] #标签部分
    # 增加对文件目录带井号的解析
    tmp=fpath.split(V_SEP)
    if len(tmp)>1:
        for j in tmp[1:]:
            if j.find('\\')<0 and j.find('/')<0:
                ftags.append(j) # 只对最后的文件夹带井号的有反应
    ftags=list(set(ftags))
    ftags.sort()
    
    return {'fname_0':fname_0,'ftags':ftags,'ffname':ffname,'fpath':fpath,'fename':fename,'tar':tar}
    
def sort_by_tag(elem):
    return str(elem[1])

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


window = tk.Tk()

# 上面功能区
frame0=ttk.LabelFrame(window,text='',height=80,width=600)
frame0.grid(row=0,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)

# 主功能区
frameMain=ttk.LabelFrame(window,text='',height=800)
frameMain.grid(row=1,column=0,columnspan=2,padx=10, pady=5,sticky=tk.NSEW)

columns = ("file", "tags", "path","file0")

bar1=tk.Scrollbar(frameMain,width=20) #右侧滚动条

str_btm=tk.StringVar() #最下面显示状态用的
str_btm.set("加载中")

tree = ttk.Treeview(frameMain, show = "headings", columns = columns, selectmode = tk.BROWSE, \
                    yscrollcommand = bar1.set, height=18)

tree.column('file', width=800, anchor='w')
tree.column('tags', width=400, anchor='w')
tree.column('path', width=80, anchor='center')
tree.column('file0', width=80, anchor='center')

tree.heading("file", text = "文件名")
tree.heading("tags", text = "标签")
tree.heading("path", text = "文件夹")
tree.heading("file0", text = "文件路径")


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
# tree.pack(expand = True, fill = tk.BOTH)

style = ttk.Style()
LARGE_FONT=12
MON_FONTSIZE=10

# style.configure("Treeview.Heading", font=(None, 12),rowheight=60)
style.configure("Treeview.Heading", font=(None, LARGE_FONT), \
                rowheight=int(LARGE_FONT*2.5))

style.configure("Treeview", font=(None, MON_FONTSIZE), rowheight=int(MON_FONTSIZE*3.5))

# 行高
# style.configure("Treeview.Heading", font=(None, 12))

# 获取当前点击行的值
def treeOpen(event): #单击
    for item in tree.selection():
        item_text = tree.item(item, "values")
        print(item_text[-1])
        os.startfile(item_text[-1]) #打开这个文件
        
def treeKey(event):
    print("检测到按键")

def input_new_tag(event=None):
    new_name=''
    for item in tree.selection():
        item_text = tree.item(item, "values")
        tmp_full_name = item_text[-1]
        tmp_file_name = get_file_part(tmp_full_name)['ffname']
        
        # new_tag = tk.simpledialog.askstring(title="添加标签", prompt="请输入新的标签")#, initialvalue=tmp)
        new_tag=v_inp.get()
        
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
    
    lst_file = get_data()
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
# tree.bind('<ButtonPress-3>', input_newname) # 右键，此功能作废



# 搜索框
def tree_clear(tree):
    x=tree.get_children()
    for item in x:
        tree.delete(item)
    
def v_tag_choose(event=None):
    tmp_tag=v_tag.get()
    tree_clear(tree)
    add_tree_item(tree,dT,tag=tmp_tag)

def v_tag_key(event):
    print(event.char)

v_tag=ttk.Combobox(frame0)

lable_tag=tk.Label(frame0, text = '按标签或名称搜索')
lable_tag.grid(row=0,column=0,padx=10, pady=5,sticky=tk.W)

v_tag['value']=lst_tags
# v_tag['state'] = 'readonly'
v_tag.grid(row=0,column=1,padx=10, pady=5,sticky=tk.W)
v_tag.bind('<<ComboboxSelected>>', v_tag_choose)
v_tag.bind('<Return>',v_tag_choose) #绑定回车键

lable_tag=tk.Label(frame0, text = '添加新标签')
lable_tag.grid(row=0,column=2,padx=10, pady=5,sticky=tk.W)

v_inp=ttk.Entry(frame0,width=16)
v_inp.grid(row=0,column=3 ,padx=10, pady=5)
v_inp.bind('<Return>',input_new_tag)

bt_clear=ttk.Button(frame0,text='点此添加标签',command=input_new_tag)
bt_clear.grid(row=0,column=4,padx=10, pady=5,sticky=tk.EW)

bt_clear=ttk.Button(frame0,text='刷新',command=my_reload)
bt_clear.grid(row=0,column=6,padx=10, pady=5,sticky=tk.EW)

bt_help=ttk.Button(frame0,text='使用说明',command=my_help)
bt_help.grid(row=0,column=99,padx=10, pady=5,sticky=tk.EW)

# 布局
tree.grid(row=1,column=0,padx=10, pady=5,sticky=tk.NSEW)
# tree.place(anchor=tk.W,relheight=1)

bar1.grid(row=1,column=1,sticky=tk.NS)
# bar1.place(x=0,y=0,anchor=tk.NE)



lable_sum=tk.Label(window, text = str_btm,textvariable=str_btm)

lable_sum.grid(row=2,column=0,padx=10, pady=5,sticky=tk.W)

#%%
# 运行

window.title(TAR+' '+VER)
# window.geometry("1600x800+100+50")
window.rowconfigure(2, weight=1)
window.columnconfigure(1, weight=1)

window.resizable(0,0) #限制尺寸
window.mainloop() 