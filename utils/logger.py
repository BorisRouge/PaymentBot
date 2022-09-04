import logging

def get_logger(    
        FORMAT     = '%(asctime)s %(levelname)s %(message)s',
        NAME       = '',
        FILE_INFO  = 'logs/info.log',
        FILE_ERROR = 'logs/errors.log'):

    logger        = logging.getLogger(NAME)
    log_formatter = logging.Formatter(FORMAT)        

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(FILE_INFO, mode='a')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.DEBUG)
    logger.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(FILE_ERROR, mode='a')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.WARNING)    
    logger.addHandler(file_handler_error)

    logger.setLevel(logging.INFO)

    return logger
