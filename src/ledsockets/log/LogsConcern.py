from ledsockets.log import get_logger


class Logs:
    LOGGER_NAME = ''

    def __init__(self):
        self._logger = get_logger(self.LOGGER_NAME)

    def _log(self, msg, level='debug',*args):
        valid_levels = [
            'debug',
            'info',
            'warning',
            'error',
            'critical'
        ]
        if level not in valid_levels:
            self._logger.warning('Invalid log level')
            msg = f"{level}: {msg}"
            level = 'debug'
        getattr(self._logger, level)(f"{msg}",*args)



