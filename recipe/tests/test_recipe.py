from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def sample_recipe(user, **params):
    """Crear y retornar receta"""
    defaults = {
        'title':'sample recipe',
        'price': 5
    }
    defaults.update(**params)

    return Recipe.objects.create(user=user, **defaults)

def sample_tag(user, name='main course'):
    """Crea tag de ejemplo"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='cinnamon'):
    """crea ingrediente de ejemplo"""
    return Ingredient.objects.create(user=user, name=name)

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeApiTest(TestCase):
    """ Prueba las recetas tags disponibles publicamente """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recipe(self):
        """Prueba obtener recetas"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_recipes_limited_to_user(self):
        """PRueba que las recetas sean del usuario"""
        user2 = get_user_model().objects.create_user(
           'test2@test.com',
            'password'
        )
 
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)        
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_detail(self):
        """Prueba ver detalles de receta"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Prueba la creacion de recetas"""
        payload = {
            'tile':'Test Recipe',
            'price': 15,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_recipe_with_tags(self):
        """Prueba la creacion de recetas con tags"""
        tag1 = sample_tag(user=self.user, name='Tag1')
        tag2 = sample_tag(user=self.user, name='Tag2')
        payload = {
            'title': 'Test recipe with two tags',
            'tags': [tag1.id, tag2.id],
            'price': 10.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Prueba la creacion de recetas con ingredientes"""
        ingredient1 = sample_tag(user=self.user, name='ingredient1')
        ingredient2 = sample_tag(user=self.user, name='ingredient2')
        payload = {
            'title': 'Test recipe with two tags',
            'ingredient': [ingredient1.id, ingredient2.id],
            'price': 10.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)