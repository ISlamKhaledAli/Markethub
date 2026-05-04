from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import SellerProfile

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = user.role
        token['user_id'] = str(user.id)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['user_id'] = self.user.id
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    store_name = serializers.CharField(required=False)  # For sellers

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'role', 'password', 'password_confirm', 'store_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        store_name = validated_data.pop('store_name', None)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone'),
            role=validated_data.get('role', 'customer')
        )

        if user.role == 'seller' and store_name:
            SellerProfile.objects.create(user=user, store_name=store_name)
        elif user.role == 'seller' and not store_name:
            # If seller but no store name, maybe use email or generic
            SellerProfile.objects.create(user=user, store_name=f"{user.email.split('@')[0]}'s Store")
            
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    seller_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'role', 'is_verified', 'created_at', 'seller_profile')
        read_only_fields = ('id', 'role', 'is_verified', 'created_at')

    def get_seller_profile(self, obj):
        if obj.role == 'seller' and hasattr(obj, 'seller_profile'):
            return {
                "store_name": obj.seller_profile.store_name,
                "description": obj.seller_profile.description,
                "is_approved": obj.seller_profile.is_approved,
                "balance": str(obj.seller_profile.balance)
            }
        return None

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
