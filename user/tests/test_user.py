from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTest(TestCase):
    """testea la autenticacion de usuarios"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """testea la creacion de usuarios validos"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',  
            'name': 'Test name'      
            }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """testea que no se pueda crear un usuario que ya existe"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',  
            'name': 'Test name'      
            }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """testea que la contraseña sea mas larga"""
        payload = {
            'email': 'test@test.com',
            'password': 'test',    
            'name': 'Test name'  
            }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        """Prueba que el token se cree"""
        payload = {
            'email': 'test@test.com',
            'password': 'test',    
            'name': 'Test name'  
            }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_credentials(self):
        """Probar que el token no se crea con credenciales invalidas"""
        create_user(email='test@test.com', password='testpass')
        payload = {'email':'test@test.com', 'password':'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_user(self):
        """Probar que el token no se crea sin un usuario"""
        payload = {'email': 'test@test.com','password': 'test'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password(self):
        """Probar que el token no se crea sin contraseña"""
        res = self.client.post(TOKEN_URL, {'email':'one', 'password':''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthenticated(self):
        """Probar que la auntenticacion sea requerida"""
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTest(TestCase):
    """testea la autenticacion de usuarios"""
    def setUp(self):
        self.user = create_user(
            email = 'user@example.com',
            password = 'password',
            name = 'name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self):
        """ testea obetener perfil del usuario exitosamente""" 
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name': self.user.name,
            'email': self.user.email,
        })
    
    def test_post_not_allowed(self):
        """prueba que el post no sea permitido"""
        res =self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_update(self):
        """testea que se actualice el perfil"""
        payload = {
            'password': 'newpassword',    
            'name': 'new name'
            }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)