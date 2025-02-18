"""
文件夹树
"""


class tree_folder:
    def __init__(self, app):
        self.app = app

    def search_folder(self, event=None):
        """
        按文件夹名称搜索
        """
        keyword_folder = self.app.entry_search_folder.get()

        if keyword_folder is None:
            keyword_folder = ''
        if len(keyword_folder.strip()) <= 0:
            keyword_folder = ''
        self.app.keyword_folder = keyword_folder
        self.update()  # tree_folder_update()

    def update(self):
        """

        """
