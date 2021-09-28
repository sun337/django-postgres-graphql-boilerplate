import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class Questionnaire(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    owner = models.ForeignKey(User, related_name="questionnaires", null=False, blank=False, on_delete=models.CASCADE)
    url = models.URLField(null=False, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    SHORT_TEXT = "short-text"

    CHOICES_HELP_TEXT = _(
        """The choices field is only used if the question type
    if the question type is 'radio', 'select', or
    'select multiple' provide a comma-separated list of
    options for this question ."""
    )

    QUESTION_TYPES = (
        (SHORT_TEXT, _("short text (one line)")),
    )
    title = models.TextField(null=False, blank=False)
    questionnaire = models.ForeignKey(Questionnaire, related_name="questions", null=False, blank=False, on_delete=models.CASCADE)
    order = models.IntegerField(_("Order"), default=0)
    type = models.CharField(_("Type"), max_length=200, choices=QUESTION_TYPES, default=SHORT_TEXT)
    choices = models.TextField(_("Choices"), blank=True, null=True, help_text=CHOICES_HELP_TEXT)

    def __str__(self):
        return self.title


class Response(models.Model):
    """
    A Response object is a collection of questions and answers.
    """
    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    survey = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="responses")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_("User"), null=True, blank=True)
    interview_uuid = models.CharField(_("Interview unique identifier"), max_length=36)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Question"), related_name="answers")
    response = models.ForeignKey(Response, on_delete=models.CASCADE, verbose_name=_("Response"), related_name="answers")
    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    body = models.TextField(_("Content"), blank=True, null=True)

