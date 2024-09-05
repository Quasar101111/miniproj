import numpy as np
from PIL import Image
import hashlib
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

def calculate_hash(image_array):
    """Calculate the SHA-256 hash of an image array."""
    return hashlib.sha256(image_array.tobytes()).hexdigest()

def get_hash_from_image(image_path):
    """Retrieve the stored hash from an image's metadata."""
    image = Image.open(image_path)
    hash_value = image.info.get("hash")
    if hash_value is None:
        raise ValueError(f"No hash found in image metadata for {image_path}")
    return hash_value

def authenticate_shares(server_share_path, user_share_path):
    """Authenticate shares by comparing their hashes and reconstructing the image."""
    # Load the shares from images
    server_share = np.array(Image.open(server_share_path).convert('L'))
    user_share = np.array(Image.open(user_share_path).convert('L'))

    # Retrieve the stored hashes from the image metadata
    expected_server_hash = get_hash_from_image(server_share_path)
    expected_user_hash = get_hash_from_image(user_share_path)

    # Calculate the actual hashes of the provided shares
    actual_server_hash = calculate_hash(server_share)
    actual_user_hash = calculate_hash(user_share)

    # Compare the actual hashes with the expected hashes
    if actual_server_hash != expected_server_hash:
        raise ValueError("Server share hash does not match. Authentication failed.")
    if actual_user_hash != expected_user_hash:
        raise ValueError("User share hash does not match. Authentication failed.")

    # Reconstruct the image from the shares using XOR operation
    reconstructed_image = np.round(np.logical_xor(server_share / 255, user_share / 255)).astype(np.uint8) * 255
    
    return reconstructed_image

def main():
    """Main function"""
    # Create a root window
    root = tk.Tk()
    root.withdraw()

    # Ask user to select the share images
    print("Please select the user share image.")
    user_share_path = filedialog.askopenfilename(title="Select User Share Image",
                                                 filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if not user_share_path:
        print("No user share image selected. Exiting.")
        exit()

    print("Please select the server share image.")
    server_share_path = filedialog.askopenfilename(title="Select Server Share Image",
                                                   filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if not server_share_path:
        print("No server share image selected. Exiting.")
        exit()

    try:
        reconstructed_image = authenticate_shares(server_share_path, user_share_path)
        # Display the reconstructed image
        plt.imshow(reconstructed_image, cmap='gray')
        plt.title('Reconstructed Image')
        plt.axis('off')
        plt.show()
        print("Authentication successful. Reconstructed image displayed.")
    except Exception as e:
        print(f"Authentication failed: {str(e)}")

if __name__ == "__main__":
    main()
