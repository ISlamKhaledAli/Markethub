from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=Category.objects.all(), message="Category with this name already exists.")]
    )
    slug = serializers.SlugField(
        max_length=120,
        validators=[UniqueValidator(queryset=Category.objects.all(), message="Category with this slug already exists.")]
    )
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'image', 'subcategories', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_subcategories(self, obj: Category) -> list[dict]:
        serializer = self.__class__(obj.subcategories.all(), many=True)
        return serializer.data

    def validate_parent(self, value: Category | None) -> Category | None:
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value