from wsgiref.headers import tspecials
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredients(TestCase):
    """Prueba api ingredientes accesibles publicamente"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ prueba si el login es requerido"""
        res =self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredients(TestCase):
    """Prueba api ingredientes accesibles privadamente"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Prueba obtener ingredientes"""
        Ingredient.objects.create(user=self.user, name="salt")
        Ingredient.objects.create(user=self.user, name="cheese")

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Prueba que los ingredientes sean del usuario"""
        user2 = get_user_model().objects.create_user(
           'test2@test.com',
            'password'
        )
        Ingredient.objects.create(user=user2, name='cacao')
        ingredient = Ingredient.objects.create(user=self.user, name='comfort food')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
    
    def test_create_tag(self):
        """prueba crear ingredientes"""
        payload = {'name': 'Chocolate'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_ingredient_invalid(self):
        """Prueba creacion invalida"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)