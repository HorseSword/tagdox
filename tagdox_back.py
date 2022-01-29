# 后端代码
# 后端的主要作用是文件的检索、返回等。
# 从设计原则上讲，尽量不涉及全局变量比较合适，都用传参的方式处理。

import os
import json
from os.path import isdir
from os.path import isfile
import time
import threading  # 多线程
from multiprocessing import Pool  # 进程
from multiprocessing import Process
import shutil
import queue
#
import subprocess  # 用于打开文件所在位置并选中文件

from libs.common_funcs import get_split_path


def show_msg_success(msg):
    print(msg)


def show_msg_error(msg):
    print(msg)
    # if False:
    #     tk.messagebox.showerror(title='错误',
    #                             message='文件移动失败。')


def exec_safe_rename_v2(old_name: str, new_name: str):
    """
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 如果重命名成功，返回(1,添加数字之后的最终文件名)；
    如果重命名失败，返回(0,原始文件名)。
    """
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
        return 1, tmp_new_full_name
    except:
        print('安全重命名失败！')
        return 0, old_name,
        pass


def safe_get_name(new_name: str, v_sep='^') -> str:
    """

    输入: 目标全路径;
    返回: 安全的新路径（可用于重命名、新建等）
    输入和输出都是字符串。

    """
    n = 1
    [tmp_path, tmp_new_name] = os.path.split(new_name)

    p = tmp_new_name.find(v_sep)
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
    return tmp_new_full_name


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
        show_msg_error('原始路径和新路径一致，跳过')
        return 7, old_name
    #
    tmp_new_full_name = safe_get_name(new_name)
    print('开始安全复制')
    print(old_name)
    print(tmp_new_full_name)
    if opt_type == 'copy':
        try:
            shutil.copy(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name)
            show_msg_success('安全复制成功')
            # os.rename(old_name,tmp_new_full_name)
            return 1, tmp_new_full_name
        except:
            res_message = '对以下文件复制失败！' + 'old_name'
            show_msg_error(res_message)
            return 0, old_name,
            pass
    elif opt_type == 'move':
        try:
            shutil.move(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name)
            show_msg_success('安全移动成功')
            # os.rename(old_name,tmp_new_full_name)
            return 1, tmp_new_full_name
        except:
            res_message = '对以下文件移动失败！' + 'old_name'
            show_msg_error(res_message)
            return 0, old_name
            pass


