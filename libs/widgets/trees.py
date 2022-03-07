from tkinter import ttk
import tkinter as tk


class TdTreeview:
    def __init__(self, base, vbar=False, hbar=False, **kwargs):
        self.bar_width = 16
        self.columns = ['tags', 'values']
        #
        self.frame = ttk.Frame(base, **kwargs)
        #
        self.bar_v = tk.Scrollbar(self.frame, width=self.bar_width)
        self.bar_h = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, width=self.bar_width)
        self.tree = ttk.Treeview(self.frame,
                                 columns=self.columns,
                                 yscrollcommand=self.bar_v.set,
                                 xscrollcommand=self.bar_h.set,
                                 )
        #
        self.bar_v.config(command=self.tree.yview)
        self.bar_h.config(command=self.tree.xview)
        #
        if vbar:
            self.bar_v.pack(side=tk.RIGHT, expand=0, fill=tk.Y)
        if hbar:
            self.bar_h.pack(side=tk.BOTTOM, expand=0, fill=tk.X)
        #

        self.tree.pack(expand=1, fill=tk.BOTH)

    def insert(self, *args, **kwargs):
        self.tree.insert(*args, **kwargs)

    def pack(self):
        self.frame.pack(expand=1, fill=tk.BOTH)

    def clear_items(self) -> None:  #
        """
        treeview 清除函数
        """
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)

    def tree_find(self, full_path='', need_update=True, the_col=None):  #
        """
        用于在 任意 treeview（默认是tree） 里面找到项目，并加高亮。
        输入参数是查找值（完整路径）。
        need_update 代表是否要刷新列表。一般否是要刷新才能保证正确，
        如果是批量查询，可以自己提前刷新，然后取消函数刷新，可以增加速度。
        只支持单项目查找，多个查询需要重复运算。
        如果返回-1，代表没有找到。
        """
        if full_path == '' or full_path is None:
            return -1
        #
        # 默认值
        the_tree = self.tree
        the_bar = self.bar_v
        if the_col is None:
            the_col = -1
        #
        # 根据完整路径，找到对应的文件并高亮
        if need_update:
            the_tree.update()  # 必须在定位之前刷新列表，否则定位会错误
        tc = the_tree.get_children()
        tc_cnt = len(tc)
        print('条目数量为：%s' % tc_cnt)
        n = 0
        print('开始查找高亮的位置')
        try:
            (b1, b2) = the_bar.get()
        except:
            print(f'查询滚动条位置出现错误')
            print(the_bar.get())
            return (-1)
        b0 = b2 - b1
        # b0=0
        print('b0=')
        print(b0)
        for i in tc:
            tmp = the_tree.item(i, "values")
            # print(tmp[the_col])
            if tmp[the_col] == full_path:
                # the_tree.focus(i) #这个并不能高亮
                the_tree.selection_add(i)
                # the_tree.selection_add(tc[0])
                print('在第%d处检查到了相应结果' % n)
                b1 = n / tc_cnt - 0.5 * b0
                b2 = n / tc_cnt + 0.5 * b0
                print((b0, b1, b2))
                if b1 < 0:
                    b1 = 0
                    b2 = b0
                elif b2 > 1:
                    b2 = 1
                    b1 = 1 - b0
                print((b1, b2))
                # the_bar.set(b1,b2)
                the_tree.yview_moveto(b1)
                return n
                break
            else:
                n += 1
        print('居然没找到：')
        print(full_path)
        return -1
        # for i in range()

    def tree_find_by_lst(self, inp_lst):
        """
        传入一个列表。tree高亮。
        输入参数是要查询的内容，必须是列表。
        """
        self.tree.update()
        if type(inp_lst) is not list:
            print('输入参数不是列表！')
            return

        for tmp_final_name in inp_lst:
            tmp_final_name = tmp_final_name.replace('\\', '/')
            print(f'正在定位 {tmp_final_name}')
            self.tree_find(tmp_final_name, need_update=False)  # 为加标签之后的项目高亮

    def test_insert(self):
        for i in range(100):
            self.insert('', i, text=' hello '+str(i),
                        values=(str(i), ' hello '+str(i)))

    def test_init(self):
        # self.name = 'test'
        self.tree.heading("tags", text="全部标签", anchor='w', command=self.tree_test)
        self.tree.heading("values", text="值", anchor='w', command=self.tree_test)
        # self.insert()

    def tree_test(self):
        self.tree_find(' hello 30')


if __name__ == '__main__':
    root = tk.Tk()
    a = TdTreeview(root, True, False)
    a.test_init()
    a.test_insert()
    a.pack()
    root.mainloop()
