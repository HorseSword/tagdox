"""
在tkinter的 tree 的基础上实现一些我自己的常用改进方案。
"""
import logging


def tree_obj_clear(tree_obj, app=None) -> None:  #
    """
    通用函数。
    通用的 treeview 清除函数，因为是通用的，所以必须带参数。
    参数是 具体的 treeview 对象。
    """
    tree_children = tree_obj.get_children()
    for item in tree_children:
        tree_obj.delete(item)
    try:
        app.window.update()
    except:
        pass


def tree_obj_mouse_highlight(event, app=None, clear_only=False, the_tree=None, ):
    """
    鼠标指向的项目加背景色，可以作为通用函数，被各种树调用
    :param event:
    :param app: 主程序对象
    :param clear_only:
    :param the_tree:
    :return:
    """
    #
    # 定义操作目标
    if the_tree is None:
        the_tree = app.tree_file
    #
    _iid = the_tree.identify_row(event.y)

    # print(event.y)
    #

    def remove_last_tag():  # 移除之前高亮的项目
        if app.last_focus:
            if app.the_tree and app.the_tree is not the_tree:
                #
                try:  # 之前的去掉高亮
                    tags_old = list(app.the_tree.item(app.last_focus, "tags"))
                    tags_old.remove('line_mouse')
                    app.the_tree.item(app.last_focus, tags=tags_old)
                except:
                    pass
            else:
                try:  # 之前的去掉高亮
                    tags_old = list(the_tree.item(app.last_focus, "tags"))
                    tags_old.remove('line_mouse')
                    the_tree.item(app.last_focus, tags=tags_old)
                except:
                    pass

    if clear_only:
        remove_last_tag()
        app.last_focus = None
        app.the_tree = the_tree
        return

    if _iid != app.last_focus:
        remove_last_tag()
        """if app.last_focus:
            try:  # 之前的去掉高亮
                tags_old = list(app.tree_file.item(app.last_focus, "tags"))
                tags_old.remove('line_mouse')
                app.tree_file.item(app.last_focus, tags=tags_old)
            except:
                pass"""
        # 新项目加高亮
        tags_new = list(the_tree.item(_iid, "tags"))
        tags_new = ['line_mouse'] + tags_new
        the_tree.item(_iid, tags=tags_new)
        #
        # 新项目保存
        app.last_focus = _iid
        app.the_tree = the_tree


def tree_obj_find(full_path='', need_update=True, the_tree=None, the_bar=None, the_col=None, app=None):  #
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
    if the_tree is None:
        the_tree = app.tree_file
    if the_bar is None:
        the_bar = app.bar_tree_v
    if the_col is None:
        the_col = -1
    #
    # 根据完整路径，找到对应的文件并高亮
    if need_update:
        the_tree.update()  # 必须在定位之前刷新列表，否则定位会错误

    n_selected, n_cnt = tree_obj_scroll_to_selection(full_path, app=app)
    return n_selected


def tree_obj_scroll_to_selection(full_path='', the_tree=None, the_bar=None, the_col=None, app=None):
    """
    用于将tree滚动到选中项目的位置上；
    """
    #
    #
    n_selected = 0
    n_cnt = 0
    if the_tree is None:
        the_tree = app.tree_file
    if the_bar is None:
        the_bar = app.bar_tree_v
    if the_col is None:
        the_col = -1
    # the_tree = app.tree_file
    # the_item = None
    try:
        (b1, b2) = the_bar.get()
    except Exception as e:
        logging.error(f'查询滚动条位置出现错误:{the_bar.get()}, {e}')
        return -1
    b0 = b2 - b1  # 滚动条长度

    #
    # 从第一行开始，
    def check_node(itm, n, c):
        for itm0 in the_tree.get_children(itm):
            c += 1
            tmp_value = the_tree.item(itm0, "values")
            if tmp_value[the_col] == full_path:
                the_tree.selection_add(itm0)  # 增加选中项目
            if itm0 in the_tree.selection() and n == 0:
                n = c
            if len(the_tree.get_children(itm0)) > 0 and the_tree.item(itm0, 'open'):
                n, c = check_node(itm0, n, c)
        return n, c

    n_selected, n_cnt = check_node(None, n_selected, n_cnt)

    b_top = n_selected / n_cnt - 0.5 * b0
    b_bottom = n_selected / n_cnt + 0.5 * b0

    if b_top <= 0:
        b_top = 0
    elif b_bottom >= 1:
        b_top = 1 - b0

    the_tree.yview_moveto(b_top)
    logging.debug(f"n_selected = {n_selected}, n_cnt = {n_cnt}, b_top = {b_top}")
    return n_selected, n_cnt