class TagdoxOptions:
    """
    配置文件类。

    """

    def __init__(self):
        self.lst_my_path_short = []
        self.lst_my_path_long = []
        self.lst_my_path_long_selected = []

        self.dict_path = {}
        self.dict_folder_groups = {}

        self.folder_path = ''  # 目标文件所在文件夹路径
        # self.DEFAULT_FILEPATH = 'D:/MyPython/开发数据/options_for_tagdox.json'
        self.DEFAULT = {
            'FILEPATH': 'D:/MyPython/开发数据/options_for_tagdox.json',
            'DEFAULT_GROUP_NAME': "默认文件夹分组",

        }
        # global json_data
        # global dict_folder_groups  # 文件夹对应分组

        try:
            if isfile(self.DEFAULT['FILEPATH']):
                print('读取开发模式的配置文件')
                self.file_path = self.DEFAULT['FILEPATH']
            else:
                print('读取标准模式的配置文件（相同路径下）')
                self.file_path = 'options_for_tagdox.json'  # 配置文件的名称
        except Exception as e:
            print('读取标准模式的配置文件（相同路径下）')
            self.file_path = 'options_for_tagdox.json'  # 配置文件的名称

        self.DEFAULT_DATA = {
            "options": {
                "sep": "^",
                "vfolders": "2",
                "note_ext": ".docx",
                "file_drag_enter": "copy",
                "TREE_SUB_SHOW": 'sub_folder',
                #
                'FOLDER_AS_TAG': '',
                'TAG_EASY': "",
            },
            "folders": [
            ]
        }  # 目标文件内容
        self.options = self.DEFAULT_DATA['options'].copy()
        self.folders = self.DEFAULT_DATA['folders'].copy()
        #
        self.data = {'options': self.options,
                     'folders': self.folders,
                     }

    def set_option_by_key(self, key1, value1, need_write=True) -> int:
        """
        修改设置项，以键值对的方式修改。
        会自动触发 exec_update_json（写入json文件）.
        参数 need_write 代表了是否需要写入文件。默认是修改后立刻写入。
        """
        try:
            self.options.update({key1: value1})
            #
            if need_write:
                self.exec_options_file_write()
                # exec_json_file_write(data=json_data)
            # exec_json_file_load()
            pass
            return 1
        except:
            print('修改设置发生错误')
            return 0

    def exec_options_file_write(self, tar=None, data=None) -> None:
        """
        将 json_data 变量的值，写入 json 文件。
        可以不带参数，随时调用就是写入 json。
        """
        tar = self.file_path if tar is None else tar
        data = self.data if data is None else data
        try:
            with open(tar, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print('json文件写入异常: ', e)

    def exec_options_file_load(self, load_settings=True, load_folders=True) -> None:
        """
        读取json文件，获取其中的参数，并存储到相应的变量中。

        如果json文件读取失败，则按照初始化标准重建这个文件。

        依赖函数：update_json。
        """

        dict_folder_groups = dict()

        need_init_json = 0
        try:
            with open(self.file_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)  # 读取到的内容

            if load_settings:  # 加载设置部分
                try:
                    opt_data = json_data['options']  # 设置
                    self.set_option_by_key('sep', opt_data['sep'], False)  # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
                    self.set_option_by_key('vfolders', int(opt_data['vfolders']), False)  # 目录最末层数名称检查，作为标签的检查层数
                    self.set_option_by_key('note_ext', opt_data['note_ext'], False)  # 默认笔记类型。
                    self.set_option_by_key('file_drag_enter', opt_data['file_drag_enter'], False)  # 默认拖动操作
                    self.set_option_by_key('sub_folder', 'sub_folder', False)  # 这个项目不再允许调整，而且不再起作用。
                    self.set_option_by_key('FOLDER_AS_TAG', opt_data['FOLDER_AS_TAG'], False)  # 最后文件夹识别。
                    self.set_option_by_key('TAG_EASY', opt_data['TAG_EASY'], False)  # 标签搜索方式
                    #
                    print('加载基本参数成功')

                except Exception as e:
                    print(e)
                    print('加载基本参数失败')
                    pass

            if load_folders:
                # lst_my_path_long_selected=lst_my_path_long.copy() #按文件夹筛选用
                self.lst_my_path_long = []
                self.lst_my_path_short = []

                json_folders_lst = json_data['folders']  # 读取到的文件夹数据部分

                for i in json_folders_lst:
                    # lst_my_path_long.append(i)
                    tmp = {'pth': i['pth'].strip()}
                    #
                    try:
                        tmp['short'] = i['short']  # 如果有自定义名称，优先加载
                    except:
                        tmp['short'] = get_split_path(i['pth'])[-1]
                    #
                    try:
                        tmp['group'] = i['group']  # 分组名称
                    except:
                        tmp['group'] = self.DEFAULT['DEFAULT_GROUP_NAME']
                    #
                    # 其他处理
                    tmp['short'] = tmp['short'].replace(' ', '_')  # 修复路径空格bug的权宜之计，以后应该可以优化

                    # 增加逻辑：避免短路径重名：
                    j = 1
                    tmp_2 = tmp['short']
                    while tmp_2 in self.lst_my_path_short:
                        j += 1
                        tmp_2 = tmp['short'] + "(" + str(j) + ")"
                        print('tmp2=', tmp_2)
                    tmp['short'] = tmp_2.strip()

                    if tmp['short'] == '' or tmp['pth'] == '':  # 出现空白文件夹
                        for j in range(len(json_folders_lst) - 1, -1, -1):
                            if json_folders_lst[j]['pth'].strip() == '':
                                json_folders_lst.pop(j)
                    else:
                        self.lst_my_path_long.append(tmp['pth'])
                        self.lst_my_path_short.append(tmp['short'])
                        #
                        self.dict_path.update({tmp['short']: tmp['pth']})
                        self.dict_folder_groups.update({tmp['short']: tmp['group']})

                self.lst_my_path_long_selected = self.lst_my_path_long.copy()  #
                # 此处有大量的可优化空间。
                print('加载关注文件夹列表成功')
                # 加载成功后，保存
                self.folders += json_folders_lst

        except Exception as e:
            print('加载json异常，错误为：', e, '；即将重置json文件')
            # need_init_json=1
            # 备份之前的文件；
            # self.file_path
            try:
                exec_safe_copy(self.file_path, self.file_path, 'copy')
                # 写新文件
                self.data = self.DEFAULT_DATA
                self.exec_options_file_write()
            except Exception as e:
                print('发生错误：', e)


if __name__ == '__main__':
    d = TagdoxOptions()
    d.exec_options_file_load()

    pass
