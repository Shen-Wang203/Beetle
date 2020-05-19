import logging
import logging.handlers

logfilename = 'testlog'
logging.basicConfig(filename=logfilename, filemode='w', level=logging.INFO)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              logfilename, maxBytes=20, backupCount=5)

logging.addHandler(handler)

for i in range(10):
    logging.info(i)