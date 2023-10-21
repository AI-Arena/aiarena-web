import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .default import *  # noqa: F403


DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY", None)
if SECRET_KEY is None:
    raise Exception("You must set the SECRET_KEY to something secure before running in production or staging.")

ALLOWED_HOSTS = ["aiarena-test.net", "aiarena.net", "*"]

#################################
# Django Storages & django-private-storage configuration #
#################################

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
PRIVATE_STORAGE_CLASS = "private_storage.storage.s3boto3.PrivateS3BotoStorage"

AWS_STORAGE_BUCKET_NAME = os.environ.get("MEDIA_BUCKET")
AWS_PRIVATE_STORAGE_BUCKET_NAME = os.environ.get("MEDIA_BUCKET")

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
if (
    not AWS_ACCESS_KEY_ID
    or not AWS_SECRET_ACCESS_KEY
    and (credentials_endpoint := os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"))
):
    import requests

    # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html
    credentials = requests.get(f"169.254.170.2{credentials_endpoint}").json()
    AWS_ACCESS_KEY_ID = credentials["AccessKeyId"]
    AWS_SECRET_ACCESS_KEY = credentials["SecretAccessKey"]


AWS_S3_REGION_NAME = "eu-central-1"
AWS_S3_OBJECT_PARAMETERS = {"ACL": "private"}
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_PRIVATE_S3_ADDRESSING_STYLE = "virtual"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_PRIVATE_S3_SIGNATURE_VERSION = "s3v4"
AWS_PRIVATE_S3_ENCRYPTION = True
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 60 * 60

# Sentry configuration
SENTRY_DSN = os.environ.get("SENTRY_DSN")
BUILD_NUMBER = os.environ.get("BUILD_NUMBER")
if SENTRY_DSN:
    sentry_kwargs = {
        "dsn": SENTRY_DSN,  # noqa: F405
        "integrations": [
            CeleryIntegration(),
            DjangoIntegration(),
            RedisIntegration(),
        ],
        "release": BUILD_NUMBER,
        "send_default_pii": True,
        # https://docs.sentry.io/performance/distributed-tracing/#python
        # https://ivelum.slack.com/archives/C0PT3267R/p1675054580786709
        "traces_sample_rate": 0.0,
        "attach_stacktrace": True,
    }
    sentry_sdk.init(**sentry_kwargs)
