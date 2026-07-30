import tkinter as tk
from tkinter import ttk
import constants as c
import math

class XPButton(tk.Canvas):
    """XP风格按钮"""
    def __init__(self, parent, text="", command=None, width=75, height=23, enabled=True):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bd=0, bg=c.BUTTON_FACE)
        self.text = text
        self.command = command
        self.enabled = enabled
        self.width = width
        self.height = height
        self.hover = False
        self.pressed = False
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()
    
    def draw(self):
        self.delete("all")
        w, h = self.width, self.height
        
        if not self.enabled:
            self.create_rectangle(1, 1, w-2, h-2, outline=c.BUTTON_SHADOW, fill=c.BUTTON_FACE)
            self.create_text(w//2, h//2, text=self.text, font=c.DEFAULT_FONT, 
                           fill=c.DISABLED_TEXT)
        elif self.pressed:
            self.create_rectangle(1, 1, w-2, h-2, outline=c.BUTTON_DARK_SHADOW)
            self.create_line(2, 2, w-3, 2, fill=c.BUTTON_SHADOW)
            self.create_line(2, 2, 2, h-3, fill=c.BUTTON_SHADOW)
            self.create_text(w//2+1, h//2+1, text=self.text, font=c.DEFAULT_FONT, 
                           fill=c.TEXT_COLOR)
        elif self.hover:
            self.create_rectangle(1, 1, w-2, h-2, outline="#0054E3")
            self.create_rectangle(2, 2, w-3, h-3, outline="#89B7FF")
            self.create_rectangle(3, 3, w-4, h-4, outline="#C3DCFF")
            self.create_line(4, 4, w-5, 4, fill="#E5F0FC")
            self.create_line(4, 4, 4, h-5, fill="#E5F0FC")
            self.create_text(w//2, h//2, text=self.text, font=c.DEFAULT_FONT, 
                           fill=c.TEXT_COLOR)
        else:
            self.create_rectangle(1, 1, w-2, h-2, outline=c.BUTTON_DARK_SHADOW)
            self.create_line(1, 1, w-2, 1, fill=c.BUTTON_HIGHLIGHT)
            self.create_line(1, 1, 1, h-2, fill=c.BUTTON_HIGHLIGHT)
            self.create_line(2, 2, w-3, 2, fill=c.BUTTON_LIGHT)
            self.create_line(2, 2, 2, h-3, fill=c.BUTTON_LIGHT)
            self.create_line(2, h-3, w-3, h-3, fill=c.BUTTON_SHADOW)
            self.create_line(w-3, 2, w-3, h-3, fill=c.BUTTON_SHADOW)
            self.create_text(w//2, h//2, text=self.text, font=c.DEFAULT_FONT, 
                           fill=c.TEXT_COLOR)
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        self.draw()
    
    def on_enter(self, event):
        if self.enabled:
            self.hover = True
            self.draw()
    
    def on_leave(self, event):
        self.hover = False
        self.pressed = False
        self.draw()
    
    def on_press(self, event):
        if self.enabled:
            self.pressed = True
            self.draw()
    
    def on_release(self, event):
        if self.enabled and self.pressed:
            self.pressed = False
            self.hover = True
            self.draw()
            if self.command:
                self.command()

class XPTitleBarButton(tk.Canvas):
    """标题栏按钮"""
    def __init__(self, parent, button_type="min", command=None):
        super().__init__(parent, width=26, height=22, highlightthickness=0, bd=0)
        self.button_type = button_type
        self.command = command
        self.hover = False
        self.pressed = False
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()
    
    def draw(self):
        self.delete("all")
        w, h = 26, 22
        
        if self.button_type == "close":
            if self.pressed:
                bg_color = "#8B2E2E"
                icon_color = "#FFFFFF"
            elif self.hover:
                bg_color = "#C13B3B"
                icon_color = "#FFFFFF"
            else:
                bg_color = None
                icon_color = "#FFFFFF"
        else:
            if self.pressed:
                bg_color = "#1A4A8C"
                icon_color = "#FFFFFF"
            elif self.hover:
                bg_color = "#4A80C8"
                icon_color = "#FFFFFF"
            else:
                bg_color = None
                icon_color = "#FFFFFF"
        
        if bg_color:
            self.create_rectangle(2, 2, w-3, h-3, fill=bg_color, outline=bg_color)
            self.create_rectangle(1, 1, w-2, h-2, outline="#0A246A" if not self.hover else "#8FB8E8")
        
        cx, cy = w//2, h//2
        if self.button_type == "min":
            self.create_line(cx-5, cy+3, cx+5, cy+3, fill=icon_color, width=2)
        elif self.button_type == "max":
            self.create_rectangle(cx-5, cy-4, cx+5, cy+3, outline=icon_color, width=1)
        elif self.button_type == "restore":
            self.create_rectangle(cx-6, cy-5, cx+2, cy+1, outline=icon_color, width=1)
            self.create_rectangle(cx-2, cy-1, cx+6, cy+5, outline=icon_color, width=1)
        elif self.button_type == "close":
            self.create_line(cx-5, cy-4, cx+5, cy+4, fill=icon_color, width=2)
            self.create_line(cx+5, cy-4, cx-5, cy+4, fill=icon_color, width=2)
    
    def set_type(self, button_type):
        self.button_type = button_type
        self.draw()
    
    def on_enter(self, event):
        self.hover = True
        self.draw()
    
    def on_leave(self, event):
        self.hover = False
        self.pressed = False
        self.draw()
    
    def on_press(self, event):
        self.pressed = True
        self.draw()
    
    def on_release(self, event):
        if self.pressed:
            self.pressed = False
            self.hover = True
            self.draw()
            if self.command:
                self.command()

