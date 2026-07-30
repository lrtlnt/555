import tkinter as tk
import os
import constants as c
from datetime import datetime

class TaskbarButton(tk.Canvas):
    """任务栏按钮"""
    def __init__(self, parent, window, text="", command=None):
        super().__init__(parent, height=22, highlightthickness=0, bd=0, bg=c.TASKBAR_COLOR)
        self.window = window
        self.text = text
        self.command = command
        self.hover = False
        self.pressed = False
        self.active = False
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Configure>", self.on_resize)
        
        self.draw()
    
    def draw(self):
        self.delete("all")
        w = self.winfo_width() or 160
        h = 22
        
        if self.active:
            # 按下/激活状态
            self.create_rectangle(2, 2, w-3, h-3, fill="#1A4A8C", outline="#0F3875")
            self.create_line(3, 3, w-4, 3, fill="#2A5A9C")
            self.create_line(3, 3, 3, h-4, fill="#2A5A9C")
            text_color = "#FFFFFF"
        elif self.pressed:
            self.create_rectangle(2, 2, w-3, h-3, fill="#1A4A8C", outline="#0F3875")
            text_color = "#FFFFFF"
        elif self.hover:
            # 悬停
            self.create_rectangle(2, 2, w-3, h-3, fill="#4C9CFF", outline="#3A8CEE")
            self.create_line(3, 3, w-4, 3, fill="#6CB0FF")
            self.create_line(3, 3, 3, h-4, fill="#6CB0FF")
            text_color = "#FFFFFF"
        else:
            # 普通状态
            self.create_rectangle(2, 2, w-3, h-3, fill="#245EDC", outline="#164EC9")
            text_color = "#FFFFFF"
        
        # 文字
        display_text = self.text
        if len(display_text) > 20:
            display_text = display_text[:17] + "..."
        self.create_text(8, h//2, text=display_text, font=c.DEFAULT_FONT, 
                        fill=text_color, anchor="w")
    
    def set_active(self, active):
        self.active = active
        self.draw()
    
    def set_text(self, text):
        self.text = text
        self.draw()
    
    def on_resize(self, event):
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

