"""Capture the actual TkForge GUI in a virtual desktop for README documentation.

Usage: xvfb-run -a python tools/capture_demo.py
Requires Pillow and a working Tkinter installation. Not a substitute for GUI tests.
"""
import base64
import io
import tkinter as tk
from pathlib import Path

from PIL import ImageGrab

from main import GUIDesigner


def main():
    root = tk.Tk()
    app = GUIDesigner(root)
    app.add_widget("label", "Label")
    app.selected_widget["text"] = "Sample login form"
    app.draw_widget(app.selected_widget)
    app.add_widget("entry", "Entry")
    app.add_widget("button", "Button")
    app.selected_widget["text"] = "Sign in"
    app.draw_widget(app.selected_widget)
    root.update_idletasks()
    root.update()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    width, height = root.winfo_width(), root.winfo_height()
    image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    image.thumbnail((1100, 700))
    output = Path("docs/screenshot.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    data = io.BytesIO()
    image.convert("P", palette=1, colors=64).save(data, "PNG", optimize=True)
    print("TKFORGE_SCREENSHOT_BASE64=" + base64.b64encode(data.getvalue()).decode("ascii"))
    root.destroy()


if __name__ == "__main__":
    main()
