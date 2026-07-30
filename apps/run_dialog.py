import tkinter as tk
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPMenuBar, XPButton, show_error

class RunDialog(XPWindow):
    """运行对话框"""
    def __init__(self, parent, app_manager=None):
        super().__init__(parent, title="运行", width=380, height=170)
        self.app_manager = app_manager
        
        # 内容区域
        content = self.content_frame
        
        # 图标和说明
        top_frame = tk.Frame(content, bg=c.WINDOW_BG)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        icon_label = tk.Label(top_frame, text="▶️", font=("Segoe UI", 32), bg=c.WINDOW_BG)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        desc_label = tk.Label(top_frame, text="请输入程序、文件夹、文档或 Internet 资源的名称，\nWindows 将为您打开它。",
                             font=c.DEFAULT_FONT, bg=c.WINDOW_BG, justify=tk.LEFT, anchor="w")
        desc_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 输入区域
        input_frame = tk.Frame(content, bg=c.WINDOW_BG)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        open_label = tk.Label(input_frame, text="打开(O):", font=c.DEFAULT_FONT, bg=c.WINDOW_BG)
        open_label.pack(side=tk.LEFT)
        
        self.cmd_entry = tk.Entry(input_frame, font=c.DEFAULT_FONT, bd=2, relief=tk.SUNKEN)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cmd_entry.focus_set()
        
        browse_btn = XPButton(input_frame, text="浏览(B)...", width=70, command=self.browse)
        browse_btn.pack(side=tk.LEFT)
        
        # 按钮区域
        btn_frame = tk.Frame(content, bg=c.WINDOW_BG)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        ok_btn = XPButton(btn_frame, text="确定", width=75, command=self.run_command)
        ok_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = XPButton(btn_frame, text="取消", width=75, command=self.close)
        cancel_btn.pack(side=tk.RIGHT)
        
        # 放置窗口
        self.place(x=250, y=200, width=self.width, height=self.height)
        self.activate()
        
        # 绑定回车
        self.cmd_entry.bind("<Return>", lambda e: self.run_command())
    
    def browse(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="浏览",
            filetypes=[("程序", "*.exe *.com *.bat *.cmd"), ("所有文件", "*.*")]
        )
        if file_path:
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, file_path)
    
    def run_command(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        
        # 仅允许内置命令
        builtin_cmds = {
            "notepad": lambda: self.app_manager.open_app("notepad"),
            "notepad.exe": lambda: self.app_manager.open_app("notepad"),
            "calc": lambda: self.app_manager.open_app("calculator"),
            "calc.exe": lambda: self.app_manager.open_app("calculator"),
            "mspaint": lambda: self.app_manager.open_app("paint"),
            "mspaint.exe": lambda: self.app_manager.open_app("paint"),
            "iexplore": lambda: self.app_manager.open_app("ie"),
            "iexplore.exe": lambda: self.app_manager.open_app("ie"),
            "explorer": lambda: self.app_manager.open_app("my_computer"),
            "explorer.exe": lambda: self.app_manager.open_app("my_computer"),
            "winver": lambda: self.app_manager.open_app("about"),
        }
        
        cmd_lower = cmd.lower()
        if cmd_lower in builtin_cmds:
            builtin_cmds[cmd_lower]()
            self.close()
            return
        
        # 其他所有命令/程序都弹出错误提示
        show_error(self.app_manager, "Windows 无法在模拟环境中运行此外部程序。")
