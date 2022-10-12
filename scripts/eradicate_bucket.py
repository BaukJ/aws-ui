#!/usr/bin/env python3
import boto3

region = "eu-west-2"
s3 = boto3.resource('s3', region)
s3control = boto3.client('s3control', region)
account_id = boto3.client('sts').get_caller_identity().get('Account')

def eradicate_bucket(bucket_name):
    bucket = s3.Bucket(bucket_name)
    # First delete all objects
    bucket.objects.all().delete()

    # Now find and delete all the access points
    aps = s3control.list_access_points(
        AccountId=account_id,
        Bucket=bucket.name
    )
    for a in aps["AccessPointList"]:
        s3control.delete_access_point(
            AccountId=account_id,
            Name=a["Name"],
        )

    # Now you can delete the bucket
    bucket.delete()

eradicate_bucket("bucket-name")
