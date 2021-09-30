from datetime import datetime


def get_date_info() -> dict:
	date_info = {
		"day_of_week" : -1,
		"is_holyday": False,
		"is_holiday": False,
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


def generate_blessing(date_info: dict) -> str:
	# 2.1 Generate based on day of week
	# 2.2 Generate based on holidays
	return


def get_stock_image(date_info: dict):
	# 3.1 Flowers / Nature / Buddhist images
	# 3.2 Image color based on day of week
	return


def generate_image(blessing: str, stock_image):
	# 4.1 Select random font / text styling 
	# 4.2 Place text on image
	# 4.3 Crop & export for tweet
	return


def post_result():
	# 5.1 Read credential
	# 5.2 Tweet
	return


if __name__ == "__main__":
	# Run this script on VM startup

	# 1. Get date info
	date_info = get_date_info()

	# 2. Generate random blessing
	blessing = generate_blessing(date_info)

	# 3. Get random stock image
	stock_image = get_stock_image(date_info)

	# 4. Generate blessing image
	output_image = generate_image(blessing, stock_image)

	# 5. Post to Twitter
	ret = post_result()

	# Auto-shutdown VM on success
	exit()