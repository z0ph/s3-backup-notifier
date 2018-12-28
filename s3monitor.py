import boto3
from botocore.exceptions import ClientError
import botocore
import datetime

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

#If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = "eu-west-1"

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
  <h1>Alfred Jeedom Backup</h1>
  <p>Jeedom backup failed today</p>
  <p>The file is not present on S3</p>
  <p>Alfred</p>
</body>
</html>
            """            

# Character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name=AWS_REGION)

# Get Today's date
today = datetime.date.today()

# Get Objects date
s3 = boto3.resource('s3',region_name=AWS_REGION)
bucket = s3.Bucket('zoph.backup')
objs = bucket.objects.filter(Prefix='Jeedom').limit(1)


def get_object_check_alarm():
    try:
        for obj in objs:
            print(obj)
            lastobjectdate = (obj.last_modified).date()
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print("There is no file")

    # Compare with defined date
    if today == lastobjectdate:
        print(today)
        print(lastobjectdate)
        print("OK, lastest file comes from today")
    else:
        print(today)
        print(lastobjectdate)
        print("Mail sent")
        # SES Notification
        # Try to send the email.
        '''
        try:
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
                # If you are not using a configuration set, comment or delete the
                # following line
                #ConfigurationSetName=CONFIGURATION_SET,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            print ("KO, file is too old, sending alert email")
        '''


def main():
    get_object_check_alarm()

# Run locally


main()# only for testing purpose