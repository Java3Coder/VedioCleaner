import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QHBoxLayout, QLineEdit, QComboBox, QGroupBox, QFormLayout, QCheckBox, QSpinBox, QDoubleSpinBox
from PyQt5.QtCore import Qt
import ffmpeg

class VideoCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("影音清理器")
        self.setGeometry(100, 100, 800, 600)
        self.selected_folder = None
        self.filtered_files = []

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
        folder = QFileDialog.getExistingDirectory(self, "选择影音文件夹")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(folder)

    def filter_videos(self):
        if not self.selected_folder:
            self.result_text.setText("请先选择文件夹！")
            return

        self.filtered_files = []
        target_width = self.resolution_width.value()
        target_height = self.resolution_height.value()
        target_fps = self.fps_spinbox.value()
        target_size_mb = self.size_spinbox.value()
        logic = self.logic_combo.currentText()

        for root, dirs, files in os.walk(self.selected_folder):
            for file in files:
                if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm')):
                    file_path = os.path.join(root, file)
                    try:
                        # 使用 ffmpeg 获取视频信息
                        probe = ffmpeg.probe(file_path)
                        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                        width = int(video_info['width'])
                        height = int(video_info['height'])
                        fps_str = video_info.get('r_frame_rate', '0/1')
                        fps = eval(fps_str) if '/' in fps_str else float(fps_str)
                        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

                        # 根据逻辑运算符判断条件
                        if logic == "与 (AND)":
                            if (width >= target_width and height >= target_height and
                                fps >= target_fps and file_size_mb >= target_size_mb):
                                self.filtered_files.append((file_path, width, height, fps, file_size_mb))
                        else:  # 或 (OR)
                            if (width >= target_width or height >= target_height or
                                fps >= target_fps or file_size_mb >= target_size_mb):
                                self.filtered_files.append((file_path, width, height, fps, file_size_mb))

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

        # 显示结果
        self.display_results()

    def display_results(self):
        if not self.filtered_files:
            self.result_text.setText("没有找到符合条件的文件。")
            return

        result_text = "符合条件的文件：\n\n"
        for file_path, width, height, fps, size_mb in self.filtered_files:
            result_text += f"文件: {os.path.basename(file_path)}\n"
            result_text += f"路径: {file_path}\n"
            result_text += f"分辨率: {width}x{height}\n"
            result_text += f"帧率: {fps:.2f} fps\n"
            result_text += f"大小: {size_mb:.2f} MB\n"
            result_text += "-" * 50 + "\n"

        self.result_text.setText(result_text)

    def delete_files(self):
        if not self.filtered_files:
            self.result_text.setText("没有文件可删除！")
            return

        for file_path, _, _, _, _ in self.filtered_files:
            try:
                os.remove(file_path)
            except Exception as e:
                self.result_text.append(f"删除 {file_path} 时出错: {e}")

        self.result_text.append("\n文件删除完成。")
        self.filtered_files = []

    def move_to_recycle_bin(self):
        if not self.filtered_files:
            self.result_text.setText("没有文件可移动到回收站！")
            return

        from send2trash import send2trash
        for file_path, _, _, _, _ in self.filtered_files:
            try:
                send2trash(file_path)
            except Exception as e:
                self.result_text.append(f"移动 {file_path} 到回收站时出错: {e}")

        self.result_text.append("\n文件已移动到回收站。")
        self.filtered_files = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoCleanerApp()
    window.show()
    sys.exit(app.exec()) 