import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance


def tilt_images_gui():
    def load_image():
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if not file_path:
            return
        try:
            global original_image
            original_image = Image.open(file_path).convert("RGB")
            process_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def process_image():
        try:
            if not original_image:
                return

            # Scale and tilt the images
            left_scale = left_size_slider.get() / 100  # Convert to decimal percentage
            right_scale = right_size_slider.get() / 100  # Convert to decimal percentage

            left_image = original_image.resize(
                (int(original_image.width * left_scale), int(original_image.height * left_scale)),
                Image.Resampling.LANCZOS
            ).rotate(-0.7, resample=Image.BICUBIC, expand=True)

            right_image = original_image.resize(
                (int(original_image.width * right_scale), int(original_image.height * right_scale)),
                Image.Resampling.LANCZOS
            ).rotate(0.7, resample=Image.BICUBIC, expand=True)

            # Apply RGB adjustments
            left_image = adjust_rgb(left_image, left_red_slider.get(), left_green_slider.get(), left_blue_slider.get())
            right_image = adjust_rgb(right_image, right_red_slider.get(), right_green_slider.get(), right_blue_slider.get())

            # Create combined canvas
            spacing = spacing_slider.get()
            total_width = left_image.width + right_image.width + spacing
            max_height = max(left_image.height, right_image.height)

            global combined_image
            combined_image = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
            combined_image.paste(left_image, (0, (max_height - left_image.height) // 2))
            combined_image.paste(right_image, (left_image.width + spacing, (max_height - right_image.height) // 2))

            # Display the result in the GUI
            display_image(combined_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")

    def adjust_rgb(image, red_offset, green_offset, blue_offset):
        r, g, b = image.split()
        r = r.point(lambda p: max(0, min(255, p + red_offset)))
        g = g.point(lambda p: max(0, min(255, p + green_offset)))
        b = b.point(lambda p: max(0, min(255, p + blue_offset)))
        return Image.merge("RGB", (r, g, b))

    def display_image(image):
        # Resize the image just for display in the GUI
        image_display = image.copy()
        image_display.thumbnail((800, 400))  # Resize to fit the GUI (preview)
        tk_image = ImageTk.PhotoImage(image_display)
        image_label.configure(image=tk_image)
        image_label.image = tk_image

        # Enable the save button
        def save_image():
            if combined_image is not None:
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
                )
                if save_path:
                    try:
                        # Save the original combined image without resizing
                        combined_image.save(save_path)
                        messagebox.showinfo("Success", f"Image saved to {save_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save image: {e}")
            else:
                messagebox.showerror("Error", "No image to save")

        save_button.config(state="normal", command=save_image)

    # Set up the GUI
    root = tk.Tk()
    root.title("Image Tilt GUI with RGB Adjustment")
    root.geometry("900x600")  # Set initial window size

    # Create a scrollable frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    global original_image, combined_image
    original_image = None
    combined_image = None  # This will store the full-size image for saving

    # Widgets
    load_button = tk.Button(scrollable_frame, text="Load Image", command=load_image, font=("Arial", 14))
    load_button.pack(pady=10)

    global image_label
    image_label = tk.Label(scrollable_frame)
    image_label.pack(pady=10)

    # Sliders
    slider_frame = tk.Frame(scrollable_frame)
    slider_frame.pack(pady=10)

    spacing_label = tk.Label(slider_frame, text="Spacing:", font=("Arial", 12))
    spacing_label.grid(row=0, column=0, padx=5)
    spacing_slider = tk.Scale(slider_frame, from_=0, to=200, orient="horizontal", command=lambda x: process_image())
    spacing_slider.set(50)  # Default spacing
    spacing_slider.grid(row=0, column=1, padx=5)

    left_size_label = tk.Label(slider_frame, text="Left Size (%):", font=("Arial", 12))
    left_size_label.grid(row=1, column=0, padx=5)
    left_size_slider = tk.Scale(slider_frame, from_=0, to=100, orient="horizontal", resolution=1, command=lambda x: process_image())
    left_size_slider.set(100)  # Default scale (100%)
    left_size_slider.grid(row=1, column=1, padx=5)

    right_size_label = tk.Label(slider_frame, text="Right Size (%):", font=("Arial", 12))
    right_size_label.grid(row=2, column=0, padx=5)
    right_size_slider = tk.Scale(slider_frame, from_=0, to=100, orient="horizontal", resolution=1, command=lambda x: process_image())
    right_size_slider.set(100)  # Default scale (100%)
    right_size_slider.grid(row=2, column=1, padx=5)

    rgb_frame = tk.Frame(scrollable_frame)
    rgb_frame.pack(pady=10)

    # Left Image RGB Adjustments
    tk.Label(rgb_frame, text="Left Image RGB", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=5)
    left_red_slider = tk.Scale(rgb_frame, from_=-255, to=0, orient="horizontal", label="Red", command=lambda x: process_image())
    left_red_slider.grid(row=1, column=0, padx=5)
    left_green_slider = tk.Scale(rgb_frame, from_=-255, to=0, orient="horizontal", label="Green", command=lambda x: process_image())
    left_green_slider.grid(row=2, column=0, padx=5)
    left_blue_slider = tk.Scale(rgb_frame, from_=-255, to=0, orient="horizontal", label="Blue", command=lambda x: process_image())
    left_blue_slider.grid(row=3, column=0, padx=5)

    # Right Image RGB Adjustments
    tk.Label(rgb_frame, text="Right Image RGB", font=("Arial", 12)).grid(row=0, column=2, columnspan=2, pady=5)
    right_red_slider = tk.Scale(rgb_frame, from_=-255, to=0, orient="horizontal", label="Red", command=lambda x: process_image())
    right_red_slider.grid(row=1, column=2, padx=5)
    right_green_slider = tk.Scale(rgb_frame, from_=-255, to=0, orient="horizontal", label="Green", command=lambda x: process_image())
    right_green_slider.grid(row=2, column=2, padx=5)
    right_blue_slider = tk.Scale(rgb_frame, from_=-255, to=0, orient="horizontal", label="Blue", command=lambda x: process_image())
    right_blue_slider.grid(row=3, column=2, padx=5)

    # Save button
    save_button = tk.Button(scrollable_frame, text="Save Image", font=("Arial", 14), state="disabled")
    save_button.pack(pady=10)

    root.mainloop()

# Run the program
if __name__ == "__main__":
    tilt_images_gui()
