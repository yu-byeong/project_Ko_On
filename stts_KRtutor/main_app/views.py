from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
# 페이지 네이터 모듈 추가
from django.core.paginator import Paginator
from .models import CheckProcess
from .models import EssentialSentenceDB, ConversationPracticeQuestionDB, ConversationPracticeAnswerDB, TipsOnModal, CheckProcess
from .models import ChapterNumberDB
import json
import os
import sys
import urllib.request
import copy
import csv

# Create your views here.
def main(request):
    return render(request, "main_app/main.html")

def chapter(request):
    chap_no = ChapterNumberDB.objects.all()
    
    #왕관 구현에 필요한 뷰 코드!
    curr_user = request.user
    chap_row = CheckProcess.objects.filter(user_id=curr_user.id)
    
    chap_check_list = [chap_row.values()[0]["chap_1"], chap_row.values()[0]["chap_2"], chap_row.values()[0]["chap_3"],
                        chap_row.values()[0]["chap_4"], chap_row.values()[0]["chap_5"], chap_row.values()[0]["chap_6"]]

    chap_config = []
    for elem in chap_check_list:
        if elem == 0 or elem == 1: 
            chap_config.append(None) #None값이면 템플릿에서 왕관 출력안됨
        elif elem == 2:
            chap_config.append(elem) #0이 아니라 1이상이면 템플릿에 왕관 출력


    if request.method == "POST":
        global en
        en = request.POST["trans_lang_option"]

    kr_trans_list = []
    for idx in range(0, len(chap_no)):

        no = chap_no.values()[idx]["ChapNo"]
        chapName_kr = chap_no.values()[idx]["ChapName"]
        trans_stc = translate(chap_no.values()[idx]["ChapName"], en)

        kr_trans_list.append([no, chapName_kr, trans_stc])

    context = {
        'chap_number': chap_no,
        'kr_trans_list': kr_trans_list,
        'chap_check': chap_config
    }

    return render(request, "main_app/chapter.html", context)


def chap_detail(request, cn_ChapNo):
    # chapter_Number를 전역변수에 담아준다.
    global chap_number
    chap_number = cn_ChapNo
    chap_detail = ChapterNumberDB.objects.get(ChapNo=cn_ChapNo)

    global check_list
    sentence_list = EssentialSentenceDB.objects.filter(ChapNo=chap_number, InnerNo=1)
    check_list = [False] * len(sentence_list)

    global check_list2
    sentence_list2 = ConversationPracticeAnswerDB.objects.filter(ChapNo=chap_number, InnerNo=2)
    check_list2 = [False] * len(sentence_list2)

    context = {
        'chap_detail': chap_detail,
    }
    
    if request.method == "POST":
        if "go_before" in request.POST:
            return redirect("/chapter")

    return render(request, 'main_app/chap_detail.html', context)


def chap_sentence_ES(request, cn_ChapNo):
    sentence_list = EssentialSentenceDB.objects.filter(ChapNo=chap_number, InnerNo=1)
    modal_sentences = TipsOnModal.objects.all()
    
    modal_sent_list = []
    for index in range(len(modal_sentences)):
        trans_stc_modal = translate(modal_sentences.values()[index]["description"], en)
        modal_sent_list.append(trans_stc_modal)

    trans_list = []
    for idx in range(len(sentence_list)):
        page = request.GET.get('page')
        if page == None:
            page = 1
            if idx == page - 1:
                trans_stc = translate(sentence_list.values()[idx]["Essentence_question"], en)
                trans_list.append(trans_stc)

        else:
            page = int(page)
            if idx == page - 1:
                trans_stc = translate(sentence_list.values()[idx]["Essentence_question"], en)
                trans_list.append(trans_stc)

    # sentence_list = EssentialSentenceDB.objects.all()
    paginator = Paginator(sentence_list, 1)
    paginator_trans = Paginator(trans_list, 1)

    page = request.GET.get('page')

    sentences = paginator.get_page(page)
    sentences_trans = paginator_trans.get_page(page)

    if request.method == "POST":
        if "sendtext" in request.POST:
            _sendtext = request.POST["sendtext"]
            _origintext = request.POST["origintext"]

            sendtext = " ".join(list(_sendtext.replace(" ", "").replace("?", "").replace(".", "")))
            origintext = " ".join(list(_origintext.replace(" ", "").replace("?", "").replace(".", "")))
            
            print(sendtext, origintext)

            sent = (sendtext, origintext)

            tfidf_vec = TfidfVectorizer(analyzer="char")
            tfidf_mat = tfidf_vec.fit_transform(sent)
            threshold = cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:2])

            if threshold >= 0.0:
                print("맞았습니다.")
                print(threshold)
                check_index = EssentialSentenceDB.objects.filter(Essentence_question=_origintext)
                check_index = check_index.values()[0]["SentenceNo"]
                check_list[check_index - 1] = True
                print(check_list)

                if all(check_list) == True:
                    print("수료하셨습니다.")

                else:
                    print("수료하지 못했습니다.")

            else:
                print(threshold)
                print("틀렸습니다. 다시 시도해주세요!")
                print("수료하지 못했습니다.")

        else:
            sendtext = False

    context = {
        "sentences": sentences,
        "sentences_trans": sentences_trans,
        "check_list": check_list,
        "is_complete": all(check_list),
        "chap_number": chap_number,
        "InnerNo": 1,
        "modal_sent_list": modal_sent_list
    }

    if request.method == "POST":
        if "go_before2" in request.POST:
            return redirect("/chapter")

    return render(request, "main_app/chap_sentence.html", context)


