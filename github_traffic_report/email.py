import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    subject,
    html,
    to_email,
    from_email,
    smtp_host,
    smtp_port,
    smtp_username,
    smtp_password,
):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html"))

    mailServer = smtplib.SMTP(smtp_host, smtp_port)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(smtp_username, smtp_password)
    mailServer.sendmail(from_email, to_email, msg.as_string())
    mailServer.close()
