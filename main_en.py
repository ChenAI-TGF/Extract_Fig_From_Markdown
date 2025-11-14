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
        self.root.title("Image Link Extractor and Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set font
        self.font = ('Arial', 10)
        
        # Create UI components
        self.create_widgets()
        
        # Store extracted links
        self.image_links = []
        
    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text input area
        ttk.Label(main_frame, text="Please enter text containing image links:", font=self.font).pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=self.font)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Button area
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.extract_btn = ttk.Button(button_frame, text="Extract Links", command=self.extract_links)
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_btn = ttk.Button(button_frame, text="Download Images", command=self.start_download, state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Result display area
        ttk.Label(main_frame, text="Extraction Results and Status:", font=self.font).pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=self.font, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """Display messages in the result area"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
    
    def extract_links(self):
        """Extract image links from text"""
        text = self.text_input.get("1.0", tk.END)
        
        # Regular expression to match ![description](link) format
        pattern = r'!\[.*?\]\((.*?)\)'
        self.image_links = re.findall(pattern, text)
        
        if self.image_links:
            self.log(f"Successfully extracted {len(self.image_links)} image links:")
            for i, link in enumerate(self.image_links, 1):
                self.log(f"{i}. {link}")
            self.download_btn.config(state=tk.NORMAL)
        else:
            self.log("No image links found")
            self.download_btn.config(state=tk.DISABLED)
    
    def start_download(self):
        """Start downloading images (execute in a new thread to avoid UI freezing)"""
        if not self.image_links:
            messagebox.showwarning("Warning", "No image links to download")
            return
        
        # Disable buttons to prevent duplicate operations
        self.extract_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        
        # Start download thread
        Thread(target=self.download_images, daemon=True).start()
    
    def download_images(self):
        """Download images and save to image folder"""
        # Create image folder
        image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            self.log(f"Created image folder: {image_dir}")
        
        total = len(self.image_links)
        success_count = 0
        
        for i, link in enumerate(self.image_links, 1):
            try:
                self.log(f"Downloading image {i}/{total}...")
                
                # Send request
                response = requests.get(link, timeout=10, stream=True)
                response.raise_for_status()  # Check if request was successful
                
                # Get file extension
                if '.' in link:
                    ext = link.split('.')[-1].lower()
                    # Restrict to common image extensions
                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                        ext = 'jpg'
                else:
                    ext = 'jpg'
                
                # Save file
                filename = f"{i}.{ext}"
                file_path = os.path.join(image_dir, filename)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                
                success_count += 1
                self.log(f"Successfully saved: {filename}")
                
            except Exception as e:
                self.log(f"Download failed (link {i}): {str(e)}")
            
            # Update progress bar
            progress = (i / total) * 100
            self.progress_var.set(progress)
            self.root.update_idletasks()
            
            # Add a small delay to avoid too frequent requests
            time.sleep(0.1)
        
        # Download completed
        self.progress_var.set(100)
        self.log(f"\nDownload completed! Successfully downloaded {success_count}/{total} images")
        self.log(f"Images saved to: {image_dir}")
        
        # Restore button states
        self.extract_btn.config(state=tk.NORMAL)
        self.download_btn.config(state=tk.NORMAL)
        
        # Show completion message
        messagebox.showinfo("Completed", f"Download completed! Successfully downloaded {success_count}/{total} images\nSaved to: {image_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLinkExtractor(root)
    root.mainloop()