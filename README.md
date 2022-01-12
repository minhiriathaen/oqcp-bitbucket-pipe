# Bitbucket Pipelines Pipe: OpenQualityChecker pipe

This pipe is for validating source with OpenQualityChecker.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
-   pipe: minhiriathaen/oqcp-bitbucket-pipe:0.0.1
    variables:
        NAME: "<string>"
        # DEBUG: "<boolean>" # Optional
```

## Variables

| Variable                      | Usage                      |
| ---                           | ---                        |
| OPENQUALITYCHECKER_ACCESS_TOKEN (*)  | OpenQualityChecker API token      |
| OPENQUALITYCHECKER_PROJECT_NAME (*)  | Name of the OpenQualityChecker projects which are related to this Bitbucket project. Example for one project `project_1` in case of multiple projects: `project_1, project_2, project_3, ...`|
| DEBUG                         | Enables logging for debug information. Default: `False` |

_(*) = required variable._

## Prerequisites

## Examples

Basic example:

```yaml
script:
    -   pipe: atlassian/demo-pipe-python:0.1.2
        variables:
            NAME: "foobar"
```

Advanced example:

```yaml
script:
    -   pipe: atlassian/demo-pipe-python:0.1.2
        variables:
            NAME: "foobar"
            DEBUG: "true"
```

## Support

