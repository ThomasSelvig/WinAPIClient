import win32gui
import win32con
import win32api

from typing import Optional, Tuple


class WinAPIClient:

	def __init__(
			self,
			*args,
			hwnd: Optional[int] = None,
			wnd_title: Optional[str] = None,
			overlay_mode: bool = True,
			**kwargs):
		
		"""
		Windows API for enabling overlay-properties on windows
		`self.hwnd` defaults to the currently active window if no hwnd is provided

		:param hwnd: Get hwnd by exact value
		:param wnd_title: Get hwnd by it's title
		:param overlay_mode: Immediately apply default overlay settings to self.hwnd
		:raises WinAPIClient.WindowNotFound: If the provided hwnd was invalid
		"""

		self.hwnd = hwnd \
			or win32gui.FindWindow(None, wnd_title) if wnd_title else None \
			or win32gui.GetActiveWindow()

		if type(self.hwnd) != int:
			raise self.WindowNotFound("Invalid window handler provided")
		elif self.hwnd == 0:
			raise self.WindowNotFound("Could not aquire window handle")
		
		if "debug" in kwargs and kwargs["debug"]:
			print(f"Found window: {win32gui.GetWindowText(self.hwnd)}")

		self.DEFAULT = {
			# win32con.GWL_EXSTYLE means "GetWindowLong variable extended_style"
			# (GWL_EXSTYLE is the extended style flags for the window with self.hwnd)
			"style": win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE),
			# (left, top, right, bottom) screen coordinates
			"pos": win32gui.GetWindowRect(self.hwnd)
		}
		self.COLOR_KEY = 130, 117, 100  # an ugly color used to represent transparency

		if overlay_mode:
			self.set_layered_mode()
			self.set_transparency(.5)
			self.set_always_toplevel()

	def set_always_toplevel(self):
		"""
		Make window always appear on top of other windows
		(priority / -1 z-index)
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
		Make window click-through and set transparency to be allowed
		"""
		self._set_exstyle(win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)

	def set_transparency(self, opacity: float, color_key: Optional[Tuple[3]] = None):
		"""
		Set transparency for current HWND

		:param opacity: Float within [0, 1]
		:param color_key: (R, G, B) integers within [0, 255]
		"""

		if not self._exstyle_contains_flag(win32con.WS_EX_LAYERED):
			raise self.RequiresLayerMode("Run self.set_layered_mode() first!")

		win32gui.SetLayeredWindowAttributes(
			self.hwnd,
			win32api.RGB(*self.COLOR_KEY),
			int(opacity * 255),
			win32con.LWA_ALPHA | win32con.LWA_COLORKEY)

	def _get_exstyle(self):
		""" get entire exstyle """
		return win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)

	def _set_exstyle_flag(self, flag: int):
		""" set a single EXSTYLE flag """
		win32gui.SetWindowLong(
			self.hwnd,
			win32con.GWL_EXSTYLE,
			self._get_exstyle() | flag)
	
	def _clear_exstyle_flag(self, flag: int):
		""" to clear: set flag bits, then XOR the flag with EXSTYLE """
		self._set_exstyle_flag(flag)
		win32gui.SetWindowLong(
			self.hwnd,
			win32con.GWL_EXSTYLE,
			self._get_exstyle() ^ flag)

	def _exstyle_contains_flag(self, flag: int):
		# example: check if layered mode: self._exstyle_contains_flag(win32con.WS_EX_LAYERED)
		exstyle_flags = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
		return exstyle_flags & flag == flag

	def reset_style(self, retain_size=False, retain_pos=False):
		"""
		Reset the window to it's original state
		"""

		# reset extended style flags
		self._set_exstyle(self.DEFAULT["style"])

		# reset position + topmost

		left, top, right, bottom = self.DEFAULT["pos"]
		x, y, w, h = left, top, right - left, bottom - top

		# set NOSIZE and NOMOVE according to params
		flags = 0 \
			| int(retain_size) * win32con.SWP_NOSIZE \
			| int(retain_pos) * win32con.SWP_NOMOVE

		win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, x, y, w, h, flags)

		# LayeredWindowAttributes reset themselves whenever WS_EX_LAYERED is disabled


	class RequiresLayerMode(Exception):
		pass
	class WindowNotFound(Exception):
		pass


if __name__ == "__main__":
	w = WinAPIClient(
		debug=True,
		wnd_title=".gitignore - Notepad",
		overlay_mode=False)
	print(w.hwnd)
