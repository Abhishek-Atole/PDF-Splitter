self.pdf_preview = PDFPreview(preview_card)
        self.pdf_preview.frame.pack(fill="both", expand=True, pady=(6, 0))

    def _build_merge_tab(self):
        """Build merge PDFs tab"""
        container = ttk.Frame(self.tab_merge, padding=8)
        container.pack(fill="both", expand=True)

        # Files list
        files_card = self._create_card(container, "📑 PDF Files to Merge")
        files_card.pack(fill="both", expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(files_card)
        list_frame.pack(fill="both", expand=True, pady=(6, 0))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, height=12, font=self.font_base,
                                   bg="#1e293b", fg="#f1f5f9", selectbackground="#3b82f6",
                                   relief="flat", yscrollcommand=scrollbar.set)
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        btn_row = ttk.Frame(files_card)
        btn_row.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_row, text="➕ Add", command=self._merge_add, width=8).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="🗑️ Remove", command=self._merge_remove, width=10).pack(side="left", padx=3)
        ttk.Button(btn_row, text="⬆️", command=self._merge_up, width=4).pack(side="left", padx=3)
        ttk.Button(btn_row, text="⬇️", command=self._merge_down, width=4).pack(side="left", padx=3)
        ttk.Button(btn_row, text="✖️ Clear", command=self._merge_clear, width=8).pack(side="left", padx=3)

        # Options and output
        bottom_row = ttk.Frame(container)
        bottom_row.pack(fill="x")
        bottom_row.columnconfigure(0, weight=1)
        bottom_row.columnconfigure(1, weight=1)

        opt_card = self._create_card(bottom_row, "⚙️ Options")
        opt_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        
        ttk.Checkbutton(opt_card, text="Reverse file order", variable=self.merge_rev_order).pack(anchor="w", pady=4)
        ttk.Checkbutton(opt_card, text="Reverse pages in each", variable=self.merge_rev_pages).pack(anchor="w", pady=4)
        
        rot_frame = ttk.Frame(opt_card)
        rot_frame.pack(fill="x", pady=6)
        ttk.Label(rot_frame, text="Rotate:", style="Sub.TLabel").pack(side="left")
        ttk.Combobox(rot_frame, values=["0°", "90°", "180°", "270°"], textvariable=self.merge_rotate, width=8, state="readonly").pack(side="left", padx=(10, 0))

        out_card = self._create_card(bottom_row, "💾 Output")
        out_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        
        self.merge_out_lbl = ttk.Label(out_card, text="No folder selected", style="Sub.TLabel", wraplength=250)
        self.merge_out_lbl.pack(anchor="w", pady=6)
        
        ttk.Button(out_card, text="📂 Choose Folder", command=self._merge_choose_out, style="Outline.TButton").pack(fill="x", pady=(0, 10))
        
        name_row = ttk.Frame(out_card)
        name_row.pack(fill="x", pady=3)
        ttk.Label(name_row, text="Name:", style="Sub.TLabel").pack(side="left")
        ttk.Entry(name_row, textvariable=self.merge_output_name, width=18).pack(side="left", padx=(8, 0), fill="x", expand=True)

        # Actions
        action_row = ttk.Frame(container)
        action_row.pack(fill="x", pady=(10, 0))
        
        self.merge_btn = ttk.Button(action_row, text="🔗 Merge PDFs", style="Accent.TButton", command=self._run_merge)
        self.merge_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.merge_btn.state(["disabled"])
        
        ttk.Button(action_row, text="↺ Reset", command=self._merge_reset, style="Outline.TButton").pack(side="left")

        # Status
        status_row = ttk.Frame(container)
        status_row.pack(fill="x", pady=(8, 0))
        self.merge_status = ttk.Label(status_row, text="Ready to merge", style="Sub.TLabel")
        self.merge_status.pack(anchor="w", pady=(0, 4))
        self.merge_progress = ttk.Progressbar(status_row, mode="determinate")
        self.merge_progress.pack(fill="x")

    def _build_image_tab(self):
        """Build image processing tab"""
        container = ttk.Frame(self.tab_images, padding=8)
        container.pack(fill="both", expand=True)
        
        # Check ImageMagick
        if not check_imagemagick():
            warning_card = self._create_card(container, "⚠️ ImageMagick Required")
            warning_card.pack(fill="x", pady=(0, 10))
            
            warning_text = """ImageMagick is not installed or not in PATH.

To use image processing features:
1. Download from: https://imagemagick.org/
2. Install and add to system PATH
3. Restart this application

Features when installed:
• Remove white backgrounds from images
• Auto-enhance (contrast, sharpness, levels)
• Batch process multiple images
• Convert any format to PNG"""
            
            ttk.Label(warning_card, text=warning_text, style="Sub.TLabel", justify="left").pack(anchor="w", pady=6)
            return
        
        # Files list
        files_card = self._create_card(container, "🖼️ Images to Process")
        files_card.pack(fill="both", expand=True, pady=(0, 10))
        
        list_frame = ttk.Frame(files_card)
        list_frame.pack(fill="both", expand=True, pady=(6, 0))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.image_listbox = tk.Listbox(list_frame, height=12, font=self.font_base,
                                        bg="#1e293b", fg="#f1f5f9", 
                                        selectbackground="#3b82f6",
                                        relief="flat", yscrollcommand=scrollbar.set)
        self.image_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        btn_row = ttk.Frame(files_card)
        btn_row.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_row, text="➕ Add Images", command=self._image_add, width=12).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="🗑️ Remove", command=self._image_remove, width=10).pack(side="left", padx=3)
        ttk.Button(btn_row, text="✖️ Clear All", command=self._image_clear, width=10).pack(side="left", padx=3)
        
        # Settings
        settings_row = ttk.Frame(container)
        settings_row.pack(fill="x")
        settings_row.columnconfigure(0, weight=1)
        settings_row.columnconfigure(1, weight=1)
        
        settings_card = self._create_card(settings_row, "⚙️ Processing Settings")
        settings_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        
        fuzz_frame = ttk.Frame(settings_card)
        fuzz_frame.pack(fill="x", pady=6)
        ttk.Label(fuzz_frame, text="Background Removal Sensitivity:", style="Sub.TLabel").pack(anchor="w", pady=(0, 4))
        
        fuzz_control = ttk.Frame(fuzz_frame)
        fuzz_control.pack(fill="x")
        ttk.Label(fuzz_control, text="Low", style="Small.TLabel").pack(side="left")
        fuzz_scale = ttk.Scale(fuzz_control, from_=5, to=25, variable=self.fuzz_percent, orient="horizontal")
        fuzz_scale.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(fuzz_control, text="High", style="Small.TLabel").pack(side="right")
        
        self.fuzz_label = ttk.Label(settings_card, text="Fuzz: 10%", style="Sub.TLabel")
        self.fuzz_label.pack(anchor="w", pady=(4, 0))
        fuzz_scale.config(command=self._update_fuzz_label)
        
        info_text = """Higher values remove more colors similar to white.
Start with 10% and adjust if needed."""
        ttk.Label(settings_card, text=info_text, style="Small.TLabel", foreground="#94a3b8").pack(anchor="w", pady=(6, 0))
        
        # Output folders
        output_card = self._create_card(settings_row, "💾 Output Folders")
        output_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        
        ttk.Label(output_card, text="Output (final images):", style="Sub.TLabel").pack(anchor="w", pady=(6, 2))
        self.image_out_lbl = ttk.Label(output_card, text="Not selected", style="Small.TLabel", wraplength=250)
        self.image_out_lbl.pack(anchor="w", pady=(0, 4))
        ttk.Button(output_card, text="📂 Choose Output", command=self._image_choose_output, style="Outline.TButton").pack(fill="x", pady=(0, 8))
        
        ttk.Label(output_card, text="Temp (intermediate files):", style="Sub.TLabel").pack(anchor="w", pady=(4, 2))
        self.image_temp_lbl = ttk.Label(output_card, text="Not selected", style="Small.TLabel", wraplength=250)
        self.image_temp_lbl.pack(anchor="w", pady=(0, 4))
        ttk.Button(output_card, text="📂 Choose Temp", command=self._image_choose_temp, style="Outline.TButton").pack(fill="x")
        
        # Actions
        action_row = ttk.Frame(container)
        action_row.pack(fill="x", pady=(10, 0))
        
        self.process_btn = ttk.Button(action_row, text="🎨 Process Images", style="Accent.TButton", command=self._run_image_processing)
        self.process_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.process_btn.state(["disabled"])
        
        ttk.Button(action_row, text="↺ Reset", command=self._image_reset, style="Outline.TButton").pack(side="left")
        
        # Status
        status_row = ttk.Frame(container)
        status_row.pack(fill="x", pady=(8, 0))
        self.image_status = ttk.Label(status_row, text="Ready to process images", style="Sub.TLabel")
        self.image_status.pack(anchor="w", pady=(0, 4))
        self.image_progress = ttk.Progressbar(status_row, mode="determinate")
        self.image_progress.pack(fill="x")

    def _build_info_tab(self):
        """Build info tab"""
        container = ttk.Frame(self.tab_info, padding=16)
        container.pack(fill="both", expand=True)
        
        welcome = self._create_card(container, "👋 Welcome to PDF Master Pro")
        welcome.pack(fill="both", expand=True)
        
        text_frame = ttk.Frame(welcome)
        text_frame.pack(fill="both", expand=True, pady=(6, 0))
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side="right", fill="y")
        
        info_text = """PDF Master Pro - Professional Document & Image Management

🎯 FEATURES:
• Split PDFs by page ranges or endpoints
• Merge multiple PDFs into one document
• Remove white backgrounds from images
• Batch process and enhance images
• Live PDF preview with page navigation
• Rotate pages during split or merge
• Professional file naming with timestamps
• Fully responsive design for all screens

📄 PDF FEATURES:
• Split: Divide PDFs into multiple files
• Merge: Combine PDFs in any order
• Preview: See pages before splitting
• Navigate: Browse through PDF pages
• Rotate: 0°, 90°, 180°, 270° options

🖼️ IMAGE FEATURES:
• Remove white backgrounds automatically
• Enhance images (auto-level, contrast, sharpen)
• Batch process unlimited images
• Adjustable sensitivity (fuzz 5-25%)
• Support all common formats
• Output high-quality PNGs

⌨️ KEYBOARD SHORTCUTS:
• Ctrl+O: Browse for PDF
• Ctrl+S: Execute split
• Ctrl+M: Execute merge
• Ctrl+R: Reset current tab
• F1: Show help
• Esc: Exit application

💡 REQUIREMENTS:
• PDF Preview: pip install pdf2image Pillow
  + System: poppler-utils
• Image Processing: ImageMagick
  Download: https://imagemagick.org/

📝 TIPS:
• Use preview to verify ranges
• Timestamp naming prevents overwrites
• Test with small batches first
• Keep original files as backup
• Adjust fuzz if removal is too aggressive

Created with ❤️ for efficient document management"""
        
        text_widget = tk.Text(text_frame, wrap="word", font=self.font_base,
                              bg="#1e293b", fg="#f1f5f9", relief="flat", 
                              padx=16, pady=16, yscrollcommand=text_scroll.set)
        text_widget.pack(side="left", fill="both", expand=True)
        text_scroll.config(command=text_widget.yview)
        
        text_widget.insert("1.0", info_text)
        text_widget.config(state="disabled")

    def _create_card(self, parent, title):
        """Create a styled card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        if title:
            ttk.Label(card, text=title, style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        return card

    def _apply_theme(self):
        """Apply color theme"""
        pal = self.palette["dark" if self.dark else "light"]
        self.root.configure(bg=pal["bg"])
        
        self.style.configure("TFrame", background=pal["panel"])
        self.style.configure("Card.TFrame", background=pal["card"])
        self.style.configure("TLabel", background=pal["panel"], foreground=pal["text"])
        self.style.configure("Section.TLabel", background=pal["card"], foreground=pal["text"])
        self.style.configure("Sub.TLabel", background=pal["card"], foreground=pal["muted"])
        self.style.configure("Small.TLabel", background=pal["panel"], foreground=pal["muted"])
        
        # Buttons
        self.style.configure("TButton", background=pal["panel"], foreground=pal["text"])
        self.style.map("TButton", background=[("active", pal["card"])])
        
        self.style.configure("Accent.TButton", background=pal["accent"], foreground="#ffffff")
        self.style.map("Accent.TButton", 
                      background=[("active", pal["accent_hover"]), ("pressed", "#1e40af")],
                      foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        self.style.configure("Outline.TButton", background=pal["card"], foreground=pal["text"])
        self.style.map("Outline.TButton", 
                      background=[("active", pal["accent"]), ("pressed", pal["accent_hover"])],
                      foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        try:
            self.style.configure("TNotebook", background=pal["bg"], borderwidth=0)
            self.style.configure("TNotebook.Tab", background=pal["tab"], foreground=pal["text"], padding=[16, 10])
            self.style.map("TNotebook.Tab", background=[("selected", pal["card"])])
        except Exception:
            pass
        
        self.mode_btn.config(text=("☀️ Light Mode" if self.dark else "🌙 Dark Mode"))
        
        if hasattr(self, 'listbox'):
            self.listbox.config(bg=pal["card"], fg=pal["text"], selectbackground=pal["accent"])
        
        if hasattr(self, 'image_listbox'):
            self.image_listbox.config(bg=pal["card"], fg=pal["text"], selectbackground=pal["accent"])
        
        if self.pdf_preview and hasattr(self.pdf_preview, 'canvas'):
            self.pdf_preview.canvas.config(bg=pal["card"])

    def _toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark = not self.dark
        self._apply_theme()

    # ========== PDF SPLIT METHODS ==========
    
    def _browse_file(self):
        """Browse for PDF file"""
        fp = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not fp:
            return
        
        self.file_path.set(fp)
        self.file_display.config(text=f"📄 {os.path.basename(fp)}")
        
        try:
            reader = PdfReader(fp)
            total = len(reader.pages)
            self.total_pages.set(total)
            self.page_info.config(text=f"Total Pages: {total} pages")
            
            self.split_status.config(text="Loading preview...")
            self.root.update_idletasks()
            
            if self.pdf_preview.load_pdf(fp, lambda msg: self.split_status.config(text=msg)):
                self.pdf_preview.show_pages()
                self.split_status.config(text="Preview loaded")
            else:
                self.split_status.config(text="Preview not available")
            
            if fp not in self.recent_files:
                self.recent_files.insert(0, fp)
                self.recent_files = self.recent_files[:5]
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read PDF:\n{str(e)}")
            self.total_pages.set(0)
            self.page_info.config(text="Total Pages: —")
            self.split_status.config(text="Error loading PDF")
        
        self._on_range_key()

    def _choose_output(self):
        """Choose output folder"""
        d = filedialog.askdirectory(title="Select Output Folder")
        if not d:
            return
        self.output_dir.set(d)
        self.out_display.config(text=f"📂 {os.path.basename(d)}")
        self._update_split_enabled()

    def _on_range_key(self, _e=None):
        """Handle range entry changes"""
        txt = self.range_entry.get().strip()
        total = self.total_pages.get()
        
        if not txt:
            self.range_status.config(text="💡 Enter ranges like 1-4,5-8 or endpoints like 4,8,12")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages()
            self._update_split_enabled()
            return
        
        ranges, invalid = parse_ranges(txt, total_pages=total)
        
        if invalid:
            self.range_status.config(text=f"❌ Invalid: {', '.join(invalid)}")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages()
        elif not ranges:
            self.range_status.config(text="⚠️ No valid ranges found")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages()
        else:
            total_pages = sum((b - a + 1) for a, b in ranges)
            self.range_status.config(text=f"✅ {len(ranges)} files • {total_pages} total pages")
            if self.pdf_preview and self.pdf_preview.all_images:
                self.pdf_preview.show_pages(ranges)
        
        self._update_split_enabled()

    def _update_split_enabled(self):
        """Enable/disable split button"""
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

    def _run_split(self):
        """Execute PDF split"""
        if self.split_btn.instate(["disabled"]):
            return
        
        txt = self.range_entry.get().strip()
        ranges, invalid = parse_ranges(txt, total_pages=self.total_pages.get())
        
        if invalid:
            messagebox.showerror("Invalid Ranges", f"Please fix: {', '.join(invalid)}")
            return
        
        if not ranges:
            messagebox.showwarning("No Ranges", "Please specify page ranges.")
            return
        
        try:
            self.split_status.config(text="⏳ Splitting PDF...")
            self.split_progress["maximum"] = len(ranges)
            self.split_progress["value"] = 0
            self.split_btn.state(["disabled"])
            self.root.update_idletasks()

            def on_progress(done, total):
                self.split_progress["value"] = done
                self.split_status.config(text=f"⏳ Splitting... {done}/{total}")
                self.root.update_idletasks()

            rot_str = self.rotate_split.get().replace("°", "").strip()
            rotate = int(rot_str) if rot_str.isdigit() else 0
            
            naming = "timestamp" if self.naming_pattern.get() == "With Timestamp" else "split"

            output_files = split_pdf(
                self.file_path.get(), ranges, self.output_dir.get(),
                rotate=rotate, naming_pattern=naming, on_progress=on_progress
            )
            
            self.output_files = output_files
            self.split_status.config(text=f"✅ Success! Created {len(output_files)} files")
            
            msg = f"Successfully split into {len(output_files)} files!\n\nOutput: {self.output_dir.get()}\n\nFiles:\n"
            for f in output_files[:5]:
                msg += f"• {os.path.basename(f)}\n"
            if len(output_files) > 5:
                msg += f"... and {len(output_files) - 5} more"
            
            messagebox.showinfo("Split Completed", msg)
            
        except Exception as e:
            self.split_status.config(text="❌ Error")
            messagebox.showerror("Error", f"Split failed:\n\n{str(e)}")
        finally:
            self.split_btn.state(["!disabled"])

    def _reset_split(self):
        """Reset split tab"""
        self.file_path.set("")
        self.output_dir.set("")
        self.file_display.config(text="No file selected")
        self.out_display.config(text="No folder selected")
        self.page_info.config(text="Total Pages: —")
        self.range_entry.delete(0, tk.END)
        self.range_status.config(text="")
        self.split_status.config(text="Ready to split")
        self.split_progress["value"] = 0
        self.rotate_split.set("0°")
        self.naming_pattern.set("Standard")
        if self.pdf_preview:
            self.pdf_preview.clear()
        self._update_split_enabled()

    # ========== PDF MERGE METHODS ==========

    def _merge_add(self):
        """Add PDFs to merge list"""
        paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not paths:
            return
        
        added = 0
        for p in paths:
            if p not in self.merge_files:
                self.merge_files.append(p)
                self.listbox.insert(tk.END, f"📄 {os.path.basename(p)}")
                added += 1
        
        if added > 0:
            self.merge_status.config(text=f"Added {added} file(s). Total: {len(self.merge_files)}")
        
        self._update_merge_enabled()

    def _merge_remove(self):
        """Remove selected PDF"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a file to remove.")
            return
        
        i = sel[0]
        removed = self.merge_files[i]
        del self.merge_files[i]
        self.listbox.delete(i)
        
        self.merge_status.config(text=f"Removed: {os.path.basename(removed)}")
        self._update_merge_enabled()

    def _merge_up(self):
        """Move selected file up"""
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

    def _merge_down(self):
        """Move selected file down"""
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

    def _merge_clear(self):
        """Clear all files"""
        if self.merge_files:
            if messagebox.askyesno("Clear All", "Remove all files?"):
                self.listbox.delete(0, tk.END)
                self.merge_files.clear()
                self.merge_status.config(text="Cleared")
                self._update_merge_enabled()

    def _merge_choose_out(self):
        """Choose output folder"""
        d = filedialog.askdirectory(title="Select Output Folder")
        if not d:
            return
        self.merge_output_dir.set(d)
        self.merge_out_lbl.config(text=f"📂 {d}")
        self._update_merge_enabled()

    def _update_merge_enabled(self):
        """Enable/disable merge button"""
        has_files = len(self.merge_files) >= 2
        has_output = bool(self.merge_output_dir.get())
        
        if has_files and has_output:
            self.merge_btn.state(["!disabled"])
        else:
            self.merge_btn.state(["disabled"])

    def _run_merge(self):
        """Execute PDF merge"""
        if self.merge_btn.instate(["disabled"]):
            return
        
        if len(self.merge_files) < 2:
            messagebox.showwarning("Not Enough Files", "Need at least 2 PDFs.")
            return
        
        out_name = self.merge_output_name.get().strip() or "merged.pdf"
        if not out_name.lower().endswith(".pdf"):
            out_name += ".pdf"
        
        out_path = os.path.join(self.merge_output_dir.get(), out_name)
        
        if os.path.exists(out_path):
            if not messagebox.askyesno("File Exists", f"Overwrite '{out_name}'?"):
                return
        
        try:
            self.merge_status.config(text="⏳ Merging...")
            self.merge_progress["maximum"] = len(self.merge_files)
            self.merge_progress["value"] = 0
            self.merge_btn.state(["disabled"])
            self.root.update_idletasks()

            def on_progress(done, total):
                self.merge_progress["value"] = done
                self.merge_status.config(text=f"⏳ Merging... {done}/{total}")
                self.root.update_idletasks()

            rot_str = self.merge_rotate.get().replace("°", "").strip()
            rotate = int(rot_str) if rot_str.isdigit() else 0

            merge_pdfs(
                self.merge_files, out_path,
                reverse_order=self.merge_rev_order.get(),
                reverse_pages_each=self.merge_rev_pages.get(),
                rotate=rotate, on_progress=on_progress
            )
            
            file_size = os.path.getsize(out_path) / (1024 * 1024)
            self.merge_status.config(text=f"✅ Success! {out_name}")
            
            msg = f"Successfully merged {len(self.merge_files)} PDFs!\n\n"
            msg += f"Output: {out_path}\n"
            msg += f"Size: {file_size:.2f} MB"
            
            messagebox.showinfo("Merge Completed", msg)
            
        except Exception as e:
            self.merge_status.config(text="❌ Error")
            messagebox.showerror("Error", f"Merge failed:\n\n{str(e)}")
        finally:
            self.merge_btn.state(["!disabled"])

    def _merge_reset(self):
        """Reset merge tab"""
        if self.merge_files:
            self.listbox.delete(0, tk.END)
            self.merge_files.clear()
        self.merge_output_dir.set("")
        self.merge_output_name.set("merged.pdf")
        self.merge_out_lbl.config(text="No folder selected")
        self.merge_rotate.set("0°")
        self.merge_rev_order.set(False)
        self.merge_rev_pages.set(False)
        self.merge_status.config(text="Ready to merge")
        self.merge_progress["value"] = 0

    # ========== IMAGE PROCESSING METHODS ==========

    def _image_add(self):
        """Add images to process"""
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("All files", "*.*")
            ]
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
            self.image_status.config(text=f"Added {added} image(s). Total: {len(self.image_files)}")
        
        self._update_image_enabled()
    
    def _image_remove(self):
        """Remove selected image"""
        sel = self.image_listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an image.")
            return
        
        i = sel[0]
        removed = self.image_files[i]
        del self.image_files[i]
        self.image_listbox.delete(i)
        
        self.image_status.config(text=f"Removed: {os.path.basename(removed)}")
        self._update_image_enabled()
    
    def _image_clear(self):
        """Clear all images"""
        if self.image_files:
            if messagebox.askyesno("Clear All", "Remove all images?"):
                self.image_listbox.delete(0, tk.END)
                self.image_files.clear()
                self.image_status.config(text="Cleared")
                self._update_image_enabled()
    
    def _image_choose_output(self):
        """Choose output folder"""
        d = filedialog.askdirectory(title="Select Output Folder")
        if not d:
            return
        self.image_output_dir.set(d)
        self.image_out_lbl.config(text=f"📂 {d}")
        self._update_image_enabled()
    
    def _image_choose_temp(self):
        """Choose temp folder"""
        d = filedialog.askdirectory(title="Select Temp Folder")
        if not d:
            return
        self.image_temp_dir.set(d)
        self.image_temp_lbl.config(text=f"📂 {d}")
        self._update_image_enabled()
    
    def _update_fuzz_label(self, value):
        """Update fuzz label"""
        fuzz_val = int(float(value))
        self.fuzz_percent.set(fuzz_val)
        self.fuzz_label.config(text=f"Fuzz: {fuzz_val}%")
    
    def _update_image_enabled(self):
        """Enable/disable process button"""
        has_images = len(self.image_files) > 0
        has_output = bool(self.image_output_dir.get())
        has_temp = bool(self.image_temp_dir.get())
        
        if has_images and has_output and has_temp:
            self.process_btn.state(["!disabled"])
        else:
            self.process_btn.state(["disabled"])
    
    def _run_image_processing(self):
        """Execute image processing"""
        if self.process_btn.instate(["disabled"]):
            return
        
        if len(self.image_files) == 0:
            messagebox.showwarning("No Images", "Please add images.")
            return
        
        if not check_imagemagick():
            messagebox.showerror("ImageMagick Not Found", 
                               "ImageMagick required.\n\nDownload: https://imagemagick.org/")
            return
        
        try:
            self.image_status.config(text="⏳ Processing...")
            self.image_progress["maximum"] = len(self.image_files)
            self.image_progress["value"] = 0
            self.process_btn.state(["disabled"])
            self.root.update_idletasks()
            
            def on_progress(current, total, filename):
                self.image_progress["value"] = current
                self.image_status.config(text=f"⏳ {current}/{total}: {filename}")
                self.root.update_idletasks()
            
            success_count, failed_files = batch_process_images(
                self.image_files,
                self.image_output_dir.get(),
                self.image_temp_dir.get(),
                fuzz_percent=self.fuzz_percent.get(),
                on_progress=on_progress
            )
            
            self.image_status.config(text=f"✅ Processed {success_count}/{len(self.image_files)}")
            
            msg = f"Processed {success_count}/{len(self.image_files)} images!\n\n"
            msg += f"Output: {self.image_output_dir.get()}\n\n"
            
            if failed_files:
                msg += f"Failed ({len(failed_files)}):\n"
                for filename, error in failed_files[:5]:
                    msg += f"• {filename}: {error}\n"
                if len(failed_files) > 5:
                    msg += f"... and {len(failed_files) - 5} more"
            
            if failed_files:
                messagebox.showwarning("Complete with Errors", msg)
            else:
                messagebox.showinfo("Complete", msg)
            
        except Exception as e:
            self.image_status.config(text="❌ Error")
            messagebox.showerror("Error", f"Processing failed:\n\n{str(e)}")
        finally:
            self.process_btn.state(["!disabled"])
    
    def _image_reset(self):
        """Reset image tab"""
        if self.image_files:
            self.image_listbox.delete(0, tk.END)
            self.image_files.clear()
        self.image_output_dir.set("")
        self.image_temp_dir.set("")
        self.image_out_lbl.config(text="Not selected")
        self.image_temp_lbl.config(text="Not selected")
        self.fuzz_percent.set(10)
        self.fuzz_label.config(text="Fuzz: 10%")
        self.image_status.config(text="Ready to process")
        self.image_progress["value"] = 0
        self._update_image_enabled()

    # ========== HELP ==========

    def _help(self):
        """Show help dialog"""
        help_text = """PDF MASTER PRO - HELP GUIDE

═══════════════════════════════════════════════════════

SPLIT PDF:
1. Browse for PDF file (Ctrl+O)
2. Enter ranges:
   • Standard: 1-5,10-15,20-25
   • Endpoints: 5,15,25
3. Preview shows selected pages
4. Choose output folder
5. Optional: Rotate and naming
6. Click Split (Ctrl+S)

MERGE PDFS:
1. Add multiple PDFs
2. Reorder with ⬆️⬇️ buttons
3. Optional: Reverse order/pages, rotate
4. Choose output folder and filename
5. Click Merge (Ctrl+M)

IMAGE PROCESSING:
1. Add images (any format)
2. Choose Output folder (final PNGs)
3. Choose Temp folder (intermediate JPGs)
4. Adjust Fuzz (5-25%)
   • Low: Only pure white
   • High: Near-white colors
5. Click Process

KEYBOARD SHORTCUTS:
• Ctrl+O: Browse PDF
• Ctrl+S: Split
• Ctrl+M: Merge
• Ctrl+R: Reset
• F1: Help
• Esc: Exit

REQUIREMENTS:
• PDF Preview: pip install pdf2image Pillow
  + poppler-utils (system)
• Images: ImageMagick
  https://imagemagick.org/

TIPS:
✓ Use preview to verify ranges
✓ Test small batches first
✓ Keep original files
✓ Adjust fuzz if needed

═══════════════════════════════════════════════════════

For more info, visit the Info tab."""
        
        help_win = tk.Toplevel(self.root)
        help_win.title("Help - PDF Master Pro")
        help_win.geometry("700x650")
        help_win.transient(self.root)
        help_win.grab_set()
        
        text_frame = ttk.Frame(help_win)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text = tk.Text(text_frame, wrap="word", font=("Segoe UI", 10), 
                      padx=20, pady=20, yscrollcommand=scrollbar.set)
        text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text.yview)
        
        text.insert("1.0", help_text)
        text.config(state="disabled")
        
        btn_frame = ttk.Frame(help_win, padding=10)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Close", command=help_win.destroy).pack(side="right")


