from datetime import datetime
import json
import os
import random; random.seed()

from PIL import Image, ImageFont, ImageDraw
import tweepy

import dictionary as d

FONTS_DIR = "./fonts/"
IMAGES_DIR = "./images/"

CREDENTIALS = "credentials.json"
TEMP_IMG = "image.png"


def get_api():
	"""
	Function to setup Twitter API v1.1
	Using v1.1 instead of v2 because media upload requires v1.1 anyway.

	Returns:
		bool: Success flag
		tweepy.API: The Twitter API object
	"""

	# https://docs.tweepy.org/en/stable/auth_tutorial.html
	# 1.1 Read credentials from system
	with open(CREDENTIALS, "r") as fp:
		auth = json.load(fp)
		# Aliases for different tokens:
		# https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens
		access_token = auth.get("Access Token")
		access_token_secret = auth.get("Access Token Secret")
		consumer_key = auth.get("API Key")
		consumer_secret = auth.get("API Key Secret")

	# # 1.2 Setup Twitter APIv1.1
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	# 1.3 Verify authorization
	try:
		api.lookup_users(screen_name=["MorningGloryBot"])
		ret = True
	except tweepy.errors.Unauthorized as e:
		# Authorization errors
		print(e)
		ret = False
	except Exception as e:
		# Any other unexpected error
		print(e)
		ret = False

	return ret, api


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

	# 3.4 Convert to RGBA for watermarking
	image = image.convert("RGBA")

	return image


def compose_image(date_info: dict, greetings: list, image: Image):

	# 4.1 Create transparent text layer to draw on
	text_layer = Image.new("RGBA", image.size, (255,255,255,0))
	# Draw object
	draw = ImageDraw.Draw(text_layer)

	# 4.2 Select random font / text styling 
	font_list = [f.path for f in os.scandir(FONTS_DIR)]
	font_path = random.choice(font_list)
	font = ImageFont.truetype(font_path, size=70, encoding="unic")

	x, y = image.size
	text_style = {
		"center": {
			"coords" : [(0.5*x, 0.1*y), (0.5*x, 0.7*y)],
			"anchor" : ["mt", "mt"]
		},
		"slant": {
			"coords" : [(0.05*x, 0.05*y), (0.95*x, 0.9*y)],
			"anchor" : ["lt", "rb"]
		}
	}
	_name, style = random.choice(list(text_style.items()))

	# 4.3 Place text on image
	fill = d.text_fill[date_info["dow"]] # Color by day of week
	for text, xy, an in zip(greetings, style["coords"], style["anchor"]):
		draw.text(
			xy,
			text,
			font = font,
			fill = fill, 
			stroke_fill = (0,0,0,128),
			stroke_width = 3,
			anchor = an
		)

	# 4.4 Watermark image
	font = ImageFont.truetype(font_path, size=18, encoding="unic")
	# Get bottom-right coordinates for watermark
	xy = [c-20 for c in image.size]
	draw.text(
		xy, 
		"@MorningGloryBot", 
		font = font,
		fill = (255,255,255,128),
		anchor = "rb"
	)

	# Combine layers
	combined = Image.alpha_composite(image, text_layer)

	return combined


def post_result(api: tweepy.API, image: Image, date_info: dict):

	# 5.1 Save PIL image to disk
	image.save(TEMP_IMG)

	# 5.2 Upload saved binary to twitter
	data = api.media_upload(TEMP_IMG)

	# 5.3 Attach the media id to tweet the image
	# Media ID is attached as a list of string ["12345...", ...]
	# One media_id_string per image.
	api.update_status(
		media_ids = [data.media_id_string], 
		status = "#สวัสดี" + d.dow_th[date_info["dow"]]
	)

	# 5.4 Delete temporary image on disk
	os.remove(TEMP_IMG)

	return


if __name__ == "__main__":
	# Run this script on VM startup

	# 1. Setup Twitter API
	ret, api = get_api()
	if not ret:
		print("Authentication Failed")
		exit()

	# 2. Get date info
	date_info = get_date_info()

	# 2. Generate random blessing
	greetings = generate_greetings(date_info)

	# 3. Get random stock image
	stock_image = get_stock_image(date_info)

	# 4. Generate blessing image
	output_image = compose_image(date_info, greetings, stock_image)

	# 5. Post to Twitter
	post_result(api, output_image, date_info)

	# Auto-shutdown VM on success
	exit()