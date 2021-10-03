# -*- coding: utf-8 -*-
from typing import Set
import os


class FileTags:
    __raw_file: bytes
    __tags: Set[str]
    __filename: str

    def __init__(self, filename: str):
        """
        构造方法\n
        :param filename: 文件名
        :return 空
        """
        with open(filename, "rb") as f:
            self.__raw_file = f.read()
        try:
            with open(filename + ":tags", "r", encoding="utf8") as f:
                self.__tags = set(list(map(lambda x: x.strip(), f.readlines())))
        except FileNotFoundError as e:
            self.__tags = set()
        self.__filename = filename

    def __str__(self):
        """
        格式化成字符串\n
        """
        return "filename: %s\ntags: %s" % (self.__filename, self.__tags)

    def add_tag(self, tag_name: str) -> None:
        """
        :param tag_name: 标签名
        :return 空
        """
        self.__tags.add(tag_name)

    def remove_tag(self, tag_name: str) -> None:
        """
        :param tag_name: 标签名
        :return 空
        """
        self.__tags.remove(tag_name)

    def clear_tags(self):
        """
        清除标签信息\n
        """
        try:
            os.remove(self.__filename + ":tags")
        except FileNotFoundError as e:
            pass

    def show_tags(self) -> None:
        """
        显示标签\n
        """
        print(self.__tags)

    def save_tags(self):
        """
        保存标签\n
        """
        with open(self.__filename + ":tags", "w", encoding="utf8") as f:
            f.writelines(list(map(lambda x: x + "\n", self.__tags)))

    def save_rawfile(self):
        """
        保存文件字节\n
        """
        with open(self.__filename, "wb") as f:
            f.write(self.__raw_file)

    def get_tags(self) -> Set[str]:
        """
        获取标签\n
        """
        return self.__tags

    def close(self):
        """
        关闭文件\n
        """
        self.save_rawfile()
        self.save_tags()


if __name__ == '__main__':
    file = FileTags(filename="../../../src/img.png")
    # file.add_tag("picture")
    # file.add_tag("icons")
    # file.add_tag("test")
    # file.save_tags()
    file.show_tags()
    # file.clear_tags()
