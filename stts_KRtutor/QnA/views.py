from django.shortcuts import render, redirect
from .models import QuestionAndAnswer
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
# Create your views here.

@login_required
def QnA_list(request):
    QnAs = QuestionAndAnswer.objects.all().order_by("-hit")

    return render(request, "QnA/list.html", context={"QnAs": QnAs})

def MyQnA(request):
    curr_user = request.user
    curr_user_name = curr_user.id
    MyQnAs = QuestionAndAnswer.objects.filter(author=curr_user_name).order_by("-hit")

    return render(request, "QnA/myqna.html", {"MyQnAs" : MyQnAs})

class QnADeleteView(LoginRequiredMixin, DeleteView):
    model = QuestionAndAnswer
    success_url = '/'
    template_name = 'QnA/delete.html'

class QnAUpdateView(LoginRequiredMixin, UpdateView):
    model = QuestionAndAnswer
    fields = ["title", "text"]
    template_name = "QnA/update.html" 

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        if form.is_valid():
            form.instance.save()
            return redirect('/')
        else:
            return self.render_to_response({"form" : form})


class QnAUploadView(LoginRequiredMixin, CreateView):
    model = QuestionAndAnswer
    fields = ["title", "text"]
    template_name = "QnA/upload.html" 

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        if form.is_valid():
            form.instance.save()
            return redirect('/')
        else:
            return self.render_to_response({"form" : form})



