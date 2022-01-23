import http

from rest_framework import generics, mixins, filters
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

from .models import Quiz, Answer, Question, Participation, QuizInvitations, Creator, Participant, AnswersGiven
from .serialisers import QuizSerialiser, DetailedQuizSerialiser, AnswerSerialiser, QuestionSerialiser, \
    ParticipationSerialiser


class QuizProgressView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request, quizid):
        if Participant.is_participant(request.user):
            try:
                participation = Participation.objects.get(user=request.user, quiz=quizid)
                quiz = Quiz.objects.get(pk=quizid)
                all_question = Question.objects.filter(quiz=quiz)
                given_answers = AnswersGiven.objects.filter(participation=participation)
                return Response(data={"answered_questions": len(given_answers), "all_questions": len(all_question)})
            except Participation.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class ParticipationScoreView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request, participationid):
        try:
            if Creator.is_creator(request.user):
                participation = Participation.objects.get(pk=participationid)
                all_question = Question.objects.filter(quiz=participation.quiz)
                correct_answers = AnswersGiven.objects.filter(participation=participation,
                                                              selectedAnswer__isCorrect=True)
                return Response(data={"score": len(correct_answers), "max_score": len(all_question)})
        except Participation.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ParticipationProgressView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request, participationid):
        if Creator.is_creator(request.user):
            try:
                participation = Participation.objects.get(pk=participationid)
                all_question = Question.objects.filter(quiz=participation.quiz)
                given_answers = AnswersGiven.objects.filter(participation=participation)
                return Response(data={"answered_questions": len(given_answers), "all_questions": len(all_question)})
            except Participation.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class QuizParticipantGiveAnswerView(APIView):
    queryset = Participation.objects.all()
    authentication_classes = [IsAuthenticated]

    def post(self, request, quizid, questionid, answerid):
        participation = Participation.objects.get(quiz=quizid, user=request.user)
        answer = Answer.objects.get(pk=answerid)
        question = Question.objects.get(pk=questionid)
        if AnswersGiven.objects.filter(participation=participation, question=question):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if answer.question != question:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        AnswersGiven(participation=participation, question=question, selectedAnswer=answer).save()
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request, quizid, questionid, answerid):
        participation = Participation.objects.get(quiz=quizid, user=request.user)
        answer = Answer.objects.get(pk=answerid)
        question = Question.objects.get(pk=questionid)

        if not AnswersGiven.objects.filter(participation=participation, question=question):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if answer.question != question:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        AnswersGiven(pk=AnswersGiven.objects.get(participation=participation, question=question).pk,
                     participation=participation, question=question, selectedAnswer=answer).save()
        return Response(status=status.HTTP_200_OK)


class QuizParticipantBrowseView(generics.ListAPIView):
    serializer_class = DetailedQuizSerialiser
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    authentication_classes = [IsAuthenticated]

    def get_queryset(self):
        quizs = Participation.objects.filter(user=self.request.user).all().values('quiz')
        return Quiz.objects.filter(pk__in=quizs)


class QuizBrowseView(generics.ListCreateAPIView):
    serializer_class = QuizSerialiser
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    authentication_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(creator=self.request.user)


class QuizUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [IsAuthenticated]

    serializer_class = QuizSerialiser

    def get_queryset(self):
        return Quiz.objects.filter(creator=self.request.user)


class QuestionUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = QuestionSerialiser

    def get_queryset(self):
        return Question.objects.filter(quiz__creator=self.request.user)


class QuestionBrowseView(generics.ListCreateAPIView):
    serializer_class = QuestionSerialiser
    search_fields = ['text']
    filter_backends = (filters.SearchFilter,)
    authentication_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(quiz__creator=self.request.user)


class AnswerBrowseView(generics.ListCreateAPIView):
    serializer_class = AnswerSerialiser
    search_fields = ['text']
    filter_backends = (filters.SearchFilter,)
    authentication_classes = [IsAuthenticated]

    def get_queryset(self):
        question = self.kwargs.get('question')
        if question is not None:
            return Answer.objects.filter(question__quiz__creator=self.request.user, question=question)
        else:
            return Answer.objects.filter(question__quiz__creator=self.request.user)


class AnswerUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = AnswerSerialiser
    authentication_classes = [IsAuthenticated]

    def get_queryset(self):
        # question = self.kwargs.get('question')
        # if question is not None:
        #     return Answer.objects.filter(question__quiz__creator=self.request.user, question=question)
        # else:
        #     return Answer.objects.filter(question__quiz__creator=self.request.user)
        return Answer.objects.filter(question__quiz__creator=self.request.user)
