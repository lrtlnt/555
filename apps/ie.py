#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internet Explorer 6 浏览器
使用urllib获取网页内容，支持文本、图片、链接渲染
"""
import tkinter as tk
from tkinter import ttk
import os
import sys
import io
import base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constants as c
from widgets import XPWindow, XPButton
import urllib.request
import urllib.error
import urllib.parse
import re
from html.parser import HTMLParser

class SimpleHTMLParser(HTMLParser):
    """简单HTML解析器，提取文本、链接和图片"""
    def __init__(self, base_url=""):
        super().__init__()
        self.elements = []  # 元素列表: ('text', text), ('link', text, url), ('image', url), ('newline',)
        self.current_link = None
        self.in_title = False
        self.title = ""
        self.tag_stack = []
        self.base_url = base_url
        self.images = []  # 图片URL列表
    
    def _make_absolute_url(self, url):
        """转换为绝对URL"""
        if not url:
            return ""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            parsed = urllib.parse.urlparse(self.base_url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        if self.base_url.endswith("/"):
            return self.base_url + url
        else:
            return os.path.dirname(self.base_url) + "/" + url
    
    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        attrs_dict = dict(attrs)
        
        if tag == "a" and "href" in attrs_dict:
            self.current_link = self._make_absolute_url(attrs_dict["href"])
        elif tag == "title":
            self.in_title = True
        elif tag == "br":
            self.elements.append(('newline',))
        elif tag == "p" or tag == "div":
            self.elements.append(('newline',))
            self.elements.append(('newline',))
        elif tag == "li":
            self.elements.append(('newline',))
            self.elements.append(('text', "• "))
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.elements.append(('newline',))
            self.elements.append(('newline',))
            self.elements.append(('heading', tag))
        elif tag == "img" and "src" in attrs_dict:
            img_url = self._make_absolute_url(attrs_dict["src"])
            self.elements.append(('image', img_url))
            self.images.append(img_url)
        elif tag == "hr":
            self.elements.append(('newline',))
            self.elements.append(('text', "─" * 80))
            self.elements.append(('newline',))
    
    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        
        if tag == "a":
            self.current_link = None
        elif tag == "title":
            self.in_title = False
        elif tag in ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"]:
            self.elements.append(('newline',))
    
    def handle_data(self, data):
        text = data
        if not text.strip() and not self.in_title:
            # 保留少量空格
            if text and self.elements and self.elements[-1][0] != 'newline':
                self.elements.append(('text', ' '))
            return
        
        if self.in_title:
            self.title += text.strip()
        
        if self.current_link:
            self.elements.append(('link', text, self.current_link))
        else:
            self.elements.append(('text', text))

class InternetExplorer(XPWindow):
    """Internet Explorer 6 浏览器"""
    def __init__(self, parent):
        super().__init__(parent, title="Internet Explorer", width=800, height=600)
        self.app_manager = parent
        self.current_url = ""
        self.history = []
        self.history_index = -1
        self.photo_images = []  # 保持图片引用
        
        self.place(x=50, y=20)
        
        self._create_toolbar()
        self._create_address_bar()
        self._create_content_area()
        self._create_statusbar()
        
        self.go_home()
        self.activate()
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=35, bd=1, relief=tk.RAISED)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        toolbar_frame.pack_propagate(False)
        
        self.toolbar_buttons = {}
        
        buttons = [
            ("⬅️ 后退", self.go_back, False),
            ("➡️ 前进", self.go_forward, False),
            ("separator", None, False),
            ("🏠 主页", self.go_home, True),
            ("🔄 刷新", self.refresh_page, True),
            ("❌ 停止", self.stop_loading, True),
            ("separator", None, False),
            ("🔍 搜索", None, False),
            ("⭐ 收藏", None, False),
        ]
        
        for item in buttons:
            if item[0] == "separator":
                sep = tk.Frame(toolbar_frame, width=2, bg=c.BUTTON_SHADOW)
                sep.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=3)
                continue
            
            text, cmd, enabled = item
            btn = tk.Label(toolbar_frame, text=text, font=c.DEFAULT_FONT,
                         bg=c.BUTTON_FACE, padx=8, pady=5)
            btn.pack(side=tk.LEFT, padx=1)
            self.toolbar_buttons[text] = (btn, cmd, enabled)
            if enabled:
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5F0FC", relief=tk.RAISED, bd=1))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.BUTTON_FACE, relief=tk.FLAT, bd=0))
                btn.bind("<Button-1>", lambda e, c=cmd: c() if c else None)
            else:
                btn.config(fg=c.DISABLED_TEXT)
    
    def _update_nav_buttons(self):
        """更新导航按钮状态"""
        back_btn = self.toolbar_buttons.get("⬅️ 后退")
        forward_btn = self.toolbar_buttons.get("➡️ 前进")
        
        if back_btn:
            btn, cmd, _ = back_btn
            if self.history_index > 0:
                btn.config(fg=c.TEXT_COLOR)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5F0FC", relief=tk.RAISED, bd=1))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.BUTTON_FACE, relief=tk.FLAT, bd=0))
                btn.bind("<Button-1>", lambda e: self.go_back())
            else:
                btn.config(fg=c.DISABLED_TEXT)
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
                btn.unbind("<Button-1>")
        
        if forward_btn:
            btn, cmd, _ = forward_btn
            if self.history_index < len(self.history) - 1:
                btn.config(fg=c.TEXT_COLOR)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E5F0FC", relief=tk.RAISED, bd=1))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=c.BUTTON_FACE, relief=tk.FLAT, bd=0))
                btn.bind("<Button-1>", lambda e: self.go_forward())
            else:
                btn.config(fg=c.DISABLED_TEXT)
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
                btn.unbind("<Button-1>")
    
    def _create_address_bar(self):
        """创建地址栏"""
        addr_frame = tk.Frame(self.content_frame, bg=c.WINDOW_BG, height=30)
        addr_frame.pack(fill=tk.X, padx=2)
        addr_frame.pack_propagate(False)
        
        tk.Label(addr_frame, text="地址(D):", font=c.DEFAULT_FONT, bg=c.WINDOW_BG).pack(side=tk.LEFT, padx=3)
        
        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(addr_frame, textvariable=self.address_var, font=c.DEFAULT_FONT)
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3, pady=3)
        self.address_entry.bind("<Return>", lambda e: self.navigate(self.address_var.get()))
        
        go_btn = XPButton(addr_frame, "转到", width=50, command=lambda: self.navigate(self.address_var.get()))
        go_btn.pack(side=tk.RIGHT, padx=3, pady=2)
    
    def _create_content_area(self):
        """创建内容显示区域"""
        content_frame = tk.Frame(self.content_frame, bg="#FFFFFF", bd=2, relief=tk.SUNKEN)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.text_scroll = ttk.Scrollbar(content_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.content_text = tk.Text(content_frame, wrap=tk.WORD, font=("Tahoma", 10),
                                   bg="#FFFFFF", fg="#000000", bd=0, padx=10, pady=10,
                                   yscrollcommand=self.text_scroll.set, cursor="arrow")
        self.content_text.pack(fill=tk.BOTH, expand=True)
        self.text_scroll.config(command=self.content_text.yview)
        
        # 配置标签样式
        self.content_text.tag_config("link", foreground="#0000FF", underline=True)
        self.content_text.tag_config("title", font=("Tahoma", 16, "bold"), spacing3=10)
        self.content_text.tag_config("h1", font=("Tahoma", 18, "bold"), spacing3=12)
        self.content_text.tag_config("h2", font=("Tahoma", 15, "bold"), spacing3=10)
        self.content_text.tag_config("h3", font=("Tahoma", 13, "bold"), spacing3=8)
        self.content_text.tag_config("h4", font=("Tahoma", 11, "bold"), spacing3=6)
        self.content_text.tag_config("bold", font=("Tahoma", 10, "bold"))
        
        # 链接点击
        self.content_text.tag_bind("link", "<Button-1>", self.on_link_click)
        self.content_text.tag_bind("link", "<Enter>", lambda e: self.content_text.config(cursor="hand2"))
        self.content_text.tag_bind("link", "<Leave>", lambda e: self.content_text.config(cursor="arrow"))
    
    def _create_statusbar(self):
        """创建状态栏"""
        statusbar = tk.Frame(self.content_frame, bg=c.BUTTON_FACE, height=22, bd=1, relief=tk.SUNKEN)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=(0, 2))
        statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(statusbar, text="完成", font=c.DEFAULT_FONT,
                                    bg=c.BUTTON_FACE, anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.security_zone = tk.Label(statusbar, text="Internet", font=c.DEFAULT_FONT,
                                     bg=c.BUTTON_FACE, bd=1, relief=tk.SUNKEN, padx=10)
        self.security_zone.pack(side=tk.RIGHT)
    
    def _load_image(self, url):
        """加载图片 - 仅支持GIF/PNG，使用tkinter内置PhotoImage"""
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                image_data = response.read()
            
            # tkinter.PhotoImage支持GIF和PNG
            photo = tk.PhotoImage(data=base64.b64encode(image_data))
            self.photo_images.append(photo)
            return photo
        except Exception as e:
            # 图片加载失败返回None，显示占位符
            return None
    
    def navigate(self, url):
        """导航到URL"""
        if not url:
            return
        
        # 处理URL
        if not url.startswith("http://") and not url.startswith("https://"):
            if url.startswith("www."):
                url = "http://" + url
            elif "." in url and " " not in url:
                url = "http://" + url
            else:
                url = f"https://www.baidu.com/s?wd={urllib.parse.quote(url)}"
        
        self.status_label.config(text=f"正在连接到 {url}...")
        self.update_idletasks()
        
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                content_type = response.headers.get('Content-Type', 'text/html')
                html_content = response.read()
                
                # 尝试检测编码
                charset = 'utf-8'
                if 'charset=' in content_type:
                    charset = content_type.split('charset=')[-1].split(';')[0].strip()
                
                try:
                    html_content = html_content.decode(charset, errors='ignore')
                except:
                    html_content = html_content.decode('utf-8', errors='ignore')
                
                final_url = response.geturl()
            
            # 解析HTML
            parser = SimpleHTMLParser(final_url)
            try:
                parser.feed(html_content)
            except:
                pass
            
            # 显示内容
            self.display_content(parser, final_url)
            
            # 更新历史
            if not self.history or self.history[self.history_index] != final_url:
                self.history = self.history[:self.history_index + 1]
                self.history.append(final_url)
                self.history_index = len(self.history) - 1
            
            self.current_url = final_url
            self.address_var.set(final_url)
            
            title = parser.title or final_url
            self.title_label.config(text=f"{title} - Microsoft Internet Explorer")
            
            self.status_label.config(text="完成")
            self._update_nav_buttons()
            
        except urllib.error.URLError as e:
            self.show_error(f"无法打开网页\n\n{str(e.reason)}")
        except Exception as e:
            self.show_error(f"无法打开网页\n\n{str(e)}")
    
    def display_content(self, parser, url):
        """显示解析后的内容"""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete("1.0", tk.END)
        self.photo_images = []
        
        # 显示标题
        if parser.title:
            self.content_text.insert(tk.END, parser.title + "\n\n", "title")
        
        # 显示元素
        for elem in parser.elements:
            elem_type = elem[0]
            
            if elem_type == 'text':
                self.content_text.insert(tk.END, elem[1])
            elif elem_type == 'link':
                _, text, link_url = elem
                self.content_text.insert(tk.END, text, ("link", link_url))
            elif elem_type == 'newline':
                self.content_text.insert(tk.END, "\n")
            elif elem_type == 'heading':
                _, level = elem
                self.content_text.insert(tk.END, "\n")
            elif elem_type == 'image':
                _, img_url = elem
                photo = self._load_image(img_url)
                if photo:
                    self.content_text.insert(tk.END, "\n")
                    self.content_text.image_create(tk.END, image=photo)
                    self.content_text.insert(tk.END, "\n")
                else:
                    # 图片加载失败显示占位符
                    self.content_text.insert(tk.END, "[图片]", "link")
        
        self.content_text.config(state=tk.DISABLED)
    
    def on_link_click(self, event):
        """点击链接"""
        index = self.content_text.index(f"@{event.x},{event.y}")
        tags = self.content_text.tag_names(index)
        
        for tag in tags:
            if tag.startswith("http://") or tag.startswith("https://"):
                self.navigate(tag)
                return
    
    def show_error(self, message):
        """显示错误页面"""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete("1.0", tk.END)
        
        self.content_text.insert(tk.END, "无法显示网页\n\n", "title")
        self.content_text.insert(tk.END, message + "\n\n")
        self.content_text.insert(tk.END, "请尝试以下操作:\n")
        self.content_text.insert(tk.END, "• 检查地址栏中输入的地址是否正确\n")
        self.content_text.insert(tk.END, "• 单击刷新按钮，或以后再试\n")
        self.content_text.insert(tk.END, "• 如果您在地址栏中键入了地址，请确保拼写正确\n")
        
        self.content_text.config(state=tk.DISABLED)
        self.status_label.config(text="完成")
    
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to_history()
    
    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.navigate_to_history()
    
    def navigate_to_history(self):
        """从历史记录导航（不添加新历史）"""
        url = self.history[self.history_index]
        self.status_label.config(text=f"正在连接到 {url}...")
        self.update_idletasks()
        
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                final_url = response.geturl()
            
            parser = SimpleHTMLParser(final_url)
            try:
                parser.feed(html_content)
            except:
                pass
            
            self.display_content(parser, final_url)
            self.current_url = final_url
            self.address_var.set(final_url)
            
            title = parser.title or final_url
            self.title_label.config(text=f"{title} - Microsoft Internet Explorer")
            self.status_label.config(text="完成")
            self._update_nav_buttons()
        except Exception as e:
            self.show_error(str(e))
    
    def go_home(self):
        """主页 - 百度"""
        self.navigate("https://www.baidu.com")
    
    def refresh_page(self):
        if self.current_url:
            self.navigate(self.current_url)
    
    def stop_loading(self):
        self.status_label.config(text="完成")
