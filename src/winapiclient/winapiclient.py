import win32gui
import win32con
import win32api
import win32process

import logging

from typing import Optional, Tuple


class Helper:
	def screen_size(dpi: float = 1.):
		""" Get screen size of main monitor """
		# TODO add monitor=int option

		# dpi = win32api.GetMonitorInfo()
		w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
		h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

		return tuple(map(int, (w / dpi, h / dpi)))

	def hwnd_selector(
			class_name: Optional[str] = None,
			window_name: Optional[str] = None,
			active_window: Optional[bool] = False,
			foreground_window: Optional[bool] = False,
			desktop_window: Optional[bool] = False,
			assert_find: Optional[bool] = False):
		"""
		:return: HWND (Window-reference)
		:rtype: int | None
		"""

		if class_name:
			return win32gui.FindWindow(class_name, None)
		if window_name:
			return win32gui.FindWindow(None, window_name)

		if active_window:
			return win32gui.GetActiveWindow()
		if foreground_window:
			return win32gui.GetForegroundWindow()
		if desktop_window:
			return win32gui.GetDesktopWindow()

		# couldn't find a window
		if assert_find:
			raise WinAPIClient.WindowNotFound("Could not aquire window handle")
	
	def get_window_text(hwnd: int):
		return win32gui.GetWindowText(hwnd)

	def get_window_PID(hwnd: int):
		# get thread_id and process_id
		t_id, p_id = win32process.GetWindowThreadProcessId(hwnd)
		return p_id


class WinAPIClient:
	def __init__(
			self,
			*args,
			hwnd: Optional[int] = None,
			wnd_title: Optional[str] = None,
			init_overlay: bool = False,
			logging_level: Optional[int] = None,
			**kwargs):
		
		"""
		Windows API for enabling overlay-properties on windows
		`self.hwnd` defaults to the currently active window if no hwnd is provided

		:param hwnd: Get hwnd by exact value
		:param wnd_title: Get hwnd by it's title
		:param init_overlay: Immediately apply default overlay settings to hwnd
		:raises WinAPIClient.WindowNotFound: If the provided hwnd was invalid
		"""

		self.hwnd = hwnd \
			or win32gui.FindWindow(None, wnd_title) if wnd_title else None \
			or win32gui.GetActiveWindow()

		if type(self.hwnd) != int:
			raise WinAPIClient.WindowNotFound("Invalid window handler provided")
		elif self.hwnd == 0:
			raise WinAPIClient.WindowNotFound("Could not aquire window handle")
		
		if logging_level is not None:
			logging.basicConfig(level=logging_level)
		logging.debug(f"Found window: {win32gui.GetWindowText(self.hwnd)}")

		self.DEFAULT = {
			# win32con.GWL_EXSTYLE means "GetWindowLong variable extended_style"
			# (GWL_EXSTYLE is the extended style flags for the window with self.hwnd)
			"style": win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE),
			# (left, top, right, bottom) screen coordinates
			"pos": win32gui.GetWindowRect(self.hwnd),
			# an ugly color used to represent transparency
			"color_key": (130, 117, 100)
		}
		self.color_key = self.DEFAULT["color_key"]

		if init_overlay:
			self.init_overlay(*args, **kwargs)

	def init_overlay(self, *args, **kwargs):
		""" Initiate overlay mode """
		logging.debug("Initiating overlay mode")
		
		self.set_layered_mode()

		# enable color_key
		self.set_transparency(**kwargs)

		self.set_always_toplevel()

	def _get_exstyle(self):
		""" Get entire exstyle """
		return win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)

	def _set_exstyle_flag(self, flag: int):
		""" Set a single EXSTYLE flag """
		win32gui.SetWindowLong(
			self.hwnd,
			win32con.GWL_EXSTYLE,
			self._get_exstyle() | flag)

	def _clear_exstyle_flag(self, flag: int):
		""" Clear a single EXSTYLE flag """
		# to clear: set flag bits, then XOR the flag with EXSTYLE
		self._set_exstyle_flag(flag)
		win32gui.SetWindowLong(
			self.hwnd,
			win32con.GWL_EXSTYLE,
			self._get_exstyle() ^ flag)

	def _exstyle_contains_flag(self, flag: int):
		""" Returns whether EXSTYLE contains flag """
		# example: check if layered mode: self._exstyle_contains_flag(win32con.WS_EX_LAYERED)
		exstyle_flags = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
		return exstyle_flags & flag == flag

	def set_always_toplevel(self):
		"""
		Make window always appear on top of other windows
		(-1 zindex / window-priority)
		"""
		old_win_pos = win32gui.GetWindowRect(self.hwnd)
		win32gui.SetWindowPos(
			self.hwnd,
			win32con.HWND_TOPMOST,
			# last two elems are wrong, but NOSIZE flag makes it ok
			*old_win_pos,
			win32con.SWP_NOSIZE)

	def set_layered_mode(self):
		"""
		Make window click-through, set transparency to be allowed, and set color_key
		"""
		# enable transparency + layered mode
		self._set_exstyle_flag(win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)

	def set_transparency(
			self, 
			*args,
			opacity: float = 1., 
			color_key: Optional[Tuple[int, int, int]] = None,
			**kwargs):
		"""
		Set transparency for current window

		:param opacity: Float within [0, 1]
		:param color_key: (R, G, B) integers within [0, 255]
		:raises WinAPIClient.RequiresLayeredMode: If called without first enabling layered-mode
		"""

		if color_key:
			self.color_key = color_key
			logging.debug(f"Updated color key: {self.color_key}")
		
		if not self._exstyle_contains_flag(win32con.WS_EX_LAYERED):
			raise self.RequiresLayeredMode("Run self.set_layered_mode() first!")

		win32gui.SetLayeredWindowAttributes(
			self.hwnd,
			win32api.RGB(*self.color_key),
			int(opacity * 255),
			win32con.LWA_ALPHA | win32con.LWA_COLORKEY)

	def reset_style(self, retain_size=False, retain_pos=False):
		"""
		Reset the window to it's original state
		"""
		logging.debug("Resetting styles and properties")

		# reset extended style flags
		self._set_exstyle_flag(self.DEFAULT["style"])

		# reset position + topmost

		left, top, right, bottom = self.DEFAULT["pos"]
		x, y, w, h = left, top, right - left, bottom - top

		# set NOSIZE and NOMOVE according to params
		flags = 0 \
			| int(retain_size) * win32con.SWP_NOSIZE \
			| int(retain_pos) * win32con.SWP_NOMOVE

		win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, x, y, w, h, flags)

		# unset layered mode
		self._clear_exstyle_flag(win32con.WS_EX_LAYERED)


	class RequiresLayeredMode(Exception):
		pass
	class WindowNotFound(Exception):
		pass


if __name__ == "__main__":
	w = WinAPIClient(
		wnd_title="*Untitled - Notepad",
		opacity=.5,
		init_overlay=True,
		logging_level=logging.DEBUG
	)
	print(w.hwnd)
