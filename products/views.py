from rest_framework import viewsets
from django.db.models import QuerySet
from .models import Category
from .serializers import CategorySerializer
from .permissions import IsAdminOrReadOnly

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by(
        '-created_at'
    )
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self) -> QuerySet[Category]:
        return super().get_queryset().prefetch_related('subcategories')
