import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io
import os

class PDFEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("1200x800")
        
        # Store the current PDF
        self.current_pdf = None
        self.current_page = 0
        self.zoom_factor = 1.0
        
        # Create main frame
        self.main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for page list
        self.left_panel = ttk.Frame(self.main_frame)
        self.main_frame.add(self.left_panel, weight=1)
        
        # Create right panel for page view and editing
        self.right_panel = ttk.Frame(self.main_frame)
        self.main_frame.add(self.right_panel, weight=4)
        
        # Create UI elements
        self.create_toolbar()
        self.create_page_list()
        self.create_page_viewer()
        self.create_text_editor()
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Delete Page", command=self.delete_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Rotate Page", command=self.rotate_page).pack(side=tk.LEFT, padx=5)
        
        # Add zoom controls
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        
    def create_page_list(self):
        # Create frame for listbox and scrollbar
        list_frame = ttk.Frame(self.left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create listbox
        self.page_listbox = tk.Listbox(list_frame)
        self.page_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        self.page_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.page_listbox.yview)
        
        # Bind selection event
        self.page_listbox.bind('<<ListboxSelect>>', self.on_page_select)
        
    def create_page_viewer(self):
        # Create a frame to hold the canvas and scrollbars
        self.canvas_frame = ttk.Frame(self.right_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self.canvas_frame, bg='gray90',
                              yscrollcommand=self.v_scrollbar.set,
                              xscrollcommand=self.h_scrollbar.set)
        
        # Configure scrollbar commands
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind mouse wheel event for scrolling
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Shift-MouseWheel>', self.on_shift_mousewheel)
        
    def create_text_editor(self):
        # Create text editor frame
        self.editor_frame = ttk.Frame(self.right_panel)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget with scrollbar
        editor_scroll = ttk.Scrollbar(self.editor_frame)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_editor = tk.Text(self.editor_frame, wrap=tk.WORD, height=10,
                                 yscrollcommand=editor_scroll.set)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        editor_scroll.config(command=self.text_editor.yview)
        
    def on_mousewheel(self, event):
        # Windows
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta/120)), "units")
        # Linux
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
                
    def on_shift_mousewheel(self, event):
        # Horizontal scrolling with Shift + mousewheel
        if event.delta:
            self.canvas.xview_scroll(int(-1 * (event.delta/120)), "units")
        
    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                self.current_pdf = fitz.open(file_path)
                self.update_page_list()
                self.current_page = 0
                self.display_page(self.current_page)
                messagebox.showinfo("Success", "PDF loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading PDF: {str(e)}")
                
    def update_page_list(self):
        self.page_listbox.delete(0, tk.END)
        if self.current_pdf:
            for i in range(len(self.current_pdf)):
                self.page_listbox.insert(tk.END, f"Page {i + 1}")
                
    def on_page_select(self, event):
        selection = self.page_listbox.curselection()
        if selection:
            self.current_page = selection[0]
            self.display_page(self.current_page)
            
    def display_page(self, page_number):
        if not self.current_pdf:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Get page
        page = self.current_pdf[page_number]
        
        # Get page dimensions
        zoom_matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=zoom_matrix)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Extract and display text
        text = page.get_text()
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, text)
        
    def save_pdf(self):
        if not self.current_pdf:
            messagebox.showerror("Error", "No PDF is currently open")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.current_pdf.save(file_path)
                messagebox.showinfo("Success", "PDF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving PDF: {str(e)}")
                
    def delete_page(self):
        if not self.current_pdf:
            messagebox.showerror("Error", "No PDF is currently open")
            return
            
        self.current_pdf.delete_page(self.current_page)
        self.update_page_list()
        self.current_page = min(self.current_page, len(self.current_pdf) - 1)
        if self.current_page >= 0:
            self.display_page(self.current_page)
            
    def rotate_page(self):
        if not self.current_pdf:
            messagebox.showerror("Error", "No PDF is currently open")
            return
            
        page = self.current_pdf[self.current_page]
        page.set_rotation((page.rotation + 90) % 360)
        self.display_page(self.current_page)
        
    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.display_page(self.current_page)
        
    def zoom_out(self):
        self.zoom_factor *= 0.8
        self.display_page(self.current_page)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditor(root)
    root.mainloop()