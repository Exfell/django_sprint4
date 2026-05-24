from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Post, Category
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .forms import PostForm

PAGIN_PAGES = 10  # в отдельную переменную, чтобы потом легче было в одном месте менять, а не в 3


def filter_posts(author=None):
    # фильтруем все посты по чтобы были опубликованы и не отложены. Если надо ещё по автору
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')  # добавляет к каждому посту поле comment_count
    if author:
        post_list = post_list.filter(author=author)

    return post_list


def get_curr_page(request, posts, num_of_posts):  # request для того, чтобы брать ?page
    pagin = Paginator(posts, num_of_posts)  # делит посты на списки по 10 штук каждый
    curr_page = request.GET.get('page')  # из строки там берем ?page=2 например
    page_obj = pagin.get_page(curr_page)  # берем нужную страницу с 10 постами
    return page_obj


def profile(request,
            username):
    # для начала, ну у нас уже есть модель User (т.е. и таблица с пользователями тоже есть, значит надо просто взять из неё нужную инфу
    template_name = 'blog/profile.html'
    User = get_user_model()
    profile = get_object_or_404(User, username=username)
    # итак, сам профиль я вернул, там потом в контексте у него поля выдергиваются. Надо ещё список постов взять
    # ак же получить посты, да? Хмм, действительно!! А ничего что у нас есть модель Post!!
    if request.user == profile:
        posts = Post.objects.filter(author=profile).annotate(comment_count=Count('comments')).order_by('-pub_date')
    else:
        posts = filter_posts(author=profile)
    page_obj = get_curr_page(request, posts, PAGIN_PAGES)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, template_name, context)

@login_required
def edit_profile(request,username):
    template_name = 'blog/user.html'
    User = get_user_model()
    user = get_object_or_404(User,username=username)
    form = UserChangeForm(request.POST or None, instance=user)
    if request.user==user:
        if form.is_valid():
            form.save()
            return redirect('blog:profile',username)
        context = {'form':form}
        return render(request,template_name,context)
    return redirect('blog:profile',username)


def index(request):
    template_name = 'blog/index.html'
    post_list = get_curr_page(request, filter_posts(), PAGIN_PAGES)
    context = {
        'page_obj': post_list,

    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    # url по типу posts/3
    template_name = 'blog/detail.html'
    posts = Post.objects.all()
    post = get_object_or_404(posts, pk=post_id)

    if (
            request.user != post.author):  # типа, если это не автор и условия не соблюдены, то мы должны ошибку кинуть 404 просто.
        # т.к. здесь мы работаем в python, то просто обращаемся к атрибутам, а не category__is_published типа
        # в .filter() мы работали с БД, там свой синтаксис с __, lte и т.д.
        if post.is_published != True or post.category.is_published != True or post.pub_date > timezone.now():
            raise Http404()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    now = timezone.now()
    category = get_object_or_404(Category.objects.filter(is_published=True,
                                                         slug=category_slug).all())  # т.е., нам нужно выбрать категорию (которую мы получили из запроса), у которой is_published!=False. Если такой нет, то ошибка
    post_list = filter_posts().filter(category=category)
    page_obj = get_curr_page(request, post_list, PAGIN_PAGES)
    context = {'page_obj': page_obj,
               'category': category}
    return render(request, template, context)


#### ДОБАВЛЕНИЕ, РЕДАКТИРОВАНИЕ, УДАЛЕНИЕ ПОСТОВ!!!!
from django.contrib.auth.decorators import login_required
from .forms import PostForm


@login_required  # только авторизованным
def create_post(request):
    # сначала надо понять, на какую страницу хотя бы переходить
    template_name = 'blog/create.html'
    # И дальше, как помнишь, два варианта - либо он уже отправляет заполненную форму, либо он сделал get запрос
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        # нужно ещё автора добавить
        post = form.save(commit=False)  # сохранили форму, но не в БД, а локально
        post.author = request.user  # request.user и request.method есть везде по умолчанию
        post.save()
        return redirect('blog:profile', username=request.user.username)
    context = {'form': form}
    return render(request, template_name, context)


def edit_post(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)  # получили пост из БД, теперь вставляем его в форму
    if request.user == post.author:  # только автор может редактировать, иначе перенаправляем по заданию
        form = PostForm(request.POST or None, request.FILES or None, instance=post)  # т.е. редактирую текущий пост
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)  # просто чтобы была более явная логика
        else:
            context = {'form': form}  # по шаблону blog/create.html посмотрел, что должно быть в контексте
            return render(request, template_name, context)
    return redirect('blog:post_detail', post_id=post_id)


def delete_post(request,post_id):
    template_name = 'blog/create.html'
    # шаблон для подтверждения удаления такой же, что для создания. Get-страницу показать, Post-удалить
    post = get_object_or_404(Post,pk=post_id)
    if request.user!=post.author:
        return redirect('blog:post_detail',post_id)
    if request.method=='POST':
        post.delete()
        return redirect('blog:index')
    form = PostForm(instance=post)
    context = {'form':form}
    return render(request,template_name,context)



### ДОБАВЛЕНИЕ, РЕДАКТИРОВАНЕ И УДАЛЕНИЕ КОММЕНТАРИЕВ
from .forms import CommentForm
from .models import Comment

# 1 что интересно, можно ли оставить одну ф-ю, а не две, раз у нас get запрос на add_comment это как profile
@login_required
def add_comment(request, post_id):
    template_name = 'blog/detail.html'  # первый вопрос всегда - какой шаблон будем использовать
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        # ещё нужно автора добавить
        form2 = form.save(commit=False)
        form2.author = request.user
        form2.post = post
        form2.save()
        return redirect('blog:post_detail', post_id=post_id)
    # если форма невалидна, мы должны подсветить, в чем невалидна, а не просто перебросить на чистую страницу
    comments = Comment.objects.filter(post=post)
    context = {'post':post,'form':form, 'comments':comments}
    return render(request,template_name,context)


def edit_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html' # для детального просмотра комментария
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    form = CommentForm(request.POST or None, instance=comment)
    if request.user == comment.author:
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            context = {'form': form, 'comment': comment}  # post здесь не нужен, он тут не используется
            return render(request, template_name, context)
    else:
        return redirect('blog:post_detail',
                        post_id=post_id)  # значит не имеет права редактировать коммент. Можно было бы 404, но по заданию надо на страницу поста


def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    post = get_object_or_404(Post,pk=post_id)
    comment = get_object_or_404(Comment,post=post,pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail',post_id=post_id)
    if request.method=='POST':
        comment.delete()
        return redirect('blog:post_detail',post_id=post_id)
    form = CommentForm(instance=comment)
    context = {'comment':comment}
    return render(request,template_name,context)
