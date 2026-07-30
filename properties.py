#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XP风格属性对话框
支持真实文件信息显示
"""
import tkinter as tk
from tkinter import ttk
import constants as c
from widgets import XPWindow, XPButton, show_error
import os
from datetime import datetime

class PropertiesDialog(XPWindow):
    """XP风格属性对话框"""
    def __init__(self, parent, file_info=None, title="属性"):
        super().__init__(parent, title=title, width=380, height=440)
        self.file_info = file_info
        self.parent_app = parent
        
        self.place(x=100, y=100)
        
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.general_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
        self.notebook.add(self.general_frame, text="常规")
        self._create_general_tab()
        
        if file_info and not file_info.is_dir:
            self.version_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
            self.notebook.add(self.version_frame, text="版本")
            self._create_version_tab()
        
        self.button_frame = tk.Frame(self.content_frame, bg=c.WINDOW_BG)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))
        
        self.btn_ok = XPButton(self.button_frame, "确定", command=self.ok, width=75)
        self.btn_ok.pack(side=tk.RIGHT, padx=5)
        
        self.btn_cancel = XPButton(self.button_frame, "取消", command=self.close, width=75)
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)
        
        self.btn_apply = XPButton(self.button_frame, "应用", command=self.apply, width=75, enabled=False)
        self.btn_apply.pack(side=tk.RIGHT, padx=5)
        
        self.activate()
    
    def _create_general_tab(self):
        """创建常规标签页"""
        top_frame = tk.Frame(self.general_frame, bg=c.WINDOW_BG)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        icon_text = self.file_info.get_icon() if self.file_info else "📄"
        icon_label = tk.Label(top_frame, text=icon_text, font=("Segoe UI", 40),
                            bg=c.WINDOW_BG)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        name_frame = tk.Frame(top_frame, bg=c.WINDOW_BG)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(name_frame, text="文件名:", font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(anchor=tk.W)
        self.name_entry = tk.Entry(name_frame, font=c.DEFAULT_FONT)
        self.name_entry.pack(fill=tk.X, pady=2)
        if self.file_info:
            self.name_entry.insert(0, self.file_info.name)
            self.name_entry.bind("<KeyRelease>", self.on_name_changed)
        
        sep = tk.Frame(self.general_frame, height=2, bg=c.BUTTON_SHADOW)
        sep.pack(fill=tk.X, padx=10, pady=5)
        
        info_frame = tk.Frame(self.general_frame, bg=c.WINDOW_BG)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if self.file_info:
            if self.file_info.is_dir:
                file_type = "文件夹"
                size_str = ""
                size_on_disk = ""
            else:
                ext = self.file_info.get_extension()
                if ext:
                    file_type = f"{ext[1:].upper()} 文件"
                else:
                    file_type = "文件"
                size_str = self.file_info.get_size_str()
                size_on_disk = size_str
            
            location = self.file_info.path
            
            created = self.file_info.created_time.strftime("%Y年%m月%d日 %H:%M:%S")
            modified = self.file_info.modified_time.strftime("%Y年%m月%d日 %H:%M:%S")
            accessed = self.file_info.accessed_time.strftime("%Y年%m月%d日 %H:%M:%S")
            
            info_items = [
                ("文件类型:", file_type),
                ("位置:", location),
            ]
            
            if not self.file_info.is_dir:
                info_items.append(("大小:", size_str))
                info_items.append(("占用空间:", size_on_disk))
            
            for i, (label, value) in enumerate(info_items):
                tk.Label(info_frame, text=label, font=c.DEFAULT_FONT, bg=c.WINDOW_BG,
                       width=10, anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=2)
                tk.Label(info_frame, text=value, font=c.DEFAULT_FONT, bg=c.WINDOW_BG,
                       anchor=tk.W, wraplength=250).grid(row=i, column=1, sticky=tk.W, pady=2)
            
            time_frame = tk.Frame(self.general_frame, bg=c.WINDOW_BG)
            time_frame.pack(fill=tk.X, padx=10, pady=10)
            
            time_items = [
                ("创建时间:", created),
                ("修改时间:", modified),
                ("访问时间:", accessed),
            ]
            
            for i, (label, value) in enumerate(time_items):
                tk.Label(time_frame, text=label, font=c.DEFAULT_FONT, bg=c.WINDOW_BG,
                       width=10, anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=2)
                tk.Label(time_frame, text=value, font=c.DEFAULT_FONT, bg=c.WINDOW_BG,
                       anchor=tk.W).grid(row=i, column=1, sticky=tk.W, pady=2)
            
            attr_frame = tk.LabelFrame(self.general_frame, text="属性", font=c.DEFAULT_FONT,
                                     bg=c.WINDOW_BG, padx=10, pady=5)
            attr_frame.pack(fill=tk.X, padx=10, pady=10)
            
            self.readonly_var = tk.BooleanVar(value=not os.access(self.file_info.path, os.W_OK) if os.path.exists(self.file_info.path) else False)
            self.hidden_var = tk.BooleanVar(value=os.path.basename(self.file_info.path).startswith("."))
            self.archive_var = tk.BooleanVar(value=True)
            
            tk.Checkbutton(attr_frame, text="只读(R)", variable=self.readonly_var,
                         font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(anchor=tk.W)
            tk.Checkbutton(attr_frame, text="隐藏(H)", variable=self.hidden_var,
                         font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(anchor=tk.W)
            tk.Checkbutton(attr_frame, text="存档(I)", variable=self.archive_var,
                         font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(anchor=tk.W)
    
    def on_name_changed(self, event=None):
        if self.file_info:
            new_name = self.name_entry.get().strip()
            if new_name != self.file_info.name:
                self.btn_apply.set_enabled(True)
            else:
                self.btn_apply.set_enabled(False)
    
    def _create_version_tab(self):
        tk.Label(self.version_frame, text="版本信息", font=c.DEFAULT_FONT,
               bg=c.WINDOW_BG).pack(padx=20, pady=20)
    
    def ok(self):
        self.apply()
        self.close()
    
    def apply(self):
        if self.file_info:
            new_name = self.name_entry.get().strip()
            if new_name and new_name != self.file_info.name:
                from filesystem import fs
                result = fs.rename_file(self.file_info.path, new_name)
                if result:
                    self.file_info = result
                    if hasattr(self.parent_app, 'refresh'):
                        self.parent_app.refresh()
                else:
                    show_error(self.parent_app, "重命名失败")
        self.btn_apply.set_enabled(False)
    
    def close(self):
        super().close()

class DisplayPropertiesDialog(XPWindow):
    """显示属性对话框"""
    def __init__(self, parent):
        super().__init__(parent, title="显示 属性", width=420, height=400)
        self.place(x=150, y=80)
        
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        theme_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
        self.notebook.add(theme_frame, text="主题")
        
        desktop_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
        self.notebook.add(desktop_frame, text="桌面")
        self._create_desktop_tab(desktop_frame)
        
        screensaver_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
        self.notebook.add(screensaver_frame, text="屏幕保护程序")
        
        appearance_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
        self.notebook.add(appearance_frame, text="外观")
        
        settings_frame = tk.Frame(self.notebook, bg=c.WINDOW_BG)
        self.notebook.add(settings_frame, text="设置")
        
        button_frame = tk.Frame(self.content_frame, bg=c.WINDOW_BG)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))
        
        XPButton(button_frame, "确定", command=self.ok, width=75).pack(side=tk.RIGHT, padx=5)
        XPButton(button_frame, "取消", command=self.close, width=75).pack(side=tk.RIGHT, padx=5)
        XPButton(button_frame, "应用", command=self.apply, width=75).pack(side=tk.RIGHT, padx=5)
        
        self.activate()
    
    def _create_desktop_tab(self, parent):
        preview_frame = tk.LabelFrame(parent, text="背景", font=c.DEFAULT_FONT,
                                    bg=c.WINDOW_BG, padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview = tk.Canvas(preview_frame, width=200, height=120, bg="#3A6EA5", bd=2, relief=tk.SUNKEN)
        self.preview.pack(pady=5)
        self._draw_bliss_preview()
        
        list_frame = tk.Frame(parent, bg=c.WINDOW_BG)
        list_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(list_frame, text="背景(K):", font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(anchor=tk.W)
        
        self.wallpaper_list = tk.Listbox(list_frame, font=c.DEFAULT_FONT, height=5)
        self.wallpaper_list.pack(fill=tk.X, pady=2)
        self.wallpaper_list.insert(tk.END, "Bliss")
        self.wallpaper_list.insert(tk.END, "Ascent")
        self.wallpaper_list.insert(tk.END, "Autumn")
        self.wallpaper_list.insert(tk.END, "Azul")
        self.wallpaper_list.insert(tk.END, "无")
        self.wallpaper_list.select_set(0)
    
    def _draw_bliss_preview(self):
        w, h = 200, 120
        for i in range(h//2):
            ratio = i / (h//2)
            r = int(100 + 135 * ratio)
            g = int(150 + 105 * ratio)
            b = int(220 + 35 * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.preview.create_line(0, i, w, i, fill=color)
        
        points = [0, h, 0, 70, 40, 55, 80, 65, 120, 50, 160, 60, 200, 45, 200, h]
        self.preview.create_polygon(points, fill="#4A8C3A", outline="")
        
        points2 = [0, h, 0, 80, 50, 70, 100, 85, 150, 75, 200, 80, 200, h]
        self.preview.create_polygon(points2, fill="#5AA04A", outline="")
    
    def ok(self):
        self.apply()
        self.close()
    
    def apply(self):
        pass
    
    def close(self):
        super().close()
