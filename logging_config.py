from loguru import logger


def setup_logging():
    logger.remove()
    logger.add(
        'logs.log',
        level='DEBUG',
        format='<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green> | '
               '<level>{level: <8}</level> | '
               '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
               '<level>{message}</level>'
    )
