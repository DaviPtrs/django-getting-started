import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days=0):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        question.choice_set.create(choice_text='choice')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        question = create_question(question_text="Future question.", days=30)
        question.choice_set.create(choice_text='choice')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        question.choice_set.create(choice_text='past choice')
        question = create_question(question_text="Future question.", days=30)
        question.choice_set.create(choice_text='future choice')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question = create_question(question_text="Past question 1.", days=-30)
        question.choice_set.create(choice_text='past choice 1')

        question = create_question(question_text="Past question 2.", days=-5)
        question.choice_set.create(choice_text='past choice 2')

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_no_choice_question(self):
        """
        The questions with no choices must not be displayed.
        """

        create_question(question_text="No choice", days=-30)

        q = create_question(question_text="With choice", days=-30)
        q.choice_set.create(choice_text='choice')

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: With choice>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        future_question.choice_set.create(choice_text='choice')

        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        past_question.choice_set.create(choice_text='choice')

        url = reverse('polls:detail', args=(past_question.id, ))
        response = self.client.get(url)

        self.assertContains(response, past_question.question_text)

    def test_no_choice_question(self):
        """
        The detail view of a question with no choices
        returns a 404 not found.
        """

        q = create_question(question_text="No choice", days=-30)

        url = reverse('polls:detail', args=(q.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        future_question.choice_set.create(choice_text='choice')

        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        past_question.choice_set.create(choice_text='choice')

        url = reverse('polls:results', args=(past_question.id, ))
        response = self.client.get(url)

        self.assertContains(response, past_question.question_text)

    def test_no_choice_question(self):
        """
        The results view of a question with no choices
        returns a 404 not found.
        """

        q = create_question(question_text="No choice", days=-30)

        url = reverse('polls:results', args=(q.id, ))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

class QuestionVoteTests(TestCase):
    def test_future_question(self):
        """
        The vote function of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        future_choice = future_question.choice_set.create(choice_text='You had one choice')

        url = reverse('polls:vote', args=(future_question.id,))
        response = self.client.post(url, {'choice': future_choice.id})
        self.assertEqual(response.status_code, 404)

        future_choice.refresh_from_db()
        self.assertEqual(future_choice.votes, 0)

    def test_past_question(self):
        """
        The vote function of a question with a pub_date in the past
        redirects to question results view (status 302).
        """
        past_question = create_question(question_text='past question.', days=-5)
        past_choice = past_question.choice_set.create(choice_text='You had one choice')
        url = reverse('polls:vote', args=(past_question.id,))
        response = self.client.post(url, {'choice': past_choice.id})
        
        url_redirect = reverse('polls:results', args=(past_question.id,))
        self.assertRedirects(response, url_redirect, status_code=302, target_status_code=200)

        past_choice.refresh_from_db()
        self.assertEqual(past_choice.votes, 1)
