from django.contrib import admin

from .models import Quiz, Question, Answer, AnswersGiven, Participation, QuizInvitations, Creator, Participant


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'questions')

    search_fields = ['name', 'creator__username']

    def questions(self, obj):
        return [i.text for i in Question.objects.filter(quiz=obj.pk)]

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text')
    search_fields = ['quiz__name', 'text']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question__quiz', 'question__text', 'text', 'isCorrect')
    search_fields = ['question__quiz__name', 'question__text', 'text']

    def question__text(self, obj):
        return obj.question.text

    def question__quiz(self, obj):
        return obj.question.quiz


@admin.register(AnswersGiven)
class AnswerGivenAdmin(admin.ModelAdmin):
    list_display = (
        'participation__user__username', 'participation__quiz__name', 'question__text', 'selectedAnswer__text')

    search_fields = ['participation__user__username', 'participation__quiz__name', 'question__text',
                     'selectedAnswer__text']

    def participation__user__username(self, obj):
        return obj.participation.creator_one.username

    def participation__quiz__name(self, obj):
        return obj.participation.quiz.name

    def question__text(self, obj):
        return obj.question.text

    def selectedAnswer__text(self, obj):
        return obj.selectedAnswer.text


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user__username', 'quiz__name' )

    search_fields = ('user__username', 'quiz__name')

    def user__username(self, obj):
        return obj.user.username

    def quiz__name(self, obj):
        return obj.quiz.name

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user__username',)

    search_fields = ['user__username']

    def user__username(self, obj):
        return obj.user.username


@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ('user__username',)

    search_fields = ['user__username']

    def user__username(self, obj):
        return obj.user.username