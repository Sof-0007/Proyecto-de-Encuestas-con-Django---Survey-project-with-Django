import datetime 
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from .models import Question 

class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        Devuelve False para preguntas cuya pub_date está en el futuro.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        Devuelve False para preguntas cuya pub_date tiene más de 1 día.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        Devuelve True para preguntas cuya pub_date está dentro del último día.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Crea una pregunta con el `question_text` dado y publica el
    número de días compensados a ahora (negativo para preguntas publicadas
    en el pasado, positivo para preguntas que aún no se han publicado).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
          Si no hay preguntas, se muestra un mensaje apropiado.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Las preguntas con una pub_date en el pasado se muestran en el
        página de índice.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
            )
        """
        La vista de detalle de una pregunta con una pub_date en el pasado
        muestra el texto de la pregunta.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question(self):
        """
        Las preguntas con una fecha de publicación futura no se muestran en
        la página del índice.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual (response.context["latest_question_list"], [])                       
        """
        La vista detallada de una pregunta con una fecha pub_date en el futuro
        devuelve un 404 no encontrado.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)                                                

    def test_future_question_and_past_question(self):
        """
        Incluso si existen tanto preguntas pasadas como futuras, solo preguntas pasadas
        se muestran.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        La página del índice de preguntas puede mostrar varias preguntas.
        """
        question1 = create_question(question_text="Pregunta anterior 1", days=-30)
        question2 = create_question(question_text="PPregunta anterior 2", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],)