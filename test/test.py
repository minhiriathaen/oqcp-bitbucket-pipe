import os
import subprocess
import time

import pytest

DOCKER_IMAGE = 'bitbucketpipelines/oqcp-bitbucket-pipe:' + os.getenv('BITBUCKET_BUILD_NUMBER',
                                                                     'local')

DOCKER_MOCKOON_IMAGE = 'oqcp/mockoon:' + os.getenv('BITBUCKET_BUILD_NUMBER', 'local')

MOCKOON_OQCP_CONTAINER_NAME = 'mockoon-openqualitychecker-' + os.getenv('BITBUCKET_BUILD_NUMBER',
                                                                        'local')
PIPE_CONTAINER_NAME = 'oqcp-bitbucket-pipe-' + os.getenv('BITBUCKET_BUILD_NUMBER', 'local')

OQCP_TEST_NETWORK_NAME = 'oqcp-test-network-' + os.getenv('BITBUCKET_BUILD_NUMBER', 'local')
OPENQUALITYCHECKER_BASE_URL = 'http://mockoon-openqualitychecker:3000/backend'


@pytest.fixture(scope="session", autouse=True)
def setup():
    print(f'\n\n----Setup test environment----')

    pipe = docker_build_pipe()
    mockoon_image = docker_build_mockoon_image()
    network = docker_network_create()
    mockoon_run = docker_run_mockoon()

    print('Waiting for Mockoon to start...')
    time.sleep(1)
    print('Wait is over')

    yield pipe, mockoon_image, network, mockoon_run

    print(f'\n\n----Teardown test environment----')

    docker_remove(MOCKOON_OQCP_CONTAINER_NAME)
    docker_remove(PIPE_CONTAINER_NAME)
    docker_remove_network()


def docker_build_pipe():
    """
    Build the docker image for tests.
    :return:
    """

    print(f'Building Docker image: {DOCKER_IMAGE}')

    args = [
        'docker',
        'build',
        '-t',
        DOCKER_IMAGE,
        '.',
    ]
    return subprocess.run(args, check=True)


def docker_build_mockoon_image():
    print(f'Building Docker image: {DOCKER_MOCKOON_IMAGE}')

    args = [
        'docker',
        'build',
        '-t',
        DOCKER_MOCKOON_IMAGE,
        './test/Mockoon',
    ]
    return subprocess.run(args, check=True)


def docker_run_mockoon():
    print(f'Running Docker container: {MOCKOON_OQCP_CONTAINER_NAME}')

    args = [
        'docker',
        'run',
        '-d',
        '--name',
        MOCKOON_OQCP_CONTAINER_NAME,
        '--rm',
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '--hostname=mockoon-openqualitychecker',
        DOCKER_MOCKOON_IMAGE,
        '-d', 'data', '-n', 'openqualitychecker', '-p', '3000',
    ]
    return subprocess.run(args, check=True, cwd='./test/Mockoon')


def docker_network_create():
    print(f'Creating Docker network: {OQCP_TEST_NETWORK_NAME}')

    args = [
        'docker',
        'network',
        'create',
        '--driver',
        'bridge',
        OQCP_TEST_NETWORK_NAME,
    ]
    return subprocess.run(args, check=False, text=True, capture_output=True)


def docker_remove(container):
    print(f'Removing Docker container: {container}')

    args = [
        'docker',
        'rm',
        '-vf',
        container,
    ]
    subprocess.run(args)


def docker_remove_network():
    print(f'Removing Docker network: {OQCP_TEST_NETWORK_NAME}')

    args = [
        'docker',
        'network',
        'rm',
        OQCP_TEST_NETWORK_NAME,
    ]
    subprocess.run(args)


def test_no_parameters():
    args = [
        'docker',
        'run',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, 'BITBUCKET_BRANCH')
    assert_output(result, 'BITBUCKET_COMMIT')
    assert_output(result, 'BITBUCKET_REPOSITORY')
    assert_output(result, 'BITBUCKET_USERNAME')
    assert_output(result, 'OPENQUALITYCHECKER_ACCESS_TOKEN')
    assert_output(result, 'OPENQUALITYCHECKER_PROJECT_NAME')


def test_openqualitychecker_not_available():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL=http://dummy_openqualitychecker_hostname',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=dummy-branch',
        '-e', 'BITBUCKET_COMMIT=dummy-commit',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=dummy_oqcp_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=dummy_oqcp_project',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, 'OpenQualityChecker not available, please try again later')


