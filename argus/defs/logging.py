import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGGING_PROD = {
        'version': 1,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'formatters': {
            'verbose': {
                'format': '[%(asctime)s]-[%(process)d]-[%(thread)x]-[%(levelname)s]-[%(module)s] --- %(message)s '
            },
            'simple':{
                'format': '[%(asctime)s]-[%(levelname)s] --- %(message)s '
            }
        },
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR+'/logs/argus.log',
                'formatter': 'simple'
            },

            'argus_handler':{
                'level':'INFO',
                'class':'logging.FileHandler',
                'filename': BASE_DIR+'/logs/argus.log',
                'formatter':'verbose',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
            'argus': {
                'handlers': ['argus_handler'],
                'level': 'INFO',
                'propagate': False,
            },
        }
    }

