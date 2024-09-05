# users/utils/image_processing.py

import numpy as np
from PIL import Image, PngImagePlugin
import hashlib
import io
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage












def calculate_hash(image_array):
    """Calculate the SHA-256 hash of an image array.
     :param image_array: numpy array of the image
    :return: hexadecimal string of the hash
    """
    return hashlib.sha256(image_array.tobytes()).hexdigest()

def save_image_with_hash(image_array, file_path, hash_value):
    """
    Save an image with a hash stored in its metadata.
    
    :param image_array: numpy array of the image
    :param file_path: path where the image will be saved
    :param hash_value: hash to be stored in the image metadata
    """
    image = Image.fromarray(image_array)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("hash", hash_value)
    image.save(file_path, pnginfo=meta)

def generate_shares(input_image):
    """
    Generate two shares from the input image.
    
    :param input_image: Django UploadedFile object
    :return: tuple of two numpy arrays (server_share, user_share)
    """
    image = np.array(Image.open(input_image).convert('L'))  # Convert to grayscale
    binary_image = np.where(image > 128, 1, 0).astype(np.uint8)  # Binarize the image
    share1 = np.random.randint(0, 2, size=binary_image.shape, dtype=np.uint8)
    share2 = binary_image ^ share1  # XOR to create the second share
    return share1 * 255, share2 * 255  # Convert shares back to [0, 255] range

def get_hash_from_image(image_path):
    """
    Retrieve the stored hash from an image's metadata.
    
    :param image_path: path of the image file
    :return: hash value stored in the image metadata
    """
    image = Image.open(image_path)
    hash_value = image.info.get("hash")
    if hash_value is None:
        raise ValueError(f"No hash found in image metadata for {image_path}")
    return hash_value