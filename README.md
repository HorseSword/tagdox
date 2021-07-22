# Tagdox / 标签文库



![我的文库图标设计0630](_img/%E6%88%91%E7%9A%84%E6%96%87%E5%BA%93%E5%9B%BE%E6%A0%87%E8%AE%BE%E8%AE%A10630.png)



## 介绍

「Tagdox/ 标签文库」是用于对文档进行「标签化管理」的免费开源工具。通过Python语言编写。

通过对文件（格式不限）按规则重命名，以#号对标签进行分割，并将标签提取出来，作为文件搜索的标记。

可实现对大量文件的标签化快速管理，熟悉后可显著提升效率。



![image-20210627192637291](_img/image-20210627192637291-1624793199714.png)



## 主要功能



#### 识别文件的标签

可以自动识别标签，对指定文件夹内部所有文件（包括子目录的文件）进行标签化管理。

识别方法1：以文件名中的 # 号（可自定义）作为标签分隔符，自动分段提取。

例如，「某某通知#通知#会议记录#发布.pdf」会识别为 「某某通知.pdf 」+ 「标签：通知、会议记录、发布」

补充：

识别方法2：对于文件名包括#号的，也会识别为标签。可以方便地进行大批量快速管理。

如果有些文件拥有相同的主题（公共标签），可以直接放在叫做「#主题名称」的文件夹内，程序会自动识别为批量标签，为文件夹里面所有项都添加这个标签，而无需重命名。

备注：识别为标签的文件夹层数默认为「最后2层」，层数可以通过设置进行自定义。



#### 按照标签快速查询文件

支持按照标签对文件进行筛选和检索。

当前文件夹的标签会自动提取到标签列表中，便于按标签快速搜索。

也可以通过手动输入文件名和路径等任意关键词进行搜索。



#### 以重命名的方式，为文件添加标签，或者删除标签。

可以为指定的文件快速添加标签。

标签将通过 # 号分隔，以重命名的方式添加到文件名中。

当然，删除标签也是一键搞定。

*注意：如果文件名不可随意修改，则禁止采用本方法。尤其是系统文件！改文件名导致的各种损失，本人概不负责哦。*





## 软件架构



本程序采用Python实现，程序界面主要依靠tkinter库完成开发。

通过pyinstaller转制为exe可执行程序，所以目前只支持 windows 系统。

其中，标签文库.py 文件是全部的源代码，options.json是设置项。



## 安装教程



将dist文件夹复制到本地，运行其中的「标签文库.exe」即可。

其中json文件可以自定义参数，如果没有此文件，将自动创建。

备注：代码已经为高分屏会出现的模糊做了特殊适配，按理说不应该存在模糊情况。

如果仍然存在模糊，可以尝试按照如下方式解决：

右击，属性 - 兼容性标签页 - 更改高DPI设置，在下面“替代高DPI缩放行为”处打钩，确定即可。



## 更新说明
#### v0.14.1.0 2021年7月22日
增加了文件夹拖动进来是移动还是复制的设置；优化设置文件的架构。
#### v0.14.0.5 2021年7月22日
按照规则优化了代码里面函数的名称，对功能没有变化。
#### v0.14.0.4 2021年7月19日
增加子文件夹区域快速添加关注的功能。
#### v0.14.0.3 2021年7月19日
增加子文件夹区域的右键菜单。
#### v0.14.0.2 2021年7月18日
修复进度条显示错误。
#### v0.14.0.1 2021年7月18日
切换文件夹时不再保留标签搜索项。

#### v0.14.0.0 2021年7月17日
将子文件夹独立为左侧列表。

#### v0.13.1.0 2021年7月16日
去掉文件夹区域下面的按钮框架。
#### v0.13.0.5 2021年7月16日
修复设置项修改后不能立刻刷新的bug；修复输入框二次刷新的bug；优化部分菜单。
#### v0.13.0.4 2021年7月15日
修复分辨率和缩放不兼容导致的启动失败问题。

#### v0.13.0.3 2021年7月14日
修复致命bug。
#### v0.13.0.2 2021年7月13日
修正了一处错别字。
#### v0.13.0.1 2021年7月12日
多进程性能太差，所以修改为多线程逻辑。
#### v0.13.0.0 2021年7月10日
加入多进程并发处理逻辑。
#### v0.12.2.0 2021年7月10日
优化代码架构。
#### v0.12.1.0 2021年7月9日
增加了文件大小数据。
#### v0.12.0.2 2021年7月9日
修复了输入框覆盖的错误。
#### v0.12.0.1 2021年7月9日
修复了提示文字的错误。
#### v0.12.0.0 2021年7月9日
增加了居中的进度条。
#### v0.11.2.4 2021年7月8日
Bug修复，性能优化。
#### v0.11.2.3 2021年7月8日
逻辑优化。
#### v0.11.2.2 2021年7月8日
修复子文件夹手动留空时候，标签列表错误的bug。
#### v0.11.2.1 2021年7月8日
优化弹窗代码逻辑；修复 ALL_FOLDERS=2 的时候取消关注文件夹的按钮失效的bug；
#### v0.11.2.0 2021年7月8日
增加列排序的可视化提示效果；优化标签的添加逻辑。

#### v0.11.1.0 2021年7月8日
优化了窗口的左上角图标。

#### v0.11.0.0 2021年7月7日
完成了自制的居中输入窗体，并优化了界面；
解决了分辨率导致的窗口位置偏移问题。

#### v0.10.2.3 2021年7月7日
修复了GBK不支持特殊空格，导致排序失败的问题。

