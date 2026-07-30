import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPButton, show_info

class Calculator(XPWindow):
    """计算器应用"""
    def __init__(self, parent):
        super().__init__(parent, title="计算器", width=240, height=300)
        
        self.current = "0"
        self.previous = ""
        self.operator = ""
        self.reset_next = False
        
        # 菜单栏
        from widgets import XPMenuBar
        self.menubar = XPMenuBar(self)
        self.menubar.pack(fill=tk.X, after=self.titlebar)
        
        self.menubar.add_menu("查看", [
            ("标准型", lambda: None),
            ("科学型", None, False),
            ("separator", None),
            ("数字分组", None, False),
        ])
        
        self.menubar.add_menu("编辑", [
            ("复制", self.copy),
            ("粘贴", self.paste),
        ])
        
        self.menubar.add_menu("帮助", [
            ("帮助主题", None, False),
            ("separator", None),
            ("关于计算器", self.about),
        ])
        
        # 显示区域
        display_frame = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, bd=2, relief=tk.SUNKEN)
        display_frame.pack(fill=tk.X, padx=6, pady=6)
        
        self.display = tk.Entry(display_frame, font=("Tahoma", 14), justify=tk.RIGHT,
                               bd=0, bg="#C0FFC0", fg="#000000", readonlybackground="#C0FFC0")
        self.display.insert(0, "0")
        self.display.config(state="readonly")
        self.display.pack(fill=tk.X, ipady=4, padx=4, pady=4)
        
        # 按钮区域
        btn_frame = tk.Frame(self.content_frame, bg=c.BUTTON_FACE)
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        
        # 按钮布局
        buttons = [
            [("Backspace", self.backspace, 2), ("CE", self.ce, 1), ("C", self.clear, 1)],
            [("7", lambda: self.press_digit("7"), 1), ("8", lambda: self.press_digit("8"), 1), 
             ("9", lambda: self.press_digit("9"), 1), ("/", lambda: self.press_op("/"), 1), ("sqrt", self.sqrt, 1)],
            [("4", lambda: self.press_digit("4"), 1), ("5", lambda: self.press_digit("5"), 1), 
             ("6", lambda: self.press_digit("6"), 1), ("*", lambda: self.press_op("*"), 1), ("%", self.percent, 1)],
            [("1", lambda: self.press_digit("1"), 1), ("2", lambda: self.press_digit("2"), 1), 
             ("3", lambda: self.press_digit("3"), 1), ("-", lambda: self.press_op("-"), 1), ("1/x", self.reciprocal, 1)],
            [("0", lambda: self.press_digit("0"), 2), ("+/-", self.negate, 1), 
             (".", lambda: self.press_digit("."), 1), ("+", lambda: self.press_op("+"), 1), ("=", self.calculate, 1)],
        ]
        
        for row_idx, row in enumerate(buttons):
            col = 0
            for btn_text, cmd, colspan in row:
                width = 42 * colspan + 6 * (colspan - 1)
                btn = XPButton(btn_frame, text=btn_text, command=cmd, width=width, height=26)
                btn.grid(row=row_idx, column=col, columnspan=colspan, padx=2, pady=2, sticky="nsew")
                col += colspan
        
        # 配置网格权重
        for i in range(5):
            btn_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            btn_frame.grid_rowconfigure(i, weight=1)
        
        # 放置窗口
        self.place(x=350, y=100, width=self.width, height=self.height)
        self.activate()
    
    def update_display(self):
        self.display.config(state="normal")
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current)
        self.display.config(state="readonly")
    
    def press_digit(self, digit):
        if self.reset_next:
            self.current = "0"
            self.reset_next = False
        
        if digit == ".":
            if "." not in self.current:
                self.current += "."
        elif self.current == "0":
            self.current = digit
        else:
            self.current += digit
        
        self.update_display()
    
    def press_op(self, op):
        if self.operator and not self.reset_next:
            self.calculate()
        self.previous = self.current
        self.operator = op
        self.reset_next = True
    
    def calculate(self):
        if not self.operator or not self.previous:
            return
        
        try:
            a = float(self.previous)
            b = float(self.current)
            
            if self.operator == "+":
                result = a + b
            elif self.operator == "-":
                result = a - b
            elif self.operator == "*":
                result = a * b
            elif self.operator == "/":
                if b == 0:
                    result = "除数不能为零"
                else:
                    result = a / b
            
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            self.current = str(result)
        except:
            self.current = "错误"
        
        self.operator = ""
        self.previous = ""
        self.reset_next = True
        self.update_display()
    
    def clear(self):
        self.current = "0"
        self.previous = ""
        self.operator = ""
        self.reset_next = False
        self.update_display()
    
    def ce(self):
        self.current = "0"
        self.reset_next = False
        self.update_display()
    
    def backspace(self):
        if len(self.current) > 1:
            self.current = self.current[:-1]
        else:
            self.current = "0"
        self.update_display()
    
    def negate(self):
        if self.current != "0":
            if self.current.startswith("-"):
                self.current = self.current[1:]
            else:
                self.current = "-" + self.current
        self.update_display()
    
    def sqrt(self):
        try:
            val = float(self.current)
            result = val ** 0.5
            if result.is_integer():
                result = int(result)
            self.current = str(result)
            self.reset_next = True
            self.update_display()
        except:
            self.current = "错误"
            self.update_display()
    
    def percent(self):
        try:
            val = float(self.current)
            result = val / 100
            self.current = str(result)
            self.update_display()
        except:
            pass
    
    def reciprocal(self):
        try:
            val = float(self.current)
            if val == 0:
                self.current = "除数不能为零"
            else:
                result = 1 / val
                self.current = str(result)
            self.reset_next = True
            self.update_display()
        except:
            self.current = "错误"
            self.update_display()
    
    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.current)
    
    def paste(self):
        try:
            text = self.clipboard_get()
            if text.replace(".", "").replace("-", "").isdigit():
                self.current = text
                self.update_display()
        except:
            pass
    
    def about(self):
        show_info(self, "Microsoft Windows XP\n计算器\n\nPython 模拟版本", title="关于计算器")
