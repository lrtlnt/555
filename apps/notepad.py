import tkinter as tk
from tkinter import filedialog, simpledialog
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPMenuBar, XPButton, show_error, show_info, XPMessageBox
from filesystem import fs

class Notepad(XPWindow):
    """记事本应用"""
    def __init__(self, parent, text="", file_path=None, file_item=None):
        super().__init__(parent, title="无标题 - 记事本", width=500, height=400)
        self.current_file = file_path
        self.file_item = file_item
        self.modified = False
        
        self.menubar = XPMenuBar(self)
        self.menubar.pack(fill=tk.X, after=self.titlebar)
        
        self.menubar.add_menu("文件", [
            ("新建", self.new_file),
            ("打开...", self.open_file),
            ("保存", self.save_file),
            ("另存为...", self.save_as),
            ("separator", None),
            ("页面设置...", None, False),
            ("打印...", None, False),
            ("separator", None),
            ("退出", self.close),
        ])
        
        self.menubar.add_menu("编辑", [
            ("撤销", None, False),
            ("separator", None),
            ("剪切", self.cut),
            ("复制", self.copy),
            ("粘贴", self.paste),
            ("删除", self.delete),
            ("separator", None),
            ("查找...", None, False),
            ("查找下一个", None, False),
            ("替换...", None, False),
            ("转到...", None, False),
            ("separator", None),
            ("全选", self.select_all),
            ("时间/日期", self.insert_datetime),
        ])
        
        self.menubar.add_menu("格式", [
            ("自动换行", self.toggle_word_wrap),
            ("字体...", None, False),
        ])
        
        self.menubar.add_menu("查看", [
            ("状态栏", None, False),
        ])
        
        self.menubar.add_menu("帮助", [
            ("帮助主题", None, False),
            ("separator", None),
            ("关于记事本", self.about),
        ])
        
        self.text_frame = tk.Frame(self.content_frame, bd=2, relief=tk.SUNKEN, bg="#FFFFFF")
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = tk.Text(self.text_frame, font=("Fixedsys", 10), wrap=tk.NONE,
                                bd=0, undo=True, bg="#FFFFFF")
        self.scroll_y = tk.Scrollbar(self.text_frame, command=self.text_area.yview)
        self.scroll_x = tk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL, 
                                    command=self.text_area.xview)
        self.text_area.config(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if file_path and os.path.exists(file_path):
            try:
                content = fs.read_file(file_path)
                self.text_area.insert("1.0", content)
                self.current_file = file_path
                self.update_title()
            except:
                if text:
                    self.text_area.insert("1.0", text)
        elif text:
            self.text_area.insert("1.0", text)
        
        self.text_area.bind("<<Modified>>", self.on_modified)
        self.text_area.bind("<Button-1>", self.activate)
        
        self.place(x=100, y=80, width=self.width, height=self.height)
        self.activate()
    
    def on_modified(self, event=None):
        if self.text_area.edit_modified():
            self.modified = True
            title = self.title
            if not title.startswith("*"):
                self.title_label.config(text="*" + title)
        self.text_area.edit_modified(False)
    
    def update_title(self):
        if self.current_file:
            title = os.path.basename(self.current_file) + " - 记事本"
        else:
            title = "无标题 - 记事本"
        if self.modified:
            title = "*" + title
        self.title_label.config(text=title)
        self.title = title.lstrip("*")
    
    def ask_save_changes(self):
        """询问是否保存更改，返回True(是)/False(否)/None(取消)"""
        result = None
        dialog = [None]
        
        def on_yes():
            nonlocal result
            result = True
            dialog[0].close()
        
        def on_no():
            nonlocal result
            result = False
            dialog[0].close()
        
        def on_cancel():
            nonlocal result
            result = None
            dialog[0].close()
        
        dialog[0] = XPMessageBox(
            self, "记事本", "是否保存更改？",
            icon="question",
            buttons=[
                ("是", on_yes),
                ("否", on_no),
                ("取消", on_cancel)
            ]
        )
        # 等待对话框关闭
        self.wait_window(dialog[0])
        return result
    
    def new_file(self):
        if self.modified:
            result = self.ask_save_changes()
            if result is None:
                return
            if result:
                self.save_file()
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.file_item = None
        self.modified = False
        self.update_title()
    
    def open_file(self):
        if self.modified:
            result = self.ask_save_changes()
            if result is None:
                return
            if result:
                self.save_file()
        
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("文本文档", "*.txt"), ("所有文件", "*.*")],
            initialdir=fs.get_desktop()
        )
        if file_path:
            try:
                content = fs.read_file(file_path)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.current_file = file_path
                self.file_item = None
                self.modified = False
                self.update_title()
            except Exception as e:
                show_error(self, f"无法打开文件: {e}", title="记事本")
    
    def save_file(self):
        content = self.text_area.get("1.0", tk.END).rstrip('\n')
        
        if self.current_file:
            try:
                fs.write_file(self.current_file, content)
                self.modified = False
                self.update_title()
                return True
            except Exception as e:
                show_error(self, f"无法保存文件: {e}", title="记事本")
                return False
        else:
            return self.save_as()
    
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文档", "*.txt"), ("所有文件", "*.*")],
            initialdir=fs.get_desktop(),
            initialfile="新建文本文档.txt"
        )
        if file_path:
            content = self.text_area.get("1.0", tk.END).rstrip('\n')
            try:
                fs.write_file(file_path, content)
                self.current_file = file_path
                self.modified = False
                self.update_title()
                if hasattr(self.app_manager, 'desktop'):
                    self.app_manager.desktop.refresh_user_files()
                return True
            except Exception as e:
                show_error(self, f"无法保存文件: {e}", title="记事本")
                return False
        return False
    
    def cut(self):
        self.text_area.event_generate("<<Cut>>")
    
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
    
    def paste(self):
        self.text_area.event_generate("<<Paste>>")
    
    def delete(self):
        try:
            self.text_area.delete("sel.first", "sel.last")
        except:
            pass
    
    def select_all(self):
        self.text_area.tag_add("sel", "1.0", tk.END)
    
    def insert_datetime(self):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M %Y-%m-%d")
        self.text_area.insert(tk.INSERT, now)
    
    def toggle_word_wrap(self):
        if self.text_area.cget("wrap") == tk.NONE:
            self.text_area.config(wrap=tk.WORD)
            self.scroll_x.pack_forget()
        else:
            self.text_area.config(wrap=tk.NONE)
            self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    def about(self):
        show_info(self, "Microsoft Windows XP\n记事本\n\nPython 模拟版本", title="关于记事本")
