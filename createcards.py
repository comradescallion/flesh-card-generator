import os
import csv
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

CARD_WIDTH, CARD_HEIGHT = 400, 600
ITEM_WIDTH, ITEM_HEIGHT = 240, 240

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.getsize(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    return lines

def draw_center_text(draw, xy, text, fill, font):
    x = xy[0]
    y = xy[1]

    x -= font.getsize(text)[0] / 2
    y -= font.getsize(text)[1] / 2

    draw.text((x, y), text, fill, font)

def create_pdf(card_folder, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    margin = 20
    page_width, page_height = letter
    grid_width = page_width - 2 * margin
    grid_height = page_height - 2 * margin

    grid_cols = 3
    cell_width = grid_width / grid_cols
    cell_height = (cell_width / CARD_WIDTH) * CARD_HEIGHT
    grid_rows = int(grid_height / cell_height) # flexible based on how many fit

    card_files = [f for f in os.listdir(card_folder) if f.lower().endswith('.png')]

    for i in range(0, len(card_files), grid_rows * grid_cols):
        images_batch = card_files[i:i + grid_rows * grid_cols]
        c.showPage()

        print(f"Creating page {int(i / (grid_rows * grid_cols)) + 1}...")
        
        for idx, image_path in enumerate(images_batch):
            x_pos = margin + (idx % grid_cols) * cell_width
            y_pos = page_height - margin - ((idx // grid_cols) + 1) * cell_height
            
            c.drawInlineImage(os.path.join(output_folder, image_path), x_pos, y_pos, width=cell_width, height=cell_height)
            print(f"\tDrew card {idx + 1}: {image_path}")

    c.save()


    print("PDF created successfully!")

    

def create_card(name, type_, energy, trigger, description, output_path):
    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(card)
    template = Image.open("blank.png")

    card.paste(template, (0, 0))
    
    try:
        font = ImageFont.truetype("FLESH.ttf", 20)
        small_font = ImageFont.truetype("FLESH.ttf", 18)
        name_small_font = ImageFont.truetype("FLESH.ttf", 16)
        font_big = ImageFont.truetype("FLESH.ttf", 30)

        # font = ImageFont.truetype("DejaVuSans.ttf", 20)
        # small_font = ImageFont.truetype("DejaVuSans.ttf", 16)
        # spec_char_font = ImageFont.truetype("DejaVuSans.ttf", 25)
    except IOError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # draw.rectangle([5, 5, 395, 595], outline="black", width=3)
    # draw.rectangle([10, 10, 350, 50], outline="black", width=3)  # Name box
    # draw.rectangle([10, 50, 80, 80], outline="black", width=3)  # Type box
    # draw.rectangle([10, 450, 390, 580], outline="black", width=3)  # Description box
    
    # if text doesn't overlap, name text
    if font.getsize(name)[0] <= 256:
        draw.text((40, 48), name, fill="black", font=font)
    else:
        draw.text((40, 52), name, fill="black", font=name_small_font)


    draw_center_text(draw, (108, 100), type_, fill="black", font=small_font) # type text

    # if food, add '+'
    if type_.lower() == "food":
        draw.text((337 - font_big.getsize("+" + energy)[0], 38), "+" + energy, fill="black", font=font_big) # type text (food)
    else: 
        draw.text((337 - font_big.getsize(energy)[0], 38), energy, fill="black", font=font_big) # type text
    
    draw.text((48, 406), trigger, fill="black", font=font) # trigger text
    description_lines = wrap_text(description, small_font, 320) # description text
    y_offset = 450
    for line in description_lines:
        draw.text((48, y_offset), line, fill="black", font=small_font)
        y_offset += small_font.getsize(line)[1]

    # add item image
    try:
        item = Image.open("images/" + name + ".png")
        item = item.convert("RGBA")
        print(f"Added image of {name}")
    except IOError:
        item = Image.new("RGBA", (ITEM_WIDTH, ITEM_HEIGHT), "white")
        print(f"No image of {name} exists")

    item = item.resize((ITEM_WIDTH, ITEM_HEIGHT), Image.BICUBIC)
    card.paste(item, ((int)(CARD_WIDTH / 2) - (int)(ITEM_WIDTH / 2), 132), item)
    
    card.save(output_path)
    print(f"Saved: {output_path}")

def generate_cards_from_tsv(tsv_file, output_folder):
    with open(tsv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            name = row['Name']
            type_ = row['Type']
            energy = row['Energy']
            trigger = row['Trigger']
            description = row['Description']
            output_path = f"{output_folder}/{name.replace(' ', '_')}.png"
            create_card(name, type_, energy, trigger, description, output_path)

tsv_file = "database.tsv"
output_folder = "cards"
# empty folder before creating cards
for filename in os.listdir(output_folder):
    file_path = os.path.join(output_folder, filename)
    os.remove(file_path)

generate_cards_from_tsv(tsv_file, output_folder)

output_pdf = "cardsheet.pdf"
print("Creating PDF...")
create_pdf(output_folder, output_pdf)