class XPWindow(tk.Frame):
    """XP风格窗口基类"""
    def __init__(self, parent, title="窗口", width=400, height=300, icon=None):
        self.parent = parent
        self.width = width
        self.height = height
        self.title = title
        self.icon = icon
        self.active = True
        self.minimized = False
        self.maximized = False
        self.restore_geometry = None
        
        super().__init__(parent, bd=0, bg=c.BUTTON_DARK_SHADOW)
        
        # 标题栏
        self.titlebar = tk.Frame(self, height=c.TITLEBAR_HEIGHT, bd=0)
        self.titlebar.pack(fill=tk.X, side=tk.TOP)
        
        # 标题栏Canvas用于渐变
        self.titlebar_canvas = tk.Canvas(self.titlebar, height=c.TITLEBAR_HEIGHT, 
                                        highlightthickness=0, bd=0)
        self.titlebar_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 标题栏图标和文字
        self.title_content = tk.Frame(self.titlebar, height=c.TITLEBAR_HEIGHT, bd=0, bg=c.TITLEBAR_GRADIENT_START)
        self.title_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        
        if icon:
            self.icon_label = tk.Label(self.title_content, image=icon, bd=0, bg=c.TITLEBAR_GRADIENT_START)
            self.icon_label.pack(side=tk.LEFT, padx=(2, 4))
        
        self.title_label = tk.Label(self.title_content, text=title, font=c.TITLE_FONT,
                                   fg=c.TITLEBAR_TEXT_ACTIVE, bd=0, bg=c.TITLEBAR_GRADIENT_START)
        self.title_label.pack(side=tk.LEFT)
        
        # 标题栏按钮
        self.title_buttons = tk.Frame(self.titlebar, height=c.TITLEBAR_HEIGHT, bd=0, bg=c.TITLEBAR_GRADIENT_START)
        self.title_buttons.pack(side=tk.RIGHT)
        
        self.btn_min = XPTitleBarButton(self.title_buttons, "min", self.minimize)
        self.btn_min.pack(side=tk.LEFT, padx=(0, 2), pady=2)
        
        self.btn_max = XPTitleBarButton(self.title_buttons, "max", self.toggle_maximize)
        self.btn_max.pack(side=tk.LEFT, padx=(0, 2), pady=2)
        
        self.btn_close = XPTitleBarButton(self.title_buttons, "close", self.close)
        self.btn_close.pack(side=tk.LEFT, padx=(0, 2), pady=2)
        
        # 菜单栏占位
        self.menubar = None
        
        # 内容区域
        self.content_frame = tk.Frame(self, bg=c.WINDOW_BG, bd=0)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))
        
        # 拖动事件
        self._drag_data = {"x": 0, "y": 0}
        for widget in [self.titlebar, self.title_content, self.title_label, self.titlebar_canvas]:
            widget.bind("<ButtonPress-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.on_drag)
            widget.bind("<ButtonRelease-1>", self.end_drag)
            widget.bind("<Double-Button-1>", lambda e: self.toggle_maximize())
        
        # 激活事件
        self.bind("<Button-1>", self.activate)
        self.content_frame.bind("<Button-1>", self.activate)
        
        # 延迟绘制标题栏渐变
        self.after(10, self.draw_titlebar)
    
    def draw_titlebar(self):
        """绘制渐变标题栏"""
        self.titlebar_canvas.delete("all")
        
        if self.active:
            start_color = c.TITLEBAR_GRADIENT_START
            end_color = c.TITLEBAR_GRADIENT_END
            text_color = c.TITLEBAR_TEXT_ACTIVE
            bg_color = c.TITLEBAR_GRADIENT_START
        else:
            start_color = c.TITLEBAR_INACTIVE_START
            end_color = c.TITLEBAR_INACTIVE_END
            text_color = c.TITLEBAR_TEXT_INACTIVE
            bg_color = c.TITLEBAR_INACTIVE_START
        
        w = self.titlebar.winfo_width() or self.width
        h = c.TITLEBAR_HEIGHT
        
        if w < 10:
            w = self.width
        
        r1, g1, b1 = self._hex_to_rgb(start_color)
        r2, g2, b2 = self._hex_to_rgb(end_color)
        
        for i in range(h):
            ratio = i / h
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.titlebar_canvas.create_line(0, i, w, i, fill=color)
        
        self.title_content.config(bg=bg_color)
        self.title_label.config(fg=text_color, bg=bg_color)
        self.title_buttons.config(bg=bg_color)
        for btn in [self.btn_min, self.btn_max, self.btn_close]:
            btn.config(bg=bg_color)
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def set_active(self, active):
        self.active = active
        self.draw_titlebar()
    
    def activate(self, event=None):
        """激活窗口"""
        self.lift()
        self.set_active(True)
        if hasattr(self.parent, 'deactivate_other_windows'):
            self.parent.deactivate_other_windows(self)
    
    def start_drag(self, event):
        if not self.maximized:
            self._drag_data["x"] = event.x_root - self.winfo_x()
            self._drag_data["y"] = event.y_root - self.winfo_y()
    
    def on_drag(self, event):
        if not self.maximized and self._drag_data["x"] and self._drag_data["y"]:
            x = event.x_root - self._drag_data["x"]
            y = event.y_root - self._drag_data["y"]
            self.place(x=x, y=y)
    
    def end_drag(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
    
    def minimize(self):
        self.minimized = True
        self.place_forget()
        if hasattr(self.parent, 'on_window_minimize'):
            self.parent.on_window_minimize(self)
    
    def toggle_maximize(self):
        if self.maximized:
            self.maximized = False
            self.btn_max.set_type("max")
            if self.restore_geometry:
                x, y, w, h = self.restore_geometry
                self.place(x=x, y=y, width=w, height=h)
        else:
            self.maximized = True
            self.btn_max.set_type("restore")
            self.restore_geometry = (self.winfo_x(), self.winfo_y(), 
                                    self.winfo_width(), self.winfo_height())
            parent_h = self.parent.winfo_height() or self.parent.winfo_screenheight()
            self.place(x=0, y=0, relwidth=1, height=parent_h - c.TASKBAR_HEIGHT)
    
    def close(self):
        if hasattr(self.parent, 'on_window_close'):
            self.parent.on_window_close(self)
        self.destroy()
    
    def resizable(self, width_resizable=True, height_resizable=True):
        pass

class XPMenuBar(tk.Frame):
    """XP风格菜单栏"""
    def __init__(self, parent):
        super().__init__(parent, bg=c.MENU_BG, bd=0, height=22)
        self.menus = {}
        self.current_menu = None
        self.popup = None
    
    def add_menu(self, label, items):
        btn = tk.Label(self, text=f" {label} ", font=c.MENU_FONT, bg=c.MENU_BG, 
                      fg=c.TEXT_COLOR, padx=3, pady=2)
        btn.pack(side=tk.LEFT)
        btn.bind("<Enter>", lambda e, b=btn: self.on_menu_hover(b))
        btn.bind("<Button-1>", lambda e, b=btn, i=items: self.show_menu(b, i))
        self.menus[btn] = items
    
    def on_menu_hover(self, btn):
        for b in self.menus.keys():
            b.config(bg=c.MENU_BG)
        btn.config(bg=c.MENU_SELECTED, fg=c.MENU_SELECTED_TEXT)
        if self.current_menu and self.current_menu != btn:
            self.hide_menu()
            self.show_menu(btn, self.menus[btn])
    
    def show_menu(self, btn, items):
        self.hide_menu()
        self.current_menu = btn
        
        x = btn.winfo_rootx() - self.winfo_rootx()
        y = btn.winfo_rooty() - self.winfo_rooty() + btn.winfo_height()
        
        self.popup = tk.Frame(self, bg=c.MENU_BORDER, bd=1)
        self.popup.place(x=x, y=y)
        
        inner = tk.Frame(self.popup, bg=c.MENU_BG, bd=1)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        for item in items:
            if item == "separator":
                sep = tk.Frame(inner, height=2, bg=c.MENU_BORDER)
                sep.pack(fill=tk.X, padx=2, pady=2)
                continue
            
            label, command = item[0], item[1]
            enabled = item[2] if len(item) > 2 else True
            
            item_label = tk.Label(inner, text=f"  {label}  ", font=c.MENU_FONT,
                                 bg=c.MENU_BG, fg=c.TEXT_COLOR if enabled else c.DISABLED_TEXT,
                                 anchor="w", padx=10, pady=2)
            item_label.pack(fill=tk.X)
            
            if enabled:
                item_label.bind("<Enter>", lambda e, l=item_label: l.config(
                    bg=c.MENU_SELECTED, fg=c.MENU_SELECTED_TEXT))
                item_label.bind("<Leave>", lambda e, l=item_label: l.config(
                    bg=c.MENU_BG, fg=c.TEXT_COLOR))
                item_label.bind("<Button-1>", lambda e, cmd=command: (self.hide_menu(), cmd()))
        
        self.winfo_toplevel().bind("<Button-1>", self.hide_menu_outside)
    
    def hide_menu(self, event=None):
        if self.popup:
            self.popup.destroy()
            self.popup = None
        self.current_menu = None
        for b in self.menus.keys():
            b.config(bg=c.MENU_BG, fg=c.TEXT_COLOR)
    
    def hide_menu_outside(self, event):
        if self.popup:
            x1 = self.popup.winfo_rootx()
            y1 = self.popup.winfo_rooty()
            x2 = x1 + self.popup.winfo_width()
            y2 = y1 + self.popup.winfo_height()
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                self.hide_menu()
                self.winfo_toplevel().unbind("<Button-1>")

class XPMessageBox(XPWindow):
    """XP风格消息框"""
    def __init__(self, parent, title, message, icon="error", buttons=None):
        super().__init__(parent, title=title, width=350, height=150)
        self.resizable(False, False)
        
        if buttons is None:
            buttons = [("确定", self.close)]
        
        # 内容区域
        content = tk.Frame(self.content_frame, bg=c.WINDOW_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 图标
        icon_text = "❌" if icon == "error" else "⚠️" if icon == "warning" else "ℹ️" if icon == "info" else "❓"
        icon_label = tk.Label(content, text=icon_text, font=("Segoe UI", 32), bg=c.WINDOW_BG)
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # 消息文本
        msg_label = tk.Label(content, text=message, font=c.DEFAULT_FONT, bg=c.WINDOW_BG,
                            justify=tk.LEFT, wraplength=220, anchor="w")
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 按钮区域
        btn_frame = tk.Frame(self.content_frame, bg=c.WINDOW_BG)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10))
        
        for btn_text, btn_cmd in buttons:
            btn = XPButton(btn_frame, btn_text, command=btn_cmd, width=75)
            btn.pack(side=tk.RIGHT, padx=5)
        
        # 居中显示
        self.update_idletasks()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        x = parent_x + (parent_w - self.width) // 2
        y = parent_y + (parent_h - self.height) // 2
        self.place(x=x, y=y)
        
        self.activate()

def show_error(parent, message, title="错误"):
    """显示错误消息框"""
    return XPMessageBox(parent, title, message, icon="error")

def show_info(parent, message, title="提示"):
    """显示信息消息框"""
    return XPMessageBox(parent, title, message, icon="info")

def bind_long_press(widget, long_press_duration=500):
    """
    给控件绑定长按事件，长按500ms自动触发鼠标右键事件(Button-3)
    适配触屏操作：手指单击=左键，长按=右键
    """
    long_press_timer = None
    start_x = 0
    start_y = 0
    
    def _on_press(event):
        nonlocal long_press_timer, start_x, start_y
        start_x = event.x
        start_y = event.y
        # 启动长按定时器
        def _long_press():
            # 触发右键事件
            event.widget.event_generate("<Button-3>", x=event.x, y=event.y, rootx=event.x_root, rooty=event.y_root)
        long_press_timer = widget.after(long_press_duration, _long_press)
    
    def _on_release(event):
        nonlocal long_press_timer
        if long_press_timer is not None:
            widget.after_cancel(long_press_timer)
            long_press_timer = None
    
    def _on_motion(event):
        nonlocal long_press_timer, start_x, start_y
        # 如果移动超过5像素，取消长按
        if abs(event.x - start_x) > 5 or abs(event.y - start_y) > 5:
            if long_press_timer is not None:
                widget.after_cancel(long_press_timer)
                long_press_timer = None
    
    widget.bind("<ButtonPress-1>", _on_press, add="+")
    widget.bind("<ButtonRelease-1>", _on_release, add="+")
    widget.bind("<B1-Motion>", _on_motion, add="+")

def show_warning(parent, message, title="警告"):
    """显示警告消息框"""
    return XPMessageBox(parent, title, message, icon="warning")
