import os

from oqc_pipe import OpenQualityCheckerPipe

parameter_schema = {
    'BITBUCKET_USERNAME': {'type': 'string', 'required': False,
                           'default': os.getenv('BITBUCKET_REPO_OWNER')},
    'BITBUCKET_PASSWORD': {'type': 'string', 'required': False},
    'BITBUCKET_REPOSITORY': {'type': 'string', 'required': False,
                             'default': os.getenv('BITBUCKET_REPO_SLUG')},
    'BITBUCKET_COMMIT': {'type': 'string', 'required': False,
                         'default': os.getenv('BITBUCKET_COMMIT')},
    'BITBUCKET_BRANCH': {'type': 'string', 'required': False,
                         'default': os.getenv('BITBUCKET_BRANCH')},
    'OPENQUALITYCHECKER_BASE_URL': {'type': 'string', 'required': False,
                                    'default': os.getenv('OPENQUALITYCHECKER_BASE_URL')},
    'OPENQUALITYCHECKER_ACCESS_TOKEN': {'type': 'string', 'required': True,
                                        'default': os.getenv('OPENQUALITYCHECKER_ACCESS_TOKEN')},
    'OPENQUALITYCHECKER_PROJECT_NAME': {'type': 'string', 'required': True,
                                        'default': os.getenv('OPENQUALITYCHECKER_PROJECT_NAME')},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False}
}

if __name__ == '__main__':
    pipe = OpenQualityCheckerPipe(pipe_metadata='/pipe.yml', schema=parameter_schema)
    pipe.run()
