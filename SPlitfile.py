import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os
from datetime import datetime
import subprocess
import shutil
from pathlib import Path

try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageTk
    PREVIEW_AVAILABLE = True
except ImportError:
    PREVIEW_AVAILABLE = False

def check_imagemagick():
    try:
        result = subprocess.run(['magick', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def process_image(input_path, output_path, temp_dir, fuzz_percent=10, on_progress=None):
    try:
        input_file = Path(input_path)
        output_file = Path(output_path)
        temp_jpg = Path(temp_dir) / f"{input_file.stem}.jpg"
        
        if input_file.suffix.lower() in ['.jpg', '.jpeg']:
            shutil.copy(input_file, temp_jpg)
        else:
            cmd = ['magick', str(input_file), str(temp_jpg)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, f"Conversion failed"
        
        if on_progress:
            on_progress("processing")
        
        cmd = ['magick', str(temp_jpg), '-fuzz', f'{fuzz_percent}%', '-transparent', 'white',
               '-auto-level', '-contrast', '-sharpen', '0x1', str(output_file)]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False, f"Processing failed"
        
        return True, None
    except Exception as e:
        return False, str(e)

def batch_process_images(input_files, output_dir, temp_dir, fuzz_percent=10, on_progress=None):
    success_count = 0
    failed_files = []
    total = len(input_files)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    
    for i, input_path in enumerate(input_files):
        input_file = Path(input_path)
        output_path = Path(output_dir) / f"{input_file.stem}.png"
        
        if on_progress:
            on_progress(i + 1, total, input_file.name)
        
        success, error = process_image(input_path, output_path, temp_dir, fuzz_percent)
        
        if success:
            success_count += 1
        else:
            failed_files.append((input_file.name, error))
    
    return success_count, failed_files

def parse_ranges(range_str, total_pages=None):
    s = (range_str or "").strip()
    if not s:
        return [], []
    
    parts = [p.strip() for p in s.split(',') if p.strip()]
    endpoints_mode = all('-' not in p for p in parts)
    ranges, invalid = [], []

    if endpoints_mode:
        try:
            ends = [int(p) for p in parts]
        except:
            return [], parts
        prev = 0
        for e in ends:
            if e <= prev or e <= 0:
                invalid.append(str(e))
            else:
                ranges.append((prev + 1, e))
                prev = e
        if total_pages and ranges and ranges[-1][1] > total_pages:
            invalid.append(f"{ranges[-1][1]} (max: {total_pages})")
    else:
        for p in parts:
            if '-' not in p:
                invalid.append(p)
                continue
            try:
                a, b = p.split('-', 1)
                start, end = int(a.strip()), int(b.strip())
                if start <= 0 or end <= 0 or start > end:
                    invalid.append(p)
                elif total_pages and (start > total_pages or end > total_pages):
                    invalid.append(f"{p} (max: {total_pages})")
                else:
                    ranges.append((start, end))
            except:
                invalid.append(p)
    return ranges, invalid

def split_pdf(file_path, ranges, output_dir, rotate=0, naming_pattern="split", on_progress=None):
    reader = PdfReader(file_path)
    total = len(reader.pages)
    output_files = []

    for i, (start, end) in enumerate(ranges):
        if start < 1 or end > total or start > end:
            raise ValueError(f"Range {start}-{end} out of bounds")
        
        writer = PdfWriter()
        for p in range(start - 1, end):
            page = reader.pages[p]
            if rotate in (90, 180, 270):
                page.rotate(rotate)
            writer.add_page(page)
        
        if naming_pattern == "timestamp":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_name = f"split_{timestamp}_{i+1}_pages{start}-{end}.pdf"
        else:
            out_name = f"split_{i+1}_pages{start}-{end}.pdf"
        
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append(out_path)
        
        if on_progress:
            on_progress(i + 1, len(ranges))
    
    return output_files

def merge_pdfs(files, output_path, reverse_order=False, reverse_pages_each=False, rotate=0, on_progress=None):
    if reverse_order:
        files = list(reversed(files))
    
    merger = PdfMerger()

    for idx, fp in enumerate(files):
        reader = PdfReader(fp)
        pages = list(reader.pages)

        if reverse_pages_each:
            pages = list(reversed(pages))

        if rotate in (90, 180, 270):
            temp = PdfWriter()
            for page in pages:
                page.rotate(rotate)
                temp.add_page(page)
            from io import BytesIO
            bio = BytesIO()
            temp.write(bio)
            bio.seek(0)
            merger.append(bio)
        else:
            merger.append(fp)

        if on_progress:
            on_progress(idx + 1, len(files))

    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, e=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text, bg="#1e293b", fg="#f1f5f9",
                       padx=12, pady=8, font=("Segoe UI", 10), borderwidth=0)
        lbl.pack()

    def hide(self, e=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class PDFPreview:
    def __init__(self, parent):
        self.parent = parent
        self.pdf_path = None
        self.current_pages = []
        self.all_images = []
        self.current_page_in_range = 0
        self.photo = None
        
        self.frame = ttk.Frame(parent)
        
        header = ttk.Frame(self.frame)
        header.pack(fill="x", pady=(0, 8))
        self.page_label = ttk.Label(header, text="No PDF loaded", style="Sub.TLabel")
        self.page_label.pack(side="left")
        
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#1e293b", highlightthickness=0)
        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(fill="x")
        
        nav_frame = ttk.Frame(self.frame)
        nav_frame.pack(fill="x", pady=(8, 0))
        
        self.prev_btn = ttk.Button(nav_frame, text="⬅ Previous", command=self.prev_page, width=12)
        self.prev_btn.pack(side="left", padx=2)
        self.prev_btn.state(["disabled"])
        
        self.next_btn = ttk.Button(nav_frame, text="Next ➡", command=self.next_page, width=12)
        self.next_btn.pack(side="left", padx=2)
        self.next_btn.state(["disabled"])
        
        self.range_label = ttk.Label(nav_frame, text="", style="Sub.TLabel")
        self.range_label.pack(side="left", padx=12)
        
    def load_pdf(self, pdf_path, status_callback=None):
        if not PREVIEW_AVAILABLE:
            self.show_message("Preview not available\nInstall: pip install pdf2image Pillow")
            return False
        
        try:
            self.pdf_path = pdf_path
            if status_callback:
                status_callback("Loading preview...")
            
            self.all_images = convert_from_path(pdf_path, dpi=150)
            
            if status_callback:
                status_callback(f"Loaded {len(self.all_images)} pages")
            
            return True
        except Exception as e:
            self.show_message(f"Preview Error:\n{str(e)}")
            return False
    
    def show_pages(self, page_ranges=None):
        if not self.all_images:
            return
        
        self.canvas.delete("all")
        
        if page_ranges:
            pages_to_show = []
            for start, end in page_ranges:
                for p in range(start - 1, end):
                    if 0 <= p < len(self.all_images):
                        pages_to_show.append(p)
            
            if not pages_to_show:
                self.show_message("No valid pages in range")
                return
            
            self.current_pages = pages_to_show
            self.current_page_in_range = 0
            
            range_info = ", ".join([f"{s}-{e}" for s, e in page_ranges])
            self.range_label.config(text=f"Ranges: {range_info}")
        else:
            self.current_pages = list(range(len(self.all_images)))
            self.range_label.config(text=f"All {len(self.all_images)} pages")
        
        self.display_current_page()
        self.update_buttons()
    
    def display_current_page(self):
        if not self.current_pages:
            return
        
        page_idx = self.current_pages[self.current_page_in_range]
        img = self.all_images[page_idx]
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 600
        
        img_width, img_height = img.size
        scale = min(canvas_width * 0.95 / img_width, 800 / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(img_resized)
        
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, 10, anchor="n", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, canvas_width, new_height + 20))
        
        actual_page = page_idx + 1
        self.page_label.config(text=f"Page {actual_page} of {len(self.all_images)} ({self.current_page_in_range + 1}/{len(self.current_pages)})")
    
    def next_page(self):
        if self.current_page_in_range < len(self.current_pages) - 1:
            self.current_page_in_range += 1
            self.display_current_page()
            self.update_buttons()
    
    def prev_page(self):
        if self.current_page_in_range > 0:
            self.current_page_in_range -= 1
            self.display_current_page()
            self.update_buttons()
    
    def update_buttons(self):
        if self.current_page_in_range > 0:
            self.prev_btn.state(["!disabled"])
        else:
            self.prev_btn.state(["disabled"])
        
        if self.current_page_in_range < len(self.current_pages) - 1:
            self.next_btn.state(["!disabled"])
        else:
            self.next_btn.state(["disabled"])
    
    def show_message(self, message):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 400
        h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 300
        self.canvas.create_text(w // 2, h // 2, text=message, fill="#94a3b8",
                               font=("Segoe UI", 12), justify="center")
        self.page_label.config(text="")
        self.prev_btn.state(["disabled"])
        self.next_btn.state(["disabled"])
    
    def clear(self):
        self.pdf_path = None
        self.all_images = []
        self.current_pages = []
        self.canvas.delete("all")
        self.page_label.config(text="No PDF loaded")
        self.range_label.config(text="")
        self.prev_btn.state(["disabled"])
        self.next_btn.state(["disabled"])

class PDFToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Master Pro")
        self.root.geometry("1400x850")
        self.root.minsize(1000, 650)

        self.dark = True
        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.total_pages = tk.IntVar(value=0)
        self.rotate_split = tk.StringVar(value="0°")
        self.naming_pattern = tk.StringVar(value="Standard")
        
        self.merge_files = []
        self.merge_output_dir = tk.StringVar()
        self.merge_output_name = tk.StringVar(value="merged.pdf")
        self.merge_rotate = tk.StringVar(value="0°")
        self.merge_rev_order = tk.BooleanVar(value=False)
        self.merge_rev_pages = tk.BooleanVar(value=False)

        self.image_files = []
        self.image_output_dir = tk.StringVar()
        self.image_temp_dir = tk.StringVar()
        self.fuzz_percent = tk.IntVar(value=10)

        self.pdf_preview = None

        self.setup_style()
        self.build_ui()
        self.apply_theme()

        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-s>", lambda e: self.run_split())
        self.root.bind("<F1>", lambda e: self.show_help())

    def setup_style(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass

        self.palette = {
            "dark": {
                "bg": "#0f172a", "panel": "#1e293b", "card": "#334155",
                "accent": "#3b82f6", "accent_hover": "#2563eb", 
                "muted": "#94a3b8", "text": "#f1f5f9"
            },
            "light": {
                "bg": "#f8fafc", "panel": "#ffffff", "card": "#f1f5f9",
                "accent": "#2563eb", "accent_hover": "#1d4ed8",
                "muted": "#64748b", "text": "#0f172a"
            }
        }
        
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Section.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Sub.TLabel", font=("Segoe UI", 11))
        self.style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=12)
        self.style.configure("Outline.TButton", font=("Segoe UI", 11), padding=8)
        self.style.configure("Card.TFrame", relief="flat")

    def build_ui(self):
        header = ttk.Frame(self.root, padding=16)
        header.pack(fill="x")
        
        ttk.Label(header, text="📑 PDF Master Pro", style="Title.TLabel").pack(side="left")
        
        self.mode_btn = ttk.Button(header, text="🌙 Dark", command=self.toggle_theme, width=12)
        self.mode_btn.pack(side="right", padx=4)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.tab_split = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_split, text="  Split PDF  ")
        self.build_split_tab()

        self.tab_merge = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_merge, text="  Merge PDFs  ")
        self.build_merge_tab()

        self.tab_images = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_images, text="  Images  ")
        self.build_image_tab()

    def build_split_tab(self):
        container = ttk.Frame(self.tab_split, padding=8)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=2)
        container.columnconfigure(1, weight=3)

        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        file_card = self.create_card(left, "📂 Input File")
        file_card.pack(fill="x", pady=(0, 10))
        
        self.file_display = ttk.Label(file_card, text="No file selected", style="Sub.TLabel")
        self.file_display.pack(anchor="w", pady=6)
        
        ttk.Button(file_card, text="Browse PDF", command=self.browse_file, style="Accent.TButton").pack(fill="x", pady=10)
        
        self.page_info = ttk.Label(file_card, text="Pages: —", style="Sub.TLabel")
        self.page_info.pack(anchor="w")

        range_card = self.create_card(left, "✂️ Split Configuration")
        range_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(range_card, text="Page ranges:", style="Sub.TLabel").pack(anchor="w", pady=6)
        
        self.range_entry = ttk.Entry(range_card, font=("Segoe UI", 11))
        self.range_entry.pack(fill="x", ipady=6)
        self.range_entry.bind("<KeyRelease>", self.on_range_key)
        
        self.range_status = ttk.Label(range_card, text="", style="Sub.TLabel")
        self.range_status.pack(anchor="w", pady=6)

        output_card = self.create_card(left, "💾 Output")
        output_card.pack(fill="x", pady=(0, 10))
        
        self.out_display = ttk.Label(output_card, text="No folder", style="Sub.TLabel")
        self.out_display.pack(anchor="w", pady=6)
        
        ttk.Button(output_card, text="Choose Folder", command=self.choose_output, style="Outline.TButton").pack(fill="x", pady=10)
        
        adv_frame = ttk.Frame(output_card)
        adv_frame.pack(fill="x")
        
        ttk.Label(adv_frame, text="Rotate:", style="Sub.TLabel").pack(side="left")
        ttk.Combobox(adv_frame, values=["0°", "90°", "180°", "270°"], textvariable=self.rotate_split, width=8, state="readonly").pack(side="left", padx=10)
        
        ttk.Label(adv_frame, text="Naming:", style="Sub.TLabel").pack(side="left", padx=(10,0))
        ttk.Combobox(adv_frame, values=["Standard", "With Timestamp"], textvariable=self.naming_pattern, width=14, state="readonly").pack(side="left", padx=10)

        action_frame = ttk.Frame(left)
        action_frame.pack(fill="x", pady=10)
        
        self.split_btn = ttk.Button(action_frame, text="Split PDF", style="Accent.TButton", command=self.run_split)
        self.split_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.split_btn.state(["disabled"])
        
        ttk.Button(action_frame, text="Reset", command=self.reset_split, style="Outline.TButton").pack(side="left")

        self.split_status = ttk.Label(left, text="Ready", style="Sub.TLabel")
        self.split_status.pack(anchor="w", pady=6)
        
        self.split_progress = ttk.Progressbar(left, mode="determinate")
        self.split_progress.pack(fill="x")

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")

        preview_card = self.create_card(right, "📄 Preview")
        preview_card.pack(fill="both", expand=True)
        
        self.pdf_preview = PDFPreview(preview_card)
        self.pdf_preview.frame.pack(fill="both", expand=True, pady=6)

    def build_merge_tab(self):
        container = ttk.Frame(self.tab_merge, padding=8)
        container.pack(fill="both", expand=True)

        files_card = self.create_card(container, "📑 PDFs to Merge")
        files_card.pack(fill="both", expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(files_card)
        list_frame.pack(fill="both", expand=True, pady=6)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, height=12, font=("Segoe UI", 11),
                                   bg="#1e293b", fg="#f1f5f9", selectbackground="#3b82f6",
                                   relief="flat", yscrollcommand=scrollbar.set)
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        btn_row = ttk.Frame(files_card)
        btn_row.pack(fill="x", pady=10)
        
        ttk.Button(btn_row, text="Add Images", command=self.image_add, width=12).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Remove", command=self.image_remove, width=10).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", command=self.image_clear, width=8).pack(side="left", padx=3)
        
        settings_row = ttk.Frame(container)
        settings_row.pack(fill="x")
        settings_row.columnconfigure(0, weight=1)
        settings_row.columnconfigure(1, weight=1)
        
        settings_card = self.create_card(settings_row, "⚙️ Settings")
        settings_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        
        ttk.Label(settings_card, text="Background Sensitivity:", style="Sub.TLabel").pack(anchor="w", pady=6)
        
        fuzz_control = ttk.Frame(settings_card)
        fuzz_control.pack(fill="x")
        ttk.Label(fuzz_control, text="Low").pack(side="left")
        fuzz_scale = ttk.Scale(fuzz_control, from_=5, to=25, variable=self.fuzz_percent, orient="horizontal")
        fuzz_scale.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(fuzz_control, text="High").pack(side="right")
        
        self.fuzz_label = ttk.Label(settings_card, text="Fuzz: 10%", style="Sub.TLabel")
        self.fuzz_label.pack(anchor="w", pady=6)
        fuzz_scale.config(command=self.update_fuzz_label)
        
        output_card = self.create_card(settings_row, "💾 Folders")
        output_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        
        ttk.Label(output_card, text="Output:", style="Sub.TLabel").pack(anchor="w")
        self.image_out_lbl = ttk.Label(output_card, text="Not selected", style="Sub.TLabel")
        self.image_out_lbl.pack(anchor="w", pady=4)
        ttk.Button(output_card, text="Choose Output", command=self.image_choose_output, style="Outline.TButton").pack(fill="x", pady=8)
        
        ttk.Label(output_card, text="Temp:", style="Sub.TLabel").pack(anchor="w")
        self.image_temp_lbl = ttk.Label(output_card, text="Not selected", style="Sub.TLabel")
        self.image_temp_lbl.pack(anchor="w", pady=4)
        ttk.Button(output_card, text="Choose Temp", command=self.image_choose_temp, style="Outline.TButton").pack(fill="x")
        
        action_row = ttk.Frame(container)
        action_row.pack(fill="x", pady=10)
        
        self.process_btn = ttk.Button(action_row, text="Process Images", style="Accent.TButton", command=self.run_image_processing)
        self.process_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.process_btn.state(["disabled"])
        
        ttk.Button(action_row, text="Reset", command=self.image_reset, style="Outline.TButton").pack(side="left")
        
        self.image_status = ttk.Label(container, text="Ready", style="Sub.TLabel")
        self.image_status.pack(anchor="w", pady=6)
        self.image_progress = ttk.Progressbar(container, mode="determinate")
        self.image_progress.pack(fill="x")

    def create_card(self, parent, title):
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        if title:
            ttk.Label(card, text=title, style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        return card

    def apply_theme(self):
        pal = self.palette["dark" if self.dark else "light"]
        self.root.configure(bg=pal["bg"])
        
        self.style.configure("TFrame", background=pal["panel"])
        self.style.configure("Card.TFrame", background=pal["card"])
        self.style.configure("TLabel", background=pal["panel"], foreground=pal["text"])
        self.style.configure("Section.TLabel", background=pal["card"], foreground=pal["text"])
        self.style.configure("Sub.TLabel", background=pal["card"], foreground=pal["muted"])
        
        self.style.configure("TButton", background=pal["panel"], foreground=pal["text"])
        self.style.configure("Accent.TButton", background=pal["accent"], foreground="#ffffff")
        self.style.map("Accent.TButton", background=[("active", pal["accent_hover"])])
        self.style.configure("Outline.TButton", background=pal["card"], foreground=pal["text"])
        self.style.map("Outline.TButton", background=[("active", pal["accent"])])
        
        try:
            self.style.configure("TNotebook", background=pal["bg"])
            self.style.configure("TNotebook.Tab", background=pal["panel"], foreground=pal["text"])
        except:
            pass
        
        self.mode_btn.config(text=("☀️ Light" if self.dark else "🌙 Dark"))
        
        if hasattr(self, 'listbox'):
            self.listbox.config(bg=pal["card"], fg=pal["text"], selectbackground=pal["accent"])
        
        if hasattr(self, 'image_listbox'):
            self.image_listbox.config(bg=pal["card"], fg=pal["text"], selectbackground=pal["accent"])
        
        if self.pdf_preview:
            self.pdf_preview.canvas.config(bg=pal["card"])

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme()

    def browse_file(self):
        fp = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files", "*.pdf")])
        if not fp:
            return
        
        self.file_path.set(fp)
        self.file_display.config(text=f"📄 {os.path.basename(fp)}")
        
        try:
            reader = PdfReader(fp)
            total = len(reader.pages)
            self.total_pages.set(total)
            self.page_info.config(text=f"Pages: {total}")
            
            self.split_status.config(text="Loading preview...")
            self.root.update_idletasks()
            
            if self.pdf_preview.load_pdf(fp, lambda msg: self.split_status.config(text=msg)):
                self.pdf_preview.show_pages()
                self.split_status.config(text="Preview loaded")
            else:
                self.split_status.config(text="Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read PDF:\n{str(e)}")
            self.total_pages.set(0)
            self.page_info.config(text="Pages: —")
        
        self.on_range_key()

    def choose_output(self):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d:
            self.output_dir.set(d)
            self.out_display.config(text=f"📂 {os.path.basename(d)}")
            self.update_split_enabled()

    def on_range_key(self, e=None):
        txt = self.range_entry.get().strip()
        total = self.total_pages.get()
        
        if not txt:
            self.range_status.config(text="Enter ranges like 1-4,5-8")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages()
            self.update_split_enabled()
            return
        
        ranges, invalid = parse_ranges(txt, total_pages=total)
        
        if invalid:
            self.range_status.config(text=f"Invalid: {', '.join(invalid)}")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages()
        elif not ranges:
            self.range_status.config(text="No valid ranges")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages()
        else:
            total_pages = sum((b - a + 1) for a, b in ranges)
            self.range_status.config(text=f"✅ {len(ranges)} files • {total_pages} pages")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages(ranges)
        
        self.update_split_enabled()

    def update_split_enabled(self):
        has_file = bool(self.file_path.get())
        has_output = bool(self.output_dir.get())
        txt = self.range_entry.get().strip()
        
        if not has_file or not has_output or not txt:
            self.split_btn.state(["disabled"])
            return
        
        ranges, invalid = parse_ranges(txt, total_pages=self.total_pages.get())
        
        if ranges and not invalid:
            self.split_btn.state(["!disabled"])
        else:
            self.split_btn.state(["disabled"])

    def run_split(self):
        if self.split_btn.instate(["disabled"]):
            return
        
        txt = self.range_entry.get().strip()
        ranges, invalid = parse_ranges(txt, total_pages=self.total_pages.get())
        
        if invalid:
            messagebox.showerror("Invalid Ranges", f"Fix: {', '.join(invalid)}")
            return
        
        try:
            self.split_status.config(text="Splitting...")
            self.split_progress["maximum"] = len(ranges)
            self.split_progress["value"] = 0
            self.split_btn.state(["disabled"])
            self.root.update_idletasks()

            def on_progress(done, total):
                self.split_progress["value"] = done
                self.split_status.config(text=f"Splitting {done}/{total}")
                self.root.update_idletasks()

            rot_str = self.rotate_split.get().replace("°", "").strip()
            rotate = int(rot_str) if rot_str.isdigit() else 0
            
            naming = "timestamp" if self.naming_pattern.get() == "With Timestamp" else "split"

            output_files = split_pdf(self.file_path.get(), ranges, self.output_dir.get(),
                                    rotate=rotate, naming_pattern=naming, on_progress=on_progress)
            
            self.split_status.config(text=f"✅ Created {len(output_files)} files")
            
            msg = f"Split into {len(output_files)} files!\n\nOutput: {self.output_dir.get()}"
            messagebox.showinfo("Success", msg)
            
        except Exception as e:
            self.split_status.config(text="❌ Error")
            messagebox.showerror("Error", str(e))
        finally:
            self.split_btn.state(["!disabled"])

    def reset_split(self):
        self.file_path.set("")
        self.output_dir.set("")
        self.file_display.config(text="No file selected")
        self.out_display.config(text="No folder")
        self.page_info.config(text="Pages: —")
        self.range_entry.delete(0, tk.END)
        self.range_status.config(text="")
        self.split_status.config(text="Ready")
        self.split_progress["value"] = 0
        self.rotate_split.set("0°")
        self.naming_pattern.set("Standard")
        if self.pdf_preview:
            self.pdf_preview.clear()
        self.update_split_enabled()

    def merge_add(self):
        paths = filedialog.askopenfilenames(title="Select PDFs", filetypes=[("PDF files", "*.pdf")])
        if not paths:
            return
        
        added = 0
        for p in paths:
            if p not in self.merge_files:
                self.merge_files.append(p)
                self.listbox.insert(tk.END, f"📄 {os.path.basename(p)}")
                added += 1
        
        if added > 0:
            self.merge_status.config(text=f"Added {added} file(s)")
        
        self.update_merge_enabled()

    def merge_remove(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        
        i = sel[0]
        del self.merge_files[i]
        self.listbox.delete(i)
        self.update_merge_enabled()

    def merge_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        
        i = sel[0]
        self.merge_files[i-1], self.merge_files[i] = self.merge_files[i], self.merge_files[i-1]
        
        a, b = self.listbox.get(i), self.listbox.get(i-1)
        self.listbox.delete(i)
        self.listbox.delete(i-1)
        self.listbox.insert(i-1, a)
        self.listbox.insert(i, b)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(i-1)

    def merge_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == self.listbox.size() - 1:
            return
        
        i = sel[0]
        self.merge_files[i+1], self.merge_files[i] = self.merge_files[i], self.merge_files[i+1]
        
        a, b = self.listbox.get(i), self.listbox.get(i+1)
        self.listbox.delete(i+1)
        self.listbox.delete(i)
        self.listbox.insert(i, b)
        self.listbox.insert(i+1, a)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(i+1)

    def merge_clear(self):
        if self.merge_files:
            if messagebox.askyesno("Clear", "Remove all files?"):
                self.listbox.delete(0, tk.END)
                self.merge_files.clear()
                self.update_merge_enabled()

    def merge_choose_out(self):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d:
            self.merge_output_dir.set(d)
            self.merge_out_lbl.config(text=f"📂 {d}")
            self.update_merge_enabled()

    def update_merge_enabled(self):
        has_files = len(self.merge_files) >= 2
        has_output = bool(self.merge_output_dir.get())
        
        if has_files and has_output:
            self.merge_btn.state(["!disabled"])
        else:
            self.merge_btn.state(["disabled"])

    def run_merge(self):
        if self.merge_btn.instate(["disabled"]):
            return
        
        out_name = self.merge_output_name.get().strip() or "merged.pdf"
        if not out_name.endswith(".pdf"):
            out_name += ".pdf"
        
        out_path = os.path.join(self.merge_output_dir.get(), out_name)
        
        if os.path.exists(out_path):
            if not messagebox.askyesno("File Exists", f"Overwrite '{out_name}'?"):
                return
        
        try:
            self.merge_status.config(text="Merging...")
            self.merge_progress["maximum"] = len(self.merge_files)
            self.merge_progress["value"] = 0
            self.merge_btn.state(["disabled"])
            self.root.update_idletasks()

            def on_progress(done, total):
                self.merge_progress["value"] = done
                self.merge_status.config(text=f"Merging {done}/{total}")
                self.root.update_idletasks()

            rot_str = self.merge_rotate.get().replace("°", "").strip()
            rotate = int(rot_str) if rot_str.isdigit() else 0

            merge_pdfs(self.merge_files, out_path,
                      reverse_order=self.merge_rev_order.get(),
                      reverse_pages_each=self.merge_rev_pages.get(),
                      rotate=rotate, on_progress=on_progress)
            
            self.merge_status.config(text=f"✅ Success!")
            messagebox.showinfo("Success", f"Merged to:\n{out_path}")
            
        except Exception as e:
            self.merge_status.config(text="❌ Error")
            messagebox.showerror("Error", str(e))
        finally:
            self.merge_btn.state(["!disabled"])

    def merge_reset(self):
        if self.merge_files:
            self.listbox.delete(0, tk.END)
            self.merge_files.clear()
        self.merge_output_dir.set("")
        self.merge_output_name.set("merged.pdf")
        self.merge_out_lbl.config(text="No folder")
        self.merge_rotate.set("0°")
        self.merge_rev_order.set(False)
        self.merge_rev_pages.set(False)
        self.merge_status.config(text="Ready")
        self.merge_progress["value"] = 0

    def image_add(self):
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"), ("All", "*.*")]
        )
        if not paths:
            return
        
        added = 0
        for p in paths:
            if p not in self.image_files:
                self.image_files.append(p)
                self.image_listbox.insert(tk.END, f"🖼️ {os.path.basename(p)}")
                added += 1
        
        if added > 0:
            self.image_status.config(text=f"Added {added} image(s)")
        
        self.update_image_enabled()
    
    def image_remove(self):
        sel = self.image_listbox.curselection()
        if not sel:
            return
        
        i = sel[0]
        del self.image_files[i]
        self.image_listbox.delete(i)
        self.update_image_enabled()
    
    def image_clear(self):
        if self.image_files:
            if messagebox.askyesno("Clear", "Remove all images?"):
                self.image_listbox.delete(0, tk.END)
                self.image_files.clear()
                self.update_image_enabled()
    
    def image_choose_output(self):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d:
            self.image_output_dir.set(d)
            self.image_out_lbl.config(text=f"📂 {d}")
            self.update_image_enabled()
    
    def image_choose_temp(self):
        d = filedialog.askdirectory(title="Select Temp Folder")
        if d:
            self.image_temp_dir.set(d)
            self.image_temp_lbl.config(text=f"📂 {d}")
            self.update_image_enabled()
    
    def update_fuzz_label(self, value):
        fuzz_val = int(float(value))
        self.fuzz_percent.set(fuzz_val)
        self.fuzz_label.config(text=f"Fuzz: {fuzz_val}%")
    
    def update_image_enabled(self):
        has_images = len(self.image_files) > 0
        has_output = bool(self.image_output_dir.get())
        has_temp = bool(self.image_temp_dir.get())
        
        if has_images and has_output and has_temp:
            self.process_btn.state(["!disabled"])
        else:
            self.process_btn.state(["disabled"])
    
    def run_image_processing(self):
        if self.process_btn.instate(["disabled"]):
            return
        
        try:
            self.image_status.config(text="Processing...")
            self.image_progress["maximum"] = len(self.image_files)
            self.image_progress["value"] = 0
            self.process_btn.state(["disabled"])
            self.root.update_idletasks()
            
            def on_progress(current, total, filename):
                self.image_progress["value"] = current
                self.image_status.config(text=f"Processing {current}/{total}")
                self.root.update_idletasks()
            
            success_count, failed_files = batch_process_images(
                self.image_files, self.image_output_dir.get(),
                self.image_temp_dir.get(), fuzz_percent=self.fuzz_percent.get(),
                on_progress=on_progress
            )
            
            self.image_status.config(text=f"✅ Processed {success_count}/{len(self.image_files)}")
            
            msg = f"Processed {success_count}/{len(self.image_files)} images!"
            if failed_files:
                msg += f"\n\nFailed: {len(failed_files)}"
            
            messagebox.showinfo("Complete", msg)
            
        except Exception as e:
            self.image_status.config(text="❌ Error")
            messagebox.showerror("Error", str(e))
        finally:
            self.process_btn.state(["!disabled"])
    
    def image_reset(self):
        if self.image_files:
            self.image_listbox.delete(0, tk.END)
            self.image_files.clear()
        self.image_output_dir.set("")
        self.image_temp_dir.set("")
        self.image_out_lbl.config(text="Not selected")
        self.image_temp_lbl.config(text="Not selected")
        self.fuzz_percent.set(10)
        self.fuzz_label.config(text="Fuzz: 10%")
        self.image_status.config(text="Ready")
        self.image_progress["value"] = 0
        self.update_image_enabled()

    def show_help(self):
        help_text = """PDF MASTER PRO

SPLIT PDF:
1. Browse for PDF
2. Enter ranges: 1-5,10-15
3. Choose output folder
4. Click Split

MERGE PDFs:
1. Add multiple PDFs
2. Reorder with arrows
3. Choose output folder
4. Click Merge

IMAGE PROCESSING:
1. Add images
2. Choose output & temp folders
3. Adjust fuzz (5-25%)
4. Click Process

SHORTCUTS:
Ctrl+O: Browse
Ctrl+S: Split
F1: Help"""
        
        messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolApp(root)
    root.mainloop()Add", command=self.merge_add, width=8).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Remove", command=self.merge_remove, width=10).pack(side="left", padx=3)
        ttk.Button(btn_row, text="⬆️", command=self.merge_up, width=4).pack(side="left", padx=3)
        ttk.Button(btn_row, text="⬇️", command=self.merge_down, width=4).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", command=self.merge_clear, width=8).pack(side="left", padx=3)

        bottom_row = ttk.Frame(container)
        bottom_row.pack(fill="x")
        bottom_row.columnconfigure(0, weight=1)
        bottom_row.columnconfigure(1, weight=1)

        opt_card = self.create_card(bottom_row, "⚙️ Options")
        opt_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        
        ttk.Checkbutton(opt_card, text="Reverse file order", variable=self.merge_rev_order).pack(anchor="w", pady=4)
        ttk.Checkbutton(opt_card, text="Reverse pages", variable=self.merge_rev_pages).pack(anchor="w", pady=4)
        
        rot_frame = ttk.Frame(opt_card)
        rot_frame.pack(fill="x", pady=6)
        ttk.Label(rot_frame, text="Rotate:", style="Sub.TLabel").pack(side="left")
        ttk.Combobox(rot_frame, values=["0°", "90°", "180°", "270°"], textvariable=self.merge_rotate, width=8, state="readonly").pack(side="left", padx=10)

        out_card = self.create_card(bottom_row, "💾 Output")
        out_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        
        self.merge_out_lbl = ttk.Label(out_card, text="No folder", style="Sub.TLabel")
        self.merge_out_lbl.pack(anchor="w", pady=6)
        
        ttk.Button(out_card, text="Choose Folder", command=self.merge_choose_out, style="Outline.TButton").pack(fill="x", pady=10)
        
        name_row = ttk.Frame(out_card)
        name_row.pack(fill="x", pady=3)
        ttk.Label(name_row, text="Name:", style="Sub.TLabel").pack(side="left")
        ttk.Entry(name_row, textvariable=self.merge_output_name, width=18).pack(side="left", padx=8, fill="x", expand=True)

        action_row = ttk.Frame(container)
        action_row.pack(fill="x", pady=10)
        
        self.merge_btn = ttk.Button(action_row, text="Merge PDFs", style="Accent.TButton", command=self.run_merge)
        self.merge_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.merge_btn.state(["disabled"])
        
        ttk.Button(action_row, text="Reset", command=self.merge_reset, style="Outline.TButton").pack(side="left")

        self.merge_status = ttk.Label(container, text="Ready", style="Sub.TLabel")
        self.merge_status.pack(anchor="w", pady=6)
        self.merge_progress = ttk.Progressbar(container, mode="determinate")
        self.merge_progress.pack(fill="x")

    def build_image_tab(self):
        container = ttk.Frame(self.tab_images, padding=8)
        container.pack(fill="both", expand=True)
        
        if not check_imagemagick():
            warning_card = self.create_card(container, "⚠️ ImageMagick Required")
            warning_card.pack(fill="x")
            ttk.Label(warning_card, text="Install ImageMagick from:\nhttps://imagemagick.org/", 
                     style="Sub.TLabel", justify="left").pack(pady=10)
            return
        
        files_card = self.create_card(container, "🖼️ Images")
        files_card.pack(fill="both", expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(files_card)
        list_frame.pack(fill="both", expand=True, pady=6)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.image_listbox = tk.Listbox(list_frame, height=12, font=("Segoe UI", 11),
                                        bg="#1e293b", fg="#f1f5f9", selectbackground="#3b82f6",
                                        relief="flat", yscrollcommand=scrollbar.set)
        self.image_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        btn_row = ttk.Frame(files_card)
        btn_row.pack(fill="x", pady=10)
        
        ttk.Button(btn_row, text="
