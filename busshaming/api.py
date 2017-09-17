from rest_framework import mixins, serializers, viewsets

from .models import Route


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'gtfs_route_id', 'short_name', 'long_name', 'description', 'url', 'color', 'text_color')


class RouteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    lookup_field = 'id'
