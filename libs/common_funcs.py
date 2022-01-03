# 本文件是全部导入的，将通用函数放在这里
import os
import time
from win32com.shell import shell, shellcon  # 此处报错是编辑器的问题，可以忽略


def get_split_path(full_path) -> list:
    """
    通用函数：
    将完整路径按照斜杠拆分，得到每个文件夹到文件名的列表。
    """
    test_str = full_path.replace('\\', '/', -1)
    test_str_res = test_str.split('/')
    return test_str_res


def del_to_recyclebin(filename):
    """
    删除到回收站
    这个函数好像没有被使用；
    """
    print('del_to_recyclebin：', filename)
    # os.remove(filename) #直接删除文件，不经过回收站
    if True:
        res = shell.SHFileOperation((0, shellcon.FO_DELETE, filename, None,
                                     shellcon.FOF_SILENT | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None,
                                     None))  # 删除文件到回收站
        if not res[1]:
            os.system('del ' + filename)


def exec_remove_to_trash(filename, remove=False):
    """
    删除文件，
    参数filename 可以是文件，也可以是文件夹。
    参数remove=True就直接删除，False移动到回收站（默认）。
    """
    if remove:
        print('直接删除')
        os.remove(filename)
    else:
        print('删除到回收站')
        print('exec_remove_to_trash：', filename)
        res = shell.SHFileOperation((0, shellcon.FO_DELETE, filename, None,
                                     shellcon.FOF_SILENT | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None,
                                     None))  # 删除文件到回收站
        print(res)  # (0, False)
        if not res[1]:
            # tk.messagebox.showerror(title='ERROR', message='删除失败，文件可能被占用！'+ str(filename))
            print('请检查删除操作的返回值')
            # os.system('del '+filename)

        # (fp,fn) = os.path.split(filename)
        # newname = fp+'/'+'~~'+fn
        # final_name = exec_safe_rename(filename, newname)
        # print(final_name)
        # send2trash.send2trash(filename)