def test_with_invalid_api_token():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=dummy-branch',
        '-e', 'BITBUCKET_COMMIT=dummy-commit',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=invalid_oqcp_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=dummy_oqcp_project',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, "Request not authorized, possible invalid API token")


def test_not_existing_project():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=dummy-branch',
        '-e', 'BITBUCKET_COMMIT=dummy-commit',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=dummy_oqcp_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=dummy_oqcp_project',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, "[dummy_oqcp_project] Project id NOT found for project name")


def test_not_existing_branch():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=not-existing-branch',
        '-e', 'BITBUCKET_COMMIT=dummy-commit',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=dummy_oqcp_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, "Branch not found: 'not-existing-branch'")


def test_not_existing_version():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=not-existing-version-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=dummy_oqcp_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result,
                  "Version not found for branch id: '285' and hash: 'not-existing-version-commit-hash'")


def test_not_existing_quality_profile():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=not-existing-quality-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=dummy_oqcp_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, "No quality profile found for version: '327'")


def test_failed_project():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=failed-quality-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=oqc_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, "The commit for project 'process-metrics' is FAILED the analysis")
    assert_output(result, 'The Code complexity (2.63) should be LE 10.0')
    assert_output(result, 'The csharpsquid:S3431 should be GT 100.0')
    assert_output(result, 'The AVGNODL should be GT 0.0')
    assert_output(result, 'The Maintainability (2.55) should be GT 5.0')
    assert_output(result, 'Fail')


def test_failed_projects():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=failed-quality-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=oqc_token',
        '-e', 'openqualitychecker_PROJECT_NAME=process-metrics, Qualityprofiletest',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
    assert_output(result, "The commit for project 'process-metrics' is FAILED the analysis")
    assert_output(result, "The commit for project 'Qualityprofiletest' is FAILED the analysis")
    assert_output(result, 'The Code complexity (2.63) should be LE 10.0')
    assert_output(result, 'The csharpsquid:S3431 should be GT 100.0')
    assert_output(result, 'The AVGNODL should be GT 0.0')
    assert_output(result, 'The Maintainability (2.55) should be GT 5.0')
    assert_output(result, 'The Code complexity (3.76) should be LE 10.0')
    assert_output(result, 'The Maintainability (4.67) should be GT 5.0')
    assert_output(result, 'Fail')


def test_partial_failed_projects():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=failed-quality-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=oqc_token',
        '-e',
        'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics, Qualityprofiletest, analyzer-client',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 1
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


def test_passed_project():
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=successful-quality-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=oqc_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)

    assert result.returncode == 0
    assert_output(result, "The commit for project 'process-metrics' is PASSED the analysis")
    assert_output(result, 'Success')


def test_passed_projects(capsys):
    args = [
        'docker',
        'run',
        '--name',
        PIPE_CONTAINER_NAME,
        f'--network={OQCP_TEST_NETWORK_NAME}',
        '-e', f'OPENQUALITYCHECKER_BASE_URL={OPENQUALITYCHECKER_BASE_URL}',
        '-e', 'BITBUCKET_USERNAME=dummy_user',
        '-e', 'BITBUCKET_PASSWORD=dummy_password',
        '-e', 'BITBUCKET_REPOSITORY=dummy_repository',
        '-e', 'BITBUCKET_BRANCH=master',
        '-e', 'BITBUCKET_COMMIT=successful-quality-commit-hash',
        '-e', 'OPENQUALITYCHECKER_ACCESS_TOKEN=oqc_token',
        '-e', 'OPENQUALITYCHECKER_PROJECT_NAME=process-metrics, analyzer-client',
        '-e', 'DEBUG=True',
        '--rm',
        DOCKER_IMAGE,
    ]

    result = subprocess.run(args, check=False, text=True, capture_output=True)

    print_result(result)
    assert_output(result, "The commit for project 'process-metrics' is PASSED the analysis")
    assert_output(result, "The commit for project 'analyzer-client' is PASSED the analysis")
    assert_output(result, 'Success')


def print_result(result):
    print(f'\n\n----Test run result----')
    print(f'Result code: {result.returncode}')
    print(f'Output:\n')
    if result.stderr:
        print(f'{result.stderr}')
    if result.stdout:
        print(f'{result.stdout}')


def assert_output(result, expected):
    assert result.stderr.count(expected) >= 1 or result.stdout.count(expected) >= 1
