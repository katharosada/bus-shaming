from rest_framework import mixins, serializers, viewsets

from .models import Route, Trip


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ('id', 'gtfs_trip_id', 'version', 'route', 'trip_headsign', 'trip_short_name', 'direction', 'wheelchair_accessible', 'bikes_allowed', 'notes', 'created_at')


class TripViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    trip_set = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='trip-detail'
    )

    class Meta:
        model = Route
        fields = ('id', 'url', 'gtfs_route_id', 'short_name', 'long_name', 'description', 'color', 'text_color', 'route_url', 'trip_set')


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
