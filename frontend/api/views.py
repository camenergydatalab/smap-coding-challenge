import time
import random

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import Consumer, MonthlyStatistics

class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'


class MonthlyStatisticsSerializer(serializers.ModelSerializer):
    consumer = ConsumerSerializer(read_only=True)

    class Meta:
        model = MonthlyStatistics
        fields = '__all__'


class ConsumerTypes(APIView):
    def get(self, request):
        return Response(Consumer.CONSUMER_TYPE_MAP)


class ConsumerList(APIView):

    def get(self, request, consumer_type=None):
        filters = {}
        if consumer_type:
            filters['consumer_type'] = consumer_type

        consumers = Consumer.objects.filter(**filters)

        serializer = ConsumerSerializer(consumers, many=True)

        return Response(serializer.data)


class ConsumerDetail(APIView):

    def get(self, request, consumer_id):
        consumer = Consumer.objects.get(pk=consumer_id)
        serializer = ConsumerSerializer(consumer)

        return Response(serializer.data)

    def post(self, request, consumer_id=None):
        name = request.POST.get('name')
        consumer_type = request.POST.get('consumer_type')
        print(name, consumer_type)

        consumer = Consumer.objects.create(name=name, consumer_type=consumer_type)

        if consumer:
            return Response(dict(success=True))

        return Response(dict(sucess=False, message='Consumer was not created.'))

    def delete(self, request, consumer_id):
        consumer = Consumer.objects.get(pk=consumer_id)

        if consumer:
            consumer.delete()
            return Response(dict(success=True))
        return Response(dict(success=False, message='No consumer with that id.'))


class MonthlyStatisticsApi(APIView):

    def get(self, request, consumer_id):
        filters = {
            'consumer': consumer_id
        }

        if request.GET.get('year'):
            filters['year'] = request.GET.get('year')

        if request.GET.get('month'):
            filters['month'] = request.GET.get('month')

        stats = MonthlyStatistics.objects.filter(**filters)

        serializer = MonthlyStatisticsSerializer(stats, many=True)

        # This simulates slow response api. Please do not remove it.
        t = random.choice(range(6, 12))
        time.sleep(t)

        return Response(serializer.data)
