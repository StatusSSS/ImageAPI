from pathlib import Path
import os
import imageio.v2 as imageio
from skimage import color, transform

PROCESSED_DIR = Path("./app/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def resize_image_imageio(image_path, output_size):
    img = imageio.imread(image_path)
    img_resized = transform.resize(img, output_size, anti_aliasing=True)
    new_path = f"{PROCESSED_DIR}/{output_size[0]}x{output_size[1]}_" + os.path.basename(image_path)
    imageio.imwrite(new_path, (img_resized * 255).astype('uint8'))
    return new_path

def convert_to_grayscale_imageio(image_path):
    img = imageio.imread(image_path)
    gray_img = color.rgb2gray(img)
    new_path = f"{PROCESSED_DIR}/grey_" + os.path.basename(image_path)
    imageio.imwrite(new_path, (gray_img * 255).astype('uint8'))
    return new_path

