import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.conf import settings
from survey.models import Questionnaire, Question
from users.models import User


class Base64DecodeNode(graphene.relay.Node):
    class Meta:
        name = 'Node'

    @staticmethod
    def to_global_id(type_, id):
        return f"{type_}-{id}"


class QuestionNode(DjangoObjectType):
    class Meta:
        model = Question
        filter_fields = ("id", "title", "type", "questionnaire")


class QuestionnaireNode(DjangoObjectType):
    class Meta:
        model = Questionnaire
        interfaces = (Base64DecodeNode,)
        filter_fields = ("id", "title", "owner", "url", "questions")


class Query(graphene.ObjectType):
    all_questionnaires = DjangoFilterConnectionField(QuestionnaireNode)
    my_questionnaires = graphene.List(QuestionnaireNode)

    def resolve_my_questionnaires(root, info, **kwargs):
        queryset = Questionnaire.objects.all()
        if info.context.user.is_anonymous:
            return queryset.none()
        return queryset.filter(owner=info.context.user)


class UpdateQuestion(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        type = graphene.String()
        order = graphene.Int()
        choices = graphene.String()
        id = graphene.ID()

    question = graphene.Field(QuestionNode)

    @classmethod
    def mutate(cls, root, info, title, type, order, choices, id):
        question = Question.objects.get(id=id)
        question.title = title
        question.type = type
        question.order = order
        question.choices = choices
        question.save()
        return UpdateQuestion(
            question=question
        )


class DeleteQuestion(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = Question.objects.get(pk=kwargs["id"])
        if obj.questionnaire.owner != info.context.user:
            return cls(ok=False)
        obj.delete()
        return cls(ok=True)


class CreateQuestion(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        type = graphene.String()
        order = graphene.Int()
        choices = graphene.String()
        questionnaire_id = graphene.ID()

    question = graphene.Field(QuestionNode)

    @classmethod
    def mutate(cls, info, title, type, order, choices, questionnaire_id):
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        question = Question(
            title=title,
            type=type,
            order=order,
            choices=choices,
            questionnaire=questionnaire
        )
        question.save()
        return CreateQuestion(
            question=question
        )


class CreateQuestionnaire(graphene.Mutation):
    class Arguments:
        title = graphene.String()

    questionnaire = graphene.Field(QuestionnaireNode)

    def mutate(self, info, title):
        questionnaire = Questionnaire(
            title=title,
            owner=info.context.user
        )

        questionnaire.save()
        # return an instance of the Mutation
        return CreateQuestionnaire(
            questionnaire=questionnaire
        )


class UpdateQuestionnaire(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        is_published = graphene.Boolean()
        id = graphene.ID()

    questionnaire = graphene.Field(QuestionnaireNode)

    @classmethod
    def mutate(cls, root, info, title, is_published, id):
        questionnaire = Questionnaire.objects.get(id=id)
        questionnaire.title = title
        questionnaire.is_published = is_published
        if is_published:
            questionnaire.url = settings.GUI_URL+str(questionnaire.id)
        questionnaire.save()
        return UpdateQuestionnaire(
            questionnaire=questionnaire
        )


class Mutation(graphene.ObjectType):
    create_question = CreateQuestion.Field()
    update_question = UpdateQuestion.Field()
    delete_question = DeleteQuestion.Field()

    create_questionnaire = CreateQuestionnaire.Field()
    update_questionnaire = UpdateQuestionnaire.Field()
