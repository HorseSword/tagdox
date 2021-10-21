"""
本文件用于处理markdown文件的移动问题，尤其是对于相对路径的移动有一定的自动化处理能力。
思路是：如果有md文件需要移动/复制的话，
- 检索md文件中的绝对链接和相对链接；
- 将这些相对链接的文件放在新的目标位置；
    - 如果目标位置已经有同名文件+同文件大小，跳过；否则提醒是跳过、保留且修改还是怎样。
"""
import re
import os
import shutil


def find_links(filepath: str):
    """
    查找md文件中的超链接，并返回绝对链接和相对链接（列表）。
    其中的相对路径开头没有斜杠，所以要手动补充斜杠获取绝对路径。

    :param filepath: 文件完整路径

    :return: Tuple(res_abs,res_rel): 绝对链接（列表），相对链接（列表）

    """

    pattern1 = re.compile(r'<img src=".+"?')
    pattern11 = re.compile(r'src=".+?"')
    pattern2 = re.compile(r'\[.*]\(.+\)?')
    pattern21 = re.compile(r'\(.+?\)+?')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk') as f:
            data = f.readlines()
    except Exception as e:
        print(e)
    finally:
        pass

    lst1 = []
    lst2 = []
    for i in data:
        for j in pattern1.findall(i):
            lst1 += pattern11.findall(j)
        for j in pattern2.findall(i):
            lst2 += pattern21.findall(j)
    res = []
    for i in lst1:
        res.append(i[5:-1])
    for i in lst2:
        res.append(i[1:-1])

    res_abs = []
    res_rel = []
    pattern_head = re.compile(r'^(.+?)(/+?)')

    for p in res:
        p = str(p).replace('\\', '/')
        try:
            if str(p).find('/') >= 0:
                if str(pattern_head.findall(p)[0]).find(':') >= 0:
                    res_abs.append(p)
                else:
                    res_rel.append(p)
            else:
                res_rel.append(p)
        except Exception as e:
            print(p)
            print(e)

    return res_abs, res_rel


def copy_md_linked_files(file_path_old: str, new_path, mode='copy'):
    """

    :param file_path_old: md文件所在完整路径（包括文件名）
    :param new_path: md文件目标位置（文件夹）
    :param mode: 移动或者复制
    :return:
    """
    lst_links_abs, lst_links_rel = find_links(file_path_old)
    fpath, fname = os.path.split(file_path_old)

    for p in lst_links_rel:
        old_pth = fpath.replace('\\', '/') + '/' + p  # 原位置
        print(old_pth)
        tar_pth = new_path.replace('\\', '/')
        if tar_pth.endswith('/'):
            tar_pth = tar_pth + p
        else:
            tar_pth = tar_pth + '/' + p
        print(tar_pth)
        tarp, tarfn = os.path.split(tar_pth)
        if not os.path.exists(tarp):
            os.makedirs(tarp)
        try:
            shutil.copyfile(old_pth, tar_pth)  # 目前，附件永远是复制，因为移动可能存在其他问题

        except Exception as e:
            print(e)


def copy_md(file_path_old: str, file_path_new: str, mode='copy'):
    """
    复制md文件到指定位置。

    :param file_path_old:
    :param file_path_new: 目标位置（文件夹 + 文件名）
    :param mode: 移动或者复制
    :return: 无
    """
    new_path, new_filename = os.path.split(file_path_new)
    copy_md_linked_files(file_path_old, new_path)

    if len(new_filename) == 0:
        fpath, fname = os.path.split(file_path_old)
        new_full_path = new_path + '/' + fname
    else:
        new_full_path = file_path_new

    try:
        if mode == 'copy':
            shutil.copyfile(file_path_old, new_full_path)
        elif mode == 'move':
            shutil.move(file_path_old, new_full_path)
    except Exception as e:
        print('复制文件出错：')
        print(e)


if __name__ == '__main__':
    file_old = r"D:\MaJian\Desktop\@短文剪辑\Python 图像库 PIL 的类 Image 及其方法介绍_leemboy 的博客 - CSDN 博客_pil.md"
    file_new = r'd:/to_delete/a/b/c/d\\e/PIL.md'
    # pth_abs, pth_rel = find_links(fip)
    # print(pth_abs)
    # print(pth_rel)
    #
    # copy_md_linked_files(fip, 'd:/to_delete')
    copy_md(file_old, file_new)
