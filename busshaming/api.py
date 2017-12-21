from rest_framework import filters, mixins, serializers, viewsets

from .models import Route, StopSequence, Trip


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ('id', 'gtfs_trip_id', 'version', 'route', 'trip_headsign', 'trip_short_name', 'direction', 'wheelchair_accessible', 'bikes_allowed', 'notes', 'created_at')


class TripViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class StopSequenceSerializer(serializers.HyperlinkedModelSerializer):
    trip_set = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='trip-detail'
    )

    class Meta:
        model = StopSequence
        fields = ('id', 'sequence_hash', 'stop_sequence', 'length', 'route', 'trip_headsign', 'trip_short_name', 'direction', 'trip_set')


class StopSequenceLiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StopSequence
        fields = ('id', 'sequence_hash', 'stop_sequence', 'length', 'route', 'trip_headsign', 'trip_short_name', 'direction')


class StopSequenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StopSequence.objects.all()
    serializer_class = StopSequenceSerializer


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    stopsequence_set = StopSequenceLiteSerializer

    class Meta:
        model = Route
        fields = ('id', 'url', 'gtfs_route_id', 'short_name', 'long_name', 'description', 'color', 'text_color', 'route_url', 'stopsequence_set')
        depth = 1


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('short_name', 'long_name', 'description')
