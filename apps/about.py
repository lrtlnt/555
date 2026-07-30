import tkinter as tk
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPButton

class AboutWindows(XPWindow):
    """关于Windows对话框"""
    def __init__(self, parent):
        super().__init__(parent, title="关于 Windows", width=400, height=350)
        
        content = self.content_frame
        
        # Windows XP Logo区域
        logo_frame = tk.Frame(content, bg=c.WINDOW_BG)
        logo_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 大logo文字
        logo_text = tk.Label(logo_frame, text="Windows", font=("Tahoma", 28, "bold"),
                            bg=c.WINDOW_BG, fg="#000000")
        logo_text.pack()
        
        xp_text = tk.Label(logo_frame, text="xp", font=("Tahoma", 36, "bold"),
                          bg=c.WINDOW_BG, fg="#E07010")
        xp_text.pack()
        
        edition_label = tk.Label(logo_frame, text="Professional", font=("Tahoma", 10),
                                bg=c.WINDOW_BG, fg="#000000")
        edition_label.pack()
        
        # 分隔线
        sep = tk.Frame(content, height=2, bg=c.BUTTON_SHADOW)
        sep.pack(fill=tk.X, padx=15, pady=5)
        
        # 版权信息
        info_frame = tk.Frame(content, bg=c.WINDOW_BG)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        version_label = tk.Label(info_frame, 
                                text="Microsoft® Windows®\n版本 5.1 (内部版本 2600.xpsp_sp3)\n\n本产品根据许可协议条款授予许可给:\n\nAdministrator\nPython 模拟用户",
                                font=c.DEFAULT_FONT, bg=c.WINDOW_BG, justify=tk.LEFT, anchor="w")
        version_label.pack(fill=tk.X)
        
        # 分隔线
        sep2 = tk.Frame(content, height=2, bg=c.BUTTON_SHADOW)
        sep2.pack(fill=tk.X, padx=15, pady=5)
        
        # 内存信息
        try:
            import psutil
            mem = psutil.virtual_memory()
            mem_mb = mem.total // (1024 * 1024)
            mem_text = f"计算机:\nIntel(R) Pentium(R) 4 CPU 2.40GHz\n{mem_mb} MB 的内存"
        except:
            mem_text = "计算机:\nIntel(R) Pentium(R) 4 CPU 2.40GHz\n512 MB 的内存"
        
        mem_label = tk.Label(info_frame, text=mem_text, font=c.DEFAULT_FONT,
                            bg=c.WINDOW_BG, justify=tk.LEFT, anchor="w")
        mem_label.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮区域
        btn_frame = tk.Frame(content, bg=c.WINDOW_BG)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=15)
        
        ok_btn = XPButton(btn_frame, text="确定", width=75, command=self.close)
        ok_btn.pack(side=tk.RIGHT)
        
        # 放置窗口
        self.place(x=300, y=150, width=self.width, height=self.height)
        self.activate()