#### v0.10.2.2 2021年7月7日
将设置窗口和关于窗口调整为模态。

#### v0.10.2.1 2021年7月7日
修复了切换文件夹的bug。

#### v0.10.2.0 2021年7月7日
实现文件列表上下移动的功能。

#### v0.10.1.0 2021年7月7日
实现文件列表的重命名和删除功能。

#### v0.10.0.4 2021年7月7日
修复了子文件夹内添加或删除标签的定位逻辑；优化通过菜单添加标签的交互。

#### v0.10.0.3 2021年7月6日
修复列表的中文排序；优化列表文件定位逻辑。

#### v0.10.0.2 2021年7月6日

修复列表文件定位错误的bug。




#### v0.10.0.1 2021年7月6日
优化设置弹窗显示。



#### v0.10.0.0 2021年7月6日

增加了子文件夹的筛选功能，进一步提高管理效率。




#### v0.9.5.4 2021年7月5日

增加设置菜单；调整分隔符的潜在兼容性错误。



#### v0.9.5.3 2021年7月5日

增加「关于」窗口功能。



#### v0.9.5.2 2021年7月5日

增加主菜单功能。



#### v0.9.5.1 2021年7月5日

增加拖拽文件直接复制到文件夹内的功能，便于处理微信文件或其他需要复制的业务。



#### v0.9.5.0 2021年7月4日

增加进度条显示；优化加载效率；优化排序加载算法，缩短排序时间。



#### v0.9.4.1 2021年7月4日

增加文件加载状态的提示，优化加载时间长期间的体验；

增加开发和实际数据的区分。



#### v0.9.4.0 2021年7月2日

新增：

- 增加了右键删除标签的功能；
- 增加了右键快速添加标签的功能。

优化：

- 切换文件夹之后会将滚动条设置到最顶部。
- 点击文件夹之后，如果并没有切换，就不执行文件夹内容刷新。



#### v0.9.3.3 2021年7月1日

修复了新建笔记定位错位的bug；增加文件列表中「在相同位置创建笔记」的功能。



#### v0.9.3.2 2021年7月1日

实现了对高分屏的适配，现在应该是默认就很清晰，不需要手动设置了。



#### v0.9.3.1 2021年6月30日

更新LOGO；

增加了切换文件夹之后是否清除筛选的变量；

完善了是否保留所有文件夹这个功能；

修复bug



#### v0.9.3 2021年6月30日

增加列表文件的高亮，包括添加标签后定位到相应位置、新建文件后定位到相应位置等。



#### v0.9.2 2021年6月29日

修复了可能导致空白文件夹的bug。



#### v0.9.0 2021年6月29日

实现了点击列标排序的功能。



#### v0.8.9 2021年6月29日

增加了右键菜单，实现跳转到文件夹等功能。

调整py文件名。

虽然重命名已完成，但不能输入特殊符号，所以暂不开放。



#### v0.8.2 2021年6月29日

升级了搜索功能，标签是直接选择，文字是直接输入，而且支持空格拆分多个输入文本片段。

调整UI，将新增标签输入框放在下面，更符合逻辑。

新增标签可以直接选择已有的标签。

默认以最大化方式启动。

增加对word缓存文档的屏蔽。

修复了一个启动时候不能刷新的bug。



#### v0.8.0 2021年6月27日

关注的文件夹列表终于完成了自定义！现在可以通过下面的增删按钮调整关注的文件夹列表，甚至可以直接鼠标拖动文件夹到文件夹列表区域，程序会自动识别并添加文件夹。

在没有设置项的时候，程序会自动创建初始化的设置文件。

优化内部逻辑，修复文件夹和文件夹简称可能重复的漏洞。



#### v0.7.0 2021年6月26日

更名为 Tagdox / 标签文库；

更新icon；

调整架构，将文件夹列表调整到左侧作为独立区间，并为以后增加子文件夹做准备；

列表增加序号列。



#### v0.6.4 2021年6月24日

优化文件夹路径简写功能，做到了 json 里面，更加规范，并且兼容了不带简写的写法。

列表按回车也能打开文件，而不仅仅是双击。



#### v0.6.3 2021年6月22日

为文件夹筛选增加了路径简写功能，简化下拉列表的显示效果，功能已经实现，但是还不够优雅。

准备做到 json 里面提供自定义功能。

而且现在这种方式存在最后文件夹名称重复的 bug ，也需要处理好。



#### v0.6.2 2021年6月22日

增加按文件夹筛选的功能。优化UI布局。



#### v0.6.1 2021年6月22日

增加排除文件夹的功能，目前包括以下规则：

- 路径中存在"."开头的文件夹
- 内容包括”_nomedia“文件
- 指定的排除文件夹名称（尚未实现自定义，以后实现） 



#### v0.6.0 2021年6月21日

实现界面自适应调整尺寸，并增加横向滚动条功能。

优化UI。



#### v0.5.2 2021年6月20日

支持对最末2层文件夹名称进行解析，如果文件夹名称包括#号也可以解析为标签（层数默认2层、分隔号默认#号，都可以自定义）。

微调UI。



#### v0.5.1 2021年6月20日

将分隔符（原来的#号）独立出来，设置为可以调整的符号。

在data.json里面可以设置。



#### v0.5.0  2021年6月19日

实现添加标签、自由搜索、结果计数的功能。



#### v0.4.0  2021年6月18日

实现按照中文音序排序标签。

将检索目录的设定方案调整到外接 json 文件中，实现程序外自定义。

优化UI、优化程序架构。



#### v0.1.0  2021年6月17日

实现文件检索、标签拆分等基础功能。




