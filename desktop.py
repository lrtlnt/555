#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows XP 桌面
实现Bliss壁纸、可拖拽图标、完整右键菜单
"""
import tkinter as tk
from tkinter import simpledialog
import constants as c
import math
import os
from xpmenu import XPContextMenu
from filesystem import fs, clipboard, FileInfo
from properties import PropertiesDialog, DisplayPropertiesDialog
from widgets import show_error, show_info, show_warning, bind_long_press

class DesktopIcon(tk.Frame):
    """可拖拽的桌面图标"""
    def __init__(self, parent, text, icon_text, command, file_path=None, x=0, y=0):
        super().__init__(parent, bg=c.DESKTOP_BG, bd=0, padx=4, pady=4)
        self.parent_desktop = parent
        self.text = text
        self.command = command
        self.file_path = file_path
        self.selected = False
        self.icon_text = icon_text
        
        # 图标 - 使用emoji文字
        self.icon_label = tk.Label(self, text=icon_text, font=("Segoe UI", 32),
                                  bg=c.DESKTOP_BG, bd=0)
        self.icon_label.pack()
        
        # 文字
        self.text_label = tk.Label(self, text=text, font=c.ICON_FONT, 
                                  fg=c.DESKTOP_ICON_TEXT, bg=c.DESKTOP_BG,
                                  wraplength=70, justify=tk.CENTER)
        self.text_label.pack()
        
        self.place(x=x, y=y)
        
        # 拖拽数据
        self._drag_data = {"x": 0, "y": 0, "dragging": False}
        
        # 事件绑定
        for widget in [self, self.icon_label, self.text_label]:
            widget.bind("<Button-1>", self.on_press)
            widget.bind("<B1-Motion>", self.on_drag)
            widget.bind("<ButtonRelease-1>", self.on_release)
            widget.bind("<Double-Button-1>", self.on_double_click)
            widget.bind("<Button-3>", self.show_context_menu)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            # 绑定长按事件，触屏长按触发右键
            bind_long_press(widget)
    
    def on_press(self, event):
        """鼠标按下"""
        if hasattr(self.master, 'deselect_all_icons'):
            self.master.deselect_all_icons()
        self.select()
        
        self._drag_data["x"] = event.x_root - self.winfo_x()
        self._drag_data["y"] = event.y_root - self.winfo_y()
        self._drag_data["dragging"] = False
    
    def on_drag(self, event):
        """拖拽中"""
        self._drag_data["dragging"] = True
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        
        x = max(0, min(x, self.master.winfo_width() - 80))
        y = max(0, min(y, self.master.winfo_height() - 80))
        
        self.place(x=x, y=y)
    
    def on_release(self, event):
        """鼠标释放"""
        self._drag_data["dragging"] = False
    
    def on_double_click(self, event):
        """双击打开"""
        if self.command:
            self.command()
    
    def on_enter(self, event):
        if not self.selected:
            self.config(bg="#4078B0")
            self.icon_label.config(bg="#4078B0")
            self.text_label.config(bg="#4078B0")
    
    def on_leave(self, event):
        if not self.selected:
            self.config(bg=c.DESKTOP_BG)
            self.icon_label.config(bg=c.DESKTOP_BG)
            self.text_label.config(bg=c.DESKTOP_BG)
    
    def select(self):
        self.selected = True
        self.config(bg="#316AC5")
        self.icon_label.config(bg="#316AC5")
        self.text_label.config(bg="#316AC5")
    
    def deselect(self):
        self.selected = False
        self.config(bg=c.DESKTOP_BG)
        self.icon_label.config(bg=c.DESKTOP_BG)
        self.text_label.config(bg=c.DESKTOP_BG)
    
    def show_context_menu(self, event):
        """显示图标右键菜单"""
        if hasattr(self.master, 'deselect_all_icons'):
            self.master.deselect_all_icons()
        self.select()
        
        x = self.winfo_x() + event.x
        y = self.winfo_y() + event.y
        
        menu = XPContextMenu(self.master)
        
        menu.add_item("打开(O)", self.open_file, icon="📂")
        menu.add_separator()
        menu.add_item("剪切(T)", self.cut_file, icon="✂️")
        menu.add_item("复制(C)", self.copy_file, icon="📋")
        menu.add_item("创建快捷方式", None, enabled=False)
        menu.add_item("删除(D)", self.delete_file, icon="🗑️")
        menu.add_item("重命名(M)", self.rename_file)
        menu.add_separator()
        menu.add_item("属性(R)", self.show_properties, icon="⚙️")
        
        menu.show(x, y)
    
    def open_file(self):
        """打开文件"""
        if self.command:
            self.command()
    
    def cut_file(self):
        """剪切"""
        if self.file_path:
            clipboard.set_files([self.file_path], 'cut')
    
    def copy_file(self):
        """复制"""
        if self.file_path:
            clipboard.set_files([self.file_path], 'copy')
    
    def delete_file(self):
        """删除"""
        if self.file_path:
            # 简单确认，后续可扩展为XP风格确认框
            fs.delete_file(self.file_path)
            self.parent_desktop.refresh()
    
    def rename_file(self):
        """重命名"""
        new_name = simpledialog.askstring("重命名", "输入新名称:", initialvalue=self.text)
        if new_name and self.file_path:
            result = fs.rename_file(self.file_path, new_name)
            if result:
                self.text = new_name
                self.text_label.config(text=new_name)
                self.file_path = result.path
            else:
                show_error(self.master.app_manager, "重命名失败，可能文件名已存在")
    
    def show_properties(self):
        """显示属性"""
        if self.file_path:
            file_info = FileInfo(self.file_path)
            PropertiesDialog(self.master.app_manager, file_info)

class Desktop(tk.Canvas):
    """XP桌面 - 使用Canvas绘制Bliss壁纸"""
    def __init__(self, parent, app_manager=None):
        super().__init__(parent, bd=0, highlightthickness=0)
        self.parent = parent
        self.app_manager = app_manager
        self.icons = []
        self.selected_icon = None
        self.context_menu = None
        
        self.pack(fill=tk.BOTH, expand=True)
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Button-3>", self.show_context_menu)
        # 绑定长按事件，触屏长按触发右键
        bind_long_press(self)
        self.bind("<Configure>", self.on_resize)
        
        self.after(100, self.draw_wallpaper)
        self.create_icons()
    
    def draw_wallpaper(self):
        """绘制Bliss壁纸 - XP经典草原"""
        self.delete("wallpaper")
        w = self.winfo_width() or self.winfo_screenwidth()
        h = self.winfo_height() or self.winfo_screenheight()
        
        if w < 10 or h < 10:
            self.after(100, self.draw_wallpaper)
            return
        
        # 天空渐变
        sky_height = int(h * 0.6)
        for i in range(sky_height):
            ratio = i / sky_height
            r = int(50 + 180 * ratio)
            g = int(120 + 135 * ratio)
            b = int(210 + 45 * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(0, i, w, i, fill=color, tags="wallpaper")
        
        # 白云
        cloud_color = "#FFFFFF"
        clouds = [
            (w*0.2, sky_height*0.3, 80),
            (w*0.6, sky_height*0.25, 100),
            (w*0.8, sky_height*0.4, 60),
        ]
        for cx, cy, size in clouds:
            for i in range(5):
                rx = size * (0.5 + i*0.2)
                ry = size * 0.3
                ox = cx + (i-2)*size*0.3
                oy = cy + math.sin(i)*5
                self.create_oval(ox-rx, oy-ry, ox+rx, oy+ry, 
                               fill=cloud_color, outline="", tags="wallpaper")
        
        hill_base = sky_height
        
        # 远山
        hill1_points = []
        for x in range(0, w+10, 10):
            y = hill_base - 40 - 30 * math.sin(x/w * math.pi * 2) - 20 * math.sin(x/w * math.pi * 5)
            hill1_points.extend([x, y])
        hill1_points.extend([w, h, 0, h])
        self.create_polygon(hill1_points, fill="#3A7A2A", outline="", tags="wallpaper")
        
        # 中山
        hill2_points = []
        for x in range(0, w+10, 10):
            y = hill_base - 20 - 25 * math.sin(x/w * math.pi * 3 + 1) - 15 * math.sin(x/w * math.pi * 7)
            hill2_points.extend([x, y])
        hill2_points.extend([w, h, 0, h])
        self.create_polygon(hill2_points, fill="#4A903A", outline="", tags="wallpaper")
        
        # 近山
        hill3_points = []
        for x in range(0, w+10, 10):
            y = hill_base - 10 * math.sin(x/w * math.pi * 4 + 2) - 8 * math.sin(x/w * math.pi * 9)
            hill3_points.extend([x, y])
        hill3_points.extend([w, h, 0, h])
        self.create_polygon(hill3_points, fill="#5AA84A", outline="", tags="wallpaper")
        
        # 草地纹理
        import random
        random.seed(42)
        for _ in range(500):
            x = random.randint(0, w)
            y = random.randint(hill_base, h)
            shade = random.randint(-20, 20)
            gr = min(255, max(0, 168 + shade))
            self.create_rectangle(x, y, x+2, y+2, 
                                fill=f"#{50:02x}{gr:02x}{40:02x}", 
                                outline="", tags="wallpaper")
    
    def on_resize(self, event):
        self.after(100, self.draw_wallpaper)
    
    def create_icons(self):
        """创建桌面图标"""
        system_icons = [
            ("我的文档", "📁", self.open_my_documents, None),
            ("我的电脑", "💻", self.open_my_computer, None),
            ("网上邻居", "🌐", self.open_network, None),
            ("回收站", "🗑️", self.open_recycle_bin, None),
            ("Internet\nExplorer", "🌍", self.open_ie, None),
        ]
        
        for i, (text, icon, cmd, file_path) in enumerate(system_icons):
            desktop_icon = DesktopIcon(self, text, icon, cmd, file_path, x=20, y=20 + i * 80)
            self.icons.append(desktop_icon)
        
        self.refresh_user_files()
    
    def refresh_user_files(self):
        """刷新桌面上的用户文件图标"""
        new_icons = []
        for icon in self.icons:
            if icon.file_path and os.path.dirname(icon.file_path) == fs.get_desktop():
                icon.destroy()
            else:
                new_icons.append(icon)
        self.icons = new_icons
        
        desktop_path = fs.get_desktop()
        desktop_files = fs.list_files(desktop_path)
        
        row = len([i for i in self.icons if not i.file_path])
        for file_info in desktop_files:
            if file_info.name == "desktop.ini":
                continue
            icon_text = file_info.get_icon()
            cmd = lambda f=file_info: self.open_real_file(f)
            icon = DesktopIcon(self, file_info.name, icon_text, cmd, file_info.path,
                             x=20, y=20 + row * 80)
            self.icons.append(icon)
            row += 1
    
    def refresh(self):
        """刷新桌面"""
        self.refresh_user_files()
    
    def deselect_all_icons(self):
        for icon in self.icons:
            if icon.winfo_exists():
                icon.deselect()
    
    def on_click(self, event):
        self.deselect_all_icons()
        self.hide_context_menu()
    
    def show_context_menu(self, event):
        """显示桌面右键菜单"""
        self.deselect_all_icons()
        self.hide_context_menu()
        
        self.context_menu = XPContextMenu(self)
        
        # 查看
        view_menu = self.context_menu.add_submenu("查看(V)", None)
        view_menu.add_item("大图标(G)", None)
        view_menu.add_item("小图标(M)", None)
        view_menu.add_separator()
        view_menu.add_item("自动排列(A)", None)
        view_menu.add_item("对齐到网格(I)", None)
        view_menu.add_item("显示桌面图标(D)", None)
        
        # 排列图标
        arrange_menu = self.context_menu.add_submenu("排列图标(I)", None)
        arrange_menu.add_item("名称(N)", None)
        arrange_menu.add_item("大小(S)", None)
        arrange_menu.add_item("类型(T)", None)
        arrange_menu.add_item("修改时间(M)", None)
        
        self.context_menu.add_item("刷新(E)", self.refresh)
        self.context_menu.add_separator()
        
        # 粘贴
        can_paste = clipboard.has_files()
        self.context_menu.add_item("粘贴(P)", self.paste, enabled=can_paste, icon="📋")
        self.context_menu.add_item("粘贴快捷方式(S)", None, enabled=False)
        self.context_menu.add_separator()
        
        # 新建
        new_menu = self.context_menu.add_submenu("新建(W)", None)
        new_menu.add_item("文件夹(F)", self.new_folder, icon="📁")
        new_menu.add_item("文本文档(T)", self.new_text_file, icon="📄")
        new_menu.add_separator()
        new_menu.add_item("快捷方式(S)", None, enabled=False)
        
        self.context_menu.add_separator()
        self.context_menu.add_item("属性(R)", self.show_properties)
        
        self.context_menu.show(event.x, event.y)
    
    def hide_context_menu(self, event=None):
        if self.context_menu:
            self.context_menu.destroy()
            self.context_menu = None
    
    def new_folder(self):
        """新建文件夹"""
        name = simpledialog.askstring("新建文件夹", "输入文件夹名:", initialvalue="新建文件夹")
        if name:
            fs.create_folder(fs.get_desktop(), name)
            self.refresh()
    
    def new_text_file(self):
        """新建文本文档"""
        name = simpledialog.askstring("新建", "输入文件名:", initialvalue="新建文本文档.txt")
        if name:
            fs.create_file(fs.get_desktop(), name, "")
            self.refresh()
    
    def paste(self):
        """粘贴"""
        if clipboard.has_files():
            for src_path in clipboard.files:
                if clipboard.operation == 'copy':
                    fs.copy_file(src_path, fs.get_desktop())
                elif clipboard.operation == 'cut':
                    fs.move_file(src_path, fs.get_desktop())
            if clipboard.operation == 'cut':
                clipboard.clear()
            self.refresh()
    
    def show_properties(self):
        """显示显示属性"""
        DisplayPropertiesDialog(self.app_manager)
    
    def open_real_file(self, file_info):
        """打开真实文件 - 统一在XP内部处理"""
        if file_info.is_dir:
            # 文件夹用资源管理器打开
            self.app_manager.open_app("my_computer", path=file_info.path)
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
    
    def open_my_documents(self):
        if self.app_manager:
            self.app_manager.open_app("my_computer", path=os.path.expanduser("~"))
    
    def open_my_computer(self):
        if self.app_manager:
            self.app_manager.open_app("my_computer", path="")
    
    def open_network(self):
        show_info(self.app_manager, "网络连接不可用", "网上邻居")
    
    def open_recycle_bin(self):
        show_info(self.app_manager, "回收站为空", "回收站")
    
    def open_ie(self):
        if self.app_manager:
            self.app_manager.open_app("ie")
