# Installing
`pip install WinAPIClient`

# Usage
```python3
# call when your desired window has finished initiating
winapi = WinAPIClient()
# alternatively select another window by title:
winapi = WinAPIClient(wnd_title="Untitled - Notepad")
#   or by manually acquired window handle:
winapi = WinAPIClient(hwnd=0xC0FFEE)

# make window top-level, enable transparency, and make click-through
winapi.init_overlay()  # same as "WinAPIClient(init_overlay_mode=True)"
# Note: It's adviceable to enable full-screen on your overlay's window


# manually set overlay settings:


# initiate layered mode (allows windows to use transparency)
# Note: layered mode will make a window click-through
winapi.set_layered_mode()

# enable transparency (sets style-flags required for transparency)
# Note: after transparency is enabled, any pixel in the window matching
#   the color "winapi.color_key" will be transparent
# this method can also manually update preferred color_key
winapi.set_transparency(opacity=1, color_key=None)

# make the window always top-level (appearing in front of other windows)
winapi.set_always_toplevel()


# other, more specific features


# make entire window transparent
winapi.set_transparency(.5)

# reset the window style to default
winapi.reset_style(retain_size=False, retain_pos=False)
```
