# 教室点歌工具

#### 介绍
适用于中（小）学教室大屏（一体机）的桌面点歌系统

已经完成的功能有：
-  **新功能：** 托盘图标
-  **新功能：** 选择展示的列信息 
- 桌面显示界面
- 编辑文本
- 设置界面
- 增加歌曲
- 编辑歌曲
- 抽奖（VIP功能）
- 删除第一项歌曲
- 音乐播放
- 其他功能

#### 软件架构
Python + PyQt6框架


#### 安装教程

```DOS
pip install PyQt6
```

#### 使用说明

 **运行条件**
- 安装了Python 3.10及以上版本
- 安装了所需要的库（主要包括`PyQT6`和`MoviePy` `PyGame`等）
```shell
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip install -r requirements.txt
```

 **关于音乐播放**

- 方法1：
需要综合搭配[zTasker v2.0及以上版本](https://everauto.net/cn/index.html)和[Classisland v1.5.1及以上版本](https://github.com/ClassIsland/ClassIsland)使用。
通过[zTasker v2.0及以上版本](https://everauto.net/cn/index.html)创建一个`运行Python脚本`的应用，右键（长按）创建桌面快捷方式。复制桌面快捷方式的属性中的路径，如`C:\Users\Seewo\AppData\Local\zTasker\zTasker.exe -exec:479`一类。再通过[Classisland 1.5.2.1及以上版本](https://github.com/ClassIsland/ClassIsland) 设置`自动化` `放学后` `运行`刚刚复制的命令行`exec`命令。

- 方法2：
使用`pyinstaller`打包`music.py`：
> [!TIP]
> 使用`pyinstaller`前需要先安装该库：
> ```shell
> pip install pyinstaller
> ```
```shell
pyinstaller -F -w music.py
```
在`源文件夹/dist`中找到`music.exe`，复制路径。再通过[Classisland 1.5.2.1及以上版本](https://github.com/ClassIsland/ClassIsland) 设置`自动化` `放学后` `运行`刚刚复制路径。

 **推荐的运行主程序方法** 
推荐使用`pyinstaller`打包`main.py`并设置自启动（拖入`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`）：
```shell
pyinstaller -F -w main.py


#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
