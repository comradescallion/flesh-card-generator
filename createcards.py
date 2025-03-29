import csv
from PIL import Image, ImageDraw, ImageFont

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

def create_card(name, type_, energy, trigger, description, output_path):
    card_width, card_height = 400, 600
    card = Image.new("RGB", (card_width, card_height), "white")
    draw = ImageDraw.Draw(card)
    
    try:
        # font = ImageFont.truetype("Excalifont-Regular.ttf", 20)
        # small_font = ImageFont.truetype("Excalifont-Regular.ttf", 16)

        font = ImageFont.truetype("DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 16)
        spec_char_font = ImageFont.truetype("DejaVuSans.ttf", 25)
    except IOError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    draw.rectangle([5, 5, 395, 595], outline="black", width=3)
    draw.rectangle([10, 10, 350, 50], outline="black", width=3)  # Name box
    draw.rectangle([275, 15, 345, 45], outline="black", width=3)  # Type box
    draw.rectangle([10, 450, 390, 580], outline="black", width=3)  # Description box
    
    # if text doesn't overlap
    if font.getsize(name)[0] <= 300:
        draw.text((20, 20), name, fill="black", font=font)
    else:
        draw.text((20, 20), name, fill="black", font=small_font)

    draw.text((287, 21), type_, fill="black", font=small_font)
    draw.text((355, 15), energy + "⚡", fill="black", font=spec_char_font)
    
    draw.text((20, 460), trigger, fill="black", font=font)
    description_lines = wrap_text(description, small_font, 360)
    y_offset = 490
    for line in description_lines:
        draw.text((20, y_offset), line, fill="black", font=small_font)
        y_offset += small_font.getsize(line)[1]
    
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
generate_cards_from_tsv(tsv_file, output_folder)