def chap_sentence_Con(request, cn_ChapNo):
    question_list = ConversationPracticeQuestionDB.objects.filter(ChapNo=chap_number, InnerNo=2)
    answer_list = ConversationPracticeAnswerDB.objects.filter(ChapNo=chap_number, InnerNo=2)

    modal_sentences = TipsOnModal.objects.all()
    
    modal_sent_list = []
    for index in range(len(modal_sentences)):
        trans_stc_modal = translate(modal_sentences.values()[index]["description"], en)
        modal_sent_list.append(trans_stc_modal)

    question_trans_list = []
    for idx in range(len(question_list)):
        page = request.GET.get('page')
        if page == None:
            page = 1
            if idx == page - 1:
                question_trans_stc = translate(question_list.values()[idx]["Cosentence_question"], en)
                question_trans_list.append(question_trans_stc)
        else:
            page = int(page)
            if idx == page - 1:
                question_trans_stc = translate(question_list.values()[idx]["Cosentence_question"], en)
                question_trans_list.append(question_trans_stc)

    answer_trans_list = []
    for idx in range(len(answer_list)):
        page = request.GET.get('page')
        if page == None:
            page = 1
            if idx == page - 1:
                answer_trans_stc = translate(answer_list.values()[idx]["Cosentence_answer"], en)
                answer_trans_list.append(answer_trans_stc)
        else:
            page = int(page)
            if idx == page - 1:
                answer_trans_stc = translate(answer_list.values()[idx]["Cosentence_answer"], en)
                answer_trans_list.append(answer_trans_stc)

    paginator_q = Paginator(question_list, 1)
    paginator_q_trans = Paginator(question_trans_list, 1)
    paginator_a = Paginator(answer_list, 1)
    paginator_a_trans = Paginator(answer_trans_list, 1)

    page = request.GET.get('page')

    question = paginator_q.get_page(page)
    question_trans = paginator_q_trans.get_page(page)
    answer = paginator_a.get_page(page)
    answer_trans = paginator_a_trans.get_page(page)

    if request.method == "POST":
        if "sendtext" in request.POST:
            _sendtext = request.POST["sendtext"]
            _origintext = request.POST["origintext"]

            sendtext = " ".join(list(_sendtext.replace(" ", "").replace("?", "").replace(".", "")))
            origintext = " ".join(list(_origintext.replace(" ", "").replace("?", "").replace(".", "")))

            print(sendtext, origintext)

            sent = (sendtext, origintext)

            tfidf_vec = TfidfVectorizer(analyzer="char")
            tfidf_mat = tfidf_vec.fit_transform(sent)
            threshold = cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:2])

            if threshold >= 0.0:
                print(threshold)
                print("맞았습니다.")
                check_index = ConversationPracticeAnswerDB.objects.filter(Cosentence_answer=_origintext)
                check_index = check_index.values()[0]["SentenceNo"]
                check_list2[check_index - 1] = True
                print(check_list2)

                if all(check_list) == True:
                    print("수료하셨습니다.")

                else:
                    print("수료하지 못했습니다.")
                    print(check_list2)

            else:
                print(threshold)
                print("틀렸습니다. 다시 시도해주세요!")
                print("수료하지 못했습니다.")
                print(check_list2)

        else:
            sendtext = False

    context = {
        "question": question,
        "question_trans": question_trans,
        "answer": answer,
        "answer_trans": answer_trans,
        "check_list2": check_list2,
        "is_complete": all(check_list2),
        "chap_number": chap_number,
        "InnerNo": 2,
        "modal_sent_list": modal_sent_list,
    }

    if request.method == "POST":
        if "go_before3" in request.POST:
            return redirect("/chapter")

    return render(request, "main_app/chap_sentence2.html", context)


