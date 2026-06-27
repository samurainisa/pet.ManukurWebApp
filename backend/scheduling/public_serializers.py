from rest_framework import serializers

from services.serializers import ServiceSerializer
from users.models import MasterProfile, PublicReview
from visits.models import VisitPhoto


class PublicMasterProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = MasterProfile
        fields = ['display_name', 'city', 'address', 'phone', 'bio', 'telegram', 'avatar']

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url


class PublicReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicReview
        fields = ['id', 'client_name', 'rating', 'text', 'created_at']


class PublicPortfolioItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    service_name = serializers.CharField(source='appointment.service.name', read_only=True)

    class Meta:
        model = VisitPhoto
        fields = ['id', 'image', 'service_name', 'created_at']

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class PublicLandingSerializer(serializers.Serializer):
    master = PublicMasterProfileSerializer()
    rating_avg = serializers.FloatField()
    reviews_count = serializers.IntegerField()
    reviews = PublicReviewSerializer(many=True)
    portfolio = PublicPortfolioItemSerializer(many=True)
    services = ServiceSerializer(many=True)
