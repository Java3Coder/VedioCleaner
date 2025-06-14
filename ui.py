from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QLabel, QTextEdit, QHBoxLayout, 
                             QComboBox, QGroupBox, QFormLayout, QSpinBox, 
                             QDoubleSpinBox)
from PyQt5.QtCore import Qt
from video_processor import VideoProcessor

class VideoCleanerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.selected_folder = None
        self.filtered_files = []
        self.init_ui()

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("影音清理器")
        self.setGeometry(100, 100, 800, 600)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 选择文件夹按钮
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("未选择文件夹")
        folder_layout.addWidget(self.folder_label)
        select_folder_button = QPushButton("选择文件夹")
        select_folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(select_folder_button)
        main_layout.addLayout(folder_layout)

        # 筛选条件区域
        filter_group = QGroupBox("筛选条件")
        filter_layout = QFormLayout(filter_group)

        # 分辨率条件
        resolution_layout = QHBoxLayout()
        self.resolution_width = QSpinBox()
        self.resolution_width.setRange(1, 10000)
        self.resolution_width.setValue(1920)
        self.resolution_height = QSpinBox()
        self.resolution_height.setRange(1, 10000)
        self.resolution_height.setValue(1080)
        resolution_layout.addWidget(self.resolution_width)
        resolution_layout.addWidget(QLabel("x"))
        resolution_layout.addWidget(self.resolution_height)
        filter_layout.addRow("分辨率:", resolution_layout)

        # 帧率条件
        self.fps_spinbox = QDoubleSpinBox()
        self.fps_spinbox.setRange(1, 1000)
        self.fps_spinbox.setValue(30)
        filter_layout.addRow("帧率 (fps):", self.fps_spinbox)

        # 文件大小条件 (MB)
        self.size_spinbox = QDoubleSpinBox()
        self.size_spinbox.setRange(0, 1000000)
        self.size_spinbox.setValue(100)
        filter_layout.addRow("文件大小 (MB):", self.size_spinbox)

        # 逻辑运算符
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["与 (AND)", "或 (OR)"])
        filter_layout.addRow("逻辑运算符:", self.logic_combo)

        main_layout.addWidget(filter_group)

        # 开始筛选按钮
        filter_button = QPushButton("开始筛选")
        filter_button.clicked.connect(self.filter_videos)
        main_layout.addWidget(filter_button)

        # 结果显示区域
        result_group = QGroupBox("筛选结果")
        result_layout = QVBoxLayout(result_group)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        main_layout.addWidget(result_group)

        # 操作按钮区域
        action_layout = QHBoxLayout()
        delete_button = QPushButton("删除选中文件")
        delete_button.clicked.connect(self.delete_files)
        action_layout.addWidget(delete_button)
        recycle_button = QPushButton("移动到回收站")
        recycle_button.clicked.connect(self.move_to_recycle_bin)
        action_layout.addWidget(recycle_button)
        main_layout.addLayout(action_layout)

    def select_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择影音文件夹")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(folder)

    def filter_videos(self):
        """筛选视频"""
        if not self.selected_folder:
            self.result_text.setText("请先选择文件夹！")
            return

        # 获取筛选条件
        conditions = {
            'width': self.resolution_width.value(),
            'height': self.resolution_height.value(),
            'fps': self.fps_spinbox.value(),
            'size_mb': self.size_spinbox.value(),
            'logic': 'AND' if self.logic_combo.currentText() == "与 (AND)" else 'OR'
        }

        # 扫描目录
        video_files = self.video_processor.scan_directory(self.selected_folder)
        
        # 筛选视频
        self.filtered_files = self.video_processor.filter_videos(video_files, conditions)
        
        # 显示结果
        self.display_results()

    def display_results(self):
        """显示筛选结果"""
        if not self.filtered_files:
            self.result_text.setText("没有找到符合条件的文件。")
            return

        result_text = "符合条件的文件：\n\n"
        for video in self.filtered_files:
            result_text += f"文件: {video['filename']}\n"
            result_text += f"路径: {video['path']}\n"
            result_text += f"分辨率: {video['width']}x{video['height']}\n"
            result_text += f"帧率: {video['fps']:.2f} fps\n"
            result_text += f"大小: {video['size_mb']:.2f} MB\n"
            result_text += "-" * 50 + "\n"

        self.result_text.setText(result_text)

    def delete_files(self):
        """删除文件"""
        if not self.filtered_files:
            self.result_text.setText("没有文件可删除！")
            return

        success_count = 0
        for video in self.filtered_files:
            if self.video_processor.delete_video(video['path']):
                success_count += 1

        self.result_text.append(f"\n成功删除 {success_count} 个文件。")
        self.filtered_files = []

    def move_to_recycle_bin(self):
        """移动到回收站"""
        if not self.filtered_files:
            self.result_text.setText("没有文件可移动到回收站！")
            return

        success_count = 0
        for video in self.filtered_files:
            if self.video_processor.move_to_recycle_bin(video['path']):
                success_count += 1

        self.result_text.append(f"\n成功移动 {success_count} 个文件到回收站。")
        self.filtered_files = [] 