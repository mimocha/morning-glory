import datetime
import logging

import azure.functions

import tweet_func

def main(mytimer):
	t_start = datetime.datetime.now()
	logging.info(f"Function triggered at {t_start}.")

	tweet_func.run()

	t_end = datetime.datetime.now()
	logging.info(f"Function execution completed at {t_end}.")
	t_delta = t_end - t_start
	logging.info(f"Total execution time {t_delta}")