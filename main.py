import sys
from PyQt5.QtWidgets import QApplication
from ui import VideoCleanerUI

def main():
    app = QApplication(sys.argv)
    window = VideoCleanerUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 