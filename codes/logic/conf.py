import json
from os.path import isfile
from libs.common_funcs import get_split_path
import logging


class td_conf:
    """
    用于存储设置项.
    用法：
    conf = td_conf()
    conf.ui_ratio = xxx
    """

    def __init__(self):
        self.name = 'tagdox'
        self.ui_ratio = 1.0
        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1080
        self.V_SEP = '^'  # 标签分隔符。// 可修改 # 已改完
        self.V_FOLDERS = 2  # 标签识别文件夹深度，// 可修改 # 已改完
        self.TREE_SUB_SHOW = 'sub_folder'  # 这个项目不再允许调整。 # 已改完
        self.FILE_DRAG_MOVE = 'move'  # 文件拖动到列表的时候，是复制，还是移动。// 可修改。# 取值：'move' 'copy'。 # 已改完
        try:
            if isfile('../options_for_tagdox.json'):
                logging.debug('读取上级目录')
                self.OPTIONS_FILE = '../options_for_tagdox.json'
            elif isfile('D:/MyPython/开发数据/options_for_tagdox.json'):
                logging.debug('读取开发模式的配置文件')
                self.OPTIONS_FILE = 'D:/MyPython/开发数据/options_for_tagdox.json'
            else:
                logging.debug('读取当前目录配置文件')
                self.OPTIONS_FILE = 'options_for_tagdox.json'  # 配置文件的名称
        except:
            logging.debug('读取标准模式的配置文件')
            self.OPTIONS_FILE = 'options_for_tagdox.json'  # 配置文件的名称 # 已改完

        self.OPT_DEFAULT = {
            "options": {
                "sep": "^",
                "vfolders": "2",
                "note_ext": ".docx",
                "file_drag_enter": "copy",
                "TREE_SUB_SHOW": self.TREE_SUB_SHOW
            },
            "folders": [
            ]
        }
        self.json_data = self.OPT_DEFAULT  # 已改完
        self.opt_data = self.json_data['options']  # 设置
        self.json_folders_lst = self.json_data['folders']
        #
        self.NOTE_EXT_LIST = ['.md', '.txt', '.docx', '.rtf', '.mm']  # 已改完
        self.NOTE_EXT = '.docx'  # 新建笔记的类型 // 可修改 # 已改完
        self.QUICK_TAGS = ['@PIN', '@TODO', '@toRead', '@Done']  # 快速添加标签 # 已改完
        #
        self.DEFAULT_GROUP_NAME = '默认文件夹分组'  # 已改完

        self.TAG_EASY = 1  # 标签筛选是严格模式还是简单模式，1是简单模式，名称有就行；0是严格模式。 // 可修改 # 已改完
        self.FOLDER_AS_TAG = 0  # 最后多少层文件夹名称，强制作为标签（即使不包括V_SEP） // 可修改 # 已改完
        self.ORDER_BY_N = 2  # 初始按哪一列排序，1代表标签，后面按顺序对应 # 已改完
        self.ORDER_DESC = True  # 是否逆序 # 已改完
        self.NOTE_NAME_DEFAULT = '未命名笔记'  # 新建笔记的默认名称 # 已改完
        self.EXP_FOLDERS = ['_img', '.git']  # 排除文件夹名称，以后会加到自定义里面 # 已改完
        self.EXP_DOT_FOLDERS = True  # 排除点开头的文件夹
        self.EXP_EXTS = ['.md', '.MD']  # 排除扩展名，这里面的强制采用传统标签； # 已改完

        self.LARGE_FONT = 10  # 表头字号
        self.MON_FONTSIZE = 9  # 正文字号
        self.FONT_TREE_HEADING = ('微软雅黑', self.LARGE_FONT)
        self.FONT_TREE_BODY = ('微软雅黑', self.MON_FONTSIZE)
        #
        self.dict_path = dict()  # 用于列表简写：实际值 # 已改完
        self.dict_folder_groups = dict()  # 组名： # 已改完
        self.lst_my_path_long_selected = []  # 已改完
        self.lst_my_path_short = []  # 已改完
        self.lst_my_path_long = []  # 已改完

    def exec_json_file_write(self, data=None):
        """
        将 json_data变量的值，写入 json 文件。
        可以不带参数，随时调用就是写入json。
        """
        if data is None:
            data = self.json_data
        try:
            with open(self.OPTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logging.error('json文件写入异常', e)

    def get_json(self):
        """
        将自身关键词转换为json格式
        """
        pass

    def set_json_options(self, key1, value1, need_write=True):
        """
        修改设置项，以键值对的方式修改。
        会自动触发 exec_update_json（写入json文件）.
        参数 need_write 代表了是否需要写入文件。默认是修改后立刻写入。
        """
        self.opt_data = self.json_data['options']  # 设置
        self.opt_data[key1] = value1
        #
        if need_write:
            self.exec_json_file_write(data=self.json_data)

    def exec_json_file_load(self, load_settings=True, load_folders=True):
        """
        读取json文件，获取其中的参数，并存储到相应的变量中。

        如果json文件读取失败，则按照初始化标准重建这个文件。

        依赖函数：update_json。
        """
        self.dict_folder_groups = dict()
        need_init_json = 0
        try:
            with open(self.OPTIONS_FILE, 'r', encoding='utf8') as fp:
                self.json_data = json.load(fp)

            if load_settings:
                try:
                    self.opt_data = self.json_data['options']  # 设置
                except Exception as e:
                    logging.warning(e)
                    pass
                try:
                    self.V_SEP = self.opt_data['sep']  # 分隔符，默认是 # 号，也可以设置为 ^ 等符号。
                except Exception as e:
                    logging.warning(e)
                    pass
                try:
                    self.V_FOLDERS = int(self.opt_data['vfolders'])  # 目录最末层数名称检查，作为标签的检查层数
                except Exception as e:
                    logging.warning(e)
                try:
                    self.NOTE_EXT = self.opt_data['note_ext']  # 默认笔记类型
                except Exception as e:
                    logging.warning(e)
                    pass
                try:
                    self.FILE_DRAG_MOVE = self.opt_data['file_drag_enter']  # 默认拖动操作
                except Exception as e:
                    logging.warning(e)
                    pass
                # try:
                #     TREE_SUB_SHOW = opt_data['TREE_SUB_SHOW']  # 默认布局
                # except Exception as e:
                #     print(e)
                #     pass

                #
                try:
                    self.FOLDER_AS_TAG = self.opt_data['FOLDER_AS_TAG']  # 最后文件夹识别
                except Exception as e:
                    logging.warning(e)
                    pass
                #
                try:
                    self.TAG_EASY = self.opt_data['TAG_EASY']  # 标签搜索方式
                except Exception as e:
                    logging.warning(e)
                    pass
                #
                logging.info('加载基本参数成功')

            if load_folders:
                # lst_my_path_long_selected=lst_my_path_long.copy() #按文件夹筛选用
                self.lst_my_path_long = []
                self.lst_my_path_short = []

                self.json_folders_lst = self.json_data['folders']

                for i in self.json_folders_lst:
                    # lst_my_path_long.append(i)
                    tmp_L = i['pth']
                    tmp_L = tmp_L.strip()
                    #
                    try:
                        tmp_S = i['short']  # 如果有自定义名称，优先加载
                    except:
                        tmp_S = get_split_path(i['pth'])[-1]
                    #
                    try:
                        tmp_G = i['group']  # 分组名称
                    except:
                        tmp_G = self.DEFAULT_GROUP_NAME

                    tmp_S = tmp_S.replace(' ', '_')  # 修复路径空格bug的权宜之计，以后应该可以优化

                    # 增加逻辑：避免短路径重名：
                    j = 1
                    tmp_2 = tmp_S
                    while tmp_2 in self.lst_my_path_short:
                        j += 1
                        tmp_2 = tmp_S + "(" + str(j) + ")"
                        print(tmp_2)
                    tmp_S = tmp_2
                    tmp_S = tmp_S.strip()

                    if tmp_S == '' or tmp_L == '':  # 出现空白文件夹
                        for j in range(len(self.json_folders_lst) - 1, -1, -1):
                            if self.json_folders_lst[j]['pth'].strip() == '':
                                self.json_folders_lst.pop(j)
                    else:
                        self.lst_my_path_long.append(tmp_L)
                        self.lst_my_path_short.append(tmp_S)
                        #
                        tmp = {tmp_S: tmp_L}
                        self.dict_path.update(tmp)
                        #
                        tmp_folder_and_group = {tmp_S: tmp_G}
                        self.dict_folder_groups.update(tmp_folder_and_group)

                self.lst_my_path_long_selected = self.lst_my_path_long.copy()  # 此处有大量的可优化空间。
                logging.info('加载关注文件夹列表成功')
        except:
            logging.warning('加载json异常，正在重置json文件')
            # need_init_json=1
            self.json_data = self.OPT_DEFAULT
            self.exec_json_file_write()
