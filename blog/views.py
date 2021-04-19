from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from .models import *
from django_redis import get_redis_connection



# Create your views here.

class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        telephone = request.POST['telephone']
        email = request.POST['email']
		print('aaa')

        if not all([username, password, telephone, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        try:
            user = User.objects.get(username=username)
        except:
            user = None

        if user:
            return render(request, 'register.html', {'errmsg', '用户名已存在'})

        db = User(username=username, password=password, telephone=telephone, email=email)
        db.save()

        info = {}
        article = Article.objects.filter().order_by('-create_time')[:10]
        for i in article:
            i.username = User.objects.get(id=i.uid).username
        info['article'] = article

        return render(request, 'index.html', info)


class IndexView(View):
    def get(self, request):
        info = {}
        article = Article.objects.filter().order_by('-create_time')[:10]
        for i in article:
            i.username = User.objects.get(id=i.uid).username
        info['article'] = article

        return render(request, 'index.html', info)


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完证'})

        try:
            user = User.objects.get(username=username, password=password)
            request.session['user'] = user
            info = {}

            # 首页展示10篇最近发的微博
            article = Article.objects.filter().order_by('-create_time')[:10]
            for i in article:
                i.username = User.objects.get(id=i.uid).username
            info['article'] = article
            return render(request, 'index.html', info)
        except:
            return render(request, 'login.html', {'errmsg': '用户名或密码不对'})


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        info = {}
        article = Article.objects.filter().order_by('-create_time')[:10]
        for i in article:
            i.username = User.objects.get(id=i.uid).username
        info['article'] = article
        return render(request, 'index.html', info)


class UserInfoView(View):
    def get(self, request):
        isSelf = True
        try:
            try:
                uid = request.GET['id']
                isSelf = False
            except:
                uid = request.session['user'].id
            if isSelf:
                info = self.data(uid, uid)
            else:
                info = self.data(int(uid), request.session['user'].id)
            return render(request, 'home.html', info)
        except:
            return render(request, 'login.html', {'errmsg': '请先登陆'})

    def post(self, request):
        introduce = request.POST['introduce']
        id = request.session['user'].id
        User.objects.filter(id=id).update(introduce=introduce)
        request.session['user'].introduce = introduce
        info = self.data(id, id)
        return render(request, 'home.html', info)

    def data(self, id, uid):
        info = {}

        # 查询该用户的微博 按时间倒排
        info['article'] = Article.objects.filter(uid=id).order_by('-create_time')
        info['user'] = User.objects.get(id=id)

        # 查询该用户关注的人
        follow_set_key = 'follow_%d' % id
        conn = get_redis_connection('default')
        follow = conn.smembers(follow_set_key)
        followUser = []
        for i in follow:
            followUser.append(User.objects.get(id=i))
        info['followUser'] = followUser

        # 查询可能认识的人 两个人关注集合做差集
        if id != uid:
            follow_set_key_self = 'follow_%d' % uid
            selfFollow = conn.sdiff(follow_set_key_self, follow_set_key)
            selfFollowUser = []
            for i in selfFollow:
                if int(i) == id or int(i) == uid:
                    continue
                selfFollowUser.append(User.objects.get(id=i))
            info['selfFollowUser'] = selfFollowUser

        # 查询关注的人发的微博
        blog_key = 'blog_%d' % id
        article_list = conn.lrange(blog_key, 0, 4)
        article = Article.objects.filter(id__in=article_list).order_by('-create_time')
        for i in article:
            i.username = User.objects.get(id=i.uid)
        info['followArticle'] = article

        # 查询历史浏览记录
        history_key = 'history_%d' % uid
        history_list = conn.lrange(history_key, 0, 4)
        history = []
        for i in history_list:
            history.append(Article.objects.get(id=int(i)))
        info['historyArticle'] = history

        return info


class EditView(View):
    def get(self, request):
        return render(request, 'edit.html')

    def post(self, request):
        title = request.POST['title']
        content = request.POST['content']
        uid = request.session['user'].id
        try:
            Article.objects.get(title=title, content=content, uid=uid)
            return render(request, 'index.html', {'errmsg': '微博内容重复'})
        except:
            # 添加新微博
            db = Article(title=title, content=content, uid=uid)
            db.save()
            info = {}
            article = Article.objects.filter().order_by('-create_time')[:10]
            for i in article:
                i.username = User.objects.get(id=i.uid).username
            info['article'] = article

            # 把新微博添加的每个关注该用户的列表
            beNotice_key = 'beNotice_%d' % request.session['user'].id
            conn = get_redis_connection('default')
            beNotice_list = conn.smembers(beNotice_key)
            for i in beNotice_list:
                blog_key = 'blog_%d' % int(i)
                conn.lpush(blog_key, article[0].id)

            return render(request, 'index.html', info)


class BlogView(View):
    def get(self, request):
        id = request.GET['id']
        uid = request.session['user'].id
        info = {}

        # 查询微博
        blog = Article.objects.get(id=id)
        blog.username = User.objects.get(id=blog.uid)
        info['blog'] = blog

        # 添加关注
        follow_set_key = 'follow_%d' % uid
        conn = get_redis_connection('default')
        isFollow = conn.sismember(follow_set_key, blog.uid)
        info['isFollow'] = isFollow

        # 添加浏览数
        browse_key = 'browse_%d' % int(id)
        cnt = conn.incr(browse_key)
        info['browseCnt'] = cnt

        # 查询点赞数目
        give_key = 'give_%d' % int(id)
        info['giveCnt'] = conn.scard(give_key)
        info['isGive'] = conn.sismember(give_key, uid)

        # 添加历史浏览记录 设置过期时间一周
        history_key = 'history_%d' % uid
        conn.lrem(history_key, 0, int(id))
        conn.lpush(history_key, int(id))
        conn.expire(history_key, 7 * 24 * 3600)

        # 查询评论
        comment = Comment.objects.filter(bid=id).order_by('-create_time')
        for i in comment:
            i.username = User.objects.get(id=i.uid).username
        info['comment'] = comment

        return render(request, 'blog.html', info)

    def post(self, request):
        content = request.POST['content']
        bid = request.POST['id']
        uid = request.session['user'].id
        try:
            Comment.objects.get(content=content, uid=uid, bid=bid)
            return render(request, 'index.html', {'errmsg': '评论内容重复'})
        except:
            # 添加新微博
            db = Comment(content=content, uid=uid, bid=bid)
            db.save()
            return HttpResponse('已评论')



class FollowView(View):
    def get(self, request):
        uid = request.GET['uid']
        user = request.session['user']

        # 关注
        follow_set_key = 'follow_%d' % user.id
        conn = get_redis_connection('default')
        conn.sadd(follow_set_key, uid)
        beNotice_key = 'beNotice_%d' % int(uid)
        conn.sadd(beNotice_key, user.id)
        return HttpResponse('已关注')


class GiveView(View):
    def get(self, request):
        id = request.GET['id']
        user = request.session['user']

        #点赞
        give_key = 'give_%d' % int(id)
        conn = get_redis_connection('default')
        conn.sadd(give_key, user.id)
        return HttpResponse('已点赞')


class CancelGiveView(View):
    def get(self, request):
        id = request.GET['id']
        user = request.session['user']

        # 取消点赞
        give_key = 'give_%d' % int(id)
        conn = get_redis_connection('default')
        conn.srem(give_key, user.id)
        return HttpResponse('已取消')


class CancelFollowView(View):
    def get(self, request):
        id = request.GET['id']
        user = request.session['user']

        # 取消关注
        follow_set_key = 'follow_%d' % user.id
        conn = get_redis_connection('default')
        conn.srem(follow_set_key, int(id))
        beNotice_key = 'beNotice_%d' % int(id)
        conn.srem(beNotice_key, user.id)
        return HttpResponse('已取消关注')


class TestView(View):
    def get(self, request):
        test_key = 'test'
        # conn = get_redis_connection('default')
        # conn.set(test_key, 'test_value')
        # conn.expire(test_key, 10)
        # res = conn.get(test_key)
        return JsonResponse({'res' : 0, 'errmsg' : 'aaa'})
