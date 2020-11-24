from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# 방법1 : 0 -> 미수료 / 1 -> 수료상태

# 방법2 : null -> 2잠금 / 1 -> 다 열림
# update 함수를 짠다.

class CheckProcess(models.Model):
    user = models.OneToOneField(User, related_name="user_checkprocess", on_delete=models.CASCADE)
    chap_1 = models.IntegerField(default=0)
    chap_2 = models.IntegerField(default=0)
    chap_3 = models.IntegerField(default=0)
    chap_4 = models.IntegerField(default=0)
    chap_5 = models.IntegerField(default=0)
    chap_6 = models.IntegerField(default=0)
    # def __str__(self):
    #     return f"{self.user.get_username()}"


class ChapterNumberDB(models.Model):  #챕터 넘버링
    ChapNo = models.IntegerField()
    InnerChapOne = models.IntegerField(default=1)
    InnerChapTwo = models.IntegerField(default=2)
    ChapName = models.CharField(max_length=50)

    def __str__(self):
        return self.ChapName


class EssentialSentenceDB(models.Model): #필수문장 적재
    ChapNo = models.IntegerField()
    InnerNo = models.IntegerField()
    SentenceNo = models.IntegerField()
    Essentence_question = models.CharField(max_length=300)
    
    def __str__(self):
        return f"{self.Essentence_question}"

class ConversationPracticeQuestionDB(models.Model): #발화실습 문장(TTS) 데이터 적재
    ChapNo = models.IntegerField()
    InnerNo = models.IntegerField()
    SentenceNo = models.IntegerField()
    Cosentence_question = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.Cosentence_question}"


class ConversationPracticeAnswerDB(models.Model): #발화실습 답변(STT) 데이터 적재
    ChapNo = models.IntegerField()
    InnerNo = models.IntegerField()
    SentenceNo = models.IntegerField()
    Cosentence_answer = models.CharField(max_length=300)
    
    def __str__(self):
        return f"{self.Cosentence_answer}"

class TipsOnModal(models.Model):
    description = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.description}"


class CheckProcessTable(models.Model):
    user = models.OneToOneField(User, related_name="user_checktable", on_delete=models.CASCADE)
    ChapNo = models.IntegerField()  #갱신 시 cn_chapno를 넣어줌
    InnerChapNo = models.IntegerField() #갱신 시 뷰 함수 내부에서 정의한 정수 값을 바탕으로 내부챕터 넘버를 갱신해준다.
    is_check = models.IntegerField(default=0)
