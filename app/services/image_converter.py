from PIL import Image

def convert_image(input_path, output_path, fmt):
    img = Image.open(input_path)
    img.save(output_path, fmt.upper())