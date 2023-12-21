"""
用于支持文件操作的功能集合。
包括，复制文件的时候找到目标文件夹，
可用名称，
"""
import os
import stat
import shutil
from os.path import isdir
from os.path import isfile
import logging

USE_STATE = False  # 是否将结果以键值对的方式返回


def safe_get_name(new_name: str, sep: str = '') -> str:
    """
    用于检查目标位置的可用安全且未被占用的文件名。
    输入和输出都是字符串。
    :param new_name: 目标全路径;
    :param sep: 名称冲突时用于检查本体和序号的分隔符
    :return: 安全的新路径（可用于重命名、新建等）
    """
    n = 1
    [tmp_path, tmp_new_name] = os.path.split(new_name)

    if len(sep) > 0:  # 如果有分隔符，比如 conf.V_SEP
        p = tmp_new_name.find(sep)  # 找到标签分隔符
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
    else:
        p = tmp_new_name.rfind('.')
        if p >= 0:
            name_1 = tmp_new_name[:p]
            name_2 = tmp_new_name[p:]
        else:  # 连'.'都没有的话
            name_1 = tmp_new_name
            name_2 = ''

    tmp_new_full_name = new_name
    while isfile(tmp_new_full_name):  # 如果有文件，就增加序号，直到没有重名为止
        tmp_new_name = name_1 + '(' + str(n) + ')' + name_2
        tmp_new_full_name = tmp_path + '/' + tmp_new_name
        n += 1
    # print(tmp_new_full_name)
    return tmp_new_full_name


def safe_rename(old_name, new_name, sep=''):
    """
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 如果重命名成功，返回添加数字之后的最终文件名；
    如果重命名失败，返回原始文件名。
    """
    old_name = old_name.replace('\\', '/')
    new_name = new_name.replace('\\', '/')
    '''
    n=1
    [tmp_path,tmp_new_name]=os.path.split(new_name)
    # tmp_path=''
    # tmp_new_name=new_name
    p=tmp_new_name.find(conf.V_SEP)
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
    tmp_new_full_name = safe_get_name(new_name, sep=sep)  # 获取可以使用的安全名称
    try:
        if is_read_only(old_name):
            clear_read_only(old_name)
        os.rename(old_name, tmp_new_full_name)
        return tmp_new_full_name
    except Exception as e:
        raise IOError('安全重命名失败！错误信息：' + str(e))
        # print('安全重命名失败！')
        # return (old_name)


def safe_copy(old_name: str, new_name: str, opt_type: str = 'copy', sep: str = ''):
    """
    安全复制或移动文件。

    :param opt_type:  'copy' 或 'move'。
    :param old_name: 旧的文件完整路径
    :param new_name: 新的文件完整路径（含文件名）
    :param sep: 分隔符
    :return: 操作之后的文件路径，如果成功返回新路径。
    """
    old_name = old_name.replace('\\', '/')
    new_name = new_name.replace('\\', '/')
    #
    # 完全相同的路径不需要执行移动操作
    if old_name == new_name and opt_type == 'move':
        print('原始路径和新路径一致，跳过')
        return old_name
    #
    tmp_new_full_name = safe_get_name(new_name, sep=sep)
    print('开始安全复制')
    print(old_name)
    print(tmp_new_full_name)
    if opt_type == 'copy':
        try:
            shutil.copy(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name)
            print('安全复制成功')
            # os.rename(old_name,tmp_new_full_name)
            return tmp_new_full_name
        except Exception as e:
            raise IOError('文件复制失败！文件：' + str(old_name) + '错误信息：' + str(e))
            # tk.messagebox.showerror(title='错误',
            #                         message='文件复制失败。')
            # print('对以下文件复制失败！')
            # print(old_name)
            # return (old_name)
            # pass
    elif opt_type == 'move':
        try:
            if is_read_only(old_name):
                clear_read_only(old_name)
            shutil.move(old_name, tmp_new_full_name)
            # os.popen('copy '+ old_name +' '+ tmp_new_full_name)
            print('安全移动成功')
            # os.rename(old_name,tmp_new_full_name)
            return tmp_new_full_name
        except Exception as e:
            raise IOError('文件移动失败！文件：' + str(old_name) + '错误信息：' + str(e))
            # tk.messagebox.showerror(title='错误',
            #                         message='文件移动失败。')
            # print('对以下文件移动失败！')
            # print(old_name)
            # return (old_name)


def safe_move(old_name: str, new_name: str, opt_type: str = 'move', sep='', ):
    safe_copy(old_name, new_name, opt_type='move', sep=sep)


def is_read_only(file_path):
    """
    用于判断是否为只读文件
    """
    # 获取文件的权限模式
    mode = os.stat(file_path).st_mode
    # 检查是否可写
    is_writable = bool(mode & stat.S_IWRITE)
    # 如果不可写，则为只读
    return not is_writable


def set_read_only(file_path):
    # 设置文件为只读
    os.chmod(file_path, os.stat(file_path).st_mode & ~stat.S_IWRITE)


def clear_read_only(file_path):
    # 清除文件的只读属性，使其变为可写
    os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IWRITE)


if __name__ == '__main__':
    # 本地测试
    print(safe_copy('./my_filetools.py', './my_filetools.bak'))
