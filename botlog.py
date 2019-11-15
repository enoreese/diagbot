"""
Class used for logging user request and errors to Logfile and output in console
"""

import logging

class BotLog():
	def __init__(self):
		logging.basicConfig(filename='Diag-log.log',
							format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	def log(self, message):
		logging.info(message)
		print(message)

	def warn(self, message):
		logging.warning(message)
		print(message)

	def error(self, message):
		logging.error(message)
		print(message)