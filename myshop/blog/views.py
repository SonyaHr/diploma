from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, BlogComment, CommentVote
from .forms import PostForm, BlogCommentForm
from django.contrib.auth.decorators import login_required

# Відображення списку постів
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

# Відображення деталей поста та коментарів
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()  # Получаем все комментарии для текущего поста

    # Подготовка информации о голосах
    user_likes = set(CommentVote.objects.filter(user=request.user, vote_type='like').values_list('comment_id', flat=True))
    user_dislikes = set(CommentVote.objects.filter(user=request.user, vote_type='dislike').values_list('comment_id', flat=True))
    
    # Подготовка количества лайков и дизлайков
    comments_info = []
    for comment in comments:
        likes_count = CommentVote.objects.filter(comment=comment, vote_type='like').count()
        dislikes_count = CommentVote.objects.filter(comment=comment, vote_type='dislike').count()
        comments_info.append({
            'comment': comment,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_liked': comment.id in user_likes,
            'user_disliked': comment.id in user_dislikes
        })
    
    if request.method == 'POST':
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        comment_form = BlogCommentForm()
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments_info': comments_info,
        'comment_form': comment_form
    })
    
    
# Створення нового поста
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('blog:post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

@login_required
def reply_to_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    parent_comment = get_object_or_404(BlogComment, id=comment_id)

    if request.method == 'POST':
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.parent = parent_comment 
            reply.user = request.user
            reply.save()
            return redirect('blog:post_detail', post_id=post_id)

    return redirect('blog:post_detail', post_id=post_id)

def like_comment(request, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id)
    user_vote = CommentVote.objects.filter(user=request.user, comment=comment, vote_type='like').first()

    if user_vote:
        user_vote.delete()  # Удаляет голос, если он уже существует
    else:
        CommentVote.objects.create(user=request.user, comment=comment, vote_type='like')
        CommentVote.objects.filter(user=request.user, comment=comment, vote_type='dislike').delete()  # Удаляет дизлайк, если он был

    return redirect('blog:post_detail', post_id=comment.post.id)

def dislike_comment(request, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id)
    user_vote = CommentVote.objects.filter(user=request.user, comment=comment, vote_type='dislike').first()

    if user_vote:
        user_vote.delete()  # Удаляет голос, если он уже существует
    else:
        CommentVote.objects.create(user=request.user, comment=comment, vote_type='dislike')
        CommentVote.objects.filter(user=request.user, comment=comment, vote_type='like').delete()  # Удаляет лайк, если он был

    return redirect('blog:post_detail', post_id=comment.post.id)
def delete_comment(request, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id)
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
    return redirect('blog:post_detail', post_id=comment.post.id)
