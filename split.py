import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter
import os

def split_pdf(file_path, ranges, output_dir):
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    for i, (start, end) in enumerate(ranges):
        if start < 1 or end > total_pages or start > end:
            messagebox.showerror("Invalid Range", f"Range {start}-{end} is out of bounds.")
            continue

        writer = PdfWriter()
        for page_num in range(start - 1, end):
            writer.add_page(reader.pages[page_num])

        output_path = os.path.join(output_dir, f"split_{i+1}_{start}-{end}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)

def parse_ranges(range_str):
    try:
        ranges = []
        for part in range_str.split(','):
            start, end = map(int, part.strip().split('-'))
            ranges.append((start, end))
        return ranges
    except:
        messagebox.showerror("Error", "Invalid range format. Use format like: 1-4,5-7,8-12")
        return []

def browse_file():
    file_path.set(filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")]))
    if file_path.get():
        file_label.config(text=f"📄 {os.path.basename(file_path.get())}")

def browse_output():
    output_path.set(filedialog.askdirectory())
    if output_path.get():
        output_label.config(text=f"📂 {output_path.get()}")

def run_split():
    if not file_path.get() or not output_path.get():
        messagebox.showerror("Missing Info", "Please select both PDF file and output folder.")
        return

    ranges = parse_ranges(range_entry.get())
    if ranges:
        split_pdf(file_path.get(), ranges, output_path.get())
        status_label.config(text="✅ PDF split successfully!", foreground="green")
        messagebox.showinfo("Success", "PDF split successfully!")

# ---------------- UI Setup ----------------
root = tk.Tk()
root.title("✨ Custom PDF Splitter ✨")
root.geometry("600x400")
root.configure(bg="#f4f6f9")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 11), padding=6)
style.configure("TLabel", font=("Segoe UI", 11), background="#f4f6f9")

file_path = tk.StringVar()
output_path = tk.StringVar()

# Title Banner
title = tk.Label(root, text="📑 PDF Splitter Tool", font=("Segoe UI", 18, "bold"), bg="#4a90e2", fg="white", pady=10)
title.pack(fill="x")

# Step 1
frame1 = tk.Frame(root, bg="#f4f6f9")
frame1.pack(pady=10)
ttk.Label(frame1, text="Step 1: Select PDF File").pack()
ttk.Button(frame1, text="Browse PDF", command=browse_file).pack(pady=5)
file_label = ttk.Label(frame1, text="No file selected", foreground="gray")
file_label.pack()

# Step 2
frame2 = tk.Frame(root, bg="#f4f6f9")
frame2.pack(pady=10)
ttk.Label(frame2, text="Step 2: Enter Page Ranges (e.g., 1-4,5-7,8-12)").pack()
range_entry = ttk.Entry(frame2, width=50)
range_entry.pack(pady=5)

# Step 3
frame3 = tk.Frame(root, bg="#f4f6f9")
frame3.pack(pady=10)
ttk.Label(frame3, text="Step 3: Choose Output Folder").pack()
ttk.Button(frame3, text="Browse Folder", command=browse_output).pack(pady=5)
output_label = ttk.Label(frame3, text="No folder selected", foreground="gray")
output_label.pack()

# Split Button
split_btn = ttk.Button(root, text="🚀 Split PDF", command=run_split)
split_btn.pack(pady=20)

# Status Bar
status_label = tk.Label(root, text="Ready", bd=1, relief="sunken", anchor="w", bg="#eaeaea", font=("Segoe UI", 10))
status_label.pack(side="bottom", fill="x")

root.mainloop()
