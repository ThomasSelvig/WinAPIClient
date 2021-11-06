from winapiclient import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class window(QWidget):
	def __init__(self, parent=None):
		super(window, self).__init__(parent, Qt.WindowStaysOnTopHint)
		self.resize(int(512 * (16/9)), 512)
		self.setWindowTitle("PyQt5")

		self.label = QLabel(self)
		self.label.setText("Hello World")
		font = QFont()
		font.setFamily("Arial")
		font.setPointSize(16)

		self.label.setFont(font)
		self.label.move(50,20)


	def gui_loaded_event(self):
		""" app is now loaded: this is useful for pywin32 """
		self.winapi = WinAPIClient(debug=True)

	def keyPressEvent(self, e):
		""" handle key events """

		if (k := e.key()) == Qt.Key_Q:
			self.close()

		elif k == Qt.Key_Space:
			# set background color to color-mask: makes the form bg invisible
			self.setStyleSheet(f"background-color: red;")
			

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = window()
	w.show()

	w.gui_loaded_event()

	sys.exit(app.exec_())
