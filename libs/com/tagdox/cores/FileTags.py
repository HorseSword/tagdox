# -*- coding: utf-8 -*-
from typing import Set, TextIO
import os
import logging
from time import sleep


class FileTags:
    __tags: Set[str]
    __filename: str
    __filestream: TextIO

    def __init__(self, filename: str):
        """
        构造方法\n
        :param filename: 文件名
        :return 空
        """
        self.__filename = filename
        self.__open_tags()

    def __str__(self):
        """
        格式化成字符串\n
        """
        return "filename: %s\ntags: %s" % (self.__filename, self.__tags)

    def __enter__(self):
        """
        允许使用with语句\n
        """
        self.__open_tags()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        允许使用with语句\n
        """
        self.close()

    def __open_tags(self):
        """
        打开标签\n
        """
        logging.debug("打开文件标签" + self.__filename)
        try:
            self.__filestream = open(self.__filename + ":tags", "r+", encoding="utf8")
            self.__tags = set(list(map(lambda x: x.strip(), self.__filestream.readlines())))
        except FileNotFoundError as e:
            self.__filestream = open(self.__filename + ":tags", "w", encoding="utf8")
            self.__tags = set()

    def add_tag(self, tag_name: str) -> None:
        """
        :param tag_name: 标签名
        :return 空
        """
        if len(tag_name) > 0:
            self.__tags.add(tag_name)
        else:
            logging.warning("文件%s新建标签不能为空" % self.__filename)

    def remove_tag(self, tag_name: str) -> None:
        """
        :param tag_name: 标签名
        :return 空
        """
        if tag_name in self.__tags:
            self.__tags.remove(tag_name)
        else:
            logging.warning("文件%s没有标签%s" % (self.__filename, tag_name))

    def clear_tags(self):
        """
        清除标签信息\n
        """
        self.__tags.clear()

    def save_tags(self):
        """
        保存标签\n
        """
        self.__filestream.seek(0)
        self.__filestream.truncate()
        if len(self.__tags) > 0:
            self.__filestream.writelines(list(map(lambda x: x + "\n", self.__tags)))

    def get_tags(self) -> Set[str]:
        """
        获取标签\n
        """
        return self.__tags

    def close(self):
        """
        关闭文件\n
        """
        self.save_tags()
        logging.debug("关闭文件标签" + self.__filename)
        self.__filestream.close()
        if len(self.__tags) == 0:
            os.remove(self.__filename + ":tags")
            sleep(0.01)         # 调用系统api删除文件是异步操作


if __name__ == '__main__':
    file = FileTags(filename="./src/img.png")
    # file.add_tag("picture")
    # file.add_tag("icons")
    # file.add_tag("test")
    # file.save_tags()
    # file.clear_tags()
    file.close()

