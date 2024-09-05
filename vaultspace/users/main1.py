import numpy as np
from PIL import Image, PngImagePlugin
import os
import datetime
from tkinter import Tk
from tkinter import filedialog
import hashlib

def generate_shares(input_file_path):
    # Load the input image
    image = np.array(Image.open(input_file_path).convert('L'))  # Convert to grayscale

    # Binarize the image (convert to black and white) using a simple thresholding technique
    binary_image = np.where(image > 128, 1, 0).astype(np.uint8)

    # Generate random binary shares
    share1 = np.random.randint(0, 2, size=binary_image.shape, dtype=np.uint8)
    share2 = binary_image ^ share1  # XOR to create the second share

    return share1 * 255, share2 * 255  # Convert shares back to [0, 255] range for saving as images

def calculate_hash(image_array):
    """Calculate the SHA-256 hash of an image array."""
    return hashlib.sha256(image_array.tobytes()).hexdigest()

def save_image_with_hash(image_array, file_path, hash_value):
    """Save an image with a hash stored in its metadata."""
    image = Image.fromarray(image_array)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("hash", hash_value)
    image.save(file_path, pnginfo=meta)

# Create a root window
root = Tk()
root.withdraw()

# Select an input image file
print("Please select an input image file.")
input_file_path = filedialog.askopenfilename(title="Select Input Image")

if not input_file_path:
    print("No input file selected. Exiting.")
    exit()

# Generate shares
server_share, user_share = generate_shares(input_file_path)

# Calculate hashes for the shares
server_share_hash = calculate_hash(server_share)
user_share_hash = calculate_hash(user_share)

# Save the server-side share with the hash
script_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
server_share_path = os.path.join(script_dir, f"server_share_{timestamp}.png")
save_image_with_hash(server_share, server_share_path, server_share_hash)
print(f"Server-side share saved with hash as '{server_share_path}'")

# Ask the user where to save the user share image
print("Please choose where to save the user share image.")
user_share_path = filedialog.asksaveasfilename(
    title="Save User Share Image",
    defaultextension=".png",
    filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
)

if not user_share_path:
    print("No output location selected. The user share will not be saved.")
else:
    # Save the user share with the hash
    save_image_with_hash(user_share, user_share_path, user_share_hash)
    print(f"User share saved with hash as '{user_share_path}'")

print("Shares generated, saved, and hashes embedded in metadata.")
