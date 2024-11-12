from rest_framework import serializers
from .models import Question, Option, CompanyInformation

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'option_text']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options']


class CompanyInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInformation
        fields = '__all__'