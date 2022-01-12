from bitbucket_pipes_toolkit import Pipe, fail, success

from openqualitychecker_service import OpenQualityCheckerService


def _get_failure_reason(results_of_rules):
    details = ''
    if results_of_rules:
        for result_of_rule in results_of_rules:
            entity = result_of_rule.get('entity')
            actual_value = result_of_rule.get('actualValue')
            operator = result_of_rule.get('operator')
            value = result_of_rule.get('value')

            if actual_value:
                actual_value = str(round(actual_value, 2))
                details += f'\n\t\t* The {entity} ({actual_value}) should be {operator} {value}'
            else:
                details += f'\n\t\t* The {entity} should be {operator} {value}. '
    return details


class OpenQualityCheckerPipe(Pipe):

    def __init__(self, pipe_metadata=None, pipe_metadata_file=None, schema=None,
                 env=None, check_for_newer_version=False):
        super().__init__(pipe_metadata=pipe_metadata, pipe_metadata_file=pipe_metadata_file,
                         schema=schema, env=env,
                         check_for_newer_version=check_for_newer_version)

        self._openqualitychecker_service = OpenQualityCheckerService(self)

    def run(self):
        super().run()

        self.log_debug('Executing the pipe...')

        oqc_project_name_parameter = self.get_variable('OPENQUALITYCHECKER_PROJECT_NAME')
        branch_name = self.get_variable('BITBUCKET_BRANCH')
        commit_hash = self.get_variable('BITBUCKET_COMMIT')

        try:
            oqc_project_names = oqc_project_name_parameter.split(',')
            total_quality_result = True

            for current_project in oqc_project_names:
                current_project = current_project.strip()
                quality_profile = self._openqualitychecker_service.get_quality_result(
                    current_project,
                    branch_name,
                    commit_hash)

                if quality_profile is None:
                    fail(f"Quality profile not available for this commit")

                quality_result = quality_profile.get('result')

                self.log_debug(
                    f"Quality profile result for project '{current_project}': {quality_result}")

                quality_details = f"The commit for project '{current_project}' "

                if quality_result:
                    quality_details += "is PASSED the analysis"

                    success(f'{quality_details}', do_exit=False)
                else:
                    quality_details += "is FAILED the analysis"

                    reason = _get_failure_reason(quality_profile.get('resultsOfRules'))

                    quality_details += f'\n\tReason: {reason}'

                    fail(f'{quality_details}', do_exit=False)

                total_quality_result = total_quality_result and quality_result

            if total_quality_result:
                success()
            else:
                fail()

        except Exception as error:
            fail(f'{error}')
