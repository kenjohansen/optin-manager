"""
Generic code sending utility for email and SMS. Supports pluggable providers.
"""
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional

class CodeSender:
    def __init__(self, email_provider: str, sms_provider: str, email_creds: dict, sms_creds: dict):
        self.email_provider = email_provider
        self.sms_provider = sms_provider
        self.email_creds = email_creds
        self.sms_creds = sms_creds

    def send_email_code(self, to_email: str, code: str, subject: str = None, body: str = None) -> bool:
        if self.email_provider == "aws_ses":
            return self._send_email_ses(to_email, code, subject=subject, body=body)
        # Future: add SendGrid, SMTP, etc.
        raise NotImplementedError(f"Email provider {self.email_provider} not supported yet.")

    def send_sms_code(self, to_phone: str, code: str, body: str = None) -> bool:
        if self.sms_provider == "aws_sns":
            return self._send_sms_sns(to_phone, code, body=body)
        # Future: add Twilio, etc.
        raise NotImplementedError(f"SMS provider {self.sms_provider} not supported yet.")

    def _send_email_ses(self, to_email: str, code: str, subject: str = None, body: str = None) -> bool:
        client = boto3.client(
            "ses",
            aws_access_key_id=self.email_creds["access_key"],
            aws_secret_access_key=self.email_creds["secret_key"],
            region_name=self.email_creds["region"],
        )
        subject = subject or "Your Verification Code"
        body = body or f"Your verification code is: {code}"
        try:
            client.send_email(
                Source=self.email_creds["from_address"],
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            return True
        except ClientError as e:
            print(f"[send_code] SES send failed: {e}")
            return False

    def _send_sms_sns(self, to_phone: str, code: str, body: str = None) -> bool:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Preparing to send SMS via AWS SNS to: {to_phone[:3]}...")
        logger.info(f"Using AWS region: {self.sms_creds['region']}")
        
        # Check if credentials are properly set
        if not self.sms_creds["access_key"] or not self.sms_creds["secret_key"]:
            logger.error("AWS credentials are missing or empty")
            return False
            
        # Validate phone number format for SNS
        if not to_phone.startswith('+'):
            logger.warning(f"Phone number does not start with +: {to_phone[:3]}...")
            to_phone = f"+{to_phone}"
            
        try:
            # Create the SNS client
            client = boto3.client(
                "sns",
                aws_access_key_id=self.sms_creds["access_key"],
                aws_secret_access_key=self.sms_creds["secret_key"],
                region_name=self.sms_creds["region"],
            )
            
            # Prepare the message
            message = body or f"Your verification code is: {code}"
            logger.info(f"SMS message length: {len(message)} characters")
            
            # Send the message
            logger.info(f"Sending SMS via AWS SNS...")
            response = client.publish(
                PhoneNumber=to_phone,
                Message=message
            )
            
            # Log the response
            logger.info(f"AWS SNS response: {response}")
            message_id = response.get('MessageId')
            logger.info(f"SMS sent successfully with MessageId: {message_id}")
            
            return True
        except ClientError as e:
            logger.error(f"AWS SNS ClientError: {e}")
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code')
            error_message = getattr(e, 'response', {}).get('Error', {}).get('Message')
            logger.error(f"Error code: {error_code}, Message: {error_message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return False
