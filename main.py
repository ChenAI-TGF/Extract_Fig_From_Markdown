import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import re
import requests
import os
from threading import Thread
import time

class ImageLinkExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("图片链接提取与下载工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.font = ('SimHei', 10)
        
        # 创建UI组件
        self.create_widgets()
        
        # 存储提取到的链接
        self.image_links = []
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本输入区域
        ttk.Label(main_frame, text="请输入包含图片链接的文本:", font=self.font).pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=self.font)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.extract_btn = ttk.Button(button_frame, text="提取链接", command=self.extract_links)
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_btn = ttk.Button(button_frame, text="下载图片", command=self.start_download, state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 结果显示区域
        ttk.Label(main_frame, text="提取结果与状态:", font=self.font).pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=self.font, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """在结果区域显示消息"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
    
    def extract_links(self):
        """从文本中提取图片链接"""
        text = self.text_input.get("1.0", tk.END)
        
        # 正则表达式匹配![描述](链接)格式
        pattern = r'!\[.*?\]\((.*?)\)'
        self.image_links = re.findall(pattern, text)
        
        if self.image_links:
            self.log(f"成功提取到 {len(self.image_links)} 个图片链接:")
            for i, link in enumerate(self.image_links, 1):
                self.log(f"{i}. {link}")
            self.download_btn.config(state=tk.NORMAL)
        else:
            self.log("未找到任何图片链接")
            self.download_btn.config(state=tk.DISABLED)
    
    def start_download(self):
        """开始下载图片（在新线程中执行以避免UI冻结）"""
        if not self.image_links:
            messagebox.showwarning("警告", "没有可下载的图片链接")
            return
        
        # 禁用按钮防止重复操作
        self.extract_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        
        # 启动下载线程
        Thread(target=self.download_images, daemon=True).start()
    
    def download_images(self):
        """下载图片并保存到image文件夹"""
        # 创建image文件夹
        image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            self.log(f"已创建image文件夹: {image_dir}")
        
        total = len(self.image_links)
        success_count = 0
        
        for i, link in enumerate(self.image_links, 1):
            try:
                self.log(f"正在下载第 {i}/{total} 张图片...")
                
                # 发送请求
                response = requests.get(link, timeout=10, stream=True)
                response.raise_for_status()  # 检查请求是否成功
                
                # 获取文件扩展名
                if '.' in link:
                    ext = link.split('.')[-1].lower()
                    # 限制常见图片扩展名
                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                        ext = 'jpg'
                else:
                    ext = 'jpg'
                
                # 保存文件
                filename = f"{i}.{ext}"
                file_path = os.path.join(image_dir, filename)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                
                success_count += 1
                self.log(f"成功保存: {filename}")
                
            except Exception as e:
                self.log(f"下载失败 (第 {i} 个链接): {str(e)}")
            
            # 更新进度条
            progress = (i / total) * 100
            self.progress_var.set(progress)
            self.root.update_idletasks()
            
            # 稍微延迟一下，避免请求过于频繁
            time.sleep(0.1)
        
        # 下载完成
        self.progress_var.set(100)
        self.log(f"\n下载完成！成功下载 {success_count}/{total} 张图片")
        self.log(f"图片保存路径: {image_dir}")
        
        # 恢复按钮状态
        self.extract_btn.config(state=tk.NORMAL)
        self.download_btn.config(state=tk.NORMAL)
        
        # 显示完成消息
        messagebox.showinfo("完成", f"下载完成！成功下载 {success_count}/{total} 张图片\n保存路径: {image_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLinkExtractor(root)
    root.mainloop()