import backoff
import requests
from bitbucket_pipes_toolkit import Pipe
from requests import HTTPError

# The maximum total amount of time in seconds to try for before
# giving up
MAX_BACKOFF_TIMEOUT = 3600


class OpenQualityCheckerApi:

    def __init__(self, pipe):
        self._pipe: Pipe = pipe
        self._oqc_api_token = self._pipe.get_variable('OPENQUALITYCHECKER_ACCESS_TOKEN')

        self._pipe.log_debug(
            f'OpenQualityCheckerApi initialized with API token: {self._oqc_api_token}')

    def get_projects(self):
        size = 100

        page = 1
        projects = []
        last_page = False

        try:
            while not last_page:
                params = {
                    'privateOnly': 'true',
                    'page': page,
                    'size': size
                }
                headers = {
                    'token': self._oqc_api_token
                }

                projects_response = requests.get(
                    f"{self._pipe.get_variable('OPENQUALITYCHECKER_BASE_URL')}/api/projects",
                    headers=headers, params=params)

                projects_response.raise_for_status()

                response_body = projects_response.json()

                if not response_body:
                    self._pipe.log_warning('OPENQUALITYCHECKER__ERROR')
                    break

                response_data = response_body['data']

                if response_data:
                    last_page = response_data['last']
                    response_project_list = response_data['content']

                    if response_project_list:
                        projects.extend(response_project_list)
                else:
                    last_page = True

                page = page + 1
        except HTTPError as error:
            if error.response.status_code == 403:
                self._pipe.log_warning(f'OPENQUALITYCHECKER__ERROR: Request not authorized')
                raise ValueError(f'Request not authorized, possible invalid API token')

            self._pipe.log_error(f'OPENQUALITYCHECKER__ERROR: {error}')
            raise ValueError(f'{error}')
        except Exception as error:
            self._pipe.log_error(f'OPENQUALITYCHECKER__ERROR: {error}')
            raise ValueError(f'OpenQualityChecker not available, please try again later')

        return projects

    def get_branches(self, project_id):
        branches = []
        try:
            headers = {
                'token': self._oqc_api_token
            }

            projects_response = requests.get(
                f"{self._pipe.get_variable('OPENQUALITYCHECKER_BASE_URL')}/api/project/{project_id}/branches",
                headers=headers)

            projects_response.raise_for_status()

            response_body = projects_response.json()

            branches = response_body.get('data')

        except Exception as error:
            self._pipe.log_error(f'OPENQUALITYCHECKER__ERROR: {error}')

        return branches

    @backoff.on_predicate(backoff.fibo, max_value=100, max_time=MAX_BACKOFF_TIMEOUT)
    def get_version(self, branch_id):
        versions = []
        try:
            headers = {
                'token': self._oqc_api_token
            }

            projects_response = requests.get(
                f"{self._pipe.get_variable('OPENQUALITYCHECKER_BASE_URL')}/api/branch/{branch_id}/versions",
                headers=headers)

            projects_response.raise_for_status()

            response_body = projects_response.json()

            versions = response_body.get('data')

        except Exception as error:
            self._pipe.log_error(f'OPENQUALITYCHECKER__ERROR: {error}')

        return versions

    @backoff.on_predicate(backoff.fibo, max_value=100, max_time=MAX_BACKOFF_TIMEOUT)
    def get_quality_profile(self, version_id):
        try:
            headers = {
                'token': self._oqc_api_token
            }

            projects_response = requests.get(
                f"{self._pipe.get_variable('OPENQUALITYCHECKER_BASE_URL')}/api/version/{version_id}/qualityProfile",
                headers=headers)

            projects_response.raise_for_status()

            response_body = projects_response.json()

            return response_body.get('data')

        except Exception as error:
            self._pipe.log_error(f'OPENQUALITYCHECKER__ERROR: {error}')
