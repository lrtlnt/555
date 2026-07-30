#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实文件系统访问模块
使用项目目录下的desktop文件夹作为模拟桌面
"""
import os
import shutil
import sys
from datetime import datetime
import platform

# 获取桌面路径 - 使用项目目录下的desktop文件夹
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP_DIR = os.path.join(PROJECT_DIR, "desktop")

# 确保desktop目录存在
os.makedirs(DESKTOP_DIR, exist_ok=True)

class FileInfo:
    """真实文件信息类"""
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.is_dir = os.path.isdir(path)
        self.is_file = os.path.isfile(path)
        
        if os.path.exists(path):
            stat = os.stat(path)
            self.size = stat.st_size
            self.created_time = datetime.fromtimestamp(stat.st_ctime)
            self.modified_time = datetime.fromtimestamp(stat.st_mtime)
            self.accessed_time = datetime.fromtimestamp(stat.st_atime)
        else:
            self.size = 0
            self.created_time = datetime.now()
            self.modified_time = datetime.now()
            self.accessed_time = datetime.now()
    
    def get_extension(self):
        return os.path.splitext(self.name)[1].lower()
    
    def get_icon(self):
        """根据文件类型返回图标"""
        if self.is_dir:
            if self.path == DESKTOP_DIR:
                return "🖥️"
            elif "WINDOWS" in self.name or "Program Files" in self.name:
                return "📂"
            return "📁"
        
        ext = self.get_extension()
        
        # 可执行文件
        if ext in ['.exe', '.com', '.bat', '.cmd', '.msi']:
            return "⚙️"
        # 文本文件
        elif ext in ['.txt', '.py', '.md', '.log', '.ini', '.cfg', '.json', '.xml', 
                    '.html', '.css', '.js', '.java', '.c', '.cpp', '.h', '.sh']:
            return "📄"
        # 图片文件
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp', '.pgm', '.ppm']:
            return "🖼️"
        # 音频文件
        elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
            return "🎵"
        # 视频文件
        elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']:
            return "🎬"
        # 文档
        elif ext in ['.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx']:
            return "📕"
        # 压缩包
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return "📦"
        else:
            return "📄"
    
    def get_size_str(self):
        """返回可读的文件大小"""
        size = self.size
        if size < 1024:
            return f"{size} 字节"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.2f} GB"

class RealFileSystem:
    """真实文件系统操作类"""
    
    def get_desktop(self):
        """获取桌面路径"""
        return DESKTOP_DIR
    
    def list_files(self, path):
        """列出目录下的文件"""
        files = []
        try:
            if os.path.isdir(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    # 跳过隐藏文件和__pycache__
                    if not item.startswith('.') and item != '__pycache__':
                        files.append(FileInfo(item_path))
                # 文件夹在前，文件在后，按名称排序
                files.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        except Exception as e:
            print(f"列出文件错误: {e}")
        return files
    
    def create_file(self, path, name, content=""):
        """创建文件"""
        file_path = os.path.join(path, name)
        # 处理重名
        counter = 1
        base, ext = os.path.splitext(name)
        while os.path.exists(file_path):
            file_path = os.path.join(path, f"{base} ({counter}){ext}")
            counter += 1
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return FileInfo(file_path)
        except Exception as e:
            print(f"创建文件错误: {e}")
            return None
    
    def create_folder(self, path, name):
        """创建文件夹"""
        folder_path = os.path.join(path, name)
        # 处理重名
        counter = 1
        while os.path.exists(folder_path):
            folder_path = os.path.join(path, f"{name} ({counter})")
            counter += 1
        
        try:
            os.makedirs(folder_path)
            return FileInfo(folder_path)
        except Exception as e:
            print(f"创建文件夹错误: {e}")
            return None
    
    def delete_file(self, path):
        """删除文件或文件夹"""
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            print(f"删除错误: {e}")
            return False
    
    def rename_file(self, old_path, new_name):
        """重命名文件"""
        dir_path = os.path.dirname(old_path)
        new_path = os.path.join(dir_path, new_name)
        
        if os.path.exists(new_path):
            return None
        
        try:
            os.rename(old_path, new_path)
            return FileInfo(new_path)
        except Exception as e:
            print(f"重命名错误: {e}")
            return None
    
    def copy_file(self, src_path, dst_dir):
        """复制文件到目标目录"""
        try:
            name = os.path.basename(src_path)
            dst_path = os.path.join(dst_dir, name)
            
            # 处理重名
            counter = 1
            base, ext = os.path.splitext(name)
            while os.path.exists(dst_path):
                if os.path.isdir(src_path):
                    dst_path = os.path.join(dst_dir, f"{base} ({counter})")
                else:
                    dst_path = os.path.join(dst_dir, f"{base} ({counter}){ext}")
                counter += 1
            
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            return FileInfo(dst_path)
        except Exception as e:
            print(f"复制错误: {e}")
            return None
    
    def move_file(self, src_path, dst_dir):
        """移动文件到目标目录"""
        try:
            name = os.path.basename(src_path)
            dst_path = os.path.join(dst_dir, name)
            
            # 处理重名
            counter = 1
            base, ext = os.path.splitext(name)
            while os.path.exists(dst_path):
                if os.path.isdir(src_path):
                    dst_path = os.path.join(dst_dir, f"{base} ({counter})")
                else:
                    dst_path = os.path.join(dst_dir, f"{base} ({counter}){ext}")
                counter += 1
            
            shutil.move(src_path, dst_path)
            return FileInfo(dst_path)
        except Exception as e:
            print(f"移动错误: {e}")
            return None
    
    def read_file(self, path):
        """读取文件内容"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件错误: {e}")
            return ""
    
    def write_file(self, path, content):
        """写入文件内容"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件错误: {e}")
            return False
    
    def get_drives(self):
        """获取所有驱动器（Windows）或根目录"""
        drives = []
        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append((f"本地磁盘 ({letter}:)", drive))
        else:
            drives.append(("文件系统根目录", "/"))
            # 添加home目录
            drives.append(("主目录", os.path.expanduser("~")))
        return drives
    
    def get_parent_path(self, path):
        """获取父目录"""
        parent = os.path.dirname(path)
        if parent == path or parent == "":
            return None
        return parent
    
    def get_special_folders(self):
        """获取特殊文件夹"""
        folders = []
        
        # 桌面
        folders.append(("桌面", DESKTOP_DIR, "🖥️"))
        
        # 我的文档/主目录
        home = os.path.expanduser("~")
        folders.append(("我的文档", home, "📂"))
        
        return folders

# 全局文件系统实例
fs = RealFileSystem()

# 剪贴板
class Clipboard:
    def __init__(self):
        self.files = []
        self.operation = None  # 'copy' or 'cut'
    
    def set_files(self, files, operation):
        self.files = files if isinstance(files, list) else [files]
        self.operation = operation
    
    def clear(self):
        self.files = []
        self.operation = None
    
    def has_files(self):
        return len(self.files) > 0 and self.operation is not None

clipboard = Clipboard()
