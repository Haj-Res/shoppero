from typing import List, Optional

from django.core.mail import EmailMessage


def send_mail(subject: str, message: str, receiver_list: List[str],
              cc_list: Optional[List[str]] = None,
              sender: Optional[str] = None,
              **kwargs) -> None:
    """
    Wrapper function to simplify sending html type emails
    :param subject: subject of the email
    :param message: email content
    :param receiver_list: a list of emails to which to send the email
    :param cc_list: optional list of emails added as cc
    :param sender: optional string of the sender's email address
    :param kwargs: other keyword arguments used by the EmailMessage class
    :return: None
    """
    if cc_list is None:
        cc_list = []
    email = EmailMessage(subject, message, sender, to=receiver_list,
                         cc=cc_list, **kwargs)
    email.content_subtype = 'html'
    email.send()