# ===============================================================================
# MAIN ENTRY POINT
# ===============================================================================

def main():
    """Main function"""
    root = tk.Tk()
    app = PDFToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
"""
PDF Master Pro - Complete Application
A comprehensive tool for PDF splitting, merging, and image background removal
Author: Assistant
Version: 1.0.0
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os
from datetime import datetime
import subprocess
import shutil
from pathlib import Path

# Try to import PDF preview libraries
try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageTk
    PREVIEW_AVAILABLE = True
except ImportError:
    PREVIEW_AVAILABLE = False
    print("Preview libraries not available. Install: pip install pdf2image Pillow")

# ===============================================================================
# IMAGE PROCESSING FUNCTIONS
# ===============================================================================

def check_imagemagick():
    """Check if ImageMagick is installed and available"""
    try:
        result = subprocess.run(['magick', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def process_image(input_path, output_path, temp_dir, fuzz_percent=10, on_progress=None):
    """
    Process a single image: convert to JPG, remove white background, enhance
    Returns: (success, error_message)
    """
    try:
        input_file = Path(input_path)
        output_file = Path(output_path)
        temp_jpg = Path(temp_dir) / f"{input_file.stem}.jpg"
        
        # Step 1: Convert to JPG if needed
        if input_file.suffix.lower() in ['.jpg', '.jpeg']:
            shutil.copy(input_file, temp_jpg)
        else:
            cmd = ['magick', str(input_file), str(temp_jpg)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, f"Conversion failed: {result.stderr}"
        
        if on_progress:
            on_progress("processing")
        
        # Step 2: Remove white background and enhance
        cmd = [
            'magick', str(temp_jpg),
            '-fuzz', f'{fuzz_percent}%',
            '-transparent', 'white',
            '-auto-level',
            '-contrast',
            '-sharpen', '0x1',
            str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False, f"Processing failed: {result.stderr}"
        
        return True, None
        
    except subprocess.TimeoutExpired:
        return False, "Processing timeout"
    except Exception as e:
        return False, str(e)

def batch_process_images(input_files, output_dir, temp_dir, fuzz_percent=10, on_progress=None):
    """
    Batch process multiple images
    Returns: (success_count, failed_files)
    """
    success_count = 0
    failed_files = []
    total = len(input_files)
    
    # Ensure directories exist
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

# ===============================================================================
# PDF PROCESSING FUNCTIONS
# ===============================================================================

def parse_ranges(range_str, total_pages=None):
    """Parse page ranges from string"""
    s = (range_str or "").strip()
    if not s:
        return [], []
    
    parts = [p.strip() for p in s.split(',') if p.strip()]
    endpoints_mode = all('-' not in p for p in parts)
    ranges, invalid = [], []

    if endpoints_mode:
        try:
            ends = [int(p) for p in parts]
        except Exception:
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
            except Exception:
                invalid.append(p)
    return ranges, invalid

def split_pdf(file_path, ranges, output_dir, rotate=0, naming_pattern="split", on_progress=None):
    """Split PDF into multiple files based on ranges"""
    reader = PdfReader(file_path)
    total = len(reader.pages)
    done = 0
    output_files = []

    for i, (start, end) in enumerate(ranges):
        if start < 1 or end > total or start > end:
            raise ValueError(f"Range {start}-{end} out of bounds (1-{total}).")
        
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
        done += 1
        if on_progress:
            on_progress(done, len(ranges))
    
    return output_files

def merge_pdfs(files, output_path, reverse_order=False, reverse_pages_each=False, rotate=0, on_progress=None):
    """Merge multiple PDFs into one file"""
    if reverse_order:
        files = list(reversed(files))
    
    merger = PdfMerger()
    total = len(files)
    done = 0

    for fp in files:
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

        done += 1
        if on_progress:
            on_progress(done, total)

    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()

# ===============================================================================
# UI COMPONENTS
# ===============================================================================

class Tooltip:
    """Tooltip widget for hover help"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _e=None):
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

    def hide(self, _e=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class PDFPreview:
    """PDF Preview widget with navigation"""
    def __init__(self, parent):
        self.parent = parent
        self.pdf_path = None
        self.current_pages = []
        self.all_images = []
        self.current_range_index = 0
        self.current_page_in_range = 0
        self.photo = None
        
        # Create preview frame
        self.frame = ttk.Frame(parent)
        
        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill="x", pady=(0, 8))
        self.page_label = ttk.Label(header, text="No PDF loaded", style="Sub.TLabel")
        self.page_label.pack(side="left")
        
        # Canvas for PDF display
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#1e293b", highlightthickness=0)
        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(fill="x")
        
        # Navigation controls
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
        """Load PDF and convert pages to images"""
        if not PREVIEW_AVAILABLE:
            self.show_message("Preview not available\n\nInstall: pip install pdf2image Pillow\nAlso install poppler-utils")
            return False
        
        try:
            self.pdf_path = pdf_path
            if status_callback:
                status_callback("Loading PDF preview...")
            
            self.all_images = convert_from_path(pdf_path, dpi=150)
            
            if status_callback:
                status_callback(f"Loaded {len(self.all_images)} pages")
            
            return True
        except Exception as e:
            self.show_message(f"Preview Error:\n{str(e)}")
            return False
    
    def show_pages(self, page_ranges=None):
        """Display pages based on ranges"""
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
            self.current_range_index = 0
            self.current_page_in_range = 0
            
            range_info = ", ".join([f"{s}-{e}" for s, e in page_ranges])
            self.range_label.config(text=f"Showing ranges: {range_info}")
        else:
            self.current_pages = list(range(len(self.all_images)))
            self.range_label.config(text=f"Showing all {len(self.all_images)} pages")
        
        self.display_current_page()
        self.update_buttons()
    
    def display_current_page(self):
        """Display the current page on canvas"""
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
        self.page_label.config(text=f"Page {actual_page} of {len(self.all_images)} (Viewing {self.current_page_in_range + 1}/{len(self.current_pages)})")
    
    def next_page(self):
        """Show next page"""
        if self.current_page_in_range < len(self.current_pages) - 1:
            self.current_page_in_range += 1
            self.display_current_page()
            self.update_buttons()
    
    def prev_page(self):
        """Show previous page"""
        if self.current_page_in_range > 0:
            self.current_page_in_range -= 1
            self.display_current_page()
            self.update_buttons()
    
    def update_buttons(self):
        """Enable/disable navigation buttons"""
        if self.current_page_in_range > 0:
            self.prev_btn.state(["!disabled"])
        else:
            self.prev_btn.state(["disabled"])
        
        if self.current_page_in_range < len(self.current_pages) - 1:
            self.next_btn.state(["!disabled"])
        else:
            self.next_btn.state(["disabled"])
    
    def show_message(self, message):
        """Show a message on canvas"""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 400
        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 300
        self.canvas.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text=message,
            fill="#94a3b8",
            font=("Segoe UI", 12),
            justify="center"
        )
        self.page_label.config(text="")
        self.prev_btn.state(["disabled"])
        self.next_btn.state(["disabled"])
    
    def clear(self):
        """Clear the preview"""
        self.pdf_path = None
        self.all_images = []
        self.current_pages = []
        self.canvas.delete("all")
        self.page_label.config(text="No PDF loaded")
        self.range_label.config(text="")
        self.prev_btn.state(["disabled"])
        self.next_btn.state(["disabled"])

