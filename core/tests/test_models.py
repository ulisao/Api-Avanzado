from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='user@test.com', password='passtest'):
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """Probar creando un nuevo usuario con email exitoso"""
        email = 'test@datadosis.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Testea si el email esta normalizado"""
        email = 'lolaso@EMAIL.COM'
        user = get_user_model().objects.create_user(
            email,
            'test123'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Testea si el email es invalido"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Testea si se puede crear un nuevo superusuario"""
        email = 'test@datadosis.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """probar representacion en texto del tag"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='meat'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Representacion en texto de los ingredientes"""
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name = 'Banana'
        )

        self.assertEqual(str(ingredient), ingredient.name)
    
    def test_recipe_str(self):
        """Representacion en texto de las recetas"""
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title='Steak and mushroom sauce',
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)