class StartMenu(tk.Frame):
    """开始菜单"""
    def __init__(self, parent, app_manager=None):
        super().__init__(parent, bd=1, bg=c.STARTMENU_HEADER)
        self.app_manager = app_manager
        self.visible = False
        
        # 顶部蓝色条
        self.header = tk.Frame(self, bg=c.STARTMENU_HEADER, height=54)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # 用户头像和名称
        self.user_frame = tk.Frame(self.header, bg=c.STARTMENU_HEADER)
        self.user_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.avatar = tk.Canvas(self.user_frame, width=42, height=42, bg="#FFFFFF", bd=0)
        self.avatar.create_rectangle(4, 4, 38, 38, fill="#3A6EA5", outline="#FFFFFF", width=2)
        self.avatar.create_text(21, 21, text="👤", font=("Segoe UI", 18))
        self.avatar.pack(side=tk.LEFT)
        
        self.username = tk.Label(self.user_frame, text="Administrator", font=("Tahoma", 11, "bold"),
                               fg="#FFFFFF", bg=c.STARTMENU_HEADER)
        self.username.pack(side=tk.LEFT, padx=10)
        
        # 主体内容（左右分栏）
        self.body = tk.Frame(self, bg=c.STARTMENU_LEFT)
        self.body.pack(fill=tk.BOTH, expand=True)
        
        # 左侧栏（白色）- 常用程序
        self.left_frame = tk.Frame(self.body, bg=c.STARTMENU_LEFT, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.left_frame.pack_propagate(False)
        
        # 左侧程序列表
        programs = [
            ("📄 记事本", lambda: self.open_app("notepad")),
            ("🧮 计算器", lambda: self.open_app("calculator")),
            ("🎨 画图", lambda: self.open_app("paint")),
            ("separator", None),
            ("📁 我的电脑", lambda: self.open_app("my_computer")),
            ("▶️ 运行...", lambda: self.open_app("run")),
        ]
        
        for item in programs:
            if item[0] == "separator":
                sep = tk.Frame(self.left_frame, height=2, bg=c.STARTMENU_SEPARATOR)
                sep.pack(fill=tk.X, padx=5, pady=3)
                continue
            
            label, cmd = item
            lbl = tk.Label(self.left_frame, text=label, font=c.DEFAULT_FONT,
                          bg=c.STARTMENU_LEFT, fg=c.TEXT_COLOR, anchor="w", padx=10, pady=4)
            lbl.pack(fill=tk.X)
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg=c.MENU_SELECTED, fg="#FFFFFF"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg=c.STARTMENU_LEFT, fg=c.TEXT_COLOR))
            lbl.bind("<Button-1>", lambda e, c=cmd: (self.hide(), c()))
        
        # 右侧栏（浅蓝色）- 系统位置
        self.right_frame = tk.Frame(self.body, bg=c.STARTMENU_RIGHT, width=180)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_frame.pack_propagate(False)
        
        right_items = [
            ("我的文档", lambda: self.open_app("my_computer", path=os.path.expanduser("~"))),
            ("我最近的文档", None),
            ("图片收藏", None),
            ("我的音乐", None),
            ("separator", None),
            ("我的电脑", lambda: self.open_app("my_computer", path="")),
            ("网上邻居", None),
            ("separator", None),
            ("控制面板", None),
            ("打印机和传真", None),
            ("separator", None),
            ("帮助和支持", None),
            ("搜索", None),
            ("运行...", lambda: self.open_app("run")),
        ]
        
        for item in right_items:
            if item[0] == "separator":
                sep = tk.Frame(self.right_frame, height=2, bg="#B0CDEF")
                sep.pack(fill=tk.X, padx=5, pady=3)
                continue
            
            label, cmd = item
            lbl = tk.Label(self.right_frame, text=f"  {label}", font=c.DEFAULT_FONT,
                          bg=c.STARTMENU_RIGHT, fg=c.TEXT_COLOR, anchor="w", padx=10, pady=3)
            lbl.pack(fill=tk.X)
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg=c.MENU_SELECTED, fg="#FFFFFF"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg=c.STARTMENU_RIGHT, fg=c.TEXT_COLOR))
            if cmd:
                lbl.bind("<Button-1>", lambda e, c=cmd: (self.hide(), c()))
        
        # 底部栏
        self.bottom = tk.Frame(self, bg=c.STARTMENU_BOTTOM, height=38)
        self.bottom.pack(fill=tk.X)
        self.bottom.pack_propagate(False)
        
        # 注销和关机按钮
        self.btn_logoff = tk.Label(self.bottom, text="  注销(L)  ", font=c.BOLD_FONT,
                                  fg="#FFFFFF", bg=c.STARTMENU_BOTTOM, padx=10, pady=5)
        self.btn_logoff.pack(side=tk.LEFT, padx=10, pady=5)
        self.btn_logoff.bind("<Enter>", lambda e: self.btn_logoff.config(bg="#4C9CFF"))
        self.btn_logoff.bind("<Leave>", lambda e: self.btn_logoff.config(bg=c.STARTMENU_BOTTOM))
        
        self.btn_shutdown = tk.Label(self.bottom, text="  关闭计算机(U)...  ", font=c.BOLD_FONT,
                                    fg="#FFFFFF", bg=c.STARTMENU_BOTTOM, padx=10, pady=5)
        self.btn_shutdown.pack(side=tk.RIGHT, padx=10, pady=5)
        self.btn_shutdown.bind("<Enter>", lambda e: self.btn_shutdown.config(bg="#C13B3B"))
        self.btn_shutdown.bind("<Leave>", lambda e: self.btn_shutdown.config(bg=c.STARTMENU_BOTTOM))
        self.btn_shutdown.bind("<Button-1>", lambda e: self.shutdown())
    
    def open_app(self, app_name, **kwargs):
        if self.app_manager:
            self.app_manager.open_app(app_name, **kwargs)
    
    def show(self, x, y):
        """显示开始菜单，从任务栏向上弹出"""
        # 先放置控件以便计算实际高度
        self.update_idletasks()
        menu_height = self.winfo_height()
        if menu_height < 10:
            menu_height = 500  # 默认高度
        # y坐标是任务栏顶部位置，菜单底部对齐任务栏顶部
        self.place(x=x, y=y - menu_height)
        self.lift()
        self.visible = True
    
    def hide(self):
        self.place_forget()
        self.visible = False
    
    def shutdown(self):
        if self.app_manager and hasattr(self.app_manager, 'shutdown'):
            self.hide()
            self.app_manager.shutdown()

