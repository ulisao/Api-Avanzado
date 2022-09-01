from multiprocessing import reduction
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BasicAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """Viewsets base"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """retorna objetos para el usuario auntenticado"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        """crea nuevo elemento"""
        serializer.save(user=self.request.user)


class TagViewSet(BasicAttrViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredientViewSet(BasicAttrViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retorna objetos para el usuario auntenticado"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Retorna el serializador apropiado"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        """crea nuevo elemento"""
        serializer.save(user=self.request.user)