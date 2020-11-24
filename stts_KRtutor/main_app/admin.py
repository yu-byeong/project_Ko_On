from django.contrib import admin
from .models import CheckProcess, ConversationPracticeAnswerDB, ConversationPracticeQuestionDB, EssentialSentenceDB, ChapterNumberDB, TipsOnModal, CheckProcessTable



admin.site.register(CheckProcess)
admin.site.register(ChapterNumberDB)
admin.site.register(EssentialSentenceDB)
admin.site.register(ConversationPracticeAnswerDB)
admin.site.register(ConversationPracticeQuestionDB)
admin.site.register(TipsOnModal)