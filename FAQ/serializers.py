from rest_framework import serializers
from .models import FAQ
#from .serializers import FAQSerializer

class FAQSerializer(serializers.ModelSerializer):
    class Meta():
        model = FAQ
        fields = ('id', 'question', 'answer', 'created_at', 'updated_at')
    