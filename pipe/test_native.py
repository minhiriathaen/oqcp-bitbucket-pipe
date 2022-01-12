import os

import pytest

from oqc_pipe import OpenQualityCheckerPipe
from pipe import parameter_schema

OPENQUALITYCHECKER_BASE_URL = 'http://localhost:3031/backend'


def test_no_parameters(capsys):
    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, 'BITBUCKET_BRANCH')
    assert_output(result, 'BITBUCKET_COMMIT')
    assert_output(result, 'BITBUCKET_REPOSITORY')
    assert_output(result, 'BITBUCKET_USERNAME')
    assert_output(result, 'OPENQUALITYCHECKER_ACCESS_TOKEN')
    assert_output(result, 'OPENQUALITYCHECKER_PROJECT_NAME')


def test_OpenQualityChecker_not_available(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"http://dummy_OpenQualityChecker_hostname"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"dummy-branch"
    os.environ["BITBUCKET_COMMIT"] = f"dummy-commit"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"dummy_oqcp_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"dummy_oqcp_project"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, 'OpenQualityChecker not available, please try again later')


def test_with_invalid_api_token(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"dummy-branch"
    os.environ["BITBUCKET_COMMIT"] = f"dummy-commit"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"invalid_oqcp_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"dummy_oqcp_project"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "Request not authorized, possible invalid API token")


def test_not_existing_project(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"dummy-branch"
    os.environ["BITBUCKET_COMMIT"] = f"dummy-commit"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"dummy_oqcp_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"dummy_oqcp_project"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "[dummy_oqcp_project] Project id NOT found for project name")


def test_not_existing_branch(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"not-existing-branch"
    os.environ["BITBUCKET_COMMIT"] = f"dummy-commit"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"dummy_oqcp_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "Branch not found: 'not-existing-branch'")


def test_not_existing_version(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"not-existing-version-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"dummy_oqcp_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result,
                  "Version not found for branch id: '285' and hash: 'not-existing-version-commit-hash'")


def test_not_existing_quality_profile(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"not-existing-quality-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"dummy_oqcp_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "No quality profile found for version: '327'")


def test_failed_project(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"failed-quality-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"oqc_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "The commit for project 'process-metrics' is FAILED the analysis")
    assert_output(result, 'The Code complexity (2.63) should be LE 10.0')
    assert_output(result, 'The csharpsquid:S3431 should be GT 100.0')
    assert_output(result, 'The AVGNODL should be GT 0.0')
    assert_output(result, 'The Maintainability (2.55) should be GT 5.0')
    assert_output(result, 'Fail')


def test_failed_projects(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"failed-quality-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"oqc_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics, Qualityprofiletest"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "The commit for project 'process-metrics' is FAILED the analysis")
    assert_output(result, "The commit for project 'Qualityprofiletest' is FAILED the analysis")
    assert_output(result, 'The Code complexity (2.63) should be LE 10.0')
    assert_output(result, 'The csharpsquid:S3431 should be GT 100.0')
    assert_output(result, 'The AVGNODL should be GT 0.0')
    assert_output(result, 'The Maintainability (2.55) should be GT 5.0')
    assert_output(result, 'The Code complexity (3.76) should be LE 10.0')
    assert_output(result, 'The Maintainability (4.67) should be GT 5.0')
    assert_output(result, 'Fail')


def test_partial_failed_projects(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"failed-quality-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"oqc_token"
    os.environ[
        "OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics, Qualityprofiletest, analyzer-client"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 1)
    assert_output(result, "The commit for project 'process-metrics' is FAILED the analysis")
    assert_output(result, "The commit for project 'Qualityprofiletest' is FAILED the analysis")
    assert_output(result, "The commit for project 'analyzer-client' is PASSED the analysis")
    assert_output(result, 'The Code complexity (2.63) should be LE 10.0')
    assert_output(result, 'The csharpsquid:S3431 should be GT 100.0')
    assert_output(result, 'The AVGNODL should be GT 0.0')
    assert_output(result, 'The Maintainability (2.55) should be GT 5.0')
    assert_output(result, 'The Code complexity (3.76) should be LE 10.0')
    assert_output(result, 'The Maintainability (4.67) should be GT 5.0')
    assert_output(result, 'Fail')


def test_passed_project(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"successful-quality-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"oqc_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 0)
    assert_output(result, "The commit for project 'process-metrics' is PASSED the analysis")
    assert_output(result, 'Success')


def test_passed_projects(capsys):
    os.environ["OPENQUALITYCHECKER_BASE_URL"] = f"{OPENQUALITYCHECKER_BASE_URL}"
    os.environ["BITBUCKET_USERNAME"] = f"dummy_user"
    os.environ["BITBUCKET_PASSWORD"] = f"dummy_password"
    os.environ["BITBUCKET_REPOSITORY"] = f"dummy_repository"
    os.environ["BITBUCKET_BRANCH"] = f"master"
    os.environ["BITBUCKET_COMMIT"] = f"successful-quality-commit-hash"
    os.environ["OPENQUALITYCHECKER_ACCESS_TOKEN"] = f"oqc_token"
    os.environ["OPENQUALITYCHECKER_PROJECT_NAME"] = f"process-metrics, analyzer-client"
    os.environ["DEBUG"] = f"True"

    result, wrapped_error = run_the_pipe(capsys)

    print(f'\n{result.out}')

    assert_exit_code(wrapped_error, 0)
    assert_output(result, "The commit for project 'process-metrics' is PASSED the analysis")
    assert_output(result, "The commit for project 'analyzer-client' is PASSED the analysis")
    assert_output(result, 'Success')


def run_the_pipe(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        pipe = OpenQualityCheckerPipe(schema=parameter_schema)
        pipe.run()

    return capsys.readouterr(), pytest_wrapped_e


def assert_exit_code(pytest_wrapped_e, expected):
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == expected


def assert_output(result, expected):
    assert result.out.count(expected) >= 1 or result.err.count(expected) >= 1
