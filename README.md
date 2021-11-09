# Installing
```
pip install WinAPIClient
```

# Usage

### Common usage
```python3
# select the currently active window
winapi = WinAPIClient()
# alternatively select another window by title:
winapi = WinAPIClient(wnd_title="Untitled - Notepad")
#   or by manually acquired window handle:
winapi = WinAPIClient(hwnd=0xC0FFEE)

# make selected window top-level, enable transparency, and make click-through
winapi.init_overlay()
# same as:
winapi = WinAPIClient(init_overlay=True)
```

### Manually set overlay settings
```python3
# initiate layered mode (allows windows to use transparency)
# Note: layered mode will make a window click-through
winapi.set_layered_mode()

# enable transparency (sets style-flags required for transparency)
# Note: after transparency is enabled, any pixel in the window matching
#   the color "winapi.color_key" will be transparent
winapi.set_transparency(opacity=1, color_key=None)

# make the window always top-level (appearing in front of other windows)
winapi.set_always_toplevel()
```

### Other methods
```python3
# make entire window transparent (not just the color_key)
winapi.set_transparency(.5)

# reset the window style to default
winapi.reset_style(retain_size=False, retain_pos=False)
```
