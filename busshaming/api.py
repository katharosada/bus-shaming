from datetime import datetime

from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from rest_framework.permissions import AllowAny


from .models import Route, Trip, TripDate, RealtimeEntry, RouteDate


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ('id', 'gtfs_trip_id', 'version', 'route', 'trip_headsign', 'trip_short_name', 'direction', 'wheelchair_accessible', 'bikes_allowed', 'notes', 'created_at')


class TripViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class RouteDateModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RouteDate
        fields = ('id', 'route', 'date', 'num_trips', 'trip_early_count', 'trip_ontime_count', 'trip_late_count', 'trip_verylate_count', 'trip_ontime_percent', 'min_delay', 'max_delay')


class RouteDateModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RouteDate.objects.all()
    serializer_class = RouteDateModelSerializer


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    recent_dates = RouteDateModelSerializer(read_only=True, many=True)

    class Meta:
        model = Route
        fields = ('id', 'url', 'gtfs_route_id', 'short_name', 'long_name', 'description', 'color', 'text_color', 'recent_dates')
        depth = 1


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('short_name', 'long_name', 'description')


class RealtimeEntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RealtimeEntry
        ordering = ['sequence']
        fields = ('id', 'stop_id', 'sequence', 'arrival_time', 'arrival_delay', 'departure_time', 'departure_delay')


class RealtimeEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RealtimeEntry.objects.all()
    serializer_class = RealtimeEntrySerializer


class TripDateSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'route_pk': 'trip__route_id',
    }

    class Meta:
        model = TripDate
        fields = ('id', 'trip_id', 'date', 'added_from_realtime')


class TripDatePlusSerializer(serializers.HyperlinkedModelSerializer):
    realtimeentry_set = serializers.SerializerMethodField('get_realtimes')

    def get_realtimes(self, obj):
        queryset = obj.realtimeentry_set.order_by('sequence')
        return RealtimeEntrySerializer(queryset, many=True).data

    class Meta:
        model = TripDate
        fields = ('id', 'trip_id', 'date', 'added_from_realtime', 'realtimeentry_set')
        depth = 1


class TripDateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TripDate.objects.all()
    serializer_class = TripDateSerializer


class RouteDateViewSet(viewsets.ViewSet):
    serializer_class = TripDateSerializer
    permission_classes = (AllowAny,)

    def list(self, request, route_pk=None):
        queryset = TripDate.objects.filter(trip__route_id=route_pk)
        serializer = TripDateSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, route_pk=None):
        start_date = datetime.strptime(pk, '%Y-%m-%d').date()
        queryset = TripDate.objects.filter(trip__route_id=route_pk, date=start_date)
        serializer = TripDateSerializer(queryset, many=True)
        return Response(serializer.data)


class RouteDateTripViewSet(viewsets.ViewSet):
    serializer_class = TripDateSerializer
    permission_classes = (AllowAny,)

    def list(self, request, route_pk=None, date_pk=None):
        start_date = datetime.strptime(date_pk, '%Y-%m-%d').date()
        queryset = TripDate.objects.filter(trip__route__id=route_pk, date=start_date)
        serializer = TripDateSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, route_pk=None, date_pk=None):
        start_date = datetime.strptime(date_pk, '%Y-%m-%d').date()
        queryset = TripDate.objects.filter(trip__route__id=route_pk, date=start_date, id=pk)
        tripdate = get_object_or_404(queryset)
        serializer = TripDatePlusSerializer(tripdate, context={'request': request})
        return Response(serializer.data)
