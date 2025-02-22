"""
通用函数
"""


def exec_list_sort(lst, char_sep='^'):
    """
    通用函数，按我的规矩为列表排序的函数。
    char_sep = conf.V_SEP
    """
    if not type(lst) is list:
        return None
    #
    lst2 = lst.copy()
    #
    # 令@开头的标签在最前
    lst_top = []
    lst_en = []
    lst_cn = []
    for i in lst2:
        if i == '':
            continue
        if str(i).startswith('@'):
            lst_top.append(i)
        else:
            lst_en.append(i)
    # 英文无论大小写都一起排序
    # 如果是^开头，就忽略这个符号，直接正常排序
    lst_en = sorted(lst_en, key=lambda x: str.lower(x.replace(char_sep, '').replace('\xa0', ' ')).encode('gbk'))
    # 中文也排序
    lst_cn = sorted(lst_cn, key=lambda x: str.lower(x.replace('\xa0', ' ')).encode('gbk'))
    # 组合起来
    lst2 = lst_top + lst_en + lst_cn
    #
    return lst2
