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
        self.CONFIG_FILE_NAME = 'options_for_tagdox.json'
        self.CONFIG_BAK_FILE_NAME = 'options_for_tagdox.bak.json'
        try:
            if isfile('../'+self.CONFIG_FILE_NAME):
                logging.debug('读取上级目录')
                self.OPTIONS_FILE = '../'+self.CONFIG_FILE_NAME
                self.OPTIONS_FILE_BAK = '../'+self.CONFIG_BAK_FILE_NAME
            elif isfile('D:/MyPython/开发数据/'+self.CONFIG_FILE_NAME):
                logging.debug('读取开发模式的配置文件')
                self.OPTIONS_FILE = 'D:/MyPython/开发数据/'+self.CONFIG_FILE_NAME
                self.OPTIONS_FILE_BAK = 'D:/MyPython/开发数据/'+self.CONFIG_BAK_FILE_NAME
            else:
                logging.debug('读取当前目录配置文件')
                self.OPTIONS_FILE = self.CONFIG_FILE_NAME  # 配置文件的名称
                self.OPTIONS_FILE_BAK = self.CONFIG_BAK_FILE_NAME  # 配置文件的名称
        except:
            logging.debug('读取标准模式的配置文件')
            self.OPTIONS_FILE = self.CONFIG_FILE_NAME  # 配置文件的名称 # 已改完
            self.OPTIONS_FILE_BAK = self.CONFIG_BAK_FILE_NAME  # 配置文件的名称
        #
        # 用于显示尺寸的设置
        self.ui_conf = {'FRAME_FOLDER_WIDTH': 360,
                        'FOLDER_STEP': 36,
                        'FRAME_README_HEIGHT': int(self.SCREEN_HEIGHT * 0.5),  #
                        'FRAME_RIGHT_WIDTH': 280,
                        'TREE_WIDTH_FILENAME': 600,
                        'TREE_WIDTH_TAGS': 200,
                        'TREE_WIDTH_MODIFY_TIME': 120,
                        'TREE_WIDTH_SIZE': 60
                        }
        self.ui = self.ui_conf  # 别名
        # 显示尺寸的配置文件
        try:
            with open('./resources/config/ui_conf.json', 'r') as f:
                ui_conf_ext = json.load(f)
            for _key in self.ui_conf.keys():
                if _key in ui_conf_ext.keys() and ui_conf_ext[_key]>0:
                    self.ui_conf[_key] = ui_conf_ext[_key]
            logging.debug(self.ui_conf)
        except:
            pass
        #
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
        self.QUICK_TAGS = ['@PIN', '@TODO', '@toRead', '@Done', '只读']  # 快速添加标签 # 已改完
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
        self.lst_open = []  # 用于存储始终展开的文件夹

    def exec_json_file_write(self, data=None):
        """
        将 json_data变量的值，写入 json 文件。
        可以不带参数，随时调用就是写入json。
        """
        if data is None:
            data = self.json_data
        try:
            with open(self.OPTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False,
                          indent=4, )
        except Exception as e:
            logging.error(f'配置文件写入异常:{e}')

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
            #
            # 加载设置项
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
            #
            # 加载文件夹
            if load_folders:
                # lst_my_path_long_selected=lst_my_path_long.copy() #按文件夹筛选用
                self.lst_my_path_long = []
                self.lst_my_path_short = []

                self.json_folders_lst = self.json_data['folders']

                for dict_folder in self.json_folders_lst:
                    # lst_my_path_long.append(dict_folder)
                    tmp_path = dict_folder['pth']  # 获取完整路径
                    tmp_path = tmp_path.strip().replace('\\', '/')
                    #
                    try:
                        tmp_short = dict_folder['short']  # 如果有自定义名称，优先加载
                    except Exception as e:
                        logging.debug(f"读取 {tmp_path} 的 short 属性不成功:{e}，忽略")
                        tmp_short = get_split_path(dict_folder['pth'])[-1]
                    tmp_short = tmp_short.replace(' ', '_')  # 修复路径空格bug的权宜之计，以后应该可以优化
                    #
                    try:
                        tmp_group = dict_folder['group']  # 分组名称
                    except Exception as e:
                        logging.debug(f"读取 {tmp_path} 的 group 属性不成功:{e}，忽略")
                        tmp_group = self.DEFAULT_GROUP_NAME
                    #
                    try:
                        tmp_open = dict_folder['open']  # 是否常开
                    except Exception as e:
                        logging.debug(f"读取 {tmp_path} 的 open 属性不成功:{e}，忽略")
                        tmp_open = 'normal'

                    # 增加逻辑：避免短路径重名：
                    j = 1
                    tmp_2 = tmp_short
                    while tmp_2 in self.lst_my_path_short:
                        j += 1
                        tmp_2 = f'{tmp_short}({j})'
                    tmp_short = tmp_2.strip()

                    if tmp_short == '' or tmp_path == '':  # 出现空白文件夹
                        for j in range(len(self.json_folders_lst) - 1, -1, -1):
                            if self.json_folders_lst[j]['pth'].strip() == '':
                                self.json_folders_lst.pop(j)
                    else:
                        self.lst_my_path_long.append(tmp_path)
                        self.lst_my_path_short.append(tmp_short)
                        #
                        self.dict_path.update({tmp_short: tmp_path})
                        #
                        tmp_folder_and_group = {tmp_short: tmp_group}
                        self.dict_folder_groups.update(tmp_folder_and_group)
                        # 常开文件夹
                        if tmp_open == 'always':
                            self.lst_open.append(tmp_path)

                self.lst_my_path_long_selected = self.lst_my_path_long.copy()  # 此处有大量的可优化空间。
                logging.info('加载关注文件夹列表成功')

        except Exception as e:
            logging.warning(f'加载json异常，正在重置json文件。 错误信息为：{e}')
            # need_init_json=1
            try:
                # 尝试将旧文件备份一次，避免全部丢失；
                with open(self.OPTIONS_FILE, 'r', encoding='utf8') as fp:
                    tmp_old_txt = fp.read()
                with open(self.OPTIONS_FILE_BAK, 'w+', encoding='utf8') as f:
                    f.write(tmp_old_txt)
            except Exception as e:
                logging.error(f"尝试备份旧文件错误： {e}")
                pass
            self.json_data = self.OPT_DEFAULT
            self.exec_json_file_write()

    def get_current_folder_detail(self):
        """
        获取当前打开的文件夹，或者文件夹分组
        """
        tmp = {'type': 'folder',
               'path': self.lst_my_path_long_selected,
               'short_name': self.lst_my_path_short,
               }
        return tmp

    def get_current_path(self):
        """
        获取当前正在打开的文件夹。只返回一个，
        如果是分组，就返回第一个结果.
        """
        try:
            return self.lst_my_path_long_selected[0]
        except:
            return ''

    def folder_open_off(self, folder_short=None, folder_path=None):
        """
        去掉文件夹的常开状态
        """
        logging.debug(f"folder_short={folder_short}, folder_path={folder_path}")
        if folder_short:
            folder_long = self.dict_path[folder_short]
        elif folder_path:
            folder_long = folder_path
        else:
            logging.error(f"ERROR: folder_short={folder_short}, folder_path={folder_path}")
            return
        if folder_long in self.lst_open:
            self.lst_open.remove(folder_long)
            for tmp_dict in self.json_data['folders']:
                if tmp_dict['pth'].replace('\\', '/') == folder_long:
                    tmp_dict['open'] = 'normal'
                    break
        self.exec_json_file_write()

    def folder_open_on(self, folder_short=None, folder_path=None):
        """
        增加文件夹的常开状态
        """
        logging.debug(f"folder_short={folder_short}, folder_path={folder_path}")
        if folder_short:
            folder_long = self.dict_path[folder_short]
        elif folder_path:
            folder_long = folder_path
        else:
            logging.error(f"ERROR: folder_short={folder_short}, folder_path={folder_path}")
            return
        if folder_long not in self.lst_open:
            self.lst_open.append(folder_long)
            for tmp_dict in self.json_data['folders']:
                if tmp_dict['pth'].replace('\\', '/')  == folder_long:
                    tmp_dict['open'] = 'always'
                    break
        self.exec_json_file_write()
