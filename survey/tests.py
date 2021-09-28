import json
from django.test import RequestFactory
from graphene.test import Client
from server.schema import schema
from graphene_django.utils.testing import GraphQLTestCase
from django.contrib.auth import get_user_model


class QuestionnaireCreateTestCase(GraphQLTestCase):

    def setUp(self):
        self.client = Client(schema)
        request_factory = RequestFactory()
        self.context = request_factory.get('/api/')
        self.context.user = get_user_model().objects.create(
            email="testuser@test.com",
            password="Password1"
        )

    def test_create_questionnaire_mutation(self):
        response = self.client.execute(
            '''
            mutation {
                createQuestionnaire(title: "DLF title") {
                    questionnaire {
                        id
                        title
                    }
                }
            }
            ''',
            op_name='createQuestionnaire',
            # input_data={'title': 'DLF qq'},
            context_value=self.context
        )

        assert response.get('data').get('createQuestionnaire') == {
            'myQuestionnaires': []
        }

    def test_my_questionnaires_query(self):
        response = self.client.execute(
            '''
            query {
              myQuestionnaires{
                id
                title,
                questions{
                  id
                }
              }
            }
            ''',
            op_name='Questionnaire',
            context_value=self.context
        )

        assert response.get('data') == {
            'myQuestionnaires': []
        }
