from datetime import datetime
import json
import os
import random; random.seed()

from PIL import Image, ImageFont, ImageDraw
from twitter import Twitter, OAuth

import dictionary as d

FONTS_DIR = "./fonts/"
IMAGES_DIR = "./images/"

CREDENTIALS = "credentials.json"


def get_date_info() -> dict:
	date_info = {
		"dow" : -1, # ISO-style day of week: Monday==1, Sunday==7
		"holy": False, # วันพระ
		"holiday": False, # Special holiday flags
		"holiday_name": ""
	}

	# 1.1 Get ISO Day of Week
	# Monday = 1 ~ Sunday = 7
	date_info["dow"] = datetime.now().isoweekday()

	# 1.2 Calculate Thai Lunar Calendar
	# https://th.wikipedia.org/wiki/%E0%B8%9B%E0%B8%8F%E0%B8%B4%E0%B8%97%E0%B8%B4%E0%B8%99%E0%B8%88%E0%B8%B1%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%84%E0%B8%95%E0%B8%B4%E0%B9%84%E0%B8%97%E0%B8%A2
	# https://en.wikipedia.org/wiki/Thai_lunar_calendar
	# 1.3 Check for Holiday, based on Lunar Calendar

	return date_info


def generate_greetings(date_info: dict) -> list():
	# 2.1 Generate based on day of week
	text_greet = d.greetings + d.dow_th.get(date_info["dow"], "วันนี้")
	text_bless = d.blessings
	output = [text_greet, text_bless]

	# 2.2 Generate based on holidays
	return output


def get_stock_image(date_info: dict) -> Image:
	# 3.1 Flowers / Nature / Buddhist images
	# 3.2 Image color based on day of week
	images_dir = os.path.join(IMAGES_DIR, str(date_info["dow"]))
	image_list = [f.path for f in os.scandir(images_dir)]
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
	font = ImageFont.truetype(font_path, size=72, encoding="unic")

	# 4.2 Place text on image
	draw = ImageDraw.Draw(image)
	fill = d.text_fill[date_info["dow"]] # Color by day of week
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
	# 5.1 Read credentials and make OAuth
	with open(CREDENTIALS, "r") as fp:
		auth = json.load(fp)
		# Aliases for different tokens:
		# https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens
		token = auth.get("Access Token")
		token_secret = auth.get("Access Token Secret")
		consumer_key = auth.get("API Key")
		consumer_secret = auth.get("API Key Secret")

		oauth_data = OAuth(token, token_secret, consumer_key, consumer_secret)

	# 5.2 Setup Twitter APIs
	t_tweet = Twitter(auth=oauth_data)
	t_upload = Twitter(domain='upload.twitter.com', auth=oauth_data)

	# 5.3 Save PIL image to disk
	image.save("image.jpg")

	# 5.4 Upload saved binary to twitter
	with open("image.jpg", "rb") as fp:
		# Get the return value
		ret = t_upload.media.upload(media=fp.read())

	# 5.5 Attach the media id to tweet the image
	media_id = ret.get("media_id_string")
	t_tweet.statuses.update(media_ids=media_id)

	# 5.6 Delete temporary image on disk
	os.remove("image.jpg")

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