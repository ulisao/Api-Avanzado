from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTest(TestCase):
    """ Prueba los api tags disponibles publicamente """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ prueba si el login es requerido"""
        res =self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTest(TestCase):
    """ Prueba los api tags disponibles privadamente """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrieve_tags(self):
        """Prueba obtener tags"""
        Tag.objects.create(user=self.user, name="Meat")
        Tag.objects.create(user=self.user, name="Banana")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """PRueba que los tags sean del usuario"""
        user2 = get_user_model().objects.create_user(
           'test2@test.com',
            'password'
        )
        Tag.objects.create(user=user2, name='raspberry')
        tag = Tag.objects.create(user=self.user, name='comfort food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag(self):
        """prueba crear tags"""
        payload = {'name': 'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_tag_invalid(self):
        """Prueba creacion invalida"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)