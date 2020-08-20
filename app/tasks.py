from datetime import datetime
import json
import os

import boto3


BUCKET = os.environ.get('BUCKET')
if BUCKET:
    s3 = boto3.client('s3')


def create_task(feedback):
    if not BUCKET:
        # no-op since env vars not set
        return True
    agree, feedback, clause = feedback.split("|")
    validated_data = dict(
        agree=agree,
        feedback=feedback,
        clause=clause
    )
    now = datetime.now().strftime("%Y-%m-%d")
    s3.put_object(
        Body=bytes(json.dumps(validated_data).encode('UTF-8')),
        Bucket=BUCKET,
        Key=f'validated_data_{now}.json'
    )
    return True