def clear(request, cn_ChapNo):

    curr_user = request.user
    print(curr_user.id)
    row = CheckProcess.objects.filter(user_id=curr_user.id).get()

    for _ in range(1):
        if cn_ChapNo == int(list("chap_1")[-1]):
            if row.chap_1 < 2:
                row.chap_1 = 1
                row.save()
        elif cn_ChapNo == int(list("chap_2")[-1]):
            if row.chap_2 < 2:
                row.chap_2 = 1
                row.save()
        elif cn_ChapNo == int(list("chap_3")[-1]):
            if row.chap_3 < 2:
                row.chap_3 = 1
                row.save()
        elif cn_ChapNo == int(list("chap_4")[-1]):
            if row.chap_4 < 2:
                row.chap_4 = 1
                row.save()
        elif cn_ChapNo == int(list("chap_5")[-1]):
            if row.chap_5 < 2:
                row.chap_5 = 1
                row.save()
        elif cn_ChapNo == int(list("chap_6")[-1]):
            if row.chap_6 < 2:
                row.chap_6 = 1
                row.save()
        else:
            pass

    context = {
        "chap_number": chap_number
    }
    
    if request.method == "POST":
        if "go_detail" in request.POST:
            return redirect('main_app:chap_detail',cn_ChapNo)

    return render(request, "main_app/clear.html", context)


def clear2(request, cn_ChapNo):
    curr_user = request.user
    print(curr_user.id)
    row = CheckProcess.objects.filter(user_id=curr_user.id).get()

    for _ in range(1):
        if cn_ChapNo == int(list("chap_1")[-1]):
            row.chap_1 = 2
            row.save()
        elif cn_ChapNo == int(list("chap_2")[-1]):
            row.chap_2 = 2
            row.save()
        elif cn_ChapNo == int(list("chap_3")[-1]):
            row.chap_3 = 2
            row.save()
        elif cn_ChapNo == int(list("chap_4")[-1]):
            row.chap_4 = 2
            row.save()
        elif cn_ChapNo == int(list("chap_5")[-1]):
            row.chap_5 = 2
            row.save()
        elif cn_ChapNo == int(list("chap_6")[-1]):
            row.chap_6 = 2
            row.save()
        else:
            pass
    
    context = {
        "chap_number": chap_number
    }

    if request.method == "POST":
        if "go_chapter" in request.POST:
            return redirect('main_app:chapter')

    return render(request, "main_app/clear2.html", context)


def translate(sentence, target_lang):
    client_id = "deribthgxo"
    client_secret = "8NOoY9KhtwKHKZwpOQYr5bovSKA6DSctcC9eClf8"
    encText = urllib.parse.quote(sentence)
    data = f"source=ko&target={target_lang}&text=" + encText

    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        result = response_body.decode('utf-8')
        json_sentence = json.loads(result)
        return json_sentence["message"]["result"]["translatedText"]

    else:
        return "Error Code:" + rescode















# csv_path = r"C:\Users\WIN10\Desktop\final_pj\Deploy_Final_Project\stts_KRtutor\main_app\data\Essential_sentence.csv"
# # sentence 데이터베이스 저장하기
# # 아래 파일들은 주석을 하나씩 해제해서, 집어넣어야함.
# # 그렇게 안하면, 매우 큰 문제가 발생합니다.....^^
# with open(csv_path, 'r', encoding='utf-8') as csvfile:
#     data_reader = csv.DictReader(csvfile)
#     for row in data_reader:
#         print(row)
#         EssentialSentenceDB.objects.create(
#             ChapNo=row["chap_no"],
#             InnerNo=row["inner_no"],
#             SentenceNo=row["sentence_no"],
#             Essentence_question=row["sentence"]
#         )

# csv_path = r"C:\Users\WIN10\Desktop\final_pj\Deploy_Final_Project\stts_KRtutor\main_app\data\answer_sentence.csv"
# # sentence 데이터베이스 저장하기
# with open(csv_path, 'r', encoding='utf-8') as csvfile:
#     data_reader = csv.DictReader(csvfile)
#     for row in data_reader:
#         print(row)
#         ConversationPracticeAnswerDB.objects.create(
#             ChapNo=row["chap_no"],
#             InnerNo=row["inner_no"],
#             SentenceNo=row["sentence_no"],
#             Cosentence_answer=row["sentence"]
#         )

# csv_path = r"C:\Users\WIN10\Desktop\final_pj\Deploy_Final_Project\stts_KRtutor\main_app\data\TTS_sentence.csv"
# # sentence 데이터베이스 저장하기
# with open(csv_path, 'r', encoding='utf-8') as csvfile:
#     data_reader = csv.DictReader(csvfile)
#     for row in data_reader:
#         print(row)
#         ConversationPracticeQuestionDB.objects.create(
#             ChapNo=row["chap_no"],
#             InnerNo=row["inner_no"],
#             SentenceNo=row["sentence_no"],
#             Cosentence_question=row["sentence"]
#         )


# csv_path = r"C:\Users\WIN10\Desktop\final_pj\Deploy_Final_Project\stts_KRtutor\main_app\data\description.csv"
# # sentence 데이터베이스 저장하기
# with open(csv_path, 'r', encoding='utf-8') as csvfile:
#     data_reader = csv.DictReader(csvfile)
#     for row in data_reader:
#         print(row)
#         TipsOnModal.objects.create(
#             description = row["description"]
#         )