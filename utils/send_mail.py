from typing import List, Optional

from django.core.mail import EmailMessage


def send_mail(subject: str, message: str, receiver_list: List[str],
              cc_list: Optional[List[str]] = None,
              sender: Optional[str] = None,
              **kwargs) -> None:
    if cc_list is None:
        cc_list = []
    email = EmailMessage(subject, message, sender, to=receiver_list,
                         cc=cc_list, **kwargs)
    email.content_subtype = 'html'
    email.send()
