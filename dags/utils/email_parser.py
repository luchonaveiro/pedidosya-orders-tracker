"Email Parser"

import email
from email.header import decode_header
from bs4 import BeautifulSoup


class EmailParser:
    def __init__(self, response):
        self.response = response
        self.msg = email.message_from_bytes(response[1])

    def get_email_subject(self):
        if isinstance(self.response, tuple):
            # decode the email subject
            subject, encoding = decode_header(self.msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)

            return subject

    def get_email_sender(self):
        if isinstance(self.response, tuple):
            # decode email sender
            From, encoding = decode_header(self.msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)

        return From

    def get_email_send_date(self, parse_date=False):
        if isinstance(self.response, tuple):
            # decode send date
            date, encoding = decode_header(self.msg.get("Date"))[0]
            if isinstance(date, bytes):
                date = date.decode(encoding)

            return date

    def get_email_body(self):
        if isinstance(self.response, tuple):

            # if the email message is multipart
            if self.msg.is_multipart():
                # iterate over email parts
                for part in self.msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
            else:
                # extract content type of email
                content_type = self.msg.get_content_type()
                # get the email body
                body = self.msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print("Body:", body)
            if content_type == "text/html":
                # print(body)
                body = BeautifulSoup(body, "html.parser")

            return body
