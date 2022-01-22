from django.urls import path

from .views import *

urlpatterns = [
    path('quiz/', QuizBrowseView.as_view(), name='browse-quiz'),
    path('quiz/<int:pk>', QuizUpdateDestroyView.as_view(), name='change-quiz'),
    path('answer/', AnswerBrowseView.as_view(), name='browse-answer'),
    path('answer/<int:question>', AnswerBrowseView.as_view(), name='browse-answer'),
    path('answer/<int:pk>', AnswerUpdateDestroyView.as_view(), name='change-answer'),
    path('participate/quiz', QuizParticipantBrowseView.as_view(), name='my-quizs'),
    path('participate/quiz/<int:quizid>/question/<int:questionid>/selectedanswer/<int:answerid>',
         QuizParticipantGiveAnswerView.as_view(), name='participate-quiz'),
    path('progress/<int:quizid>', QuizProgressView.as_view(), name='progress-quiz'),
    path('participations/<int:participationid>/score', ParticipationScoreView.as_view(), name='participation-score'),
    path('participations/<int:participationid>/progress', ParticipationProgressView.as_view(), name='participation-progress')

]