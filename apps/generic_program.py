#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用EXE程序容器
模拟Windows程序在XP内运行的窗口
"""
import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPButton

class GenericProgram(XPWindow):
    """通用程序容器窗口"""
    def __init__(self, parent, program_name="程序", program_path=None):
        # 标题显示程序名
        title = f"{program_name}"
        super().__init__(parent, title=title, width=600, height=450)
        self.program_name = program_name
        self.program_path = program_path
        
        # 菜单栏（简单模拟）
        from widgets import XPMenuBar
        self.menubar = XPMenuBar(self)
        self.menubar.pack(fill=tk.X, after=self.titlebar)
        
        self.menubar.add_menu("文件", [
            ("新建", None, False),
            ("打开...", None, False),
            ("保存", None, False),
            ("另存为...", None, False),
            ("separator", None),
            ("退出", self.close),
        ])
        
        self.menubar.add_menu("编辑", [
            ("撤销", None, False),
            ("separator", None),
            ("剪切", None, False),
            ("复制", None, False),
            ("粘贴", None, False),
            ("全选", None, False),
        ])
        
        self.menubar.add_menu("帮助", [
            ("关于", self.about),
        ])
        
        # 工具栏（简单模拟）
        toolbar = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=30, bd=1, relief=tk.RAISED)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)
        
        # 简单工具栏按钮
        for icon in ["📄", "📂", "💾", "✂️", "📋", "📝"]:
            btn = tk.Label(toolbar, text=icon, font=("Segoe UI", 12), bg=c.BUTTON_FACE, padx=6, pady=3)
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5F0FC", relief=tk.RAISED, bd=1))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.BUTTON_FACE, relief=tk.FLAT, bd=0))
        
        # 客户区 - 空白编辑区域，模拟程序界面
        client_frame = tk.Frame(self.content_frame, bd=2, relief=tk.SUNKEN, bg="#FFFFFF")
        client_frame.pack(fill=tk.BOTH, expand=True)
        
        # 简单的文本区域，模拟程序内容
        self.text_area = tk.Text(client_frame, font=("Fixedsys", 10), wrap=tk.WORD,
                                bd=0, bg="#FFFFFF", padx=5, pady=5)
        scroll_y = tk.Scrollbar(client_frame, command=self.text_area.yview)
        self.text_area.config(yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 状态栏
        statusbar = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=20, bd=1, relief=tk.SUNKEN)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        statusbar.pack_propagate(False)
        
        status_label = tk.Label(statusbar, text=f"就绪", font=c.DEFAULT_FONT,
                               bg=c.BUTTON_FACE, anchor="w", padx=5)
        status_label.pack(fill=tk.X)
        
        # 初始显示提示
        self.text_area.insert("1.0", f"{program_name} 已在Windows XP模拟环境中启动。\n\n")
        self.text_area.insert(tk.END, "这是一个模拟的程序窗口，所有操作都在XP模拟器内部完成。\n")
        self.text_area.insert(tk.END, "您可以拖动标题栏移动窗口，点击最小化/最大化/关闭按钮。\n")
        self.text_area.config(state=tk.DISABLED)
        
        # 放置窗口，随机一点位置避免重叠
        import random
        x = random.randint(80, 200)
        y = random.randint(50, 120)
        self.place(x=x, y=y, width=self.width, height=self.height)
        self.activate()
    
    def about(self):
        from widgets import show_info
        show_info(self, f"{self.program_name}\n\nWindows XP 模拟版本\n\n此程序在模拟环境中运行", title=f"关于 {self.program_name}")
