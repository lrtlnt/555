#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows XP 模拟器 - Python Tkinter 实现
1:1 还原经典XP界面，支持文件操作和网页浏览
"""
import tkinter as tk
from tkinter import simpledialog
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import constants as c
from desktop import Desktop
from taskbar import Taskbar
from filesystem import fs, FileInfo
from widgets import show_error, show_info
from apps import Notepad, Calculator, Paint, MyComputer, RunDialog, AboutWindows, InternetExplorer, ImageViewer, GenericProgram

class WindowsXP(tk.Tk):
    """Windows XP 主窗口"""
    def __init__(self):
        super().__init__()
        
        # 窗口设置 - 跨平台兼容最大化
        self.title("Windows XP")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        if os.name == "nt":
            try:
                self.state('zoomed')  # Windows下最大化
            except:
                pass
        self.configure(bg=c.DESKTOP_BG)
        self.minsize(800, 600)
        
        # 窗口管理
        self.windows = []
        self.active_window = None
        self.app_instances = {}
        self.external_counter = 0
        
        # 创建桌面
        self.desktop = Desktop(self, app_manager=self)
        
        # 创建任务栏
        self.taskbar = Taskbar(self, app_manager=self)
        
        # 绑定全局事件
        self.bind("<Control-Escape>", lambda e: self.taskbar.toggle_start_menu())
        self.bind("<Alt-F4>", self.alt_f4)
        
        # 关闭确认
        self.protocol("WM_DELETE_WINDOW", self.shutdown)
        
        # 添加右键新建文件功能
        self._add_new_file_menu()
    
    def _add_new_file_menu(self):
        """添加桌面右键新建菜单功能"""
        # 这个方法在桌面右键菜单中实现
        pass
    
    def close_all_menus(self):
        """关闭所有打开的菜单"""
        for child in self.winfo_children():
            if hasattr(child, 'hide_context_menu'):
                child.hide_context_menu()
    
    def open_app(self, app_name, **kwargs):
        """打开内置应用程序"""
        # 关闭开始菜单
        if self.taskbar.start_menu and self.taskbar.start_menu.visible:
            self.taskbar.start_menu.hide()
        
        # IE浏览器每次打开新窗口
        if app_name == "ie":
            window = InternetExplorer(self)
            self.windows.append(window)
            self.taskbar.add_window_button(window)
            self.set_active_window(window)
            return window
        
        # 检查是否已打开（单实例应用）
        single_instance_apps = ["calculator", "my_computer", "run", "about"]
        if app_name in single_instance_apps:
            if app_name in self.app_instances and self.app_instances[app_name].winfo_exists():
                window = self.app_instances[app_name]
                window.lift()
                window.activate()
                if hasattr(window, 'minimized') and window.minimized:
                    window.minimized = False
                    window.place(x=window.winfo_x(), y=window.winfo_y())
                return window
        
        # 创建新窗口
        if app_name == "notepad":
            window = Notepad(self, **kwargs)
        elif app_name == "calculator":
            window = Calculator(self)
        elif app_name == "paint":
            window = Paint(self)
        elif app_name == "my_computer":
            window = MyComputer(self, **kwargs)
        elif app_name == "run":
            window = RunDialog(self, app_manager=self)
        elif app_name == "about":
            window = AboutWindows(self)
        elif app_name == "image_viewer":
            window = ImageViewer(self, **kwargs)
        elif app_name == "generic_program":
            window = GenericProgram(self, **kwargs)
        else:
            window = Notepad(self, text=f"未知应用: {app_name}")
        
        self.windows.append(window)
        self.app_instances[app_name] = window
        
        # 添加任务栏按钮
        self.taskbar.add_window_button(window)
        
        # 激活窗口
        self.set_active_window(window)
        
        return window
    
    def open_file(self, file_path):
        """打开文件 - 统一在XP内部处理"""
        if not os.path.exists(file_path):
            show_error(self, f"找不到文件: {file_path}")
            return
        
        file_info = FileInfo(file_path)
        
        if file_info.is_dir:
            # 文件夹用资源管理器打开
            self.open_app("my_computer", path=file_info.path)
            return
        
        ext = file_info.get_extension()
        
        # 文本类文件 - 用记事本打开
        text_exts = ['.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js', 
                    '.csv', '.log', '.ini', '.conf', '.cfg', '.java', '.c', '.cpp', 
                    '.h', '.hpp', '.sh', '.yaml', '.yml', '.toml', '.bat', '.cmd']
        if ext in text_exts:
            self.open_app("notepad", file_path=file_info.path)
            return
        
        # 图片类文件 - 用图片查看器打开
        image_exts = ['.png', '.gif', '.pgm', '.ppm', '.bmp']
        if ext in image_exts:
            self.open_app("image_viewer", image_path=file_info.path)
            return
        
        # 可执行文件 - 打开通用程序容器
        exe_exts = ['.exe', '.msi', '.bat', '.cmd', '.sh', '.com', '.scr']
        if ext in exe_exts:
            program_name = os.path.basename(file_path)
            self.open_app("generic_program", program_name=program_name, program_path=file_path)
            return
        
        # 其他不支持的文件类型
        show_info(self, "Windows 无法打开此文件。该文件类型不受支持，或需要相应的程序才能打开。")
    
    def create_new_text_file(self):
        """在桌面新建文本文档"""
        name = simpledialog.askstring("新建", "输入文件名:", initialvalue="新建文本文档.txt")
        if name:
            fs.create_file(fs.get_desktop(), name, "")
            self.desktop.refresh_user_files()
    
    def create_new_folder(self):
        """在桌面新建文件夹"""
        name = simpledialog.askstring("新建文件夹", "输入文件夹名:", initialvalue="新建文件夹")
        if name:
            fs.create_folder(fs.get_desktop(), name)
            self.desktop.refresh_user_files()
    
    def set_active_window(self, window):
        """设置活动窗口"""
        self.active_window = window
        for w in self.windows:
            if w.winfo_exists():
                w.set_active(w == window)
        self.taskbar.set_active_window(window)
    
    def deactivate_other_windows(self, window):
        """停用其他窗口"""
        for w in self.windows:
            if w != window and w.winfo_exists():
                w.set_active(False)
        self.taskbar.deactivate_buttons(except_window=window)
        self.active_window = window
    
    def on_window_minimize(self, window):
        """窗口最小化"""
        if window in self.taskbar.window_buttons:
            self.taskbar.window_buttons[window].set_active(False)
    
    def on_window_close(self, window):
        """窗口关闭"""
        if window in self.windows:
            self.windows.remove(window)
        self.taskbar.remove_window_button(window)
        
        for app_name, instance in list(self.app_instances.items()):
            if instance == window:
                del self.app_instances[app_name]
                break
    
    def alt_f4(self, event=None):
        """Alt+F4 关闭活动窗口"""
        if self.active_window and self.active_window.winfo_exists():
            self.active_window.close()
    
    def shutdown(self):
        """关机"""
        show_info(self, "正在关闭Windows...\n(模拟)")
        self.destroy()

def main():
    """主函数"""
    app = WindowsXP()
    
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f'{width}x{height}+{x}+{y}')
    
    app.mainloop()

if __name__ == "__main__":
    main()
