from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class SoftDeleteModel(models.Model):
    """
    Add the fields and methods necessary to support soft delete of the model
    """
    deleted = models.DateTimeField(
        _('date of deletion'),
        null=True,
        blank=True,
        default=None,
        help_text=_('The date and time when the object was deleted')
    )

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """
        Mark object as soft deleted.
        :return: None
        """
        self.deleted = timezone.now()

    def undelete(self) -> None:
        """
        Mark the object as not soft deleted
        :return: None
        """
        self.deleted = None
