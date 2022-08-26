import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import translators as ts


from question.models import Question


def check_duplicate(question):
    question_query = Question.objects.all()
    questions = [question.question for question in question_query]
    print(questions)
    questions.append(question)
    corpus = questions
    vectorizer_1 = TfidfVectorizer()
    X = vectorizer_1.fit_transform(corpus)
    threshold = 0.7
    for x in range(X.shape[0] - 1):
        if cosine_similarity(X[x], X[X.shape[0] - 1]) > threshold:
            print(corpus[x])
            print("Cosine similarity:", cosine_similarity(X[x], X[X.shape[0] - 1]))
            print()
            return True
    return False


def translate_question(string, from_lang="en", to_lang="ka"):
    string = ts.google(string, from_language=from_lang, to_language=to_lang)
    print(string)
    return string
