import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPMenuBar, XPButton, show_info

class Paint(XPWindow):
    """画图程序"""
    def __init__(self, parent):
        super().__init__(parent, title="未命名 - 画图", width=600, height=450)
        
        self.current_tool = "pencil"
        self.current_color = "#000000"
        self.line_width = 2
        self.drawing = False
        self.last_x = 0
        self.last_y = 0
        
        # 菜单栏
        self.menubar = XPMenuBar(self)
        self.menubar.pack(fill=tk.X, after=self.titlebar)
        
        self.menubar.add_menu("文件", [
            ("新建", self.new_canvas),
            ("打开...", None, False),
            ("保存", None, False),
            ("另存为...", None, False),
            ("separator", None),
            ("打印预览", None, False),
            ("页面设置", None, False),
            ("打印", None, False),
            ("separator", None),
            ("设为墙纸(居中)", None, False),
            ("设为墙纸(平铺)", None, False),
            ("separator", None),
            ("退出", self.close),
        ])
        
        self.menubar.add_menu("编辑", [
            ("撤销", None, False),
            ("重复", None, False),
            ("separator", None),
            ("剪切", None, False),
            ("复制", None, False),
            ("粘贴", None, False),
            ("清除选定内容", None, False),
            ("全选", None, False),
            ("separator", None),
            ("复制到", None, False),
            ("粘贴来源", None, False),
        ])
        
        self.menubar.add_menu("查看", [
            ("工具箱", self.toggle_tools),
            ("颜料盒", self.toggle_colors),
            ("状态栏", None, False),
            ("separator", None),
            ("缩放", None, False),
            ("查看位图", None, False),
        ])
        
        self.menubar.add_menu("图像", [
            ("翻转/旋转", None, False),
            ("拉伸/扭曲", None, False),
            ("反色", None, False),
            ("属性", None, False),
            ("清除图像", self.clear_canvas),
            ("不透明处理", None, False),
        ])
        
        self.menubar.add_menu("颜色", [
            ("编辑颜色", None, False),
        ])
        
        self.menubar.add_menu("帮助", [
            ("帮助主题", None, False),
            ("separator", None),
            ("关于画图", self.about),
        ])
        
        # 主布局
        self.main_frame = tk.Frame(self.content_frame, bg=c.WINDOW_BG)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧工具栏
        self.tools_frame = tk.Frame(self.main_frame, bg=c.BUTTON_FACE, width=55, bd=2, relief=tk.RAISED)
        self.tools_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.tools_frame.pack_propagate(False)
        
        tools = [
            ("✂️", "select", "选择"),
            ("⬜", "rect_select", "矩形选择"),
            ("🧹", "eraser", "橡皮"),
            ("🪣", "fill", "填充"),
            ("💧", "dropper", "取色"),
            ("🔍", "zoom", "放大镜"),
            ("✏️", "pencil", "铅笔"),
            ("🖌️", "brush", "刷子"),
            ("💨", "spray", "喷枪"),
            ("📝", "text", "文字"),
            ("➖", "line", "直线"),
            ("〰️", "curve", "曲线"),
            ("▭", "rect", "矩形"),
            ("🔲", "polygon", "多边形"),
            ("⭕", "ellipse", "椭圆"),
            ("🔳", "round_rect", "圆角矩形"),
        ]
        
        for i, (icon, tool, tooltip) in enumerate(tools):
            row = i // 2
            col = i % 2
            btn = tk.Canvas(self.tools_frame, width=22, height=22, bg=c.BUTTON_FACE, bd=1, relief=tk.RAISED)
            btn.create_text(11, 11, text=icon, font=("Segoe UI", 10))
            btn.grid(row=row, column=col, padx=2, pady=2)
            btn.bind("<Button-1>", lambda e, t=tool, b=btn: self.select_tool(t, b))
            if tool == "pencil":
                btn.config(relief=tk.SUNKEN)
                self.selected_tool_btn = btn
        
        # 线宽选择
        self.width_frame = tk.Frame(self.tools_frame, bg=c.BUTTON_FACE, bd=1, relief=tk.SUNKEN)
        self.width_frame.grid(row=8, column=0, columnspan=2, padx=2, pady=4, sticky="nsew")
        for i in range(1, 5):
            w = i * 2
            line_canvas = tk.Canvas(self.width_frame, height=15, bg=c.BUTTON_FACE, bd=0, highlightthickness=0)
            line_canvas.pack(fill=tk.X, padx=2, pady=2)
            line_canvas.create_line(5, 7, 45, 7, width=w, fill="#000000")
            line_canvas.bind("<Button-1>", lambda e, lw=w: self.set_line_width(lw))
        
        # 底部颜色面板
        self.colors_frame = tk.Frame(self.main_frame, bg=c.BUTTON_FACE, bd=2, relief=tk.RAISED, height=40)
        self.colors_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(2, 0))
        self.colors_frame.pack_propagate(False)
        
        # 当前颜色预览
        self.current_color_frame = tk.Frame(self.colors_frame, bg=c.BUTTON_FACE)
        self.current_color_frame.pack(side=tk.LEFT, padx=5, pady=3)
        
        self.color_preview = tk.Canvas(self.current_color_frame, width=30, height=30, 
                                      bg=c.BUTTON_FACE, bd=2, relief=tk.SUNKEN)
        self.color_preview.create_rectangle(3, 3, 27, 27, fill=self.current_color, outline="")
        self.color_preview.pack()
        
        # 调色板
        self.palette_frame = tk.Frame(self.colors_frame, bg=c.BUTTON_FACE)
        self.palette_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        colors = [
            "#000000", "#808080", "#800000", "#808000", "#008000", "#008080", "#000080", "#800080",
            "#FFFFFF", "#C0C0C0", "#FF0000", "#FFFF00", "#00FF00", "#00FFFF", "#0000FF", "#FF00FF",
            "#FFFFE0", "#A0A0A0", "#FFA0A0", "#FFFFA0", "#A0FFA0", "#A0FFFF", "#A0A0FF", "#FFA0FF",
        ]
        
        for i, color in enumerate(colors):
            row = i // 8
            col = i % 8
            color_btn = tk.Canvas(self.palette_frame, width=16, height=16, bg=color, bd=1, relief=tk.RAISED)
            color_btn.grid(row=row, column=col, padx=1, pady=1)
            color_btn.bind("<Button-1>", lambda e, c=color: self.set_color(c))
            color_btn.bind("<Double-1>", lambda e, c=color: self.set_color(c))
        
        # 画布区域
        self.canvas_frame = tk.Frame(self.main_frame, bg="#808080", bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#FFFFFF", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # 绑定画布事件
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<Button-3>", lambda e: self.set_color_bg(e))
        
        # 放置窗口
        self.place(x=150, y=50, width=self.width, height=self.height)
        self.activate()
    
    def select_tool(self, tool, btn):
        self.current_tool = tool
        if hasattr(self, 'selected_tool_btn'):
            self.selected_tool_btn.config(relief=tk.RAISED)
        btn.config(relief=tk.SUNKEN)
        self.selected_tool_btn = btn
    
    def set_line_width(self, width):
        self.line_width = width
    
    def set_color(self, color):
        self.current_color = color
        self.color_preview.delete("all")
        self.color_preview.create_rectangle(3, 3, 27, 27, fill=color, outline="")
    
    def set_color_bg(self, event):
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        items = self.canvas.find_closest(x, y)
        if items:
            try:
                color = self.canvas.itemcget(items[0], "fill")
                if color and color != "":
                    self.set_color(color)
            except:
                pass
    
    def start_draw(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        
        if self.current_tool in ["pencil", "brush", "spray"]:
            self.canvas.create_oval(event.x - self.line_width/2, event.y - self.line_width/2,
                                   event.x + self.line_width/2, event.y + self.line_width/2,
                                   fill=self.current_color, outline=self.current_color)
    
    def draw(self, event):
        if not self.drawing:
            return
        
        x, y = event.x, event.y
        
        if self.current_tool == "pencil":
            self.canvas.create_line(self.last_x, self.last_y, x, y, 
                                   fill=self.current_color, width=self.line_width,
                                   capstyle=tk.ROUND, smooth=True)
        elif self.current_tool == "brush":
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                   fill=self.current_color, width=self.line_width * 2,
                                   capstyle=tk.ROUND, smooth=True)
        elif self.current_tool == "eraser":
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                   fill="#FFFFFF", width=self.line_width * 4,
                                   capstyle=tk.ROUND, smooth=True)
        elif self.current_tool == "spray":
            import random
            for _ in range(10):
                sx = x + random.randint(-self.line_width*3, self.line_width*3)
                sy = y + random.randint(-self.line_width*3, self.line_width*3)
                self.canvas.create_oval(sx-1, sy-1, sx+1, sy+1, fill=self.current_color, outline="")
        
        self.last_x = x
        self.last_y = y
    
    def stop_draw(self, event):
        self.drawing = False
    
    def new_canvas(self):
        self.canvas.delete("all")
    
    def clear_canvas(self):
        self.canvas.delete("all")
    
    def toggle_tools(self):
        if self.tools_frame.winfo_viewable():
            self.tools_frame.pack_forget()
        else:
            self.tools_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2), before=self.canvas_frame)
    
    def toggle_colors(self):
        if self.colors_frame.winfo_viewable():
            self.colors_frame.pack_forget()
        else:
            self.colors_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(2, 0))
    
    def about(self):
        show_info(self, "Microsoft Windows XP\n画图\n\nPython 模拟版本", title="关于画图")
