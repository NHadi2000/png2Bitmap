import os
from PIL import Image

# Configuration
WIDTH = 10 #25  # Width of each character
HEIGHT = 15 #40  # Height of each character
OUTPUT_C_FILE = "font_ascii_output.c"
PLACEHOLDER = "________"  # Placeholder for empty rows
ASCII_START = 0x30  # Starting ASCII character (e.g., '0')
ASCII_END = 0x3A #0x39    # Ending ASCII character (e.g., '9')

# Map binary values to macros
BIT_TO_MACRO = {i: f"{format(i, '08b').replace('0', '_').replace('1', 'X')}" for i in range(256)}

# Function to process a single row into 8-bit groups WITHOUT leading padding
def convert_row_to_8bit_groups(row):
    groups = []
    byte = 0
    bit_count = 0

    for pixel in row:
        bit = 1 if pixel == 0 else 0  # Black -> 1, White -> 0
        byte = (byte << 1) | bit
        bit_count += 1

        if bit_count == 8:  # If 8 bits are packed, add to groups
            groups.append(BIT_TO_MACRO[byte])
            byte = 0
            bit_count = 0

    # Handle remaining bits in the last group (skip leading `_` padding)
    if bit_count > 0:
        byte = byte << (8 - bit_count)  # Pad remaining bits with zeros (only at the end)
        groups.append(BIT_TO_MACRO[byte])

    return groups

# Function to process an image into rows of macros split into columns
def process_image(image_path):
    img = Image.open(image_path).convert("L")  # Convert to grayscale
    img = img.point(lambda px: 0 if px < 128 else 255, "1")  # Threshold to monochrome
    img_resized = img.resize((WIDTH, HEIGHT))  # Resize to 25x40

    bitmap = []
    for y in range(img_resized.height):
        row = [img_resized.getpixel((x, y)) for x in range(img_resized.width)]
        bitmap.append(convert_row_to_8bit_groups(row))
    return bitmap

# Generate the C file
def generate_c_file(image_folder):
    available_images = {f.split('-')[0]: f for f in os.listdir(image_folder) if f.endswith('.png')}
    print("Available images:", available_images)

    c_data = "const uint8_t font_table[][40 * 4] = {\n"

    for ascii_code in range(ASCII_START, ASCII_END + 1):
        char = chr(ascii_code)
        char = check_char(char)
        comment = f"// 0x{ascii_code:02X} (ASCII '{char}')"
        image_name = available_images.get(char, None) #check image base on character

        if image_name:
            image_path = os.path.join(image_folder, image_name)
            bitmap = process_image(image_path)
        else:
            bitmap = [[PLACEHOLDER] * ((WIDTH + 7) // 8)] * HEIGHT  # Placeholder for missing rows

        # Format C output
        c_data += f"{comment}\n {{\n"
        c_data += f"   f6x8_MONO_WIDTH,\n   f6x8_MONO_HEIGHT,\n"
        for row in bitmap:
            c_data += "   " + ", ".join(row) + ",\n"
        c_data += "  },\n"

    c_data += "};\n"

    with open(OUTPUT_C_FILE, "w", encoding="utf-8") as f:
        f.write(c_data)
    print(f"C file generated: {OUTPUT_C_FILE}")

def check_char(char):
    if char == ':':
        char = "colon"
    return char

def user_input():
    global WIDTH
    global HEIGHT
    global OUTPUT_C_FILE
    WIDTH, HEIGHT = map(int, input("Enter width and height separated by space: ").split())
    print("First number:", WIDTH)
    print("Second number:", HEIGHT)
    OUTPUT_C_FILE = input("Enter output file name: ")
    print(">> ", OUTPUT_C_FILE)


# Run the script
if __name__ == "__main__":
    user_input()
    # WIDTH, HEIGHT = input("Enter width and height separated by space: ").split()
    # print("First number:", WIDTH)
    # print("Second number:", HEIGHT)

    image_folder = r"./"  # Replace with your actual folder
    generate_c_file(image_folder)

    

