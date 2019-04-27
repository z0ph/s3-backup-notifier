import datetime

import boto3

import botocore

from botocore.exceptions import ClientError

# Get Today's date
today = datetime.date.today()
todaystr = str(today)

AWS_REGION = "eu-west-1"

# Create a new SES resource and specify a region.
client = boto3.client('ses', region_name=AWS_REGION)

# Get Objects date
s3 = boto3.resource('s3', region_name=AWS_REGION)
bucket = s3.Bucket('zoph.backup')
objs = bucket.objects.filter(Prefix='Jeedom').all()


def main(event, context):
    print objs
    try:
        for obj in objs:
            print obj
            lastobjectdate = (obj.last_modified).date()
            print lastobjectdate
            lastobjectstr = str(lastobjectdate)
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print("There is no file in this bucket")
        else:
            print e

    # Compare with defined date
    if today == lastobjectdate:
        print("OK, latest file comes from " + lastobjectstr + ". We are: " + todaystr)
    else:
        # SES Notification
        # Try to send the email.
        try:
            # Email Setting (SES)
            # Replace sender@example.com with your "From" address.
            # This address must be verified with Amazon SES.
            SENDER = "Alfred Backup <victor.grenu@gmail.com>"

            # Replace recipient@example.com with a "To" address. If your account
            # is still in the sandbox, this address must be verified.
            RECIPIENT = "victor.grenu@gmail.com"

            # Specify a configuration set. If you do not want to use a configuration
            # set, comment the following variable, and the
            # ConfigurationSetName=CONFIGURATION_SET argument below.
            #CONFIGURATION_SET = "ConfigSet"

            # Subject line for the email.
            SUBJECT = "Alfred Backup Failed"

            # Email body for recipients with non-HTML email clients.
            BODY_TEXT = ("Alert - Warning\r\n"
                        "Jeedom Backup Failed"
                        "Alfred"
                        )
                        
            # HTML body of the email.
            BODY_HTML = """<html>
            <head></head>
            <body>
            <h1>Alfred Jeedom Automated Backup</h1>
            <p>Jeedom backup failed on """ + todaystr + """</p>
            <p>The latest key in S3 comes from """ + lastobjectstr + """</p>
            <p>Alfred</p>
            </body>
            </html>
                        """

            # Character encoding for the email.
            CHARSET = "UTF-8"
            # Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("We are: " + todaystr + ". file is old: " + lastobjectstr)
            print("Email sent! Message ID:"),
            print(response['MessageId'])

# Run locally for testing purpose
# main()
