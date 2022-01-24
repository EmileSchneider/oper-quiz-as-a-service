import http

from rest_framework import generics, mixins, filters
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

from .models import Quiz, Answer, Question, Participation, QuizInvitations, Creator, Participant, AnswersGiven
from .serialisers import QuizSerialiser, DetailedQuizSerialiser, AnswerSerialiser, QuestionSerialiser, \
    ParticipationSerialiser, AnswerGivenSerialiser


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


import datetime


class DailyReportView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        date = datetime.datetime.today()
        year = date.year
        month = date.month
        day = date.day
        if request.user.is_staff:
            created_quizs = Quiz.objects.filter(created_at__year=year, created_at__month=month, created_at__day=day)
            changed_quizs = Quiz.objects.filter(updated_at__year=year, updated_at__month=month, updated_at__day=day)

            created_questions = Question.objects.filter(created_at__year=year, created_at__month=month,
                                                        created_at__day=day)
            changed_questions = Question.objects.filter(updated_at__year=year, updated_at__month=month,
                                                        updated_at__day=day)

            created_answers = Answer.objects.filter(created_at__year=year, created_at__month=month, created_at__day=day)
            updated_answers = Answer.objects.filter(updated_at__year=year, updated_at__month=month, updated_at__day=day)

            newly_given_answers = AnswersGiven.objects.filter(created_at__year=year, created_at__month=month,
                                                              created_at__day=day)
            updated_given_answers = AnswersGiven.objects.filter(updated_at__year=year, updated_at__month=month,
                                                                updated_at__day=day)

            return Response(data={
                "created_quizs": QuizSerialiser(created_quizs, many=True).data,
                "changed_quizs": QuizSerialiser(changed_quizs, many=True).data,
                "created_questions": QuestionSerialiser(created_questions, many=True).data,
                "changed_questions": QuestionSerialiser(changed_questions, many=True).data,
                "created_answers": AnswerSerialiser(created_answers, many=True).data,
                "changed_answers": AnswerSerialiser(updated_answers, many=True).data,
                "created_given_answer": AnswerGivenSerialiser(newly_given_answers, many=True).data,
                "changed_given_answer": AnswerGivenSerialiser(updated_given_answers, many=True).data
            })


from django.core.mail import send_mail


class SendInvitationView(APIView):

    def __invite_over_email_to_setup_account__(self, email):
        send_mail(
            'You have been invited to participate in a quiz',
            'Please register an account at our-website to participate in the quiz',
            'thisemail@our-website.com',
            [email],
            fail_silently=False,
        )

    def __notify_user_new_quiz_inivitation__(self, user):
        send_mail(
            'You have been invited to participate in a quiz',
            'you can accept the invitation on our website',
            'thisemail@our-website.com',
            [user.email],
            fail_silently=False,
        )

    def post(self, request, email, quizid):
        quiz = Quiz.objects.get(pk=quizid)
        part = Participation.objects.filter(user__email=email, quiz=quiz)
        if len(part) == 0:
            # user already registered?
            user = User.objects.filter(email=email)
            if len(user) == 0:
                self.__invite_over_email_to_setup_account__(email)
                print(email)

                QuizInvitations(email=email, quiz=quizid).save()
                return Response({})

            else:
                user = user[0]
                QuizInvitations(email=user.email, user=user, quiz=quiz).save()
                self.__notify_user_new_quiz_inivitation__(user)
            return Response({})

        if len(part) == 1:
            # already invited do nothing
            return Response({})


from .serialisers import QuizInvitationsSerialiser


class AcceptInvitationView(generics.ListAPIView):
    serializer_class = QuizInvitationsSerialiser

    def get_queryset(self):
        return QuizInvitations.objects.filter(email=self.request.user.email)

    def post(self, request, invitationid):
        user = request.user
        try:
            invite = QuizInvitations.objects.get(pk=invitationid)
            if invite.accepted:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                invite.accepted = True
                invite.save()
                Participation(user=user, quiz=invite.quiz).save()
                return Response(status=status.HTTP_200_OK)
        except QuizInvitations.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
