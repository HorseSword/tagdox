"""
程序主题设置。
"""

def set_style(style, app, conf):
    """
    显示的样式
    """
    # style = ttk.Style()
    # 修复 treeview 背景色的bug；
    def fixed_map(option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.

        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in style.map('Treeview', query_opt=option) if
                elm[:2] != ('!disabled', '!selected')]

    def fixed_map_v2(tar, option):
        return [elm for elm in style.map(tar, query_opt=option) if
                elm[:2] != ('!disabled', '!selected')]

    style.map('Treeview',
              foreground=fixed_map('foreground'),
              background=fixed_map('background')
              )
    style.map('TFrame',
              foreground=fixed_map_v2('Frame', 'foreground'),
              background=fixed_map_v2('Frame', 'background'),
              )
    # style.map('TButton', foreground=fixed_map_v2('TButton','foreground'), background=fixed_map_v2('TButton','background'))
    #
    MY_THEME = 'third_party'

    if MY_THEME == 'third_party':
        """
        第三方主题
        """
        app.window.tk.call('lappend', 'auto_path', './resources/styles/awthemes-10.4.0')
        app.window.tk.call('package', 'require', 'awlight')
        app.window.tk.call('package', 'require', 'awdark')
        #
        style.theme_use('awlight')  # awlight awdark clam X
        #
        LIGHT_THEME = True
        #
        # 标签生效顺序是，定义在前面的优先生效，和实际标签列表里面的顺序没有关系
        #
        if LIGHT_THEME:
            #
            # 独立设定效果
            app.tree_file.tag_configure('line_mouse', background="#dddfe2")
            app.tree_lst_folder.tag_configure('line_mouse', background="#242425",foreground="#2eb8ac",)
            # app.tree_lst_folder.tag_configure('line_mouse', background="#242425")
            app.tree_lst_sub_tag.tag_configure('line_mouse', background="#FFFFFF")
            app.tree_lst_sub_tag.tag_configure('line1', background="#EBEFF2")
            #
            #
            # 通用的
            for tar in [app.tree_lst_folder, app.XX_tree_lst_sub_folder, app.tree_file]:
                # tar.tag_configure('line_mouse', background="#dddfe2")
                tar.tag_configure('line1', background="#F2F2F2")
                tar.tag_configure('line_folder', background="#dbe2e8")
                # tar.tag_configure('line1',background="#F8F8F8")
                # tar.tag_configure('line1',background="#FFFFFF")
                # tar.tag_configure('folder2',background="#FFFFFF")
                tar.tag_configure('folder0', foreground=app.COLOR_DICT['blue_light'])
                tar.tag_configure('folder2', background="#1e1e1e")
                tar.tag_configure('folder_searched', foreground="#b1fc28", background="#1e1e1e")
                tar.tag_configure('pick_up', foreground="#f37625",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
                tar.tag_configure('pick_copy', foreground="#2d7d9a",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))

        else:
            for tar in [app.tree_lst_folder, app.XX_tree_lst_sub_folder, app.tree_lst_sub_tag, app.tree_file]:
                tar.tag_configure('line1', background="#343a40")
                # tar.tag_configure('line1',background="#F8F8F8")
                # tar.tag_configure('line1',background="#FFFFFF")
                # tar.tag_configure('folder2',background="#FFFFFF")
                # tar.tag_configure('folder2',background="#1e1e1e")
                tar.tag_configure('pick_up', foreground="#f37625",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
                tar.tag_configure('pick_copy', foreground="#2d7d9a",
                                  font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))

        # app.window.tk.call('source', './resources/styles/ttk-Breeze-master/breeze.tcl')
        # style.theme_use('Breeze') #

        style.configure("Treeview.Heading",
                        font=conf.FONT_TREE_HEADING, \
                        rowheight=int(conf.LARGE_FONT * 4 * conf.ui_ratio),
                        height=int(conf.LARGE_FONT * 4), \
                        background='white',
                        foreground='black',
                        relief='flat',
                        borderwidth=0,
                        padding=(int(conf.LARGE_FONT / 2), int(conf.LARGE_FONT / 2), 0, int(conf.LARGE_FONT / 2)),
                        )

        style.configure("Treeview",
                        font=conf.FONT_TREE_BODY,
                        rowheight=int(conf.MON_FONTSIZE * 4 * conf.ui_ratio),
                        fieldbackground='#e8e8e7',
                        background='#e8e8e7',
                        foreground='black',
                        relief='flat',
                        borderwidth=0,
                        )
        style.layout("Treeview", [('Dark.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        style.configure("Taglist.Treeview",
                        # font=conf.FONT_TREE_BODY,
                        # fontsize=-15,
                        # rowheight=int(conf.MON_FONTSIZE * 3.5), \
                        fieldbackground='#5c6164',  # 没有行部分的颜色
                        background='#dbe2e8',  # 空白行的颜色
                        foreground='black',
                        # relief='flat',
                        # borderwidth=0,
                        )
        style.configure("Dark.Treeview",
                        # font=conf.FONT_TREE_BODY,
                        # fontsize=-15,
                        # rowheight=int(conf.MON_FONTSIZE * 3.5), \
                        fieldbackground=app.COLOR_DICT['darkback_1'],  # 没有行部分的颜色
                        background='#2a333c',
                        foreground='white',
                        indent=conf.ui_conf['FOLDER_STEP'],
                        # rowheight=60, # 行间距
                        # relief='flat',
                        # borderwidth=0,
                        )
        style.layout("Dark.Treeview", [
            ('Dark.Treeview.treearea', {'sticky': 'nswe'}) # Remove the borders
        ])
        # style.configure("Dark.Treeview", rowheight=60)  # 调整行间距
        # style.configure("Dark.Treeview.Heading", font=("Arial", 14))  # 调整表头字体
        # style.configure("Dark.Treeview.Cell", padding=(100, 50))  # 调整图标与文字之间的间距 # 无效

        style.configure("TCombobox",
                        relief='flat',
                        background="#e8e8e7",
                        foreground='black',
                        )
        style.configure("TEntry",
                        relief='flat',
                        background="#e8e8e7",
                        foreground='black',
                        )

        style.configure("TFrame",
                        relief='flat',
                        background="#e8e8e7",
                        foreground='black',
                        )  # 静态

        style.configure("Dark.TFrame",
                        relief='flat',
                        background="#2a333c",
                        foreground='white',
                        )  # 静态

        style.configure("TButton",
                        relief='flat',
                        font=conf.FONT_TREE_BODY,
                        background=app.COLOR_DICT['blue'],  # '#3a92c5',
                        foreground='white',
                        )  # 静态

        style.map('TButton',
                  background=[('active', app.COLOR_DICT['cyan']),
                              ('pressed', app.COLOR_DICT['blue']),
                              ('disabled', '#bfbfbf')
                              ]
                  )

        # style.configure("Light.TButton",
        #                 background='#e8e8e7')  # app.COLOR_DICT['#2a333c'])

        style.configure("Menu.TButton",
                        background='#2a333c')  # app.COLOR_DICT['#2a333c'])

        style.map('Menu.TButton',
                  background=[
                      ('active', '#5f6368'),
                      ('pressed', '#414141'),
                  ]
                  )  #

        style.configure("TProgressbar",  # Horizontal.
                        relief='flat',
                        background=app.COLOR_DICT['blue'],  # '#3a92c5',
                        )


    elif MY_THEME == 'built-in':

        style.theme_use('clam')  # winnative clam
        #
        # treeview
        style.configure("Treeview.Heading", font=conf.FONT_TREE_HEADING, \
                        rowheight=int(conf.LARGE_FONT * 4 * conf.ui_ratio), height=int(conf.LARGE_FONT * 4), \
                        relief='flat', borderwidth=0)

        style.configure("Treeview", font=conf.FONT_TREE_BODY, \
                        rowheight=int(conf.MON_FONTSIZE * 3.5 * conf.ui_ratio), \
                        fieldbackground='white', background='#666666', \
                        relief='flat', borderwidth=0)
        # style.configure("Treeview.Item",font=5)
        style.configure("Dark.Treeview", fieldbackground='#333333', background='black')
        style.configure("Dark.Treeview.Heading", fieldbackground='blue', \
                        background='black', foreground='white')
        #
        # 框架
        style.configure("TFrame", fieldbackground='white', background='#EEEEEE', \
                        borderwidth=0, relief='flat')
        #
        # 按钮
        style.configure("TButton", fieldbackground='#666666',
                        background='#999900',
                        activeforeground=" #ff0000", activebackground="#00ff00",
                        height=int(16*conf.ui_ratio),
                        borderwidth=1, relief='flat')
        #
        style.configure("TEntry", fieldbackground='#FFFFFF', background='#EEEEEE', \
                        borderwidth=1, relief='solid')

    else:
        style.configure("Treeview.Heading", font=conf.FONT_TREE_HEADING, \
                        rowheight=int(conf.LARGE_FONT * 4 * conf.ui_ratio), height=int(conf.LARGE_FONT * 4))
        style.configure("Treeview", font=conf.FONT_TREE_BODY, \
                        rowheight=int(conf.MON_FONTSIZE * 3.5 * conf.ui_ratio), relief='flat', borderwidth=0)
        # style.configure("Vertical.TScrollbar", width=8)

        for tar in [app.tree_lst_folder, app.XX_tree_lst_sub_folder, app.tree_lst_sub_tag, app.tree_file]:
            tar.tag_configure('line1', background="#F2F2F2")
            # tar.tag_configure('line1',background="#F8F8F8")
            # tar.tag_configure('line1',background="#FFFFFF")
            # tar.tag_configure('folder2',background="#FFFFFF")
            tar.tag_configure('folder2', background="#F2F2F2")
            tar.tag_configure('pick_up', foreground="#f37625", font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
            tar.tag_configure('pick_copy', foreground="#2d7d9a", font=(conf.FONT_TREE_BODY[0], conf.FONT_TREE_BODY[1], "italic"))