# ===============================================================================
# MAIN APPLICATION
# ===============================================================================

class PDFToolApp:
    """Main application class"""
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Master Pro - Professional Document & Image Tools")
        self.root.geometry("1400x850")
        self.root.minsize(1000, 650)

        # Initialize variables
        self.dark = True
        
        # PDF Split variables
        self.file_path = tk.StringVar(master=self.root)
        self.output_dir = tk.StringVar(master=self.root)
        self.total_pages = tk.IntVar(master=self.root, value=0)
        self.rotate_split = tk.StringVar(master=self.root, value="0°")
        self.naming_pattern = tk.StringVar(master=self.root, value="Standard")
        
        # PDF Merge variables
        self.merge_files = []
        self.merge_output_dir = tk.StringVar(master=self.root)
        self.merge_output_name = tk.StringVar(master=self.root, value="merged.pdf")
        self.merge_rotate = tk.StringVar(master=self.root, value="0°")
        self.merge_rev_order = tk.BooleanVar(master=self.root, value=False)
        self.merge_rev_pages = tk.BooleanVar(master=self.root, value=False)

        # Image processing variables
        self.image_files = []
        self.image_output_dir = tk.StringVar(master=self.root)
        self.image_temp_dir = tk.StringVar(master=self.root)
        self.fuzz_percent = tk.IntVar(master=self.root, value=10)

        # Misc
        self.recent_files = []
        self.output_files = []
        self.pdf_preview = None

        self._setup_style()
        self._build_ui()
        self._apply_theme()

        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self._browse_file())
        self.root.bind("<Control-s>", lambda e: self._run_split())
        self.root.bind("<Control-m>", lambda e: self._run_merge())
        self.root.bind("<Control-r>", lambda e: self._reset_split())
        self.root.bind("<F1>", lambda e: self._help())
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _setup_style(self):
        """Setup ttk styles"""
        self.style = ttk.Style(master=self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.palette = {
            "dark": {
                "bg": "#0f172a", "panel": "#1e293b", "card": "#334155",
                "accent": "#3b82f6", "accent_hover": "#2563eb", 
                "success": "#10b981", "warning": "#f59e0b", "error": "#ef4444",
                "muted": "#94a3b8", "text": "#f1f5f9", "border": "#475569",
                "status": "#1e293b", "tab": "#1e293b", "input": "#0f172a"
            },
            "light": {
                "bg": "#f8fafc", "panel": "#ffffff", "card": "#f1f5f9",
                "accent": "#2563eb", "accent_hover": "#1d4ed8",
                "success": "#059669", "warning": "#d97706", "error": "#dc2626",
                "muted": "#64748b", "text": "#0f172a", "border": "#cbd5e1",
                "status": "#f1f5f9", "tab": "#ffffff", "input": "#ffffff"
            }
        }
        
        self.font_title = ("Segoe UI", 20, "bold")
        self.font_section = ("Segoe UI", 14, "bold")
        self.font_base = ("Segoe UI", 11)
        self.font_small = ("Segoe UI", 10)

        self.style.configure("Title.TLabel", font=self.font_title)
        self.style.configure("Section.TLabel", font=self.font_section)
        self.style.configure("Sub.TLabel", font=self.font_base)
        self.style.configure("Small.TLabel", font=self.font_small)
        self.style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=12)
        self.style.configure("Outline.TButton", font=self.font_base, padding=8)
        self.style.configure("Status.TLabel", padding=8)
        self.style.configure("Card.TFrame", relief="flat", borderwidth=0)

    def _build_ui(self):
        """Build the user interface"""
        # Header
        header = ttk.Frame(self.root, padding=16)
        header.pack(fill="x")
        
        title_frame = ttk.Frame(header)
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="📑 PDF Master Pro", style="Title.TLabel").pack(side="left")
        ttk.Label(title_frame, text="Professional Document & Image Tools", style="Small.TLabel").pack(side="left", padx=(12, 0))
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")
        self.mode_btn = ttk.Button(btn_frame, text="🌙 Dark Mode", command=self._toggle_theme, width=15)
        self.mode_btn.pack(side="right", padx=4)
        ttk.Button(btn_frame, text="❓ Help", command=self._help, width=10).pack(side="right", padx=4)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Create tabs
        self.tab_split = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_split, text="  📄 Split PDF  ")
        self._build_split_tab()

        self.tab_merge = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_merge, text="  🔗 Merge PDFs  ")
        self._build_merge_tab()

        self.tab_images = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_images, text="  🖼️ Images  ")
        self._build_image_tab()

        self.tab_info = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_info, text="  ℹ️ Info  ")
        self._build_info_tab()

    def _build_split_tab(self):
        """Build split PDF tab"""
        container = ttk.Frame(self.tab_split, padding=8)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=2, minsize=350)
        container.columnconfigure(1, weight=3, minsize=400)
        container.rowconfigure(0, weight=1)

        # Left panel with scrolling
        left_container = ttk.Frame(container)
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        canvas = tk.Canvas(left_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # File Selection
        file_card = self._create_card(scrollable_frame, "📂 Input File")
        file_card.pack(fill="x", pady=(0, 10))
        
        self.file_display = ttk.Label(file_card, text="No file selected", style="Sub.TLabel", wraplength=300)
        self.file_display.pack(anchor="w", pady=(6, 0))
        
        browse_btn = ttk.Button(file_card, text="📁 Browse PDF", command=self._browse_file, style="Accent.TButton")
        browse_btn.pack(fill="x", pady=(10, 0))
        
        self.page_info = ttk.Label(file_card, text="Total Pages: —", style="Sub.TLabel")
        self.page_info.pack(anchor="w", pady=(10, 0))

        # Range Configuration
        range_card = self._create_card(scrollable_frame, "✂️ Split Configuration")
        range_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(range_card, text="Define page ranges:", style="Sub.TLabel").pack(anchor="w", pady=(6, 3))
        
        examples = ttk.Frame(range_card)
        examples.pack(fill="x", pady=(0, 8))
        ttk.Label(examples, text="Ex: 1-4,5-8 or 4,8,12", style="Small.TLabel", foreground="#94a3b8").pack(side="left")
        
        self.range_entry = ttk.Entry(range_card, font=("Segoe UI", 11))
        self.range_entry.pack(fill="x", ipady=6)
        self.range_entry.bind("<KeyRelease>", self._on_range_key)
        
        self.range_status = ttk.Label(range_card, text="", style="Sub.TLabel", wraplength=300)
        self.range_status.pack(anchor="w", pady=(6, 0))

        # Output Settings
        output_card = self._create_card(scrollable_frame, "💾 Output Settings")
        output_card.pack(fill="x", pady=(0, 10))
        
        self.out_display = ttk.Label(output_card, text="No folder selected", style="Sub.TLabel", wraplength=300)
        self.out_display.pack(anchor="w", pady=(6, 0))
        
        ttk.Button(output_card, text="📂 Choose Output Folder", command=self._choose_output, style="Outline.TButton").pack(fill="x", pady=(10, 6))
        
        adv_frame = ttk.Frame(output_card)
        adv_frame.pack(fill="x", pady=(6, 0))
        
        rot_frame = ttk.Frame(adv_frame)
        rot_frame.pack(fill="x", pady=3)
        ttk.Label(rot_frame, text="Rotate:", style="Sub.TLabel").pack(side="left")
        ttk.Combobox(rot_frame, values=["0°", "90°", "180°", "270°"], textvariable=self.rotate_split, width=8, state="readonly").pack(side="left", padx=(10, 0))
        
        name_frame = ttk.Frame(adv_frame)
        name_frame.pack(fill="x", pady=3)
        ttk.Label(name_frame, text="Naming:", style="Sub.TLabel").pack(side="left")
        ttk.Combobox(name_frame, values=["Standard", "With Timestamp"], textvariable=self.naming_pattern, width=16, state="readonly").pack(side="left", padx=(10, 0))

        # Action buttons
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill="x", pady=(0, 10))
        
        self.split_btn = ttk.Button(action_frame, text="✂️ Split PDF", style="Accent.TButton", command=self._run_split)
        self.split_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.split_btn.state(["disabled"])
        
        ttk.Button(action_frame, text="↺ Reset", command=self._reset_split, style="Outline.TButton").pack(side="left")

        # Status
        status_card = self._create_card(scrollable_frame, "")
        status_card.pack(fill="x")
        
        self.split_status = ttk.Label(status_card, text="Ready to split", style="Sub.TLabel")
        self.split_status.pack(anchor="w", pady=(0, 4))
        
        self.split_progress = ttk.Progressbar(status_card, mode="determinate")
        self.split_progress.pack(fill="x")

        # Right panel - Preview
        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")

        preview_card = self._create_card(right, "📄 PDF Preview")
        preview_card.pack(fill="both", expand=True)
        
        self.pdf_preview = PDFPreview
