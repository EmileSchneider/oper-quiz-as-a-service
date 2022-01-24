from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Creator, Participant, Question, Quiz, Participation, Answer, AnswersGiven, QuizInvitations


class TestQuizCreatorAPI(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.creator_one = get_user_model().objects.create_user(
            'testingCreatorOne',
            'testingcreatorone@mail.com'
        )
        self.creator_two = get_user_model().objects.create_user(
            'testingCreatorTwo',
            'testingcreatortwo@mail.com'
        )
        Creator(user=self.creator_two).save()
        Creator(user=self.creator_one).save()

        self.participant_one = get_user_model().objects.create_user(
            'testingParticipantOne',
            'testingparticipantone@mail.com'
        )
        Participant(user=self.participant_one).save()

        self.__setup_quizs_creator_one__()
        self.__setup_quizs_creator_two__()

    def __setup_quizs_creator_one__(self):
        qz1 = Quiz(name='TestQuizOne', creator=self.creator_one)
        qz1.save()
        qz1q1 = Question(quiz=qz1, text='TestQuizOneQuestionOne')
        qz1q1.save()
        qz1q2 = Question(quiz=qz1, text='TestQuizOneQuestionTwo')
        qz1q2.save()
        qz1q3 = Question(quiz=qz1, text='TestQuizOneQuestionTwo')
        qz1q3.save()
        Answer(question=qz1q1, text='AnswerQuestionOneCorrect', isCorrect=True).save()
        Answer(question=qz1q1, text='AnswerQuestionOneWrong', isCorrect=False).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoCorrect', isCorrect=True).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoWrong', isCorrect=False).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeCorrect', isCorrect=True).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeWrong', isCorrect=False).save()
        qz2 = Quiz(name='TestQuizTwo', creator=self.creator_one)
        qz2.save()
        qz2q1 = Question(quiz=qz2, text='TestQuizTwoQuestionOne')
        qz2q1.save()
        qz2q2 = Question(quiz=qz2, text='TestQuizTwoQuestionTwo')
        qz2q2.save()
        qz2q3 = Question(quiz=qz2, text='TestQuizTwoQuestionThree')
        qz2q3.save()
        Answer(question=qz2q1, text='AnswerQuizTwoQuestionOneCorrect', isCorrect=True).save()
        Answer(question=qz2q1, text='AnswerQuizTwoQuestionOneWrong', isCorrect=False).save()
        Answer(question=qz2q2, text='AnswerQuizTwoQuestionTwoCorrect', isCorrect=True).save()
        Answer(question=qz2q2, text='AnswerQuizTwoQuestionTwoWrong', isCorrect=False).save()
        Answer(question=qz2q3, text='AnswerQuizTwoQuestionThreeCorrect', isCorrect=True).save()
        Answer(question=qz2q3, text='AnswerQuizTwoQuestionThreeWrong', isCorrect=False).save()

    def __setup_quizs_creator_two__(self):
        qz1 = Quiz(name='TestQuizThree', creator=self.creator_two)
        qz1.save()
        qz1q1 = Question(quiz=qz1, text='TestQuizThreeQuestionOne')
        qz1q1.save()
        qz1q2 = Question(quiz=qz1, text='TestQuizThreeQuestionTwo')
        qz1q2.save()
        qz1q3 = Question(quiz=qz1, text='TestQuizThreeQuestionTwo')
        qz1q3.save()
        Answer(question=qz1q1, text='AnswerQuestionOneCorrect', isCorrect=True).save()
        Answer(question=qz1q1, text='AnswerQuestionOneWrong', isCorrect=False).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoCorrect', isCorrect=True).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoWrong', isCorrect=False).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeCorrect', isCorrect=True).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeWrong', isCorrect=False).save()

    def test_browse_quizs(self):
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('browse-quiz'))
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['name'], 'TestQuizOne')
        self.assertEqual(res.data[1]['name'], 'TestQuizTwo')

    def test_browse_quizs_different_creator(self):
        self.client.force_authenticate(self.creator_two)
        res = self.client.get(reverse('browse-quiz'))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'TestQuizThree')

    def test_create_new_quiz(self):
        self.client.force_authenticate(self.creator_one)
        self.client.post(reverse('browse-quiz'), {'name': 'CreatedTestQuiz'}, format='json')
        res = self.client.get(reverse('browse-quiz'))
        self.assertEqual(res.data[2]['name'], 'CreatedTestQuiz')

    def test_update_quiz(self):
        self.client.force_authenticate(self.creator_one)
        self.client.put(reverse('change-quiz', kwargs={'pk': 1}), {'name': 'UpdatedNameQuiz'}, format='json')
        res = self.client.get(reverse('browse-quiz'))
        self.assertEqual('UpdatedNameQuiz', res.data[0]['name'])

    def test_update_foreign_quiz(self):
        self.client.force_authenticate(self.creator_two)
        res = self.client.put(reverse('change-quiz', kwargs={'pk': 1}), {'name': 'hahahchangedyoutrhing'},
                              format='json')
        self.assertEqual(404, res.status_code)

    def test_delete_quiz(self):
        self.client.force_authenticate(self.creator_one)
        self.client.delete(reverse('change-quiz', kwargs={'pk': 1}))
        res = self.client.get(reverse('browse-quiz'))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'TestQuizTwo')

    def test_search_quiz(self):
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('browse-quiz'), {'search': 'Two'})
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'TestQuizTwo')

    def test_search_in_all_answers(self):
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('browse-answer'), {'search': 'QuestionOne'})
        self.assertEqual(4, len(res.data))

    def test_search_in_question_answer(self):
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('browse-answer', kwargs={'question': 1}), {'search': 'QuestionOne'})
        self.assertEqual(2, len(res.data))

    def test_browse_all_answers(self):
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('browse-answer'))
        self.assertEqual(len(res.data), 12)

    def test_browse_question_answers(self):
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('browse-answer', kwargs={'question': 1}))
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['text'], 'AnswerQuestionOneCorrect')
        self.assertEqual(res.data[1]['text'], 'AnswerQuestionOneWrong')

    def test_add_answer(self):
        self.client.force_authenticate(self.creator_one)
        self.client.post(reverse('browse-answer'), {'question': 1, 'text': 'CreatedAnswer', 'isCorrect': True})
        res = self.client.get(reverse('browse-answer', kwargs={'question': 1}))
        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.data[2]['text'], 'CreatedAnswer')

    def test_update_answer(self):
        self.client.force_authenticate(self.creator_one)
        self.client.patch(reverse('change-answer', kwargs={'pk': 1}),
                          {'text': 'change the answer'}, format='json')
        res = self.client.get(reverse('browse-answer'))
        self.assertEqual('change the answer', res.data[0]['text'])

    def test_delete_answer(self):
        self.client.force_authenticate(self.creator_one)
        self.client.delete(reverse('change-answer', kwargs={'pk': 1}))
        res = self.client.get(reverse('browse-answer'))
        self.assertEqual(2, res.data[0]['id'])
        self.assertEqual('AnswerQuestionOneWrong', res.data[0]['text'])


