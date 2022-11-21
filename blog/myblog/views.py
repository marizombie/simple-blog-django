from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from taggit.models import Tag
from .models import *
from .forms import *


class MainView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        return render(
            request,
            'myblog/index.html', 
            context={'posts': posts}
        )


class PostDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, url=slug)
        common_tags = Post.tags.most_common()
        last_posts = Post.objects.all().order_by('-id')[:5]
        comment_form = CommentForm()
        return render(request, 'myblog/post_detail.html', context={
            'post': post,
            'common_tags': common_tags,
            'last_posts': last_posts,
            'comment_form': comment_form
    })

    def post(self, request, slug, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = request.POST['text']
            username = self.request.user
            post = get_object_or_404(Post, url=slug)
            comment = Comment.objects.create(post=post, username=username, text=text)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return render(request, 'myblog/post_detail.html', context={
            'comment_form': comment_form
        })


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SigUpForm()
        return render(request, 'myblog/signup.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SigUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'myblog/signup.html', context={
            'form': form,
        })


class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        return render(request, 'myblog/signin.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'myblog/signin.html', context={
            'form': form,
        })


class ContactsView(View):
    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, 'myblog/contact.html', context={
            'form': form,
            'title': 'Contact me'
        })

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(f"From {name} | {subject}', f'{message}\n\nSender's email: {from_email}", 
                from_email=from_email, recipient_list=['avdotfedorov@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid subject')
            return HttpResponseRedirect('success')
        return render(request, 'myblog/contact.html', context={
            'form': form,
        })


class SuccessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'myblog/success.html', context={
            'title': 'Thank you for contacting me'
        })


RESULTS_PER_PAGE = 5

class SearchResultsView(View):
   def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        results = ""
        if query:
            results = Post.objects.filter(
                Q(h1__icontains=query) | 
                Q(description__icontains=query) |
                Q(content__icontains=query)
            )
            
        paginator = Paginator(results, RESULTS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'myblog/search.html', context={
            'title': 'Search',
            'results': page_obj,
            'count': paginator.count
        })


class TagsView(View):
    def get(self, request, slug, *args, **kwargs):
        tag = get_object_or_404(Tag, slug=slug)
        posts = Post.objects.filter(tags=tag)
        common_tags = Post.tags.most_common()
        return render(request, 'myblog/tags.html', context={
            'title': f'#tag {tag}',
            'posts': posts,
            'common_tags': common_tags
        })