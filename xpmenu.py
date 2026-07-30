#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XP风格上下文菜单组件
支持蓝色悬停高亮、3D边框、分隔线、子菜单
"""
import tkinter as tk
import constants as c

class XPMenuItem(tk.Label):
    """菜单项"""
    def __init__(self, parent, text, command=None, enabled=True, icon=None, is_submenu=False):
        self.text = text
        self.command = command
        self.enabled = enabled
        self.icon = icon
        self.is_submenu = is_submenu
        self.submenu = None
        
        display_text = f"  {text}"
        if icon:
            display_text = f" {icon}  {text}"
        if is_submenu:
            display_text += " ▶"
        display_text += "    "
        
        super().__init__(parent, text=display_text, font=c.MENU_FONT,
                        bg=c.MENU_BG, fg=c.TEXT_COLOR if enabled else c.DISABLED_TEXT,
                        anchor="w", padx=5, pady=3, bd=0)
        
        if enabled:
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)
            self.bind("<Button-1>", self.on_click)
    
    def on_enter(self, event):
        self.config(bg=c.MENU_SELECTED, fg=c.MENU_SELECTED_TEXT)
        # 如果有子菜单，显示子菜单
        if self.is_submenu and self.submenu:
            self.show_submenu()
    
    def on_leave(self, event):
        self.config(bg=c.MENU_BG, fg=c.TEXT_COLOR if self.enabled else c.DISABLED_TEXT)
    
    def on_click(self, event):
        if self.command:
            # 关闭所有菜单
            top = self.winfo_toplevel()
            if hasattr(top, 'close_all_menus'):
                top.close_all_menus()
            self.command()
    
    def show_submenu(self):
        pass

class XPContextMenu(tk.Frame):
    """XP风格上下文菜单"""
    def __init__(self, parent):
        super().__init__(parent, bg=c.MENU_BORDER, bd=1)
        self.parent = parent
        self.inner = tk.Frame(self, bg=c.MENU_BG, bd=1)
        self.inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.items = []
        self.visible = False
        
        # 点击外部关闭
        self.bind_all("<Button-1>", self.on_outside_click, add="+")
    
    def add_item(self, text, command=None, enabled=True, icon=None):
        """添加菜单项"""
        item = XPMenuItem(self.inner, text, command, enabled, icon)
        item.pack(fill=tk.X)
        self.items.append(item)
        return item
    
    def add_separator(self):
        """添加分隔线"""
        sep = tk.Frame(self.inner, height=2, bg=c.MENU_BORDER)
        sep.pack(fill=tk.X, padx=2, pady=2)
        self.items.append(sep)
    
    def add_submenu(self, text, items_config):
        """添加子菜单"""
        item = XPMenuItem(self.inner, text, None, True, None, True)
        item.pack(fill=tk.X)
        self.items.append(item)
        return item
    
    def show(self, x, y):
        """显示菜单"""
        self.place(x=x, y=y)
        self.visible = True
        self.lift()
    
    def hide(self):
        """隐藏菜单"""
        self.place_forget()
        self.visible = False
    
    def on_outside_click(self, event):
        """点击外部关闭菜单"""
        if self.visible:
            x1 = self.winfo_rootx()
            y1 = self.winfo_rooty()
            x2 = x1 + self.winfo_width()
            y2 = y1 + self.winfo_height()
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                self.hide()

def show_context_menu(parent, x, y, items):
    """
    便捷函数：显示上下文菜单
    items: 列表，每个元素是 (text, command, enabled, icon) 或 "separator"
    """
    menu = XPContextMenu(parent)
    for item in items:
        if item == "separator":
            menu.add_separator()
        else:
            text = item[0]
            command = item[1] if len(item) > 1 else None
            enabled = item[2] if len(item) > 2 else True
            icon = item[3] if len(item) > 3 else None
            menu.add_item(text, command, enabled, icon)
    
    menu.show(x, y)
    return menu
