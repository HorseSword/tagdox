# -*- coding: utf-8 -*-
from com.tagdox.cores.FileTags import FileTags
from typing import Set


def get_tags(filename: str) -> Set[str]:
    """
    获取文件标签\n
    :param filename: 文件路径
    :return: 标签字典
    """
    with FileTags(filename) as f:
        return f.get_tags()


def add_tag(filename: str, tag: str) -> None:
    """
    增加标签\n
    :param filename: 文件路径
    :param tag: 标签名
    :return: 空
    """
    with FileTags(filename) as f:
        f.add_tag(tag)


def remove_tag(filename: str, tag: str) -> None:
    """
    删除标签\n
    :param filename: 文件路径
    :param tag: 标签名
    :return: 空
    """
    with FileTags(filename) as f:
        f.remove_tag(tag)


def clear_tags(filename: str) -> None:
    """
    清除标签\n
    :param filename: 文件路径
    :return: 空
    """
    with FileTags(filename) as f:
        f.clear_tags()


if __name__ == '__main__':
    clear_tags("./src/img.png")
    # add_tag("./src/img.png", "test")
    # add_tag("./src/img.png", "tag")
    # print(get_tags("./src/img.png"))
    # remove_tag("./src/img.png", "test")
    print(get_tags("./src/img.png"))