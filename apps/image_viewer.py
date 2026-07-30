import tkinter as tk
from tkinter import filedialog
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPButton, show_info, show_error

class ImageViewer(XPWindow):
    """Windows 图片和传真查看器"""
    def __init__(self, parent, image_path=None):
        super().__init__(parent, title="Windows 图片和传真查看器", width=600, height=500)
        self.current_image = None
        self.photo = None
        self.image_path = image_path
        
        # 工具栏
        self.toolbar = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=30)
        self.toolbar.pack(fill=tk.X, side=tk.TOP)
        self.toolbar.pack_propagate(False)
        
        self.btn_open = XPButton(self.toolbar, "打开", command=self.open_image, width=60)
        self.btn_open.pack(side=tk.LEFT, padx=5, pady=3)
        
        # 图片显示区域
        self.canvas_frame = tk.Frame(self.content_frame, bg="#000000")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#000000", bd=0, highlightthickness=0)
        self.scroll_y = tk.Scrollbar(self.canvas_frame, command=self.canvas.yview)
        self.scroll_x = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, 
                                    command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.statusbar = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=20)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(self.statusbar, text="", font=c.DEFAULT_FONT,
                                    bg=c.BUTTON_FACE, fg=c.TEXT_COLOR, anchor="w", padx=5)
        self.status_label.pack(fill=tk.X)
        
        # 打开初始图片
        if image_path and os.path.exists(image_path):
            self.load_image(image_path)
        
        # 放置窗口
        self.place(x=150, y=80, width=self.width, height=self.height)
        self.activate()
    
    def load_image(self, path):
        """加载图片"""
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == '.bmp':
                # BMP格式简单提示，因为tkinter原生支持有限
                show_info(self, "BMP格式暂不支持预览", title="提示")
                return False
            
            # 加载图片
            self.photo = tk.PhotoImage(file=path)
            self.current_image = path
            
            # 简单适应窗口：如果图片太大，用subsample缩小
            img_w = self.photo.width()
            img_h = self.photo.height()
            canvas_w = self.canvas.winfo_width() or 500
            canvas_h = self.canvas.winfo_height() or 400
            
            # 计算缩放比例
            scale = 1
            if img_w > canvas_w or img_h > canvas_h:
                scale_w = img_w / canvas_w
                scale_h = img_h / canvas_h
                scale = max(scale_w, scale_h)
                if scale > 1:
                    scale = int(scale) + 1
                    if scale > 20:
                        scale = 20
                    self.photo = self.photo.subsample(scale, scale)
            
            # 居中显示
            self.canvas.delete("all")
            self.canvas.update_idletasks()
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            img_w = self.photo.width()
            img_h = self.photo.height()
            
            x = max(0, (canvas_w - img_w) // 2)
            y = max(0, (canvas_h - img_h) // 2)
            
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=(0, 0, img_w, img_h))
            
            # 更新标题和状态栏
            self.title_label.config(text=f"{os.path.basename(path)} - Windows 图片和传真查看器")
            self.title = f"{os.path.basename(path)} - Windows 图片和传真查看器"
            self.status_label.config(text=f"{os.path.basename(path)}    {img_w} x {img_h} 像素")
            
            return True
        except Exception as e:
            show_error(self, f"无法加载图片: {e}", title="错误")
            return False
    
    def open_image(self):
        """打开图片文件"""
        file_path = filedialog.askopenfilename(
            title="打开",
            filetypes=[
                ("图片文件", "*.png *.gif *.pgm *.ppm"),
                ("PNG图片", "*.png"),
                ("GIF图片", "*.gif"),
                ("所有文件", "*.*")
            ],
            initialdir=os.path.expanduser("~")
        )
        if file_path:
            self.load_image(file_path)
