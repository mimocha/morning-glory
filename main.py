from datetime import datetime
from io import BytesIO
import json
import random; random.seed()
import re
import urllib.parse

from PIL import Image, ImageFont, ImageDraw
import requests
import tweepy

import dictionary as d

CREDENTIALS = "credentials.json"


def get_api():
	"""
	Function to setup Twitter API v1.1
	Using v1.1 instead of v2 because media upload requires v1.1 anyway.

	Returns:
		tweepy.API: The Twitter API object
		str: The pexel API key
	"""

	# TODO Replace credentials with Azure Key Vault
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
		pexel_key = auth.get("Pexel API Key")

	# # 1.2 Setup Twitter APIv1.1
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	return api, pexel_key


def get_date_info() -> dict:
	"""
	Function to generate date info for blessing images.
	Firstly, get day of week.
	Second, check if this is holyday. -> Can be done with lunar calendar or Lookup table
	Third, check if it is a special holiday.
	To be decided if a single image is generated with multiple blessings, 
	or multiple images will be generated.

	Returns:
		dict: Dict containing the date infos
	"""

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
	"""
	Function to generate the greetings, separated into two parts.
	The first is the intro-greetings. -> Hello, today is the day...
	The second is a randomly chosen blessing.

	Args:
		date_info (dict): Requires the date info for the intro-greetings

	Returns:
		list: List of two strings in the format: [Greeting, Blessing]
	"""

	# 2.1 Generate based on day of week
	text_greet = d.greetings() + d.dow_th[date_info["dow"]]
	text_bless = d.blessings()
	output = [text_greet, text_bless]

	# 2.2 Generate based on holidays
	return output


def get_stock_image(date_info: dict, pexel_key: str):
	"""
	Function to get stock image from Pexel.
	Randomly pick based on color of the day.

	Args:
		date_info (dict): Requires the day of week for color theme
		pexel_key (str): Pexel API Key for making request to Pexel

	Returns:
		Image: Stock image for compositing
		dict: Metadata of image, for tweet crediting
	"""

	# 3.1 Generate image query for day of the week
	query = "query={}".format(d.get_obj())
	color = "color={}".format(d.get_color(date_info["dow"]))
	page = "page={}".format(random.randint(1,500)) # Randomly select from 500 images
	per_page = "per_page=1" # Query for a single result - no need to waste bandwidth
	query_url = f"https://api.pexels.com/v1/search?{query}&{color}&{page}&{per_page}"

	# 3.2 Query Pexel for image
	# 3.2.1 Get request for a random image
	r = requests.get(url=query_url, headers={"Authorization":pexel_key})
	if r.status_code != 200:
		print (f"Warning! Status code {r.status_code} on search request!")

	# 3.2.2 Extract image URL & metadata from response
	response = r.json()
	metadata = response["photos"][0]
	original_url = metadata["src"]["original"]

	# 3.2.3 Use Pexel APIs to crop image for us
	height = f"&h={800}"
	width = f"&w={800}"
	crop = f"&fit=crop{height}{width}"
	query_url = f"{original_url}?auto=compress&cs=tinysrgb{crop}"

	# 3.2.4 Request for the image data, no Auth needed
	r = requests.get(query_url)
	if r.status_code != 200:
		print (f"Warning! Status code {r.status_code} on image request!")
	# Convert response binary data into PIL image
	# https://docs.python-requests.org/en/latest/user/quickstart/#binary-response-content
	image = Image.open(BytesIO(r.content))

	# 3.3 Convert to RGBA for watermarking
	image = image.convert("RGBA")

	return image, metadata


def get_font(greetings: list) -> BytesIO:
	"""
	Function to query a random font from Google Fonts API.
	Returns a file-like object instead of a Pillow font object, 
	because we may have to reload the font object multiple times to reduce the size.
	Returning a single file-like object prevents having to query the same data multiple times

	Args:
		greetings (list): Greeting text strings and watermark text, distilled into the minimum set of chars.
		This helps Google API return the minimum ttf file that contains the character set we need.

	Returns:
		BytesIO: Returns a file-like object
	"""

	# Reduce full query text into minimum set of characters for Google fonts API query
	query_text = "".join(greetings)
	query_char = "".join(set(query_text))
	# Encode text into web format
	web_text = urllib.parse.quote(query_char)

	base_url = "https://fonts.googleapis.com/css2?"
	family = f"family={d.font()}"
	text = f"&text={web_text}"
	query_url = f"{base_url}{family}{text}"

	# Query Google Fonts API for font file URL
	r = requests.get(query_url)
	# Extract with Regex
	match = re.search(r"\((https.*?)\)", r.text)
	font_url = match.groups()[0]

	# Query for actual font binary
	r = requests.get(font_url)
	# Read into memory : fp is a file-like object
	# This is equivalent to:
	# fp = open("font.ttf", "rb")
	fp = BytesIO(r.content)

	return fp


