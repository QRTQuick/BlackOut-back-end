from PIL import Image

def convert_image(input_path, output_path, fmt):
    img = Image.open(input_path)
    
    # Convert RGB if saving as JPEG (JPEG doesn't support transparency)
    if fmt.lower() in ['jpg', 'jpeg']:
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        fmt = 'JPEG'  # PIL uses 'JPEG' not 'JPG'
    
    img.save(output_path, fmt.upper())