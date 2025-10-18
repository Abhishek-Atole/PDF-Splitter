import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os
from datetime import datetime
import subprocess
import shutil
from pathlib import Path
from io import BytesIO

try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageTk
    PREVIEW_AVAILABLE = True
except ImportError:
    PREVIEW_AVAILABLE = False


def _rotate_page_obj(page, degrees):
    """Rotate a PyPDF2 PageObject by degrees in a robust way supporting multiple PyPDF2 versions."""
    if not degrees or degrees % 360 == 0:
        return page
    try:
        if hasattr(page, "rotate"):
            try:
                page.rotate(degrees)
                return page
            except TypeError:
                pass
        if hasattr(page, "rotate_clockwise"):
            return page.rotate_clockwise(degrees)
        if hasattr(page, "rotateCounterClockwise"):
            return page.rotateCounterClockwise(degrees)
        if hasattr(page, "rotate_counter_clockwise"):
            return page.rotate_counter_clockwise(360 - degrees)
    except Exception:
        return page
    return page


def check_imagemagick():
    try:
        result = subprocess.run(['convert', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def process_image(input_path, output_path, temp_dir, fuzz_percent=10, on_progress=None):
    temp_jpg = None
    try:
        input_file = Path(input_path)
        output_file = Path(output_path)
        temp_dir_path = Path(temp_dir)
        temp_dir_path.mkdir(parents=True, exist_ok=True)
        temp_jpg = temp_dir_path / f"{input_file.stem}.jpg"

        if input_file.suffix.lower() in ['.jpg', '.jpeg']:
            shutil.copy(input_file, temp_jpg)
        else:
            cmd = ['convert', str(input_file), str(temp_jpg)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, "Conversion failed"

        cmd = ['convert', str(temp_jpg), '-fuzz', f'{fuzz_percent}%', '-transparent', 'white',
               '-auto-level', '-contrast', '-sharpen', '0x1', str(output_file)]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False, "Processing failed"

        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if temp_jpg and temp_jpg.exists():
            try:
                temp_jpg.unlink()
            except Exception:
                pass

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
    os.makedirs(output_dir, exist_ok=True)

    for i, (start, end) in enumerate(ranges):
        if start < 1 or end > total or start > end:
            raise ValueError(f"Range {start}-{end} out of bounds")
        
        writer = PdfWriter()
        for p in range(start - 1, end):
            page = reader.pages[p]
            if rotate in (90, 180, 270):
                page = _rotate_page_obj(page, rotate)
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
    temp_streams = []
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    for idx, fp in enumerate(files):
        reader = PdfReader(fp)
        pages = list(reader.pages)

        if reverse_pages_each:
            pages = list(reversed(pages))

        needs_writer = rotate in (90, 180, 270) or reverse_pages_each

        if needs_writer:
            temp_writer = PdfWriter()
            for page in pages:
                if rotate in (90, 180, 270):
                    page = _rotate_page_obj(page, rotate)
                temp_writer.add_page(page)
            bio = BytesIO()
            temp_writer.write(bio)
            bio.seek(0)
            merger.append(bio)
            temp_streams.append(bio)
        else:
            merger.append(fp)

        if on_progress:
            on_progress(idx + 1, len(files))

    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()
    for stream in temp_streams:
        try:
            stream.close()
        except Exception:
            pass

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
        lbl = tk.Label(self.tip, text=self.text, bg="#2d2d30", fg="#e8e8e8",
                       padx=12, pady=8, font=("Segoe UI", 9), borderwidth=0)
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
        
        self.canvas = tk.Canvas(canvas_frame, bg="#1f1f23", highlightthickness=0, relief="flat")
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
                self.frame.after(1, lambda: status_callback("Loading PDF..."))

            self.all_images = convert_from_path(pdf_path, dpi=72)

            if status_callback:
                self.frame.after(1, lambda: status_callback(f"Loaded {len(self.all_images)} pages"))

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
        
        try:
            img = self.all_images[page_idx]
        except (IndexError, AttributeError):
            self.show_message("Failed to load page image")
            return
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 600
        
        img_width, img_height = img.size
        scale = min(canvas_width * 0.95 / img_width, 800 / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.LANCZOS
        
        img_resized = img.resize((new_width, new_height), resample_method)
        self.photo = ImageTk.PhotoImage(img_resized)

        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, 10, anchor="n", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, canvas_width, new_height + 20))

        actual_page = page_idx + 1
        total_pages = len(self.all_images)
        self.page_label.config(text=f"Page {actual_page} of {total_pages} ({self.current_page_in_range + 1}/{len(self.current_pages)})")
    
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
        self.canvas.create_text(w // 2, h // 2, text=message, fill="#7a7a80",
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
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 700)

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

        # Bind resize events for responsiveness
        self.root.bind("<Configure>", self.on_window_resize)

        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-s>", lambda e: self.run_split())
        self.root.bind("<F1>", lambda e: self.show_help())

    def setup_style(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass

        # Windows 11 Fluent Design colors
        self.palette = {
            "dark": {
                "bg": "#1f1f23",           # Dark background
                "panel": "#2d2d30",         # Panel background
                "card": "#3e3e42",          # Card background
                "card_hover": "#4a4a50",   # Card hover
                "accent": "#0078d4",        # Windows blue
                "accent_hover": "#0063b1",  # Darker blue
                "accent_light": "#005a9e", # Light accent
                "border": "#3f3f46",        # Border color
                "text": "#ffffff",          # Main text
                "text_muted": "#b4b4b8",   # Muted text
                "success": "#107c10",       # Success green
                "error": "#e81123",         # Error red
            },
            "light": {
                "bg": "#ffffff",
                "panel": "#f3f3f3",
                "card": "#fafafa",
                "card_hover": "#e8e8e8",
                "accent": "#0078d4",
                "accent_hover": "#0063b1",
                "accent_light": "#005a9e",
                "border": "#e1e1e1",
                "text": "#000000",
                "text_muted": "#717171",
                "success": "#107c10",
                "error": "#e81123",
            }
        }
        
        # Configure styles
        self.style.configure("TFrame", background="#2d2d30", relief="flat", borderwidth=0)
        self.style.configure("TLabel", background="#2d2d30", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#ffffff")
        self.style.configure("Section.TLabel", font=("Segoe UI", 13, "bold"), foreground="#ffffff")
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#b4b4b8")
        
        self.style.configure("TButton", font=("Segoe UI", 10), padding=10)
        self.style.map("TButton",
                      foreground=[("active", "#ffffff")],
                      background=[("active", "#0063b1")])
        
        self.style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=12)
        self.style.configure("Outline.TButton", font=("Segoe UI", 10), padding=8)
        
        self.style.configure("Card.TFrame", relief="flat", background="#3e3e42", borderwidth=1)
        self.style.configure("TNotebook", background="#2d2d30", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(15, 8))
        self.style.configure("Treeview", background="#3e3e42", foreground="#ffffff", fieldbackground="#3e3e42")

    def build_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding=0)
        main_container.pack(fill="both", expand=True)

        # Header
        header = ttk.Frame(main_container, padding=16)
        header.pack(fill="x", padx=0, pady=0)
        header.configure(bg="#2d2d30")
        
        title_frame = ttk.Frame(header)
        title_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(title_frame, text="📑 PDF Master Pro", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_frame, text="Professional PDF manipulation tool", style="Sub.TLabel").pack(anchor="w", pady=(4, 0))
        
        self.mode_btn = ttk.Button(header, text="🌙 Dark Mode", command=self.toggle_theme, width=15)
        self.mode_btn.pack(side="right", padx=4)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)

        self.tab_split = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_split, text="  ✂️  Split PDF  ")
        self.build_split_tab()

        self.tab_merge = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_merge, text="  🔗  Merge PDFs  ")
        self.build_merge_tab()

        self.tab_images = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_images, text="  🖼️  Images  ")
        self.build_image_tab()

    def build_split_tab(self):
        container = ttk.Frame(self.tab_split, padding=8)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=2, minsize=300)
        container.columnconfigure(1, weight=3, minsize=400)
        container.rowconfigure(0, weight=1)

        # Left panel
        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)

        # File selection card
        file_card = self.create_card(left, "📂 Input File")
        file_card.pack(fill="x", pady=(0, 10))
        
        self.file_display = ttk.Label(file_card, text="No file selected", style="Sub.TLabel", wraplength=280)
        self.file_display.pack(anchor="w", pady=6, padx=10)
        
        ttk.Button(file_card, text="Browse PDF", command=self.browse_file).pack(fill="x", pady=10, padx=10)
        
        self.page_info = ttk.Label(file_card, text="Pages: —", style="Sub.TLabel")
        self.page_info.pack(anchor="w", padx=10)

        # Range card
        range_card = self.create_card(left, "✂️  Split Configuration")
        range_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(range_card, text="Page ranges:", style="Sub.TLabel").pack(anchor="w", pady=(6, 3), padx=10)
        
        self.range_entry = ttk.Entry(range_card, font=("Segoe UI", 10))
        self.range_entry.pack(fill="x", ipady=6, padx=10)
        self.range_entry.bind("<KeyRelease>", self.on_range_key)
        
        self.range_status = ttk.Label(range_card, text="", style="Sub.TLabel")
        self.range_status.pack(anchor="w", pady=(6, 10), padx=10)

        # Output card
        output_card = self.create_card(left, "💾 Output Settings")
        output_card.pack(fill="x", pady=(0, 10))
        
        self.out_display = ttk.Label(output_card, text="No folder selected", style="Sub.TLabel", wraplength=280)
        self.out_display.pack(anchor="w", pady=6, padx=10)
        
        ttk.Button(output_card, text="Choose Folder", command=self.choose_output).pack(fill="x", pady=10, padx=10)
        
        adv_frame = ttk.Frame(output_card)
        adv_frame.pack(fill="x", padx=10, pady=(0, 10))
        adv_frame.columnconfigure(1, weight=1)
        adv_frame.columnconfigure(3, weight=1)
        
        ttk.Label(adv_frame, text="Rotate:", style="Sub.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Combobox(adv_frame, values=["0°", "90°", "180°", "270°"], textvariable=self.rotate_split, width=8, state="readonly").grid(row=0, column=1, sticky="ew", padx=(10, 20))
        
        ttk.Label(adv_frame, text="Naming:", style="Sub.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Combobox(adv_frame, values=["Standard", "With Timestamp"], textvariable=self.naming_pattern, width=14, state="readonly").grid(row=0, column=3, sticky="ew")

        # Action buttons
        action_frame = ttk.Frame(left)
        action_frame.pack(fill="x", pady=10)
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        self.split_btn = ttk.Button(action_frame, text="Split PDF", command=self.run_split)
        self.split_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.split_btn.state(["disabled"])
        
        ttk.Button(action_frame, text="Reset", command=self.reset_split).grid(row=0, column=1, sticky="ew")

        self.split_status = ttk.Label(left, text="Ready", style="Sub.TLabel")
        self.split_status.pack(anchor="w", pady=6)
        
        self.split_progress = ttk.Progressbar(left, mode="determinate", length=250)
        self.split_progress.pack(fill="x")

        # Right panel - Preview
        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")

        preview_card = self.create_card(right, "📄 PDF Preview")
        preview_card.pack(fill="both", expand=True)
        
        self.pdf_preview = PDFPreview(preview_card)
        self.pdf_preview.frame.pack(fill="both", expand=True, pady=6, padx=6)

    def build_merge_tab(self):
        container = ttk.Frame(self.tab_merge, padding=8)
        container.pack(fill="both", expand=True)

        files_card = self.create_card(container, "📑 PDFs to Merge")
        files_card.pack(fill="both", expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(files_card)
        list_frame.pack(fill="both", expand=True, pady=6, padx=6)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, height=12, font=("Segoe UI", 10),
                                   bg="#3e3e42", fg="#ffffff", selectbackground="#0078d4",
                                   relief="flat", yscrollcommand=scrollbar.set, bd=0)
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        btn_row = ttk.Frame(files_card)
        btn_row.pack(fill="x", pady=10, padx=6)
        
        ttk.Button(btn_row, text="Add", command=self.merge_add, width=8).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Remove", command=self.merge_remove, width=10).pack(side="left", padx=3)
        ttk.Button(btn_row, text="⬆️", command=self.merge_up, width=4).pack(side="left", padx=3)
        ttk.Button(btn_row, text="⬇️", command=self.merge_down, width=4).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", command=self.merge_clear, width=8).pack(side="left", padx=3)

        bottom_row = ttk.Frame(container)
        bottom_row.pack(fill="x")
        bottom_row.columnconfigure(0, weight=1)
        bottom_row.columnconfigure(1, weight=1)

        opt_card = self.create_card(bottom_row, "⚙️  Options")
        opt_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        
        ttk.Checkbutton(opt_card, text="Reverse file order", variable=self.merge_rev_order).pack(anchor="w", pady=4, padx=10)
        ttk.Checkbutton(opt_card, text="Reverse pages", variable=self.merge_rev_pages).pack(anchor="w", pady=4, padx=10)
        
        rot_frame = ttk.Frame(opt_card)
        rot_frame.pack(fill="x", pady=6, padx=10)
        ttk.Label(rot_frame, text="Rotate:", style="Sub.TLabel").pack(side="left")
        ttk.Combobox(rot_frame, values=["0°", "90°", "180°", "270°"], textvariable=self.merge_rotate, width=8, state="readonly").pack(side="left", padx=10)

        out_card = self.create_card(bottom_row, "💾 Output")
        out_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        
        self.merge_out_lbl = ttk.Label(out_card, text="No folder selected", style="Sub.TLabel", wraplength=280)
        self.merge_out_lbl.pack(anchor="w", pady=6, padx=10)
        
        ttk.Button(out_card, text="Choose Folder", command=self.merge_choose_out).pack(fill="x", pady=10, padx=10)
        
        name_row = ttk.Frame(out_card)
        name_row.pack(fill="x", pady=(0, 10), padx=10)
        ttk.Label(name_row, text="Name:", style="Sub.TLabel").pack(side="left")
        ttk.Entry(name_row, textvariable=self.merge_output_name, width=18).pack(side="left", padx=8, fill="x", expand=True)

        action_row = ttk.Frame(container)
        action_row.pack(fill="x", pady=10)
        action_row.columnconfigure(0, weight=1)
        action_row.columnconfigure(1, weight=1)
        
        self.merge_btn = ttk.Button(action_row, text="Merge PDFs", command=self.run_merge)
        self.merge_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.merge_btn.state(["disabled"])
        
        ttk.Button(action_row, text="Reset", command=self.merge_reset).grid(row=0, column=1, sticky="ew")

        self.merge_status = ttk.Label(container, text="Ready", style="Sub.TLabel")
        self.merge_status.pack(anchor="w", pady=6)
        self.merge_progress = ttk.Progressbar(container, mode="determinate")
        self.merge_progress.pack(fill="x")

    def build_image_tab(self):
        container = ttk.Frame(self.tab_images, padding=8)
        container.pack(fill="both", expand=True)
        
        if not check_imagemagick():
            warning_card = self.create_card(container, "⚠️  ImageMagick Required")
            warning_card.pack(fill="x")
            ttk.Label(warning_card, text="Install ImageMagick from:\nhttps://imagemagick.org/", 
                     style="Sub.TLabel", justify="left").pack(pady=10, padx=10)
            return
        
        files_card = self.create_card(container, "🖼️  Images")
        files_card.pack(fill="both", expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(files_card)
        list_frame.pack(fill="both", expand=True, pady=6, padx=6)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.image_listbox = tk.Listbox(list_frame, height=12, font=("Segoe UI", 10),
                                        bg="#3e3e42", fg="#ffffff", selectbackground="#0078d4",
                                        relief="flat", yscrollcommand=scrollbar.set, bd=0)
        self.image_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        btn_row = ttk.Frame(files_card)
        btn_row.pack(fill="x", pady=10, padx=6)
        
        ttk.Button(btn_row, text="Add", command=self.image_add, width=8).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Remove", command=self.image_remove, width=10).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", command=self.image_clear, width=8).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Choose Output", command=self.image_choose_out, width=12).pack(side="left", padx=3)

        out_frame = ttk.Frame(files_card)
        out_frame.pack(fill="x", pady=8, padx=6)
        ttk.Label(out_frame, text="Temp dir:", style="Sub.TLabel").pack(side="left")
        ttk.Entry(out_frame, textvariable=self.image_temp_dir).pack(side="left", padx=6, fill="x", expand=True)
        ttk.Button(out_frame, text="Browse", command=self.image_choose_temp, width=10).pack(side="left", padx=6)

        proc_row = ttk.Frame(container)
        proc_row.pack(fill="x", pady=10)
        ttk.Label(proc_row, text="Fuzz %:", style="Sub.TLabel").pack(side="left")
        ttk.Entry(proc_row, textvariable=self.fuzz_percent, width=6).pack(side="left", padx=6)
        ttk.Button(proc_row, text="Process Images", command=self.run_image_process).pack(side="left", padx=6)
        ttk.Button(proc_row, text="Reset", command=self.image_reset).pack(side="left")

        self.image_status = ttk.Label(container, text="Ready", style="Sub.TLabel")
        self.image_status.pack(anchor="w", pady=6)
        self.image_progress = ttk.Progressbar(container, mode="determinate")
        self.image_progress.pack(fill="x")

    def create_card(self, parent, title):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(frame, text=title, style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        return frame

    def choose_output(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.output_dir.set(d)
            self.out_display.config(text=d)
            self.on_range_key()

    def browse_file(self):
        fp = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF files","*.pdf")])
        if not fp:
            return
        self.file_path.set(fp)
        display_name = os.path.basename(fp)
        self.file_display.config(text=display_name)
        try:
            reader = PdfReader(fp)
            self.total_pages.set(len(reader.pages))
            self.page_info.config(text=f"Pages: {len(reader.pages)}")
            if self.pdf_preview and PREVIEW_AVAILABLE:
                self.pdf_preview.load_pdf(fp)
                self.pdf_preview.show_pages()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")

    def on_range_key(self, event=None):
        s = self.range_entry.get()
        ranges, invalid = parse_ranges(s, total_pages=self.total_pages.get() or None)
        if invalid:
            self.range_status.config(text="Invalid: " + ", ".join(invalid))
            self.split_btn.state(["disabled"])
        elif not ranges:
            self.range_status.config(text="No ranges entered")
            self.split_btn.state(["disabled"])
        else:
            self.range_status.config(text="✓ Valid ranges")
            if self.output_dir.get():
                self.split_btn.state(["!disabled"])
            else:
                self.split_btn.state(["disabled"])
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages(ranges)

    def reset_split(self):
        self.file_path.set("")
        self.file_display.config(text="No file selected")
        self.output_dir.set("")
        self.out_display.config(text="No folder selected")
        self.range_entry.delete(0, tk.END)
        self.range_status.config(text="")
        self.page_info.config(text="Pages: —")
        self.split_btn.state(["disabled"])
        self.split_status.config(text="Ready")
        if self.pdf_preview:
            self.pdf_preview.clear()

    def run_split(self):
        fp = self.file_path.get()
        out_dir = self.output_dir.get()
        if not fp or not out_dir:
            messagebox.showwarning("Missing", "Select input PDF and output folder")
            return
        os.makedirs(out_dir, exist_ok=True)
        s = self.range_entry.get()
        ranges, invalid = parse_ranges(s, total_pages=self.total_pages.get() or None)
        if invalid or not ranges:
            messagebox.showerror("Invalid ranges", f"Please fix ranges. Invalid: {', '.join(invalid)}")
            return

        try:
            rot = int(self.rotate_split.get().replace("°",""))
        except:
            rot = 0
        naming = "timestamp" if self.naming_pattern.get().lower().startswith("with") else "split"
        self.split_status.config(text="Splitting...")
        self.split_progress.config(maximum=len(ranges), value=0)
        try:
            outs = split_pdf(fp, ranges, out_dir, rotate=rot, naming_pattern=naming, on_progress=lambda i, total: self.split_progress.step(1))
            self.split_status.config(text=f"✓ Created {len(outs)} files")
            messagebox.showinfo("Done", f"Created {len(outs)} files in {out_dir}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.split_status.config(text="Error")

    def merge_add(self):
        fps = filedialog.askopenfilenames(title="Select PDFs to merge", filetypes=[("PDF files","*.pdf")])
        if not fps:
            return
        for f in fps:
            self.merge_files.append(f)
            self.listbox.insert("end", os.path.basename(f))
        if self.merge_output_dir.get():
            self.merge_btn.state(["!disabled"])

    def merge_remove(self):
        sel = list(self.listbox.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            self.listbox.delete(idx)
            try:
                del self.merge_files[idx]
            except:
                pass
        if not self.merge_files:
            self.merge_btn.state(["disabled"])

    def merge_up(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        if idx == 0: return
        item = self.merge_files.pop(idx)
        self.merge_files.insert(idx-1, item)
        txt = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx-1, txt)
        self.listbox.select_set(idx-1)

    def merge_down(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        if idx >= len(self.merge_files)-1: return
        item = self.merge_files.pop(idx)
        self.merge_files.insert(idx+1, item)
        txt = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx+1, txt)
        self.listbox.select_set(idx+1)

    def merge_clear(self):
        self.listbox.delete(0, "end")
        self.merge_files = []
        self.merge_btn.state(["disabled"])

    def merge_choose_out(self):
        d = filedialog.askdirectory(title="Choose output folder for merge")
        if d:
            self.merge_output_dir.set(d)
            self.merge_out_lbl.config(text=d)
            if self.merge_files:
                self.merge_btn.state(["!disabled"])

    def merge_reset(self):
        self.merge_files = []
        self.listbox.delete(0, "end")
        self.merge_output_dir.set("")
        self.merge_out_lbl.config(text="No folder selected")
        self.merge_output_name.set("merged.pdf")
        self.merge_btn.state(["disabled"])

    def run_merge(self):
        if not self.merge_files or not self.merge_output_dir.get():
            messagebox.showwarning("Missing", "Select files and output folder")
            return
        out_name = self.merge_output_name.get().strip() or "merged.pdf"
        if not out_name.lower().endswith(".pdf"):
            out_name += ".pdf"
        out_path = os.path.join(self.merge_output_dir.get(), out_name)
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        rev_order = self.merge_rev_order.get()
        rev_pages = self.merge_rev_pages.get()
        try:
            rot = int(self.merge_rotate.get().replace("°",""))
        except:
            rot = 0
        self.merge_status.config(text="Merging...")
        self.merge_progress.config(maximum=len(self.merge_files), value=0)
        try:
            merge_pdfs(self.merge_files, out_path, reverse_order=rev_order, reverse_pages_each=rev_pages, rotate=rot, on_progress=lambda i,total: self.merge_progress.step(1))
            self.merge_status.config(text=f"✓ Merged to {os.path.basename(out_path)}")
            messagebox.showinfo("Done", f"Merged to {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.merge_status.config(text="Error")

    def image_add(self):
        fps = filedialog.askopenfilenames(title="Select Images", filetypes=[("Images","*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.bmp")])
        if not fps: return
        for f in fps:
            self.image_files.append(f)
            self.image_listbox.insert("end", os.path.basename(f))
        if self.image_output_dir.get():
            self.image_progress.config(value=0)

    def image_remove(self):
        sel = list(self.image_listbox.curselection())
        if not sel: return
        for idx in reversed(sel):
            self.image_listbox.delete(idx)
            try:
                del self.image_files[idx]
            except:
                pass

    def image_clear(self):
        self.image_listbox.delete(0, "end")
        self.image_files = []
        self.image_status.config(text="Ready")
        self.image_progress.config(value=0)

    def image_choose_out(self):
        d = filedialog.askdirectory(title="Choose image output folder")
        if d:
            self.image_output_dir.set(d)

    def image_choose_temp(self):
        d = filedialog.askdirectory(title="Choose temp folder for processing")
        if d:
            self.image_temp_dir.set(d)

    def image_reset(self):
        self.image_files = []
        self.image_listbox.delete(0, "end")
        self.image_output_dir.set("")
        self.image_temp_dir.set("")
        self.fuzz_percent.set(10)
        self.image_status.config(text="Ready")
        self.image_progress.config(value=0)

    def run_image_process(self):
        if not self.image_files or not self.image_output_dir.get() or not self.image_temp_dir.get():
            messagebox.showwarning("Missing", "Select images, output folder and temp folder")
            return
        try:
            fuzz = int(self.fuzz_percent.get())
        except:
            fuzz = 10
        self.image_status.config(text="Processing...")
        self.image_progress.config(maximum=len(self.image_files), value=0)
        succ, failed = batch_process_images(self.image_files, self.image_output_dir.get(), self.image_temp_dir.get(), fuzz_percent=fuzz, on_progress=lambda i,total,name: self.image_progress.step(1))
        self.image_status.config(text=f"✓ Success: {succ} | Failed: {len(failed)}")
        if failed:
            msg = "\n".join([f"{n}: {err}" for n,err in failed])
            messagebox.showwarning("Some files failed", msg)

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme()

    def apply_theme(self):
        pal = self.palette['dark' if self.dark else 'light']
        self.root.configure(bg=pal['bg'])
        self.mode_btn.config(text="☀️  Light Mode" if self.dark else "🌙 Dark Mode")
        
        self.style.configure("TFrame", background=pal['panel'])
        self.style.configure("TLabel", background=pal['panel'], foreground=pal['text'])
        self.style.configure("Title.TLabel", background=pal['panel'], foreground=pal['text'])
        self.style.configure("Section.TLabel", background=pal['card'], foreground=pal['text'])
        self.style.configure("Sub.TLabel", background=pal['panel'], foreground=pal['text_muted'])
        self.style.configure("Card.TFrame", background=pal['card'], borderwidth=1)
        self.style.configure("TNotebook", background=pal['panel'])
        self.style.configure("TCheckbutton", background=pal['panel'], foreground=pal['text'])
        self.style.configure("Treeview", background=pal['card'], foreground=pal['text'], fieldbackground=pal['card'])

    def on_window_resize(self, event=None):
        # This can be used for advanced responsive features
        pass

    def show_help(self):
        help_text = """PDF Master Pro - Keyboard Shortcuts

Ctrl+O  - Open PDF file
Ctrl+S  - Start splitting
F1      - Show this help

Features:
• Split PDFs by page ranges
• Merge multiple PDFs
• Batch process images
• Live PDF preview
• Dark/Light theme"""
        messagebox.showinfo("Help", help_text)

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFToolApp(root)
    root.mainloop()
