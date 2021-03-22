# EventBridge Rules DST

This lambda helps managed EventBridge Rules in your account that depend on
daylight saving time (DST). You create two versions of a scheduled rule, one
for daylight saving time and one for standard time, and the Lambda enables and
disables the corrent one.

## Using

For rules that depend on DST you create two versions: one for DST with the
timezone abbreviation as the suffix, and one for standard time with the
timezone abbreviation as the suffix. When the rule is created the Lambda will
disable the one that shouldn't be currently active, and at the transition
times it will switch all the relavent rules in your account.

For example, if you are in the `US/Central` timezone then the two abbreviations
are `CST` and `CDT`. If you wanted a task to run at noon then you'd create
these two rules:

- `my-task-CST` with a schedule expression of `cron(0 18 * * ? *)` (18:00 UTC).
- `my-task-CDT` with a schedule expression of `cron(0 17 * * ? *)` (17:00 UTC).

The lambda will enable `my-task-CST` between the 1st Sunday of November at
07:01 UTC and the 2nd Sunday of March before 08:01 UTC. It will enable
`my-task-CDT` between the 2nd Sunday of March at 08:01 UTC and the 1st Sunday
of November before 07:01 UTC.

**We highly recommend you do not schedule events between the ambiguous local
times.** Events between 1am and 2am on the 1st Sunday in November may repeat, and
events between 2am and 3am on the 2nd Sunday in March may be skipped.

## Deploying

This lambda is developed as a SAM Application. You can deploy it manually using
the SAM CLI:

```bash
sam build
sam deploy --guided
```

If you want to deploy this with terraform you will need to package it in an
S3 bucket and then use the packaged template in a terraform
`aws_cloudformation_stack` resource:

```bash
sam build
sam package --s3-bucket my-artifacts-bucket --s3-prefix eventrules-dst \
    --output-template-file packaged-template.yml
```

You can also deploy it automatically using CodePipeline and CodeBuild. The
`buildspec.yml` contains more information about the expected CodeBuild
environment variables.

Each deployment only supports managing DST for a single timezone. If you need
to manage DST in multiple timezones then create multiple deployments, one for
each timezone.

### Configuration

The only parameter that is configurable is the `LocalTimezone`. You can specify
these values: `US-Eastern`, `US-Central`, `US-Mountain`, and `US-Pacific`. If
you need a timezone not listed then submit a pull request with the necessary
changes to the `TimezoneMap` mapping.

There are other internal parameters related to our common configurations:
`LambdaMonitorTemplateURL`; `LambdaMonitorAlarmTopicARN`; `LogSubscriptionARN`;
`LogKMSKeyARN`. You do not need to specify these and the lambda should work fine
without them.

## Development

You can setup your own development environment using virtuan-env:

```bash
python3.8 -mvenv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install awscli aws-sam-cli
pip install -r tests/requirements.txt
```

Every time you make a change to the source code you must run `sam build` before
running the lint or test commands. This is because the linter and unit tester
look at the code in `.aws-sam/build/` and **not** the code in `src/`. For
example:

```bash
sam build
pylint .aws-sam/build/EventsDSTFunction/
pytest -v tests/EventsDSTFunction/
```
