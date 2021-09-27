import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from survey.models import Questionnaire, Question


class Base64DecodeNode(graphene.relay.Node):
    class Meta:
        name = 'Node'

    @staticmethod
    def to_global_id(type_, id):
        return f"{type_}-{id}"


class QuestionNode(DjangoObjectType):
    class Meta:
        model = Question
        interfaces = (Base64DecodeNode,)
        filter_fields = ("id", "title", "type", "questionnaire")


class QuestionnaireNode(DjangoObjectType):
    class Meta:
        model = Questionnaire
        interfaces = (Base64DecodeNode,)
        filter_fields = ("id", "title", "owner", "url", "questions")


class QuestionnaireConnection(graphene.relay.Connection):
    class Meta:
        node = QuestionnaireNode


class Query(graphene.ObjectType):
    all_questionnaires = DjangoFilterConnectionField(QuestionnaireNode)
    my_questionnaires = graphene.relay.ConnectionField(QuestionnaireConnection)

    def resolve_my_questionnaires(root, info, **kwargs):
        queryset = Questionnaire.objects.all()
        if info.context.user.is_anonymous:
            return queryset.none()
        return queryset.filter(owner=info.context.user)


class UpdateQuestion(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        id = graphene.ID()

    question = graphene.Field(QuestionNode)

    @classmethod
    def mutate(cls, root, info, text, id):
        question = Question.objects.get(id=id)
        question.title = text
        question.save()
        return UpdateQuestion(question=question)


class CreateQuestion(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        type = graphene.String()
        order = graphene.Int()
        choices = graphene.String()
        questionnaire_id = graphene.ID()

    question = graphene.Field(QuestionNode)

    # Where you really do all the mutation 🦁 🐉
    def mutate(self, info, title, type, questionnaire_id):
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        question = Question.objects.create(
            title=title,
            type=type,
            questionnaire=questionnaire
        )

        question.save()
        # return an instance of the Mutation 🤷‍♀️
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
        # The input arguments for this mutation
        title = graphene.String(required=True)
        id = graphene.ID()

    # The class attributes define the response of the mutation
    questionnaire = graphene.Field(QuestionnaireNode)

    @classmethod
    def mutate(cls, root, info, title, id):
        questionnaire = Questionnaire.objects.get(id=id)
        questionnaire.title = title
        questionnaire.save()
        # Notice we return an instance of this mutation
        return UpdateQuestionnaire(questionnaire=questionnaire)


class Mutation(graphene.ObjectType):
    create_question = CreateQuestion.Field()
    update_question = UpdateQuestion.Field()

    create_questionnaire = CreateQuestionnaire.Field()
    update_questionnaire = UpdateQuestionnaire.Field()
