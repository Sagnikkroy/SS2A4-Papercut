import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

class ScreenshotStitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A4 Screenshot Arranger - Pro Layout")
        self.root.geometry("500x550")

        self.image_paths = []

        # UI Elements
        self.label = tk.Label(root, text="Screenshots to Combine:", font=('Arial', 12, 'bold'))
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=60, height=15)
        self.listbox.pack(padx=20, pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Images", command=self.add_images).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Move Up", command=self.move_up).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Move Down", command=self.move_down).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Remove", command=self.remove_item).grid(row=0, column=3, padx=5)

        tk.Button(root, text="Generate A4 PDF", command=self.generate_pdf, bg="#2ecc71", fg="white", font=('Arial', 10, 'bold'), height=2).pack(pady=20)

    def add_images(self):
        files = filedialog.askopenfilenames(title="Select Screenshots", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if files:
            for f in files:
                self.image_paths.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def move_up(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == 0: return
        i = idx[0]
        self.image_paths[i], self.image_paths[i-1] = self.image_paths[i-1], self.image_paths[i]
        self._refresh_listbox(i-1)

    def move_down(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == len(self.image_paths) - 1: return
        i = idx[0]
        self.image_paths[i], self.image_paths[i+1] = self.image_paths[i+1], self.image_paths[i]
        self._refresh_listbox(i+1)

    def remove_item(self):
        idx = self.listbox.curselection()
        if not idx: return
        self.image_paths.pop(idx[0])
        self.listbox.delete(idx)

    def _refresh_listbox(self, select_idx):
        self.listbox.delete(0, tk.END)
        for p in self.image_paths:
            self.listbox.insert(tk.END, os.path.basename(p))
        self.listbox.select_set(select_idx)

    def generate_pdf(self):
        if not self.image_paths:
            messagebox.showwarning("Error", "Please add some images first!")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not save_path: return

        try:
            self.process_images(save_path)
            messagebox.showinfo("Success", f"PDF created successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def process_images(self, output_path):
        # A4 Constants at 300 DPI
        A4_W, A4_H = 2480, 3508
        
        # --- ADJUST THESE VALUES TO CONTROL SPACING ---
        SIDE_MARGIN = 300        # Large left/right space to make images smaller
        TOP_BOTTOM_MARGIN = 150  # Space at the very top and bottom of page
        GAP_BETWEEN_IMAGES = 100 # Vertical space between screenshots
        # ----------------------------------------------

        pages = []
        current_page = Image.new('RGB', (A4_W, A4_H), (255, 255, 255))
        y_offset = TOP_BOTTOM_MARGIN
        
        max_draw_width = A4_W - (2 * SIDE_MARGIN)

        for path in self.image_paths:
            img = Image.open(path).convert("RGB")
            
            # Calculate new size based on the restricted width
            aspect = img.height / img.width
            new_w = max_draw_width
            new_h = int(new_w * aspect)
            
            # If a single image is still taller than the page, scale it down
            if new_h > (A4_H - (2 * TOP_BOTTOM_MARGIN)):
                new_h = A4_H - (2 * TOP_BOTTOM_MARGIN)
                new_w = int(new_h / aspect)

            resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Check if this image fits or if we need a new page
            if y_offset + new_h + TOP_BOTTOM_MARGIN > A4_H:
                pages.append(current_page)
                current_page = Image.new('RGB', (A4_W, A4_H), (255, 255, 255))
                y_offset = TOP_BOTTOM_MARGIN

            # Paste image (Centered horizontally)
            x_centering = (A4_W - new_w) // 2
            current_page.paste(resized_img, (x_centering, y_offset))
            
            # Update offset for next image
            y_offset += new_h + GAP_BETWEEN_IMAGES

        pages.append(current_page)
        pages[0].save(output_path, save_all=True, append_images=pages[1:], resolution=300.0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotStitcherApp(root)
    root.mainloop()