# collaboration/serializers.py
from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    is_owner = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'is_owner', 'owner']
        read_only_fields = ['is_owner', 'owner']

    def create(self, validated_data):
        # Ensure owner is set correctly when creating a new document
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
