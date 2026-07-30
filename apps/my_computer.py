#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows XP 资源管理器
浏览真实文件系统
"""
import tkinter as tk
from tkinter import ttk, simpledialog
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPButton, show_error, show_info, bind_long_press
from xpmenu import XPContextMenu
from filesystem import fs, clipboard, FileInfo
from properties import PropertiesDialog

class FileIcon(tk.Frame):
    """文件列表中的图标"""
    def __init__(self, parent, file_info, on_double_click, on_right_click, app_manager=None):
        super().__init__(parent, bg=c.WINDOW_BG, bd=2, padx=4, pady=4)
        self.file_info = file_info
        self.on_double_click = on_double_click
        self.on_right_click = on_right_click
        self.app_manager = app_manager
        self.selected = False
        
        icon_text = file_info.get_icon()
        
        self.icon_label = tk.Label(self, text=icon_text, font=("Segoe UI", 32),
                                  bg=c.WINDOW_BG, bd=0)
        self.icon_label.pack()
        
        self.text_label = tk.Label(self, text=file_info.name, font=c.ICON_FONT,
                                  bg=c.WINDOW_BG, wraplength=80, justify=tk.CENTER)
        self.text_label.pack()
        
        for widget in [self, self.icon_label, self.text_label]:
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Double-Button-1>", self.on_double)
            widget.bind("<Button-3>", self.on_right)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
    
    def on_click(self, event):
        if hasattr(self.master, 'deselect_all'):
            self.master.deselect_all()
        self.select()
    
    def on_double(self, event):
        if self.on_double_click:
            self.on_double_click(self.file_info)
    
    def on_right(self, event):
        if self.on_right_click:
            self.on_right_click(self, event)
    
    def on_enter(self, event):
        if not self.selected:
            self.config(bg="#E5F0FC")
            self.icon_label.config(bg="#E5F0FC")
            self.text_label.config(bg="#E5F0FC")
    
    def on_leave(self, event):
        if not self.selected:
            self.config(bg=c.WINDOW_BG)
            self.icon_label.config(bg=c.WINDOW_BG)
            self.text_label.config(bg=c.WINDOW_BG)
    
    def select(self):
        self.selected = True
        self.config(bg="#316AC5")
        self.icon_label.config(bg="#316AC5")
        self.text_label.config(bg="#316AC5", fg="#FFFFFF")
    
    def deselect(self):
        self.selected = False
        self.config(bg=c.WINDOW_BG)
        self.icon_label.config(bg=c.WINDOW_BG)
        self.text_label.config(bg=c.WINDOW_BG, fg=c.TEXT_COLOR)

class DriveIcon(tk.Frame):
    """驱动器图标"""
    def __init__(self, parent, name, path, on_double_click):
        super().__init__(parent, bg=c.WINDOW_BG, bd=2, padx=4, pady=4)
        self.path = path
        
        self.icon_label = tk.Label(self, text="💽", font=("Segoe UI", 32), bg=c.WINDOW_BG)
        self.icon_label.pack()
        
        self.text_label = tk.Label(self, text=name, font=c.ICON_FONT, bg=c.WINDOW_BG)
        self.text_label.pack()
        
        for widget in [self, self.icon_label, self.text_label]:
            widget.bind("<Double-Button-1>", lambda e: on_double_click(path))
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
    
    def on_click(self, event):
        if hasattr(self.master, 'deselect_all'):
            self.master.deselect_all()
        self.config(bg="#316AC5")
        self.icon_label.config(bg="#316AC5")
        self.text_label.config(bg="#316AC5", fg="#FFFFFF")
    
    def on_enter(self, event):
        self.config(bg="#E5F0FC")
        self.icon_label.config(bg="#E5F0FC")
        self.text_label.config(bg="#E5F0FC")
    
    def on_leave(self, event):
        self.config(bg=c.WINDOW_BG)
        self.icon_label.config(bg=c.WINDOW_BG)
        self.text_label.config(bg=c.WINDOW_BG, fg=c.TEXT_COLOR)

class MyComputer(XPWindow):
    """我的电脑/资源管理器"""
    def __init__(self, parent, folder=None, path=None, **kwargs):
        super().__init__(parent, title="我的电脑", width=780, height=520)
        self.app_manager = parent
        self.current_path = path if path is not None else ""
        self.history = []
        self.history_index = -1
        self.file_icons = []
        self.selected_file = None
        
        self.place(x=50, y=30)
        
        self._create_toolbar()
        self._create_address_bar()
        
        self.main_paned = ttk.PanedWindow(self.content_frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self._create_left_panel()
        self._create_file_panel()
        self._create_statusbar()
        
        self.navigate_to(self.current_path)
        self.activate()
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=30, bd=1, relief=tk.RAISED)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        toolbar_frame.pack_propagate(False)
        
        buttons = [
            ("⬅️ 后退", self.go_back, False),
            ("➡️ 前进", self.go_forward, False),
            ("⬆️ 向上", self.go_up, True),
            ("separator", None, False),
            ("🔍 搜索", None, False),
            ("📂 文件夹", None, False),
            ("separator", None, False),
            ("✂️ 剪切", self.cut_selected, False),
            ("📋 复制", self.copy_selected, False),
            ("📄 粘贴", self.paste, clipboard.has_files()),
            ("❌ 删除", self.delete_selected, False),
            ("separator", None, False),
            ("📊 查看", None, False),
        ]
        
        self.toolbar_buttons = {}
        
        for item in buttons:
            if item[0] == "separator":
                sep = tk.Frame(toolbar_frame, width=2, bg=c.BUTTON_SHADOW)
                sep.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
                continue
            
            text, cmd, enabled = item
            btn = tk.Label(toolbar_frame, text=text, font=c.DEFAULT_FONT,
                         bg=c.BUTTON_FACE, padx=5, pady=3)
            btn.pack(side=tk.LEFT, padx=1)
            self.toolbar_buttons[text] = (btn, cmd, enabled)
            if enabled:
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5F0FC", relief=tk.RAISED, bd=1))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.BUTTON_FACE, relief=tk.FLAT, bd=0))
                btn.bind("<Button-1>", lambda e, c=cmd: c() if c else None)
            else:
                btn.config(fg=c.DISABLED_TEXT)
    
    def _update_toolbar_buttons(self):
        """更新工具栏按钮状态"""
        for text, (btn, cmd, enabled) in self.toolbar_buttons.items():
            if text == "⬅️ 后退":
                enabled = self.history_index > 0
            elif text == "➡️ 前进":
                enabled = self.history_index < len(self.history) - 1
            elif text == "⬆️ 向上":
                enabled = self.current_path != ""
            elif text == "📄 粘贴":
                enabled = clipboard.has_files() and self.current_path != ""
            elif text in ["✂️ 剪切", "📋 复制", "❌ 删除"]:
                enabled = self.selected_file is not None
            
            if enabled:
                btn.config(fg=c.TEXT_COLOR)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5F0FC", relief=tk.RAISED, bd=1))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.BUTTON_FACE, relief=tk.FLAT, bd=0))
                btn.bind("<Button-1>", lambda e, c=cmd: c() if c else None)
            else:
                btn.config(fg=c.DISABLED_TEXT)
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
                btn.unbind("<Button-1>")
    
    def _create_address_bar(self):
        """创建地址栏"""
        addr_frame = tk.Frame(self.content_frame, bg=c.WINDOW_BG, height=28)
        addr_frame.pack(fill=tk.X, padx=2)
        addr_frame.pack_propagate(False)
        
        tk.Label(addr_frame, text="地址(D):", font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(side=tk.LEFT, padx=3)
        
        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(addr_frame, textvariable=self.address_var, font=c.DEFAULT_FONT)
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3, pady=3)
        self.address_entry.bind("<Return>", self.on_address_enter)
        
        go_btn = XPButton(addr_frame, "转到", width=50, command=self.on_address_go)
        go_btn.pack(side=tk.RIGHT, padx=3, pady=2)
    
    def _create_left_panel(self):
        """创建左侧常见任务面板"""
        left_frame = tk.Frame(self.main_paned, bg=c.WINDOW_BG, width=200)
        self.main_paned.add(left_frame, weight=1)
        
        self.left_canvas = tk.Canvas(left_frame, bg=c.WINDOW_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.left_canvas.yview)
        self.left_content = tk.Frame(self.left_canvas, bg=c.WINDOW_BG)
        
        self.left_content.bind("<Configure>", 
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all")))
        
        self.left_canvas.create_window((0, 0), window=self.left_content, anchor="nw")
        self.left_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if self.current_path:
            self._create_task_panel("文件和文件夹任务", [
                ("📄 创建新文件夹", self.create_new_folder),
                ("🌐 发布到Web", None),
                ("📤 共享此文件夹", None),
            ])
        
        self._create_task_panel("其他位置", [
            ("🏠 桌面", lambda: self.navigate_to(fs.get_desktop())),
            ("📁 我的文档", lambda: self.navigate_to(os.path.expanduser("~"))),
            ("💻 我的电脑", lambda: self.navigate_to("")),
        ])
        
        self.detail_frame = self._create_task_panel("详细信息", [])
    
    def _create_task_panel(self, title, items):
        """创建一个任务面板组"""
        panel = tk.Frame(self.left_content, bg=c.WINDOW_BG, bd=1, relief=tk.GROOVE)
        panel.pack(fill=tk.X, padx=5, pady=3)
        
        title_frame = tk.Frame(panel, bg="#316AC5", height=20)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_canvas = tk.Canvas(title_frame, height=20, highlightthickness=0, bg="#316AC5")
        title_canvas.pack(fill=tk.BOTH, expand=True)
        title_canvas.create_text(10, 10, text=title, font=c.BOLD_FONT, fill="#FFFFFF", anchor=tk.W)
        
        content_frame = tk.Frame(panel, bg="#D6E5F5", padx=10, pady=5)
        content_frame.pack(fill=tk.X)
        
        for text, cmd in items:
            lbl = tk.Label(content_frame, text=text, font=c.DEFAULT_FONT, bg="#D6E5F5",
                         fg="#003399", cursor="hand2", anchor=tk.W, pady=2)
            lbl.pack(fill=tk.X)
            if cmd:
                lbl.bind("<Button-1>", lambda e, c=cmd: c())
                lbl.bind("<Enter>", lambda e, l=lbl: l.config(fg="#316AC5", underline=True))
                lbl.bind("<Leave>", lambda e, l=lbl: l.config(fg="#003399", underline=False))
        
        return content_frame
    
    def _create_file_panel(self):
        """创建右侧文件列表面板"""
        right_frame = tk.Frame(self.main_paned, bg=c.WINDOW_BG)
        self.main_paned.add(right_frame, weight=4)
        
        self.file_canvas = tk.Canvas(right_frame, bg=c.WINDOW_BG, highlightthickness=0)
        file_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.file_canvas.yview)
        
        self.file_frame = tk.Frame(self.file_canvas, bg=c.WINDOW_BG)
        self.file_frame.bind("<Configure>",
            lambda e: self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all")))
        
        self.file_canvas.create_window((0, 0), window=self.file_frame, anchor="nw")
        self.file_canvas.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_canvas.bind("<Button-3>", self.show_context_menu)
        self.file_frame.bind("<Button-3>", self.show_context_menu)
        # 绑定长按事件，触屏长按触发右键
        bind_long_press(self.file_canvas)
        bind_long_press(self.file_frame)
    
    def _create_statusbar(self):
        """创建状态栏"""
        statusbar = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=22, bd=1, relief=tk.SUNKEN)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=(0, 2))
        statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(statusbar, text="", font=c.DEFAULT_FONT, bg=c.BUTTON_FACE, anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_objects = tk.Label(statusbar, text="0 个对象", font=c.DEFAULT_FONT, 
                                      bg=c.BUTTON_FACE, bd=1, relief=tk.SUNKEN, padx=10)
        self.status_objects.pack(side=tk.RIGHT)
    
    def navigate_to(self, path, add_history=True):
        """导航到指定路径"""
        if add_history and self.current_path != path:
            self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index = len(self.history) - 1
        
        self.current_path = path
        
        if path == "":
            self.title_label.config(text="我的电脑")
            self.address_var.set("我的电脑")
        else:
            self.title_label.config(text=os.path.basename(path) or path)
            self.address_var.set(path)
        
        self.refresh()
    
    def refresh(self):
        """刷新文件列表"""
        for icon in self.file_icons:
            icon.destroy()
        self.file_icons = []
        self.selected_file = None
        
        row, col = 0, 0
        max_cols = 6
        
        if self.current_path == "":
            # 显示驱动器和特殊文件夹
            drives = fs.get_drives()
            for name, drive_path in drives:
                icon = DriveIcon(self.file_frame, name, drive_path, self.navigate_to)
                icon.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                self.file_icons.append(icon)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # 特殊文件夹
            for name, folder_path, icon_text in fs.get_special_folders():
                icon = FileIcon(self.file_frame, FileInfo(folder_path) if folder_path else FileInfo(""),
                              self.on_file_double_click, self.show_file_context_menu, self.app_manager)
                icon.text_label.config(text=name)
                icon.icon_label.config(text=icon_text)
                icon.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                self.file_icons.append(icon)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        else:
            # 显示文件列表
            files = fs.list_files(self.current_path)
            for file_info in files:
                icon = FileIcon(self.file_frame, file_info, self.on_file_double_click,
                              self.show_file_context_menu, self.app_manager)
                icon.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                self.file_icons.append(icon)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        obj_count = len(self.file_icons)
        self.status_objects.config(text=f"{obj_count} 个对象")
        if self.current_path == "":
            self.status_label.config(text="  我的电脑")
        else:
            self.status_label.config(text=f"  {self.current_path}")
        
        self._update_toolbar_buttons()
    
    def on_file_double_click(self, file_info):
        """双击文件 - 统一在XP内部处理"""
        if file_info.is_dir:
            self.navigate_to(file_info.path)
            return
        
        ext = file_info.get_extension()
        
        # 文本类文件 - 用记事本打开
        text_exts = ['.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js', 
                    '.csv', '.log', '.ini', '.conf', '.cfg', '.java', '.c', '.cpp', 
                    '.h', '.hpp', '.sh', '.yaml', '.yml', '.toml', '.bat', '.cmd']
        if ext in text_exts:
            self.app_manager.open_app("notepad", file_path=file_info.path)
            return
        
        # 图片类文件 - 用图片查看器打开
        image_exts = ['.png', '.gif', '.pgm', '.ppm', '.bmp']
        if ext in image_exts:
            self.app_manager.open_app("image_viewer", image_path=file_info.path)
            return
        
        # 可执行文件 - 打开通用程序容器
        exe_exts = ['.exe', '.msi', '.bat', '.cmd', '.sh', '.com', '.scr']
        if ext in exe_exts:
            program_name = file_info.name
            self.app_manager.open_app("generic_program", program_name=program_name, program_path=file_info.path)
            return
        
        # 其他不支持的文件类型
        show_info(self.app_manager, "Windows 无法打开此文件。该文件类型不受支持，或需要相应的程序才能打开。")
    
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to(self.history[self.history_index], add_history=False)
    
    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.navigate_to(self.history[self.history_index], add_history=False)
    
    def go_up(self):
        if self.current_path:
            parent = fs.get_parent_path(self.current_path)
            if parent is not None:
                self.navigate_to(parent)
            else:
                self.navigate_to("")
    
    def create_new_folder(self):
        name = simpledialog.askstring("新建文件夹", "输入文件夹名:", initialvalue="新建文件夹")
        if name and self.current_path:
            fs.create_folder(self.current_path, name)
            self.refresh()
    
    def paste(self):
        if clipboard.has_files() and self.current_path:
            for src_path in clipboard.files:
                if clipboard.operation == 'copy':
                    fs.copy_file(src_path, self.current_path)
                elif clipboard.operation == 'cut':
                    fs.move_file(src_path, self.current_path)
            if clipboard.operation == 'cut':
                clipboard.clear()
            self.refresh()
    
    def on_address_enter(self, event):
        self.on_address_go()
    
    def on_address_go(self):
        path = self.address_var.get()
        if path == "我的电脑" or path == "":
            self.navigate_to("")
        elif os.path.exists(path):
            self.navigate_to(path)
        else:
            show_error(self.app_manager, f"找不到路径 '{path}'")
    
    def deselect_all(self):
        for icon in self.file_icons:
            if hasattr(icon, 'deselect'):
                icon.deselect()
        self.selected_file = None
        self._update_toolbar_buttons()
    
    def show_context_menu(self, event):
        self.deselect_all()
        
        menu = XPContextMenu(self)
        menu.add_item("查看(V)", None)
        menu.add_item("排列图标(I)", None)
        menu.add_separator()
        menu.add_item("刷新(E)", self.refresh)
        menu.add_separator()
        
        if self.current_path:
            menu.add_item("粘贴(P)", self.paste, enabled=clipboard.has_files(), icon="📋")
            menu.add_item("粘贴快捷方式(S)", None, enabled=False)
            menu.add_separator()
            
            new_menu = menu.add_submenu("新建(W)", None)
            new_menu.add_item("文件夹(F)", self.create_new_folder, icon="📁")
            new_menu.add_item("文本文档(T)", self.create_new_text_file, icon="📄")
            
            menu.add_separator()
            menu.add_item("属性(R)", None)
        
        menu.show(event.x, event.y)
    
    def create_new_text_file(self):
        name = simpledialog.askstring("新建", "输入文件名:", initialvalue="新建文本文档.txt")
        if name and self.current_path:
            fs.create_file(self.current_path, name, "")
            self.refresh()
    
    def show_file_context_menu(self, file_icon, event):
        self.deselect_all()
        file_icon.select()
        self.selected_file = file_icon.file_info
        self._update_toolbar_buttons()
        
        x = file_icon.winfo_x() + event.x
        y = file_icon.winfo_y() + event.y
        
        menu = XPContextMenu(self.file_frame)
        menu.add_item("打开(O)", lambda: self.on_file_double_click(file_icon.file_info), icon="📂")
        menu.add_separator()
        menu.add_item("剪切(T)", lambda: self.cut_file(file_icon.file_info), icon="✂️")
        menu.add_item("复制(C)", lambda: self.copy_file(file_icon.file_info), icon="📋")
        menu.add_item("创建快捷方式", None, enabled=False)
        menu.add_item("删除(D)", lambda: self.delete_file(file_icon.file_info), icon="🗑️")
        menu.add_item("重命名(M)", lambda: self.rename_file(file_icon))
        menu.add_separator()
        menu.add_item("属性(R)", lambda: self.show_properties(file_icon.file_info), icon="⚙️")
        
        menu.show(x, y)
    
    def cut_file(self, file_info):
        clipboard.set_files([file_info.path], 'cut')
        self._update_toolbar_buttons()
    
    def copy_file(self, file_info):
        clipboard.set_files([file_info.path], 'copy')
        self._update_toolbar_buttons()
    
    def delete_file(self, file_info):
        # 简单确认，后续可扩展为XP风格确认框
        fs.delete_file(file_info.path)
        self.refresh()
    
    def rename_file(self, file_icon):
        new_name = simpledialog.askstring("重命名", "输入新名称:", 
                                       initialvalue=file_icon.file_info.name)
        if new_name:
            result = fs.rename_file(file_icon.file_info.path, new_name)
            if result:
                self.refresh()
            else:
                show_error(self.app_manager, "重命名失败")
    
    def show_properties(self, file_info):
        PropertiesDialog(self.app_manager, file_info)
    
    def cut_selected(self):
        if self.selected_file:
            self.cut_file(self.selected_file)
    
    def copy_selected(self):
        if self.selected_file:
            self.copy_file(self.selected_file)
    
    def delete_selected(self):
        if self.selected_file:
            self.delete_file(self.selected_file)
