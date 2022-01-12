from uuid import uuid4

from bitbucket_pipes_toolkit import CodeInsights, get_logger, get_variable

logger = get_logger()


class BitbucketApi:

    def get_or_create_report(self, commit):
        logger.info("get_or_create_report")

        bitbucket_user = get_variable('BITBUCKET_USERNAME')
        bitbucket_repository = get_variable('BITBUCKET_REPOSITORY')

        if get_variable('BITBUCKET_PASSWORD'):
            logger.info(
                f"Creating authenticated API client for repository: {bitbucket_repository} and user: {bitbucket_user}")

            insights = CodeInsights(repo=bitbucket_repository,
                                    username=bitbucket_user,
                                    auth_type='basic',
                                    app_password=get_variable('BITBUCKET_PASSWORD'))
        else:
            logger.info(
                f"Creating unauthenticated API client for repository: {bitbucket_repository} and user: {bitbucket_user}")

            insights = CodeInsights(repo=bitbucket_repository,
                                    username=bitbucket_user)

        expected_external_id = f'openqualitychecker-warning-report-{commit}'

        reports = insights.get_reports(commit)

        logger.info(f"Existing reports: {reports}")

        for report in reports['values']:
            if report['external_id'] == expected_external_id:
                return report

        report_data = {
            "type": "report",
            "report_type": "BUG",
            "title": "OpenQualityChecker warning report",
            "details": "TODO report details",
            "result": "FAILED",
            "reporter": "OpenQualityChecker Pipe",
            "external_id": expected_external_id,
        }
        report = insights.create_report(commit, report_data=report_data)

        logger.info(f"Created report: {report}")

        return report

    def annotate(self, path, line_number, commit, report_id):
        logger.info("annotate")

        bitbucket_user = get_variable('BITBUCKET_USERNAME')
        bitbucket_repository = get_variable('BITBUCKET_REPOSITORY')

        insights = CodeInsights(repo=bitbucket_repository,
                                username=bitbucket_user)

        annotation_data = {
            "annotation_type": "VULNERABILITY",
            "external_id": str(uuid4()),
            "summary": get_variable('ANNOTATION_SUMMARY'),
            "details": get_variable('ANNOTATION_DESCRIPTION'),
            "severity": "HIGH",
            "result": "FAILED",
            "line": line_number,
            "path": path
        }

        annotation = insights.create_annotation(commit, report_id, annotation_data)

        logger.info(f"Created annotation: {annotation}")
