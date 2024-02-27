import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import threading
import time

MARKER = "1010101010101010"  # Reserved pattern as the marker


def text_to_binary(text):
    binary_code = "".join(format(ord(char), "08b") for char in text)
    return binary_code


def binary_to_text(binary):
    return "".join(chr(int(binary[i : i + 8], 2)) for i in range(0, len(binary), 8))


def check_fitness(message, pixels):
    message_length = len(message)
    if message_length > pixels:
        raise ValueError("Message is too large to be embedded in the image.")


def encode_image():
    # Get image path
    image_path = filedialog.askopenfilename(title="Choose Image to Encode")
    if not image_path:
        return

    # Display chosen image in the box
    img = Image.open(image_path)
    img.thumbnail((300, 300))
    img = ImageTk.PhotoImage(img)
    label_img.config(image=img)
    label_img.image = img

    # Get secret message
    secret_message = entry_secret.get()

    # Get encoded image path
    encoded_image_path = filedialog.asksaveasfilename(title="Save Encoded Image As")
    if not encoded_image_path:
        return

    # Create an encoding animation
    encoding_animation = EncodingAnimation(label_img)
    encoding_animation.start()

    # Encode the secret message into the cover image in a separate thread
    encode_thread = threading.Thread(
        target=perform_encoding,
        args=(image_path, secret_message, encoded_image_path, encoding_animation),
    )
    encode_thread.start()


def perform_encoding(image_path, secret_message, encoded_image_path, animation):
    try:
        cover_image = Image.open(image_path)
        width, height = cover_image.size
        binary_message = text_to_binary(secret_message)
        binary_message += MARKER
        check_fitness(binary_message, width * height * 3)
        img_array = np.array(cover_image)
        img_flat = img_array.flatten()
        for index, bit in enumerate(binary_message):
            bit_value = int(bit)
            pixel_value = img_flat[index]
            modified_value = (pixel_value & 0xFE) | bit_value
            img_flat[index] = modified_value
            time.sleep(0.01)  # Simulate encoding delay for animation
            animation.update_progress(
                index / len(img_flat)
            )  # Update progress in animation
        stego_array = img_flat.reshape(height, width, -1)
        stego_image = Image.fromarray(stego_array.astype("uint8"))
        stego_image.save(encoded_image_path)
        messagebox.showinfo("Success", "Message embedded successfully.")
        # Clear secret message entry after encoding
        entry_secret.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        animation.stop()  # Stop encoding animation


class EncodingAnimation:
    def __init__(self, parent):
        self.parent = parent
        self.progress = 0
        self.running = False
        self.label_animation = tk.Label(parent)
        self.label_animation.pack()

    def start(self):
        self.running = True
        self.update_animation()

    def stop(self):
        self.running = False

    def update_animation(self):
        if self.running:
            self.label_animation.config(
                text="Encoding... {:.0f}%".format(self.progress * 100)
            )
            if self.progress >= 1:
                self.progress = 1
                self.label_animation.config(text="Encoding... 100%")
            else:
                self.progress += 0.01
            self.parent.after(10, self.update_animation)
        else:
            self.label_animation.config(text="")

    def update_progress(self, progress):
        self.progress = progress


def decode_image():
    # Get encoded image path
    encoded_image_path = filedialog.askopenfilename(
        title="Choose Encoded Image to Decode"
    )
    if not encoded_image_path:
        return

    # Decode the secret message from the stego image
    try:
        stego_image = Image.open(encoded_image_path)
        stego_array = np.array(stego_image)
        stego_flat = stego_array.flatten()
        binary_message = ""
        for pixel in stego_flat:
            bit = str(pixel & 1)
            binary_message += bit
            if binary_message.endswith(MARKER):
                binary_message = binary_message[: -len(MARKER)]
                break
        message = binary_to_text(binary_message)
        messagebox.showinfo("Decoded Message", message)
        # Clear secret message entry after decoding
        entry_secret.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Create main window
root = tk.Tk()
root.title("Steganography Image Encoder/Decoder")

# Create and pack widgets
placeholder_img = Image.open("placeholder.jpg")  # You can use any placeholder image
placeholder_img.thumbnail((300, 300))
placeholder_img = ImageTk.PhotoImage(placeholder_img)
label_img = tk.Label(root, image=placeholder_img)
label_img.pack()

label_secret = tk.Label(root, text="Secret Message:")
label_secret.pack()

entry_secret = tk.Entry(root, width=50)
entry_secret.pack()

encode_button = tk.Button(root, text="Encode", command=encode_image)
encode_button.pack()

decode_button = tk.Button(root, text="Decode", command=decode_image)
decode_button.pack()

root.mainloop()
