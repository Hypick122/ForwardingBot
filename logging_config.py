import logging.config

LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'advanced': {
            'format': '%(asctime)s %(name)s:%(levelname)s:%(message)s'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO',
            'formatter': 'standard'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'advanced',
            'filename': 'app.log',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['stdout', 'file'],
            'level': 'INFO'
        }
    }
}

logging.config.dictConfig(LOGGING)