class TestQuizParticipantApi(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.creator_one = get_user_model().objects.create_user(
            'testingCreatorOne',
            'testingcreatorone@mail.com'
        )
        self.creator_two = get_user_model().objects.create_user(
            'testingCreatorTwo',
            'testingcreatortwo@mail.com'
        )
        Creator(user=self.creator_two).save()
        Creator(user=self.creator_one).save()

        self.participant_one = get_user_model().objects.create_user(
            'testingParticipantOne',
            'testingparticipantone@mail.com'
        )
        Participant(user=self.participant_one).save()

        self.__setup_quizs_creator_one__()
        self.__setup_quizs_creator_two__()

        Participation(user=self.participant_one, quiz=self.qz1).save()

    def __setup_quizs_creator_one__(self):
        self.qz1 = Quiz(name='TestQuizOne', creator=self.creator_one)
        self.qz1.save()
        qz1q1 = Question(quiz=self.qz1, text='TestQuizOneQuestionOne')
        qz1q1.save()
        qz1q2 = Question(quiz=self.qz1, text='TestQuizOneQuestionTwo')
        qz1q2.save()
        qz1q3 = Question(quiz=self.qz1, text='TestQuizOneQuestionTwo')
        qz1q3.save()
        Answer(question=qz1q1, text='AnswerQuestionOneCorrect', isCorrect=True).save()
        Answer(question=qz1q1, text='AnswerQuestionOneWrong', isCorrect=False).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoCorrect', isCorrect=True).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoWrong', isCorrect=False).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeCorrect', isCorrect=True).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeWrong', isCorrect=False).save()
        qz2 = Quiz(name='TestQuizTwo', creator=self.creator_one)
        qz2.save()
        qz2q1 = Question(quiz=qz2, text='TestQuizTwoQuestionOne')
        qz2q1.save()
        qz2q2 = Question(quiz=qz2, text='TestQuizTwoQuestionTwo')
        qz2q2.save()
        qz2q3 = Question(quiz=qz2, text='TestQuizTwoQuestionThree')
        qz2q3.save()
        Answer(question=qz2q1, text='AnswerQuizTwoQuestionOneCorrect', isCorrect=True).save()
        Answer(question=qz2q1, text='AnswerQuizTwoQuestionOneWrong', isCorrect=False).save()
        Answer(question=qz2q2, text='AnswerQuizTwoQuestionTwoCorrect', isCorrect=True).save()
        Answer(question=qz2q2, text='AnswerQuizTwoQuestionTwoWrong', isCorrect=False).save()
        Answer(question=qz2q3, text='AnswerQuizTwoQuestionThreeCorrect', isCorrect=True).save()
        Answer(question=qz2q3, text='AnswerQuizTwoQuestionThreeWrong', isCorrect=False).save()

    def __setup_quizs_creator_two__(self):
        qz1 = Quiz(name='TestQuizThree', creator=self.creator_two)
        qz1.save()
        qz1q1 = Question(quiz=qz1, text='TestQuizThreeQuestionOne')
        qz1q1.save()
        qz1q2 = Question(quiz=qz1, text='TestQuizThreeQuestionTwo')
        qz1q2.save()
        qz1q3 = Question(quiz=qz1, text='TestQuizThreeQuestionTwo')
        qz1q3.save()
        Answer(question=qz1q1, text='AnswerQuestionOneCorrect', isCorrect=True).save()
        Answer(question=qz1q1, text='AnswerQuestionOneWrong', isCorrect=False).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoCorrect', isCorrect=True).save()
        Answer(question=qz1q2, text='AnswerQuestionTwoWrong', isCorrect=False).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeCorrect', isCorrect=True).save()
        Answer(question=qz1q3, text='AnswerQuestionThreeWrong', isCorrect=False).save()

    def test_browse_quizs_as_participant(self):
        self.client.force_authenticate(self.participant_one)
        res = self.client.get(reverse('my-quizs'))
        self.assertEqual('TestQuizOne', res.data[0]['name'])

    def test_answer_question_of_quiz(self):
        self.client.force_authenticate(self.participant_one)
        res = self.client.post(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 1}))
        self.assertEqual(201, res.status_code)
        self.assert_(AnswersGiven.objects.get(question=1, selectedAnswer=1))

    def test_change_answer_to_question_of_quiz(self):
        self.client.force_authenticate(self.participant_one)
        self.client.post(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 1}))
        self.client.put(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 2}))
        self.assert_(AnswersGiven.objects.get(question=1, selectedAnswer=2))

    def test_search_partcipants_quizs(self):
        self.client.force_authenticate(self.participant_one)
        res = self.client.get(reverse('my-quizs'), {'search': 'one'})
        self.assertEqual('TestQuizOne', res.data[0]['name'])

    def test_progress_of_quiz(self):
        self.client.force_authenticate(self.participant_one)
        self.client.post(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 1}))
        res = self.client.get(reverse('progress-quiz', kwargs={'quizid': 1}))
        self.assertEqual(1, res.data['answered_questions'])
        self.assertEqual(3, res.data['all_questions'])

    def test_creator_view_score_of_participation(self):
        #participants answers single question
        self.client.force_authenticate(self.participant_one)
        self.client.post(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 1}))

        #actual test
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('participation-score', kwargs={'participationid': 1}))
        self.assertEqual(1, res.data['score'])
        self.assertEqual(3, res.data['max_score'])

    def test_creator_view_progress_of_participation(self):
        # participants answers single question
        self.client.force_authenticate(self.participant_one)
        self.client.post(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 1}))

        #actual test
        self.client.force_authenticate(self.creator_one)
        res = self.client.get(reverse('participation-progress', kwargs={'participationid': 1}))
        self.assertEqual(1, res.data['answered_questions'])
        self.assertEqual(3, res.data['all_questions'])

    def test_get_daily_usage(self):
        self.client.force_authenticate(self.participant_one)
        self.client.post(reverse('participate-quiz', kwargs={'quizid': 1, 'questionid': 1, 'answerid': 1}))

        self.client.force_authenticate(get_user_model().objects.create_superuser(
            username='admin'
        ))
        res = self.client.get(reverse('dailyusage'))
        print(res.data)

    def test_sending_invite(self):
        self.client.force_authenticate(self.creator_two)
        self.client.post(reverse('invitation-send', kwargs={'email': 'testingparticipantone@mail.com', 'quizid': 3}))
        self.assertEqual(1, len(QuizInvitations.objects.all()))

    def test_accepting_invite(self):
        self.client.force_authenticate(self.creator_two)
        self.client.post(reverse('invitation-send', kwargs={'email': 'testingparticipantone@mail.com', 'quizid': 3}))

        self.client.force_authenticate(self.participant_one)
        res = self.client.get(reverse('invitation-accept'))
        print(res.data)
        res = self.client.get(reverse('my-quizs'))
        print(res.data)
        self.client.post(reverse('invitation-accept', kwargs={'invitationid': 1}))
        res = self.client.get(reverse('my-quizs'))
        print(res.data)