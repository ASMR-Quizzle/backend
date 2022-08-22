from celery import shared_task
from question.models import CSVFile, Question, Topic
import pandas as pd
from user.models import AppUser
import os


@shared_task
def uploadCSVTask(csv_id, appuser_id):
    file = CSVFile.objects.get(pk=csv_id)
    appuser = AppUser.objects.get(pk=appuser_id)
    reader = pd.read_csv(file.file)
    question_count = 0
    saved_count = 0
    for _, row in reader.iterrows():
        question_count += 1
        question = row["Question"]
        A = row["A"]
        B = row["B"]
        C = row["C"]
        D = row["D"]
        answer = row["Answer"]
        topic_name = row["Topic"]
        explanation = row["Explanation"]
        difficulty_score = row["Difficulty"]
        if not (
            A
            or B
            or C
            or D
            or answer
            or question
            or topic
            or explanation
            or difficulty_score
        ):
            continue
        if not Topic.objects.filter(name=topic_name).exists():
            topic = Topic(name=topic_name)
            topic.save()
        topic = Topic.objects.get(name=topic_name)
        topic.question_count += 1
        new_question = Question(
            setter=appuser,
            question=question,
            A=A,
            B=B,
            C=C,
            D=D,
            answer=answer,
            difficulty_score=difficulty_score,
            acceptance_score=75,
            is_accepted=True,
            status="ACCEPTED",
            reviews=3,
            explanation=explanation,
        )
        new_question.save()
        new_question.topics.add(topic)
        new_question.reviewers.add(appuser)
        new_question.save()
        saved_count += 1
    file.delete()
    os.remove(file.file.path)
    return {
        "total_questions": question_count,
        "successful_uploads": saved_count,
    }
