# Mail Service
This service is used for sending emails to users or participants among data space.

### Security
Access to service is restricted and only clients using specific api-key can take actions via requests. \
`slowapi library` allows to limit 5 requests from single IP address per minute to ensure stability and availability of the system in case of DOS.

### Actions
POST endpoint is available at "/email". If client has proper api-key and provides legitimate credentials to his email-client. The email will be automatically sent.

### Data protection
All requests will use `HTTPS protocol` so will be encrypted during transportation. \
No data of clients are stored in this shared service. It is for the usage of multiple clients so the service protects from stealing credentials. It is trusted service for all users and participants of Data Space. 

### Request body
```
{
    "config": {
        "MAIL_USERNAME": <email_username>,
        "MAIL_PASSWORD": <password_to_email>,
        "MAIL_FROM": <email_username>,
        "MAIL_PORT": <outcoming_port>,
        "MAIL_SERVER": <mail_server>,
        "MAIL_FROM_NAME": <desired_name>,
        "MAIL_STARTTLS" : Optional<bool>,
        "MAIL_SSL_TLS" : Optional<bool>,
        "USE_CREDENTIALS" : Optional<bool>,
        "VALIDATE_CERTS" : Optional<bool>
    },
    "recipients": [
        <recipient_1>,
        <recipient_2>,
        ...
    ],
    "subject": <subject>,
    "body": <body_or_rendered_template>,
    "body_type": <"html"/"plain">
}
```