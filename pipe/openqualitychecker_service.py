import backoff
from bitbucket_pipes_toolkit import Pipe
from colorlog import colorlog

from openqualitychecker_api import OpenQualityCheckerApi, MAX_BACKOFF_TIMEOUT


class OpenQualityCheckerService:

    def __init__(self, pipe):
        self._pipe: Pipe = pipe
        self._pipe.logger.handlers.__getitem__(0).setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s %(levelname)-6s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        self._open_quality_checker_api = OpenQualityCheckerApi(pipe)

    def get_quality_result(self, oqc_project_name, branch_name, commit_hash):
        oqc_project_id = self._find_project_id_by_name(oqc_project_name)

        branch_id = self._find_branch_id(oqc_project_name, oqc_project_id, branch_name)
        version_id = self._find_version_id(oqc_project_name, branch_id, commit_hash)
        return self._find_quality_profile(oqc_project_name, version_id)

    def _find_project_id_by_name(self, project_name):

        self._pipe.log_info(
            f"[{project_name}] Searching project id by name")

        oqc_projects = self._open_quality_checker_api.get_projects()

        if not oqc_projects:
            self._pipe.log_warning(
                f"[{project_name}] No OpenQualityChecker project is found for the given token")

        for oqc_project in oqc_projects:
            current_project_name = oqc_project.get('projectName')

            self._pipe.log_debug(
                f"[{project_name}] Current project name for checking: '{current_project_name}'")

            if current_project_name == project_name:
                return oqc_project.get('id')

        raise ValueError(f"[{project_name}] Project id NOT found for project name")

    @backoff.on_exception(backoff.fibo, ValueError, max_value=100, max_time=MAX_BACKOFF_TIMEOUT)
    def _find_version_id(self, oqc_project_name, branch_id, commit_hash):
        self._pipe.log_info(
            f"[{oqc_project_name}] Searching version for branch id: '{branch_id}' and commit: '{commit_hash}'")

        versions = self._open_quality_checker_api.get_version(branch_id)

        for version in versions:
            if version.get('hash') == commit_hash:
                return version.get('id')

        raise ValueError(
            f"[{oqc_project_name}] Version not found for branch id: '{branch_id}' and hash: '{commit_hash}'")

    def _find_branch_id(self, oqc_project_name, oqc_project_id, branch_name):
        self._pipe.log_info(
            f"[{oqc_project_name}] Searching branch id for project: '{oqc_project_id}' and branch name: '{branch_name}'")

        branches = self._open_quality_checker_api.get_branches(oqc_project_id)

        for branch in branches:
            current_branch_name = branch.get('branchName')
            self._pipe.log_debug(
                f"[{oqc_project_name}] Current branch for checking: '{current_branch_name}'")
            if current_branch_name == branch_name:
                return branch.get('id')

        raise ValueError(f"[{oqc_project_name}] Branch not found: '{branch_name}'")

    def _find_quality_profile(self, oqc_project_name, version_id):
        self._pipe.log_info(
            f"[{oqc_project_name}] Searching quality profile for branch version: '{version_id}'")

        quality = self._open_quality_checker_api.get_quality_profile(version_id)

        if quality is None:
            raise ValueError(
                f"[{oqc_project_name}] No quality profile found for version: '{version_id}'")

        return quality