def compose_image(date_info: dict, greetings: list, image: Image) -> Image:
	"""
	Function to combine base image and blessings into the output image.
	Requires libraqm for the correct layout (unix only).

	Args:
		date_info (dict): Date info for color of the day.
		greetings (list): List of two strings, blessing and greeting.
		image (Image): Stock image for compositing.

	Returns:
		Image: Composited image
	"""

	# 4.1 Query random font from Google Fonts
	# Returns a file pointer, as we may reload font again
	# This prevents having to re-download anything, speeding up the process
	# Need to append watermark text as part of required char set
	watermark_text = "@MorningGloryBot"
	font_fp = get_font(greetings + [watermark_text])

	# 4.2 Select text styling / positioning
	x, y = image.size
	# Dict must be defined here due to the relative positioning used
	text_style = {
		"center": {
			"coords" : [(0.5*x, 0.1*y), (0.5*x, 0.7*y)],
			"anchor" : ["mt", "mt"],
			"align" : ["center", "center"]
		},
		"slant": {
			"coords" : [(0.05*x, 0.05*y), (0.95*x, 0.9*y)],
			"anchor" : ["lt", "rb"],
			"align" : ["left", "right"]
		}
	}
	_name, style = random.choice(list(text_style.items()))

	# 4.3 Create transparent text layer to draw on
	text_layer = Image.new("RGBA", image.size, (255,255,255,0))
	draw = ImageDraw.Draw(text_layer)

	# 4.4 Iteratively reduce font size until text fits in frame
	font_size = 80
	font_size_fit = False
	while not font_size_fit:
		# This is always False on the first iteration, forcing a load
		if not font_size_fit:
			# Need to seek pointer to start of file every time
			font_fp.seek(0)
			font = ImageFont.truetype(
				font = font_fp, 
				size = font_size,
				encoding = "unic", 
				layout_engine = ImageFont.LAYOUT_RAQM
			)
			# Reduces font size for the next iteration
			font_size -= 2

		# List boolean values, each a test for one text box
		size_tests = list()
		for text, xy, an, al in zip(greetings, style["coords"], style["anchor"], style["align"]):
			# Generate text bbox
			bbox = draw.textbbox(xy, text, font=font, anchor=an, align=al)
			# Check if text bbox is in-bound
			# Checks: (Lower bound) and (Upper bound)
			size_tests.append( (bbox[:2] >= (0,0)) and (bbox[2:] <= image.size) )
		# Check that all is True (text fits in boundary)
		font_size_fit = all(size_tests)

	# 4.5 Place text on image
	fill = d.text_fill[date_info["dow"]] # Color by day of week
	for text, xy, an, al in zip(greetings, style["coords"], style["anchor"], style["align"]):
		draw.text(
			xy = xy,
			text = text,
			font = font,
			fill = fill, 
			stroke_fill = (0,0,0,255),
			stroke_width = 4,
			anchor = an,
			align = al
		)

	# 4.6 Watermark image
	# Get bottom-right coordinates for watermark
	xy = [c-20 for c in image.size]
	# Need to seek pointer to start of file every time
	font_fp.seek(0)
	font = ImageFont.truetype(
		font = font_fp,
		size = 24,
		encoding = "unic", 
		layout_engine = ImageFont.LAYOUT_RAQM
	)
	draw.text(
		xy, 
		watermark_text, 
		font = font,
		fill = (255,255,255,128),
		stroke_fill = (0,0,0,128),
		stroke_width = 2,
		anchor = "rb"
	)

	# Combine text and image layer into final output image
	output = Image.alpha_composite(image, text_layer)

	# Close font file pointer
	font_fp.close()

	return output


def generate_tweet(date_info: dict, metadata: dict) -> str:
	"""
	Function to generate the tweet text itself.
	Includes the greetings hashtag for finding on twitter.
	Then add the photographer and Pexel attribution.

	Args:
		date_info (dict): Day of the week for Thai Hashtag
		metadata (dict): Image author for attribution

	Returns:
		str: Tweet string
	"""

	# 5. Generate tweet text
	hashtag = f"#สวัสดี{d.dow_th[date_info['dow']]}"
	attribute = f"Photo by {metadata['photographer']} | Pexels.com"
	tweet = f"{hashtag}\n{attribute}"

	return tweet


def post_result(api: tweepy.API, image: Image, tweet_text: str):
	"""
	Function to post results to twitter, using the tweepy library.
	Use tweepy library for best support, afaik.

	Args:
		api (tweepy.API): Tweepy library API
		image (Image): Composited image
	"""

	# 6.1 Save PIL image in-memory for upload. See sample by tweepy dev:
	# https://github.com/tweepy/tweepy/issues/1412
	b = BytesIO() # Create Python BytesIO
	image.save(b, "PNG") # Save PIL image in-memory
	b.seek(0)

	# 6.2 Upload saved binary to twitter
	# Will fail if not authorized to post (Twitter app not set up properly?)
	data = api.simple_upload(filename='', file=b)

	# 6.3 Attach the media id to tweet the image
	# Media ID is attached as a list of string ["12345...", ...]
	# One media_id_string per image.
	api.update_status(
		media_ids = [data.media_id_string],
		status = tweet_text
	)

	return


if __name__ == "__main__":
	# 1. Setup API & Credentials
	api, pexel_key = get_api()

	# 2. Get date info
	date_info = get_date_info()

	# 2. Generate random blessing
	greetings = generate_greetings(date_info)

	# 3. Get random stock image
	image, metadata = get_stock_image(date_info, pexel_key)

	# 4. Generate blessing image
	output_image = compose_image(date_info, greetings, image)

	# 5. Generate tweet text
	tweet_text = generate_tweet(date_info, metadata)

	# 6. Post to Twitter
	post_result(api, output_image, tweet_text)

	exit()