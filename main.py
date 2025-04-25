import sys, json, os, requests, random, logging, webbrowser, re
from PyQt6.QtWidgets import (
    QCheckBox,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QLabel,
    QLineEdit,
    QFormLayout,
    QMessageBox,
    QFontComboBox,
    QSpinBox,
    QRadioButton,
    QFileDialog,
    QTextEdit,
    QComboBox,
    QSystemTrayIcon,
    QMenu,
    QToolButton
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont, QGuiApplication, QAction, QIcon, QCursor

log_file = os.path.join(os.getcwd(), "log.log")  # 日志文件路径
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,  # 设置日志级别
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 时间格式
    encoding="utf-8",
)

logger = logging.getLogger(__name__)  # 日志记录器


class DraggableFrame(QFrame):
    """窗口拖动条"""

    def __init__(self, parent=None):
        """
        创建拖动条
        
        参数：
        parent (QWidget, optional): 父窗口。默认为 None。
        
        """
        super().__init__(parent)
        self.setFixedHeight(25)  # 设置横条的高度
        self.setStyleSheet("background-color: #333;")  # 设置横条的背景颜色

    def mousePressEvent(self, event):
        """
        鼠标按下事件
        
        参数：
        event (QMouseEvent): 鼠标事件

        """
        if event.button() == Qt.MouseButton.LeftButton:
            parent = self.parentWidget()
            if parent:
                self.drag_start_position = (
                    event.globalPosition().toPoint() - parent.pos()
                )
                event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件
        
        参数：
        event (QMouseEvent): 鼠标事件

        """
        if event.buttons() & Qt.MouseButton.LeftButton:
            parent = self.parentWidget()
            if parent and hasattr(self, "drag_start_position"):
                parent.move(event.globalPosition().toPoint() - self.drag_start_position)
                event.accept()


class LotteryDialog(QDialog):
    """抽奖对话框"""

    def __init__(self, parent=None):
        """初始化抽奖对话框"""
        super().__init__(parent)
        self.setWindowTitle("抽奖")
        self.setFixedSize(300, 200)
        self.parent_window = parent  # 保存父窗口引用

        layout = QVBoxLayout()

        # 创建下拉菜单
        self.musicComboBox = QComboBox(self)
        self.musicComboBox.setFont(QFont("HarmonyOS Sans SC", 12))
        layout.addWidget(self.musicComboBox)

        # 创建抽奖按钮
        self.lotteryButton = QPushButton("开始抽奖", self)
        self.lotteryButton.setFont(QFont("HarmonyOS Sans SC", 12))
        self.lotteryButton.clicked.connect(self.start_lottery)
        layout.addWidget(self.lotteryButton)

        self.setLayout(layout)

        # 加载音乐数据到下拉菜单
        self.load_music_list()

    def load_music_list(self):
        """加载音乐列表到下拉菜单"""
        self.musicComboBox.clear()  # 清空之前的项
        try:
            with open("data/data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                music_list = data.get("music", [])
                for music in music_list:
                    self.musicComboBox.addItem(music.get("name", ""))
        except FileNotFoundError:
            pass

    def start_lottery(self):
        """开始抽奖"""
        # 获取选择的歌曲索引
        selected_index = self.musicComboBox.currentIndex()
        if selected_index < 0:
            QMessageBox.warning(self, "警告", "请选择一首歌曲进行抽奖。")
            return

        # 概率抽中奖

        with open("data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            music_list = data.get("music", [])
            lottery = data.get("lottery", 0.04)
        is_win = random.random() < lottery
        # 用户
        selected_music = music_list[selected_index]
        user_name = selected_music.get("user", "")
        user_level = None
        with open("data/overlayer.json", "r", encoding="utf-8") as file:
            user_data = json.load(file)
        for user in user_data:
            if user.get("user") == user_name:
                user_level = user.get("level", "普通用户")
                break

        if user_level == "vip":
            True
        else:
            QMessageBox.warning(
                self, "警告", f"您的身份为 {user_level} ，没有抽奖资格！"
            )
            return
        if selected_index == 0:
            QMessageBox.warning(
                self, "警告", f"第一位还抽？？"
            )
            return
        
        if is_win:
            # 随机选择一个在选中歌曲之前的位置
            new_position = random.randint(0, selected_index - 1)
            # 获取音乐列表
            music_list = data.get("music", [])
            # 获取选中的歌曲
            selected_music = music_list.pop(selected_index)
            # 将选中的歌曲插入到新的位置
            music_list.insert(new_position, selected_music)
            # 更新表格和保存数据
            self.parent_window.load_music_data(music_list)
            self.save_music_data(music_list)
            self.load_music_list()  # 刷新下拉菜单
            QMessageBox.information(
                self, "恭喜", f"您中奖了！歌曲已插队到第 {new_position + 1} 位。"
            )
            # 存插队日志
            logger.info(
                f"用户 {user_name} （身份：{user_level} ） 中奖。歌曲 {selected_music.get('name')} 插队到第 {new_position + 1} 位。"
            )
        else:
            QMessageBox.information(self, "未中奖", "很遗憾，您未中奖。")

    def save_music_data(self, music_list):
        """
        保存音乐数据到 data.json
        
        参数：
        music_list (list): 音乐列表
        """
        try:
            with open("data/data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"music": []}

        data["music"] = music_list
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


class EditTextDialog(QDialog):
    """文本编辑对话框"""

    def __init__(self, parent=None):
        """
        文本编辑对话框
        
        参数：
        parent (QWidget, optional): 父窗口。默认为 None。

        """
        super().__init__(parent)
        self.setWindowTitle("编辑文本")

        self.setFixedSize(1100, 700)
        self.layout = QVBoxLayout(self)

        # 创建文本编辑框
        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        # 设置文本编辑框的字体和大小
        font = QFont("HarmonyOS Sans SC", 16)
        self.text_edit.setFont(font)

        # 输入用户名框
        self.user_name_edit = QLineEdit(self)
        self.user_name_edit.setPlaceholderText("请输入用户名")
        self.layout.addWidget(self.user_name_edit)

        # 输入密码框
        self.password_edit = QLineEdit(self)
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_edit)

        # 按钮
        self.ok_button = QPushButton("确定", self)
        self.cancel_button = QPushButton("取消", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        # 加载现有文本
        self.load_text()

    def load_text(self):
        """加载现有文本"""
        try:
            with open("data/data.json", "r", encoding="utf-8") as file:
                data = file.read()
                self.text_edit.setPlainText(str(data))
        except FileNotFoundError:
            pass

    def get_text(self):
        """获取文本"""
        return self.text_edit.toPlainText()

    def accept(self):
        """保存并关闭对话框"""
        text = self.get_text()
        username = self.user_name_edit.text()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空。")
            return  # 如果用户名或密码为空，不保存并返回

        try:
            # 尝试解析文本为 JSON 格式
            data = json.loads(text)
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self, "JSON 格式错误", f"文本不符合 JSON 格式: {str(e)}"
            )
            return  # 如果格式不正确，不保存并返回
        try:
            with open("data/overlayer.json", "r", encoding="utf-8") as file:
                password_data = json.load(file)
            temp = {}
            for user_info in password_data:
                if user_info.get("level") == "coder":
                    user_temp = user_info.get("user")
                    password_temp = user_info.get("password")
                    temp[user_temp] = password_temp
            
            if username in temp and temp[username] == password:
                with open("data/data.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                logging.warning(f"用户 {username} 保存了data.json文件")
            else:
                QMessageBox.warning(self, "警告", "用户名或密码错误。")
                return  # 如果用户名或密码错误，不保存并返回
        except:pass
        # 刷新 MainWindow 中的表格
        if self.parent() and isinstance(self.parent(), MainWindow):
            self.parent().load_text_data()

        super().accept()


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        """
        设置对话框
        
        参数：
        parent (QWidget, optional): 父窗口。默认为 None。
        """
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.layout = QFormLayout(self)
        self.settings = self.load_settings()  # 初始化 self.settings

        # 字体选择
        self.font_combo = QFontComboBox(self)
        self.layout.addRow(QLabel("字体:"), self.font_combo)

        # 字体大小
        self.font_size_spinbox = QSpinBox(self)
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(72)
        self.layout.addRow(QLabel("字体大小:"), self.font_size_spinbox)

        # 获取屏幕尺寸
        primary_screen = QGuiApplication.primaryScreen()
        screen_geometry = primary_screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 窗口宽度
        self.window_width_spinbox = QSpinBox(self)
        self.window_width_spinbox.setMinimum(100)
        self.window_width_spinbox.setMaximum(screen_width)
        self.window_width_spinbox.setSingleStep(20)
        self.layout.addRow(QLabel("窗口宽度:"), self.window_width_spinbox)

        # 窗口高度
        self.window_height_spinbox = QSpinBox(self)
        self.window_height_spinbox.setMinimum(400)
        self.window_height_spinbox.setMaximum(screen_height)
        self.window_height_spinbox.setSingleStep(30)
        self.layout.addRow(QLabel("窗口高度:"), self.window_height_spinbox)

        # 列表距离
        self.list_spacing_radio_manual = QRadioButton("手动设置")
        self.list_spacing_radio_auto = QRadioButton("自动")
        self.list_spacing_radio_manual.setChecked(True)
        self.list_spacing_spinbox = QSpinBox(self)
        self.list_spacing_spinbox.setMinimum(0)
        self.list_spacing_spinbox.setMaximum(50)
        self.list_spacing_spinbox.setEnabled(False)

        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(self.list_spacing_radio_manual)
        spacing_layout.addWidget(self.list_spacing_spinbox)
        spacing_layout.addWidget(self.list_spacing_radio_auto)
        self.layout.addRow(QLabel("列表间距:"), spacing_layout)

        # 显示列设置
        self.show_name_checkbox = QCheckBox("显示音乐名", self)
        self.show_name_checkbox.setChecked(self.settings.get("show_name", True))
        self.layout.addRow(self.show_name_checkbox)

        self.show_singer_checkbox = QCheckBox("显示歌手", self)
        self.show_singer_checkbox.setChecked(self.settings.get("show_singer", True))
        self.layout.addRow(self.show_singer_checkbox)

        self.show_user_checkbox = QCheckBox("显示点歌人", self)
        self.show_user_checkbox.setChecked(self.settings.get("show_user", True))
        self.layout.addRow(self.show_user_checkbox)

        self.show_note_checkbox = QCheckBox("显示备注", self)
        self.show_note_checkbox.setChecked(self.settings.get("show_note", True))
        self.layout.addRow(self.show_note_checkbox)

        # 连接信号和槽
        self.list_spacing_radio_manual.toggled.connect(self.toggle_spacing_spinbox)

        # 按钮
        self.ok_button = QPushButton("确定", self)
        self.cancel_button = QPushButton("取消", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addRow(button_layout)

        # 加载现有设置
        self.settings = self.load_settings()
        self.apply_settings(self.settings)

    def toggle_spacing_spinbox(self, checked):
        """
        切换间距输入框的启用状态
        
        参数：
        checked (bool): 间距输入框是否启用
        """
        self.list_spacing_spinbox.setEnabled(checked)

    def load_settings(self):
        """加载设置"""
        try:
            with open("settings.json", "r", encoding="utf-8") as file:
                settings = json.load(file)
        except FileNotFoundError:
            settings = {
                "font": "HarmonyOS Sans SC",
                "font_size": 14,
                "window_width": 400,
                "window_height": 600,
                "list_spacing": {"type": "auto", "value": 0},
                "show_name": True,
                "show_singer": True,
                "show_user": True,
                "show_note": True,
            }
        return settings


    def accept(self):
        """保存设置"""
        settings = self.get_settings()
        with open("settings.json", "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)
        super().accept()

    def apply_settings(self, settings):
        """
        应用设置
        
        参数：
        settings (dict): 设置字典

        """
        self.font_combo.setCurrentText(settings.get("font", "HarmonyOS Sans SC"))
        self.font_size_spinbox.setValue(settings.get("font_size", 14))
        self.window_width_spinbox.setValue(settings.get("window_width", 400))
        self.window_height_spinbox.setValue(settings.get("window_height", 600))
        list_spacing = settings.get("list_spacing", {"type": "auto", "value": 0})
        if list_spacing["type"] == "manual":
            self.list_spacing_radio_manual.setChecked(True)
            self.list_spacing_spinbox.setValue(list_spacing["value"])
        else:
            self.list_spacing_radio_auto.setChecked(True)

        self.show_name_checkbox.setChecked(settings.get("show_name", True))
        self.show_singer_checkbox.setChecked(settings.get("show_singer", True))
        self.show_user_checkbox.setChecked(settings.get("show_user", True))
        self.show_note_checkbox.setChecked(settings.get("show_note", True))

    def get_settings(self):
        """获取设置"""
        return {
            "font": self.font_combo.currentText(),
            "font_size": self.font_size_spinbox.value(),
            "window_width": self.window_width_spinbox.value(),
            "window_height": self.window_height_spinbox.value(),
            "list_spacing": {
                "type": (
                    "manual" if self.list_spacing_radio_manual.isChecked() else "auto"
                ),
                "value": (
                    self.list_spacing_spinbox.value()
                    if self.list_spacing_radio_manual.isChecked()
                    else 0
                ),
            },
            "show_name": self.show_name_checkbox.isChecked(),
            "show_singer": self.show_singer_checkbox.isChecked(),
            "show_user": self.show_user_checkbox.isChecked(),
            "show_note": self.show_note_checkbox.isChecked(), 
            
        }


class MusicDialog(QDialog):
    """音乐对话框"""


    def __init__(self, parent=None):
        """
        初始化音乐对话框

        参数:
            parent (QWidget, optional): 父窗口。默认为 None。
        """
        super().__init__(parent)
        self.setWindowTitle("添加音乐")
        self.layout = QFormLayout(self)
        self.setFixedSize(700, 400)

        # 设置输入框字体
        font = QFont(
            "HarmonyOS Sans SC", 12
        )  # 设置输入框字体为 HarmonyOS Sans SC，字号为 12

        # 添加说明文本框
        self.instructions_text = QTextEdit(self)
        self.instructions_text.setFont(font)
        self.instructions_text.setReadOnly(True)  # 设置为只读
        self.instructions_text.setFrameShape(QFrame.Shape.NoFrame)  # 无边框
        self.instructions_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)  # 始终显示垂直滚动条
        
        # 从文件加载说明文字
        try:
            with open("./data/music.txt", "r", encoding="utf-8") as f:
                instructions = f.read()
        except FileNotFoundError:
            instructions = "说明文件未找到"
        except Exception as e:
            instructions = f"加载说明时出错: {str(e)}"
        
        self.instructions_text.setPlainText(instructions)
        self.layout.addRow(QLabel("说明:"), self.instructions_text)

        self.name_input = QLineEdit(self)
        self.name_input.setFont(font)  # 设置输入框字体

        self.singer_input = QLineEdit(self)
        self.singer_input.setFont(font)  # 设置输入框字体

        self.url_input = QLineEdit(self)
        self.url_input.setFont(font)  # 设置输入框字体

        self.user_input = QLineEdit(self)
        self.user_input.setFont(font)  # 设置输入框字体

        # 文件选择
        self.url_layout = QHBoxLayout()
        self.url_input.setPlaceholderText("输入 URL 或选择文件")
        self.file_button = QPushButton("选择文件", self)
        self.file_button.clicked.connect(self.select_music_file)
        self.file_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.url_layout.addWidget(self.url_input)
        self.url_layout.addWidget(self.file_button)

        self.layout.addRow(QLabel("音乐名:"), self.name_input)
        self.layout.addRow(QLabel("歌手:"), self.singer_input)
        self.layout.addRow(QLabel("URL或文件路径:"), self.url_layout)
        self.layout.addRow(QLabel("用户名:"), self.user_input)

        self.ok_button = QPushButton("确定", self)
        self.ok_button.setFont(font)  # 设置按钮字体
        self.ok_button.setFocus()
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.setFont(font)  # 设置按钮字体
        self.cancel_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addRow(button_layout)

    def _markdown_to_html(self, markdown_text):
        """
        Markdown 转 HTML (支持基本语法)
        """
        # 处理加粗 **text**
        html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', markdown_text)
        # 处理斜体 *text*
        html = re.sub(r'\*(.+?)\*', r'<i>\1</i>', html)
        # 处理代码 `text`
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        # 处理链接 [text](url)
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        # 处理换行（Markdown 两空格换行）
        html = html.replace('  \n', '<br>')
        # 默认段落处理
        html = f"<div style='font-family: HarmonyOS Sans SC; font-size: 12pt;'>{html}</div>"
        return html

    def get_music_data(self): 
        """
        获取音乐数据
        
        返回：
        (dict): 音乐数据
        dict["name"] (str): 音乐名
        dict["singer"] (str): 歌手
        dict["url"] (str): URL或文件路径
        dict["user"] (str): 用户名
        """
        return {
            "name": self.name_input.text(),
            "singer": self.singer_input.text(),
            "url": self.url_input.text(),
            "user": self.user_input.text(),
        }

    def select_music_file(self):
        """选择音乐文件并将其路径显示在输入框中"""
        # 定义文件过滤器
        file_filter = "音乐文件 (*.mp3 *.m4a *.flac);;所有文件 (*.*)"

        # 弹出文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音乐文件", filter=file_filter
        )
        if file_path:
            self.url_input.setText(file_path)


class ModifyMusicDialog(QDialog):
    def __init__(self, music_list, parent=None):
        """
        初始化修改音乐对话框

        参数：
        music_list (list): 音乐列表
        parent: 父窗口

        """
        super().__init__(parent)
        self.setWindowTitle("选择要修改的音乐")
        self.music_list = music_list
        self.selected_index = -1

        layout = QVBoxLayout()

        self.musicComboBox = QComboBox(self)
        self.musicComboBox.setFont(QFont("HarmonyOS Sans SC", 12))
        for music in self.music_list:
            self.musicComboBox.addItem(music.get("name", ""))
        layout.addWidget(self.musicComboBox)

        button_layout = QHBoxLayout()
        self.select_button = QPushButton("选择", self)
        self.select_button.clicked.connect(self.accept)
        button_layout.addWidget(self.select_button)
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class EditMusicDialog(QDialog):
    def __init__(self, music_data, parent=None):
        """
        初始化编辑音乐对话框
        
        参数：
        music_data: 要编辑的音乐数据
        parent: 父窗口

        """
        super().__init__(parent)
        self.setWindowTitle("编辑音乐信息")
        self.music_data = music_data
        self.setFixedSize(700, 400)
        layout = QFormLayout(self)
        font = QFont("HarmonyOS Sans SC", 12)

        self.name_input = QLineEdit(self)
        self.name_input.setFont(font)
        self.name_input.setText(music_data.get("name", ""))
        layout.addRow(QLabel("音乐名:"), self.name_input)

        self.singer_input = QLineEdit(self)
        self.singer_input.setFont(font)
        self.singer_input.setText(music_data.get("singer", ""))
        layout.addRow(QLabel("歌手:"), self.singer_input)

        self.url_input = QLineEdit(self)
        self.url_input.setFont(font)
        self.url_input.setText(music_data.get("url", ""))
        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_input)
        self.file_button = QPushButton("选择文件", self)
        self.file_button.clicked.connect(self.select_music_file)
        url_layout.addWidget(self.file_button)
        layout.addRow(QLabel("URL或文件路径:"), url_layout)

        self.user_input = QLineEdit(self)
        self.user_input.setFont(font)
        self.user_input.setText(music_data.get("user", ""))
        layout.addRow(QLabel("点歌人:"), self.user_input)

        self.note_input = QLineEdit(self)
        self.note_input.setFont(font)
        self.note_input.setText(music_data.get("note", ""))
        layout.addRow(QLabel("备注:"), self.note_input)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("保存", self)
        self.ok_button.setFont(font)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.setFont(font)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)

    def get_music_data(self):
        """获取音乐数据"""
        return {
            "name": self.name_input.text(),
            "singer": self.singer_input.text(),
            "url": self.url_input.text(),
            "user": self.user_input.text(),
            "note": self.note_input.text() 
        }

    def select_music_file(self):
        """
        选择音乐文件并将其路径显示在输入框中

        """
        file_filter = "音乐文件 (*.mp3 *.m4a *.flac);;所有文件 (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音乐文件", filter=file_filter
        )
        if file_path:
            self.url_input.setText(file_path)


class OtherWindow():
    """更多外部功能跳转"""
    def __init__(self):
        pass

    def xinhua_net():
        """打开新华网"""
        webbrowser.open("http://news.cn/")
    
    def smartedu_net():
        """打开智慧中小学（国家中小学智慧教育平台）"""
        webbrowser.open("https://basic.smartedu.cn/")

    def class_swap():
        """打开ClassIsland换课窗口"""
        webbrowser.open("classisland://app/class-swap")

    def ci_setting():
        """打开ClassIsland设置窗口"""
        webbrowser.open("classisland://app/settings/components")
        
    def deepseek_website():
        """打开DeepSeek对话网页"""
        webbrowser.open("https://chat.deepseek.com/")



class MainWindow(QWidget):
    """主窗口"""

    def __init__(self):
        """初始化窗口"""
        super().__init__()
        self.position = None  # 初始化位置变量
        self.initUI()
        self.load_text_data()
        self.load_and_apply_settings()  # 加载并应用设置
        self.move_timer = QTimer(self)  # 创建定时器
        self.move_timer.setInterval(200)  # 设置定时器间隔为200毫秒
        self.move_timer.timeout.connect(
            self.save_window_position
        )  # 定时器超时后保存位置
        self.init_tray_icon()  # 初始化托盘图标

    def initUI(self):
        """初始化界面"""
        # 获取屏幕尺寸
        primary_screen = QGuiApplication.primaryScreen()
        geometry = primary_screen.availableGeometry()
        screen_width = geometry.width()
        screen_height = geometry.height()

        # 设置窗口大小为屏幕的20%
        window_width = int(screen_width * 0.2)
        window_height = int(screen_height * 0.6)

        # 设置窗口位置
        if self.position:
            self.move(self.position)  # 使用 self.position 设置窗口位置
        else:
            self.setGeometry(900, 100, window_width, window_height)

        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnBottomHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )

        # 设置窗口透明度（可选）
        self.setWindowOpacity(0.8)

        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加可拖拽的横条
        draggable_frame = DraggableFrame(self)
        layout.addWidget(draggable_frame, alignment=Qt.AlignmentFlag.AlignTop)

        # 设置文字字体
        font = QFont("HarmonyOS Sans SC", 14)

        # 设置按钮字体
        button_font = QFont("HarmonyOS Sans SC", 12)

        # 添加表格
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)  # 改为4列
        self.table_widget.setHorizontalHeaderLabels(["音乐名", "歌手", "点歌人", "备注"])  # 添加备注列
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setFont(font)

        # 设置表头字体
        header_font = QFont("HarmonyOS Sans SC", 14, QFont.Weight.Bold)
        self.table_widget.horizontalHeader().setFont(header_font)

        # 表头居中对齐
        self.table_widget.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # 列宽自适应内容
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table_widget.verticalHeader().setVisible(False)

        layout.addWidget(self.table_widget)

        # 创建一个布局
        self.edit = QToolButton(self)
        self.edit.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        # 创建编辑菜单
        self.edit_menu = QMenu(self)
        menu_font = QFont("HarmonyOS Sans SC", 10)  # 设置字体和大小
        self.edit_menu.setFont(menu_font)
        self.add_music_action = self.edit_menu.addAction("添加音乐（点歌）")
        self.add_music_action.triggered.connect(self.add_music)
        self.lottery_action = self.edit_menu.addAction("抽奖")
        self.lottery_action.triggered.connect(self.open_lottery_dialog)
        self.delete_first_action = self.edit_menu.addAction("删除第一项")
        self.delete_first_action.triggered.connect(self.delete_first_music)
        self.modify_music_action = self.edit_menu.addAction("修改音乐信息")
        self.modify_music_action.triggered.connect(self.open_modify_music_dialog)
        self.edit_text_action = self.edit_menu.addAction("编辑文本（仅管理员可操作）")
        self.edit_text_action.triggered.connect(self.open_edit_text_dialog)
        self.edit.setMenu(self.edit_menu) # 将编辑菜单设置到工具按钮上


        # 创建一个布局
        self.other = QToolButton(self)
        self.other.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        # 创建编辑菜单
        self.other_menu = QMenu(self)
        menu_font = QFont("HarmonyOS Sans SC", 10)  # 设置字体和大小
        self.other_menu.setFont(menu_font)
        self.open_xinhua = self.other_menu.addAction("打开新华网")
        self.open_xinhua.triggered.connect(OtherWindow.xinhua_net)
        self.open_smartedu = self.other_menu.addAction("打开智慧中小学")
        self.open_smartedu.triggered.connect(OtherWindow.smartedu_net)
        self.class_swap = self.other_menu.addAction("ClassIsland换课面板")
        self.class_swap.triggered.connect(OtherWindow.class_swap)
        self.ci_setting = self.other_menu.addAction("ClassIsland设置")
        self.ci_setting.triggered.connect(OtherWindow.ci_setting)
        self.open_deepseek_website = self.other_menu.addAction("打开DeepSeek")
        self.open_deepseek_website.triggered.connect(OtherWindow.deepseek_website)
        self.other.setMenu(self.other_menu) # 将编辑菜单设置到工具按钮上


        # 创建一个水平布局
        settings_close_layout = QHBoxLayout()
        self.add_button = QPushButton("点歌", self)
        self.add_button.setFont(button_font)
        self.add_button.clicked.connect(self.add_music)
        settings_close_layout.addWidget(self.add_button)
        self.edit.setText("修改歌单")
        self.edit.setFont(button_font)
        settings_close_layout.addWidget(self.edit)
        self.other.setText("  更多  ")
        self.other.setFont(button_font)
        settings_close_layout.addWidget(self.other)
        self.close_button = QPushButton("关闭窗口", self)
        self.close_button.setFont(button_font)
        self.close_button.clicked.connect(self.hide)
        settings_close_layout.addWidget(self.close_button)
        layout.addLayout(settings_close_layout) # 将水平布局添加到主布局

        # 设置布局
        self.setLayout(layout)

        # 加载并显示初始数据
        self.load_text_data()

    def init_tray_icon(self):
        """初始化托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # 设置托盘图标，替换为你的图标路径

        # 将菜单设置到托盘图标
        self.menu()
        self.tray_icon.setContextMenu(self.tray_menu)

        # 连接托盘图标的点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

    def menu(self):
        """托盘菜单"""

        # 创建托盘菜单
        self.tray_menu = QMenu()
        menu_font = QFont("HarmonyOS Sans SC", 12)  # 设置字体和大小
        self.tray_menu.setFont(menu_font)

        # 添加菜单项
        self.show_action = QAction("显示主窗口", self)
        self.show_action.triggered.connect(self.show)
        self.tray_menu.addAction(self.show_action)

        self.hide_action = QAction("隐藏主窗口", self)
        self.hide_action.triggered.connect(self.hide)
        self.tray_menu.addAction(self.hide_action)

        self.load = QAction("刷新", self)
        self.load.triggered.connect(self.load_text_data)
        self.tray_menu.addAction(self.load)

        self.hide_action = QAction("设置", self)
        self.hide_action.triggered.connect(self.open_settings_dialog)
        self.tray_menu.addAction(self.hide_action)

        self.about_action = QAction("关于", self)
        self.about_action.triggered.connect(self.about)
        self.tray_menu.addAction(self.about_action)

        self.quit_action = QAction("退出", self)
        self.quit_action.triggered.connect(QApplication.quit)
        self.tray_menu.addAction(self.quit_action)
    
    def about(self):
        """关于"""
        text = """
        MusicList教室大屏桌面点歌工具

        介绍：
        一个用于教室大屏的点歌工具，可以添加音乐，修改音乐信息，删除音乐，编辑文本，抽奖，修改设置等。

        版本：1.1
        作者：Dong
        仓库地址：https://github.com/DongSX1217/MusicList
        """
        QMessageBox.about(self, "关于", text)


    def on_tray_icon_activated(self, reason):
        """ 处理托盘图标的点击事件

        参数：
        reason (QSystemTrayIcon.ActivationReason): 托盘图标的激活原因

        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 左键单击
            self.tray_menu.exec(QCursor.pos())  # 在鼠标当前位置弹出菜单  # 弹出菜单

    def open_edit_text_dialog(self):
        """打开编辑文本对话框"""
        dialog = EditTextDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """
        关闭事件

        参数：
        event: 事件对象
        
        """
        self.hide()
        event.ignore()

    def save_window_position(self):
        """保存窗口位置"""
        if self.move_timer.isActive():
            self.move_timer.stop()  # 停止定时器
        self.position = self.pos()
        settings = self.load_settings()
        settings["window_position"] = [self.position.x(), self.position.y()]
        settings_path = os.path.abspath("settings.json")
        print(f"Saving settings to: {settings_path}")
        with open(settings_path, "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)
        print(f"Settings saved: {settings}")  # 打印保存的设置

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as file:
                settings = json.load(file)
        except FileNotFoundError:
            settings = {
                "font": "HarmonyOS Sans SC",
                "font_size": 14,
                "window_width": 400,
                "window_height": 600,
                "list_spacing": {"type": "auto", "value": 0},
                "show_name": True,
                "show_singer": True,
                "show_user": True,
                "window_position": [100, 100],  # 添加默认值
            }
        if "window_position" not in settings:
            settings["window_position"] = [100, 100]  # 设置默认值
        return settings

    def load_and_apply_settings(self):
        """加载并应用设置"""
        settings = self.load_settings()
        print(f"Loaded settings: {settings}")  # 打印加载的设置
        self.position = QPoint(*settings["window_position"])  # 加载窗口位置
        print(f"Setting window position to: {self.position}")  # 打印设置的位置
        self.apply_settings(settings)  # 应用设置
        self.load_text_data()  # 刷新表格数据以应用字体设置

    def open_settings_dialog(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.apply_settings(new_settings)

    def moveEvent(self, event):
        """
        窗口移动事件
        
        参数：
        event (QMoveEvent): 窗口移动事件
        """
        super().moveEvent(event)
        self.move_timer.start()  # 重置定时器

    def check_and_save_position(self):
        """检查并保存窗口位置"""
        if not self.is_moving:  # 如果窗口已经停止移动
            self.save_window_position()
        else:
            self.is_moving = False  # 重置标志

    def apply_settings(self, settings):
        """
        应用设置

        参数：
        settings (dict): 设置字典
        """
        self.settings = settings
        # 更新字体
        font = QFont(settings["font"], settings["font_size"])
        header_font = QFont(settings["font"], settings["font_size"], QFont.Weight.Bold)
        self.setFont(font)
        self.table_widget.setFont(font)
        self.table_widget.horizontalHeader().setFont(header_font)
        # 使用样式表设置表头字体
        self.table_widget.setStyleSheet(
            "QHeaderView::section { font: %dpt '%s'; }"
            % (header_font.pointSize(), header_font.family())
        )
        # 更新窗口大小
        self.setFixedSize(settings["window_width"], settings["window_height"])
        # 更新列表间距
        if settings["list_spacing"]["type"] == "manual":
            spacing_value = settings["list_spacing"]["value"]
            self.table_widget.setStyleSheet(
                f"QTableWidget::item {{ padding: {spacing_value}px; }} "
                + "QHeaderView::section { font: %dpt '%s'; }"
                % (header_font.pointSize(), header_font.family())
            )
        else:
            self.table_widget.setStyleSheet(
                "QTableWidget::item { padding: 0px; } "
                + "QHeaderView::section { font: %dpt '%s'; }"
                % (header_font.pointSize(), header_font.family())
            )
        # 显示/隐藏列
        show_name = settings.get("show_name", True)
        show_singer = settings.get("show_singer", True)
        show_user = settings.get("show_user", True)
        show_note = settings.get("show_note", True)
        self.table_widget.setColumnHidden(0, not show_name)
        self.table_widget.setColumnHidden(1, not show_singer)
        self.table_widget.setColumnHidden(2, not show_user)
        self.table_widget.setColumnHidden(3, not show_note)
        # 更新窗口位置
        self.move(self.position)

    def load_text_data(self):
        """加载文本数据"""
        try:
            with open("data/data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.load_music_data(data.get("music", []))
        except FileNotFoundError:
            pass

    def open_lottery_dialog(self):
        """打开抽奖对话框"""
        dialog = LotteryDialog(self)
        dialog.exec()

    def load_music_data(self, music_list):
        """
        加载音乐数据并更新表格，确保换行内容完全显示
        
        参数：
        music_list (list): 音乐列表
        """
        self.table_widget.clear()
        self.table_widget.setColumnCount(4)  
        self.table_widget.setHorizontalHeaderLabels(["音乐名", "歌手", "点歌人", "备注"])
        self.table_widget.setRowCount(len(music_list))

        # 设置表格属性以支持换行
        self.table_widget.setWordWrap(True)
        self.table_widget.setTextElideMode(Qt.TextElideMode.ElideNone)
        
        # 清除可能影响显示的样式表
        self.table_widget.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        # 获取当前字体度量
        font = self.table_widget.font()
        font_metrics = self.table_widget.fontMetrics()
        line_height = font_metrics.height()

        for row, music in enumerate(music_list):
            # 处理音乐名（支持换行符）
            original_name = music.get("name", "").replace('\\n', '\n')
            url = music.get("url", "")
            display_name = f"*{original_name}" if not url.strip() else original_name
            
            # 处理歌手名（支持换行符）
            singer_text = music.get("singer", "").replace('\\n', '\n')

            # 添加备注项
            note_item = QTableWidgetItem(music.get("note", "").replace('\\n', '\n'))
            note_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            note_item.setFlags(note_item.flags() | Qt.ItemFlag.ItemIsEditable)
            
                    
            # 创建表格项
            name_item = QTableWidgetItem(display_name)
            singer_item = QTableWidgetItem(singer_text)
            user_item = QTableWidgetItem(music.get("user", ""))

            # 设置文本对齐方式（居中）
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            singer_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            user_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # 启用文本换行
            name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)  # 保持可编辑状态
            singer_item.setFlags(singer_item.flags() | Qt.ItemFlag.ItemIsEditable)
            
            # 保存原始名称
            name_item.setData(Qt.ItemDataRole.UserRole, original_name)
            
            self.table_widget.setItem(row, 0, name_item)
            self.table_widget.setItem(row, 1, singer_item)
            self.table_widget.setItem(row, 2, user_item)
            self.table_widget.setItem(row, 3, note_item)

            # 计算需要的行高
            name_lines = display_name.split('\n')
            singer_lines = singer_text.split('\n')
            note_lines = music.get("note", "").split('\n')
            max_lines = max(len(name_lines), len(singer_lines), len(note_lines), 1)
            
            # 设置行高（基础高度 + 每行额外高度 + 边距）
            self.table_widget.setRowHeight(row, line_height * max_lines + 10)

        # 调整列宽
        self.table_widget.resizeColumnsToContents()
        
        # 确保列宽足够显示内容
        for col in range(self.table_widget.columnCount()):
            self.table_widget.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
            # 设置最小宽度防止内容被压缩
            current_width = self.table_widget.columnWidth(col)
            self.table_widget.setColumnWidth(col, max(current_width, 100))
        
        # 调整窗口宽度
        total_width = sum(
            [self.table_widget.columnWidth(i) for i in range(self.table_widget.columnCount())]
        ) + self.table_widget.verticalScrollBar().width() + 20
        
        if total_width > self.width():
            self.setFixedWidth(min(total_width, self.screen().availableGeometry().width() - 50))

    def check_new(a,b):
        if re.search(a,b):
            return True
        else:
            return False

    def add_music(self):
        """添加音乐"""
        dialog = MusicDialog(self)
            
        if dialog.exec() == QDialog.DialogCode.Accepted:
            music_data = dialog.get_music_data()
            
            try:
                with open("data/data.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {"text": "", "music": [], "music_already": []}
            try:
                if data['wall']['user']:
                    a = data['wall']
                    b = music_data['user']
                    if re.search(a,b):
                        QMessageBox.information(self,"错误","歌单列表从 Internet\
    上的主页中检索失败，可能是服务器繁忙所致，请稍候重试。给您带来的不便，敬请谅解！")
                        return
            except:pass
            self.table_widget.insertRow(self.table_widget.rowCount())
            name_item = QTableWidgetItem(music_data["name"])
            singer_item = QTableWidgetItem(music_data["singer"])
            user_item = QTableWidgetItem(music_data["user"])

            # 设置单元格内容居中
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            singer_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            user_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table_widget.setItem(self.table_widget.rowCount() - 1, 0, name_item)
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 1, singer_item)
            self.table_widget.setItem(self.table_widget.rowCount() - 1, 2, user_item)

            # 调整列宽和行高以适应内容
            self.table_widget.resizeColumnsToContents()
            self.table_widget.resizeRowsToContents()

            # 计算表格所需的最小宽度，并相应地调整窗口宽度
            total_width = (
                self.table_widget.horizontalHeader().length()
                + self.table_widget.verticalScrollBar().width()
                + 20
            )  # 加上滚动条宽度和边距
            if total_width > self.width():
                self.setFixedWidth(total_width)

            # 保存到 text_data.json 文件
            try:
                with open("data/data.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {"text": "", "music": [], "music_already": []}

            data["music"].append(music_data)
            with open("data/data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            # 刷新表格数据
            self.load_text_data()

            QMessageBox.information(self, "成功", "音乐已添加！")
            logger.info(f"用户{music_data['user']}添加了音乐{music_data['name']}")
        else:
            QMessageBox.warning(self, "取消", "未添加音乐。")

    def delete_first_music(self):
        """删除音乐列表中的第一项"""
        try:
            with open("data/data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                music_list = data.get("music", [])
        except FileNotFoundError:
            QMessageBox.warning(self, "错误", "未找到音乐数据文件。")
            return

        if not music_list:
            QMessageBox.warning(self, "警告", "音乐列表为空，无法删除。")
            return

        # 弹出确认窗口
        confirm = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除音乐列表中的第一项吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # 删除第一项
            data0 = music_list[0]
            deleted_music = music_list.pop(0)
            data["music"] = music_list

            # 保存更新后的数据
            with open("data/data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            # 刷新表格
            self.load_music_data(music_list)

            # 提示用户删除成功
            QMessageBox.information(
                self, "成功", f"已删除音乐：{deleted_music.get('name', '未知')}"
            )
            logger.warning(f"用户删除了第一首歌曲，歌曲名：{data0}")


    def open_modify_music_dialog(self):
        """打开修改音乐信息对话框"""
        try:
            with open("data/data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                music_list = data.get("music", [])
        except FileNotFoundError:
            music_list = []

        if not music_list:
            QMessageBox.warning(self, "警告", "音乐列表为空，没有音乐可以修改。")
            return

        dialog = ModifyMusicDialog(music_list, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:  # 如果用户点击了确定按钮
            selected_index = dialog.musicComboBox.currentIndex()
            if selected_index >= 0:  # 如果用户选择了一个音乐
                music_data = music_list[selected_index]
                edit_dialog = EditMusicDialog(music_data, self)
                if (
                    edit_dialog.exec() == QDialog.DialogCode.Accepted
                ):  # 如果用户点击了确定按钮
                    new_music_data = edit_dialog.get_music_data()
                    music_list[selected_index] = new_music_data
                    with open("data/data.json", "r", encoding="utf-8") as file:
                        data = json.load(file)
                    with open("data/data.json", "w", encoding="utf-8") as file:
                        data["music"] = music_list
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    self.load_text_data()
                    QMessageBox.information(self, "成功", "音乐信息已更新。")
                    logger.info(f"Music data updated: {new_music_data['name']}")
            else:
                QMessageBox.warning(self, "警告", "请选择一个音乐。")


if __name__ == "__main__":
    """主函数"""
    app = QApplication(sys.argv)  # 创建QApplication对象
    ex = MainWindow()  # 创建窗口对象
    ex.show()  # 显示窗口
    logger.info("Program started.")  # 记录日志
    sys.exit(app.exec())  # 运行程序，并等待退出
