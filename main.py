from datetime import datetime
import os
import random; random.seed()

from PIL import Image, ImageFont, ImageDraw

import dictionary as d

FONTS_DIR = "./fonts/"
IMAGES_DIR = "./images/"


def get_date_info() -> dict:
	date_info = {
		"day_of_week" : -1, # ISO-style day of week: Monday==1, Sunday==7
		"is_holy_day": False, # วันพระ
		"is_holiday": False, # Special holiday flags
		"holiday_name": ""
	}

	# 1.1 Get Day of Week
	# Monday = 1 ~ Sunday = 7
	date_info["day_of_week"] = datetime.now().isoweekday()

	# 1.2 Calculate Thai Lunar Calendar
	# https://th.wikipedia.org/wiki/%E0%B8%9B%E0%B8%8F%E0%B8%B4%E0%B8%97%E0%B8%B4%E0%B8%99%E0%B8%88%E0%B8%B1%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%84%E0%B8%95%E0%B8%B4%E0%B9%84%E0%B8%97%E0%B8%A2
	# https://en.wikipedia.org/wiki/Thai_lunar_calendar
	# 1.3 Check for Holiday, based on Lunar Calendar

	return date_info


def generate_greetings(date_info: dict) -> list():
	# 2.1 Generate based on day of week
	text_greet = d.greetings + d.dow_th.get(date_info["day_of_week"], "วันนี้")
	text_bless = d.blessings
	output = [text_greet, text_bless]

	# 2.2 Generate based on holidays
	return output


def get_stock_image(date_info: dict) -> Image:
	# 3.1 Flowers / Nature / Buddhist images
	# 3.2 Image color based on day of week
	image_list = [f.path for f in os.scandir(IMAGES_DIR)]
	image_path = random.choice(image_list)
	image = Image.open(image_path)

	# 3.3 Center crop to square image
	xy = image.size # Original Image Dimension
	dim = min(min(xy), 800) # Cropped Dimension, cap to 800
	half = round(dim/2) # Half of New Dimension
	c = [round(c/2) for c in xy] # Center Coordinate XY
	lurl = (c[0]-half, c[1]-half, c[0]+half, c[1]+half) # Left, Upper, Right, Lower
	image = image.crop(box=lurl)

	return image


def compose_image(date_info: dict, greetings: list, image: Image):
	# 4.1 Select random font / text styling 
	# 4.1.1 Select random font
	font_list = [f.path for f in os.scandir(FONTS_DIR)]
	font_path = random.choice(font_list)
	print(font_path)
	font = ImageFont.truetype(font_path, size=72, encoding="unic")

	# 4.2 Place text on image
	draw = ImageDraw.Draw(image)
	fill = d.text_fill[date_info["day_of_week"]] # Color by day of week
	stroke_fill = (255, 255, 255)
	coords = [(100, 100), (100, 200)]
	for text, xy in zip(greetings, coords):
		draw.text(
			xy, text, 
			font=font, 
			fill=fill, 
			stroke_fill=stroke_fill,
			stroke_width=3
		)

	# 4.3 Watermark image
	font = ImageFont.truetype(font_path, size=24, encoding="unic")
	xy = image.size
	xy = [c-20 for c in xy]
	draw.text(
		xy, 
		"@MorningGloryBot", 
		font=font,
		fill=(255, 255, 255),
		anchor="rb"
	)

	return image


def post_result(image: Image):
	# 5.1 Read credential
	# 5.2 Tweet
	image.show()
	return


if __name__ == "__main__":
	# Run this script on VM startup

	# 1. Get date info
	date_info = get_date_info()

	# 2. Generate random blessing
	greetings = generate_greetings(date_info)

	# 3. Get random stock image
	stock_image = get_stock_image(date_info)

	# 4. Generate blessing image
	output_image = compose_image(date_info, greetings, stock_image)

	# 5. Post to Twitter
	ret = post_result(output_image)

	# Auto-shutdown VM on success
	exit()