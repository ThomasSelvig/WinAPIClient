import sys
import logging

from typing import Optional, Tuple

from winapiclient import WinAPIClient, Helper

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ExampleWidget(QWidget):
	def __init__(self, parent, root_window, geo):
		super().__init__(parent)
		self._r = root_window

		self.frame = QFrame(self)
		self.frame.setGeometry(geo)
		self.frame.setStyleSheet(";\n".join([
			"background-color: darkslateblue",
			"color: white"
		]))

		self.main_label = QLabel("Markdown: Lorem ~~ipsum~~ dolor **sit** amet", self.frame)
		self.main_label.setTextFormat(Qt.MarkdownText)
		self.main_label.setWordWrap(True)
		self.main_label.setFont(QFont("Segoe UI", 24))


class WidgetManager(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self._r = parent  # root window

		w, h = self._r.SIZE

		self.widgets = [
			# top-right of screen
			ExampleWidget(
				self, 
				self._r, 
				QRect(*map(int, (
					w / 4 * 3,
					0,
					w / 4,
					h / 4 )))),

			# down-left of the one above
			ExampleWidget(
				self, 
				self._r, 
				QRect(*map(int, (
					w / 2,
					h / 4,
					w / 4,
					h / 4 ))))
		]


class Overlay(QMainWindow):
	def __init__(self, parent=None, qt_flags=None):
		super().__init__(parent, *(qt_flags or tuple()))

		self.setWindowTitle("Overlay")

	def gui_loaded_event(self, dpi, res: Optional[Tuple[int, int]] = None):
		"""
		Most initial style-logic is in here because now
			the GUI has finished loading (so pywin32 can target it)
		"""
		# initiate WinAPIClient
		self.winapi = WinAPIClient(
			init_overlay=True,
			logging_level=logging.DEBUG
		)

		self.DPI = dpi
		self.SIZE = res or Helper.screen_size()
		self.DPI_SIZE = [int(v / dpi) for v in self.SIZE]
		logging.debug(f"Resize -> \n\tRes: {self.SIZE}\n\tDPI: {self.DPI}")

		# set resolution
		self.resize(*self.SIZE)
		self.showFullScreen()
	
		# make background invisible
		self.setStyleSheet("background-color: rgb{};".format(
			str(tuple(self.winapi.color_key))
		))

		# make central widget
		self.central = WidgetManager(self)
		self.setCentralWidget(self.central)

	def keyPressEvent(self, e: QKeyEvent):
		# close on Q or ESC
		if e.key() in (Qt.Key_Q, Qt.Key_Escape):
			self.close()


if __name__ == '__main__':
	DPI_ADJUSTED_RES = Helper.screen_size()

	app = QApplication(sys.argv)
	overlay = Overlay()

	# Now the resolution has updated: since it's a thread it's DPI-unadjusted
	DPI_UNADJUSTED_RES = Helper.screen_size()

	overlay.show()
	overlay.gui_loaded_event(DPI_UNADJUSTED_RES[0]/DPI_ADJUSTED_RES[0])

	sys.exit(app.exec_())
