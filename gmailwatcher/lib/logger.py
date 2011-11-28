import os
import logging


logger = logging.getLogger('gmailwatcher')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(os.path.join(os.path.expanduser('~'), '.gmailwatcher.log'))
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)




