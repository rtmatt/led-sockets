import sys

from ledsockets.logging import get_logger

logger = get_logger('ledsockets.client.manager')


class ClientManager:

    def __init__(self):
        logger.debug('Initializing')

    def start(self):
        """
        :return: False for error, truthy for success
        """
        logger.info('Starting')

        return True


def exec_commend_line():
    server = ClientManager()

    # drawn from fail2ban
    if (server.start()):
        sys.exit(0)
    else:
        sys.exit(255)


if __name__ == '__main__':
    exec_commend_line()
