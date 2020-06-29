import logging

logfilename = 'runlog.log'
logging.basicConfig(filename=logfilename, filemode='w', level=logging.INFO)

logging.info('Run')