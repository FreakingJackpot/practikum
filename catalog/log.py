from logging import Handler, LogRecord
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from practikum.settings import SENDGRID_API_KEY, SENDGRID_MAIL_FROM

from .models import Settings


class EmailHandler(Handler):
    def emit(self, record: LogRecord) -> None:
        self.notice_admins(record.levelname, record.msg)

    def notice_admins(self, level, message):
        setting = Settings.objects.get(key='request_emails')
        emails = setting.value.split(',')
        if emails:
            message = Mail(from_email=SENDGRID_MAIL_FROM, to_emails=emails, subject=level,
                           plain_text_content=message)

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
