# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 16:05:43 2021

@author: MaJian
"""

# 用于可视化配置设置参数
# 准备基础数据
import os
# 用tk的表格处理
import tkinter as tk
from tkinter import ttk
import json

with open('data.json','r',encoding='utf8')as fp:
    json_data = json.load(fp)
    # tag_data=json_data['tags']      #标签
    opt_data=json_data['options']   #设置
    
lst_my_path=[]
for i in opt_data['tar']:
    lst_my_path.append(i)

V_SEP=opt_data['sep'] # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
V_FOLDERS=int(opt_data['vfolders']) # 目录最末层数名称检查，作为标签的检查层数

#%%
#设置

form_setting=tk.Tk()
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

def setting_yes(event=None):
    # 获得新参数
    
    pass

bt_setting_yes=ttk.Button(form_setting,text='确定',command=setting_yes)
bt_setting_yes.grid(row=10,column=0,padx=10, pady=5,sticky=tk.EW)

bt_setting_cancel=ttk.Button(form_setting,text='取消',command=form_setting.destroy)
bt_setting_cancel.grid(row=10,column=1,padx=10, pady=5,sticky=tk.EW)

form_setting.title('设置')
form_setting.resizable(0,0) #限制尺寸
form_setting.grab_set()
form_setting.mainloop() 