"""
app/utils/send_code.py

Generic code sending utility for email and SMS with pluggable provider support.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional

class CodeSender:
    """
    A utility class for sending verification codes via email and SMS.
    
    This class implements a provider-agnostic approach to sending verification codes,
    which is essential for the opt-in verification workflow. The pluggable provider
    architecture allows the system to switch between different email and SMS services
    without changing the core verification logic, providing flexibility and resilience
    against provider outages or future provider changes.
    """
    
    def __init__(self, email_provider: str, sms_provider: str, email_creds: dict, sms_creds: dict):
        """
        Initialize the CodeSender with provider configurations.
        
        The separation of provider selection and credentials allows for dynamic
        configuration changes through the admin interface, enabling administrators
        to switch providers or update credentials without code changes.
        
        Args:
            email_provider (str): The email service provider to use (e.g., "aws_ses")
            sms_provider (str): The SMS service provider to use (e.g., "aws_sns")
            email_creds (dict): Credentials and configuration for the email provider
            sms_creds (dict): Credentials and configuration for the SMS provider
        """
        self.email_provider = email_provider
        self.sms_provider = sms_provider
        self.email_creds = email_creds
        self.sms_creds = sms_creds

    def send_email_code(self, to_email: str, code: str, subject: str = None, body: str = None) -> bool:
        """
        Send a verification code via email.
        
        Email verification is critical for confirming user identity and consent
        before allowing opt-in/opt-out actions. This method abstracts away the
        specific email provider implementation, routing the request to the
        appropriate provider-specific method based on configuration.
        
        Args:
            to_email (str): The recipient's email address
            code (str): The verification code to send
            subject (str, optional): Custom email subject line
            body (str, optional): Custom email body text
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
            
        Raises:
            NotImplementedError: If the configured email provider is not supported
        """
        if self.email_provider == "aws_ses":
            return self._send_email_ses(to_email, code, subject=subject, body=body)
        # Future: add SendGrid, SMTP, etc.
        raise NotImplementedError(f"Email provider {self.email_provider} not supported yet.")

    def send_sms_code(self, to_phone: str, code: str, body: str = None) -> bool:
        """
        Send a verification code via SMS.
        
        SMS verification provides an alternative to email verification and is often
        preferred for time-sensitive communications. This method abstracts away the
        specific SMS provider implementation, routing the request to the appropriate
        provider-specific method based on configuration.
        
        Args:
            to_phone (str): The recipient's phone number in E.164 format
            code (str): The verification code to send
            body (str, optional): Custom SMS message text
            
        Returns:
            bool: True if the SMS was sent successfully, False otherwise
            
        Raises:
            NotImplementedError: If the configured SMS provider is not supported
        """
        if self.sms_provider == "aws_sns":
            return self._send_sms_sns(to_phone, code, body=body)
        # Future: add Twilio, etc.
        raise NotImplementedError(f"SMS provider {self.sms_provider} not supported yet.")

    def _send_email_ses(self, to_email: str, code: str, subject: str = None, body: str = None) -> bool:
        """
        Send an email using Amazon SES (Simple Email Service).
        
        AWS SES is used as the primary email provider due to its reliability,
        deliverability rates, and cost-effectiveness at scale. This implementation
        uses the AWS SDK to interact with the SES API, handling the complexities
        of authentication and request formatting.
        
        Args:
            to_email (str): The recipient's email address
            code (str): The verification code to include in the email
            subject (str, optional): Custom email subject line
            body (str, optional): Custom email body text
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
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
        """
        Send an SMS using Amazon SNS (Simple Notification Service).
        
        AWS SNS is used as the primary SMS provider due to its global reach,
        reliability, and integration with other AWS services. This implementation
        includes extensive logging to help troubleshoot delivery issues, which
        are common with SMS services due to carrier restrictions and international
        regulations.
        
        Args:
            to_phone (str): The recipient's phone number in E.164 format
            code (str): The verification code to include in the SMS
            body (str, optional): Custom SMS message text
            
        Returns:
            bool: True if the SMS was sent successfully, False otherwise
        """
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
