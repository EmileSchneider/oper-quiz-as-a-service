from rest_framework import serializers

from django.contrib.auth.models import User

from .models import Quiz, Question, Answer, AnswersGiven, Participation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class QuizSerialiser(serializers.ModelSerializer):

    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = Quiz
        fields = ['name', 'creator']


class DetailedQuizSerialiser(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = '__all__'

    def get_questions(self, obj):
        return DetailedQuestionSerialiser(Question.objects.filter(quiz=obj.pk), many=True).data


class AnswerSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'isCorrect']


class QuestionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'quiz']


class DetailedQuestionSerialiser(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']

    def get_answers(self, obj):
        return AnswerSerialiser(Answer.objects.filter(question=obj.pk), many=True).data


class ParticipationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = '__all__'