class SystemTray(tk.Frame):
    """系统托盘"""
    def __init__(self, parent):
        super().__init__(parent, bg="#1245A0", bd=0, padx=5)
        
        # 音量图标
        self.volume = tk.Label(self, text="🔊", font=("Segoe UI", 10), bg="#1245A0", fg="#FFFFFF")
        self.volume.pack(side=tk.LEFT, padx=3)
        
        # 网络图标
        self.network = tk.Label(self, text="📶", font=("Segoe UI", 10), bg="#1245A0", fg="#FFFFFF")
        self.network.pack(side=tk.LEFT, padx=3)
        
        # 时间
        self.time_label = tk.Label(self, text="", font=c.DEFAULT_FONT, bg="#1245A0", fg="#FFFFFF")
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        self.update_time()
    
    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        self.time_label.config(text=time_str)
        self.after(1000, self.update_time)

class Taskbar(tk.Frame):
    """XP任务栏"""
    def __init__(self, parent, app_manager=None):
        super().__init__(parent, bg=c.TASKBAR_COLOR, height=c.TASKBAR_HEIGHT, bd=1)
        self.parent = parent
        self.app_manager = app_manager
        self.window_buttons = {}
        self.start_menu = None
        
        self.pack(side=tk.BOTTOM, fill=tk.X)
        self.pack_propagate(False)
        
        # 开始按钮
        self.start_btn = tk.Canvas(self, width=100, height=c.TASKBAR_HEIGHT, 
                                  highlightthickness=0, bd=0, bg=c.TASKBAR_COLOR)
        self.start_btn.pack(side=tk.LEFT, padx=0)
        self.draw_start_button()
        self.start_btn.bind("<Button-1>", self.toggle_start_menu)
        self.start_btn.bind("<Enter>", lambda e: self.draw_start_button(hover=True))
        self.start_btn.bind("<Leave>", lambda e: self.draw_start_button(hover=False))
        
        # 快速启动栏
        self.quick_launch = tk.Frame(self, bg=c.TASKBAR_COLOR, padx=3)
        self.quick_launch.pack(side=tk.LEFT)
        
        # 快速启动按钮
        ql_buttons = [
            ("🖥️", lambda: app_manager.open_app("my_computer")),
            ("🌐", lambda: app_manager.open_app("notepad", text="IE浏览器")),
            ("📄", lambda: app_manager.open_app("notepad")),
        ]
        
        for icon, cmd in ql_buttons:
            btn = tk.Label(self.quick_launch, text=icon, font=("Segoe UI", 12),
                          bg=c.TASKBAR_COLOR, fg="#FFFFFF", padx=3)
            btn.pack(side=tk.LEFT)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=c.TASKBAR_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.TASKBAR_COLOR))
            btn.bind("<Button-1>", lambda e, c=cmd: c())
        
        # 分隔线
        sep = tk.Frame(self, width=2, bg="#1641B0")
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
        
        # 窗口按钮区域
        self.buttons_frame = tk.Frame(self, bg=c.TASKBAR_COLOR)
        self.buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        
        # 系统托盘
        self.tray = SystemTray(self)
        self.tray.pack(side=tk.RIGHT)
    
    def draw_start_button(self, hover=False, pressed=False):
        self.start_btn.delete("all")
        w = 100
        h = c.TASKBAR_HEIGHT
        
        if pressed:
            start_color = "#0F3875"
            end_color = "#2A5A9C"
        elif hover:
            start_color = "#2A6AD0"
            end_color = "#5CACFF"
        else:
            start_color = c.TASKBAR_START
            end_color = c.TASKBAR_END
        
        # 渐变背景
        for i in range(h):
            ratio = i / h
            r1, g1, b1 = self._hex_to_rgb(start_color)
            r2, g2, b2 = self._hex_to_rgb(end_color)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.start_btn.create_line(0, i, w, i, fill=color)
        
        # 边框
        self.start_btn.create_line(1, 1, w-2, 1, fill="#5CACFF" if hover else "#4C9CFF")
        self.start_btn.create_line(1, 1, 1, h-2, fill="#5CACFF" if hover else "#4C9CFF")
        self.start_btn.create_line(1, h-2, w-2, h-2, fill="#0A246A")
        self.start_btn.create_line(w-2, 1, w-2, h-2, fill="#0A246A")
        
        # Windows徽标和文字
        self.start_btn.create_oval(8, 5, 28, 25, fill="#000000", outline="")
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
        for i, color in enumerate(colors):
            x = 12 + (i % 2) * 8
            y = 9 + (i // 2) * 8
            self.start_btn.create_rectangle(x, y, x+6, y+6, fill=color, outline="#FFFFFF")
        
        self.start_btn.create_text(38, h//2, text="开始", font=("Tahoma", 9, "bold"),
                                  fill="#FFFFFF", anchor="w")
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def toggle_start_menu(self, event=None):
        if not self.start_menu:
            self.start_menu = StartMenu(self.winfo_toplevel(), self.app_manager)
        
        if self.start_menu.visible:
            self.start_menu.hide()
            self.draw_start_button()
        else:
            self.draw_start_button(pressed=True)
            x = self.start_btn.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
            y = self.winfo_rooty() - self.winfo_toplevel().winfo_rooty()
            self.start_menu.show(x, y)
    
    def add_window_button(self, window):
        """添加窗口按钮到任务栏"""
        btn = TaskbarButton(self.buttons_frame, window, window.title, 
                          lambda w=window: self.on_window_button_click(w))
        btn.pack(side=tk.LEFT, padx=2, fill=tk.Y)
        self.window_buttons[window] = btn
        return btn
    
    def remove_window_button(self, window):
        """移除窗口按钮"""
        if window in self.window_buttons:
            self.window_buttons[window].destroy()
            del self.window_buttons[window]
    
    def on_window_button_click(self, window):
        # 判断是否是外部窗口（没有place方法）
        is_external = not hasattr(window, 'place')
        
        if is_external:
            # 外部窗口处理
            if window.minimized:
                window.minimized = False
                window.activate()
                self.window_buttons[window].set_active(True)
            elif window.active:
                window.minimize()
                self.window_buttons[window].set_active(False)
            else:
                window.activate()
                for w, btn in self.window_buttons.items():
                    btn.set_active(w == window)
        else:
            # 内部窗口处理
            if window.minimized:
                # 恢复窗口
                window.minimized = False
                window.place(x=window.winfo_x(), y=window.winfo_y())
                window.lift()
                window.activate()
                self.window_buttons[window].set_active(True)
            elif window.active:
                # 最小化
                window.minimize()
                self.window_buttons[window].set_active(False)
            else:
                window.activate()
                for w, btn in self.window_buttons.items():
                    btn.set_active(w == window)
    
    def deactivate_buttons(self, except_window=None):
        for w, btn in self.window_buttons.items():
            if w != except_window:
                btn.set_active(False)
    
    def set_active_window(self, window):
        for w, btn in self.window_buttons.items():
            btn.set_active(w == window)
