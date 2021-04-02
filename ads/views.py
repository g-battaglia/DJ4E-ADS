from .forms import CommentForm
from .models import Ad, Comment, Fav
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import get_object_or_404

# Favorites:
# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

# Search:
from django.contrib.humanize.templatetags.humanize import naturaltime
from ads.utils import dump_queries
from django.db.models import Q






class adListView(OwnerListView):
    model = Ad
    # By convention:
    template_name = "ads/ad_list.html"

    # * Favorites:
    def get(self, request) :
        #  Search
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval) 
            query.add(Q(text__icontains=strval), Q.OR)
            objects = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            objects = Ad.objects.all().order_by('-updated_at')[:10]
        
        # Augment the post_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)


        ad_list = objects  # Old: ad_list = Ad.objects.all()

        favorites = list()

        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        ctx = {'ad_list' : ad_list, 'favorites': favorites, 'search': strval}

        retval = render(request, self.template_name, ctx)
        dump_queries()
        return retval


class adDetailView(OwnerDetailView):
    model = Ad

    def get_context_data(self, **kwargs):
        # pk = int(self.object.pk)
        print('HEY!------>', self.kwargs)
        context = super().get_context_data()
        comments = Comment.objects.filter(ad=self.object).order_by('-updated_at')
        comment_form = CommentForm()
        context['comments'] = comments
        context['comment_form'] = comment_form
        return context


class adCreateView(OwnerCreateView):
    model = Ad
    fields = ['title', 'price','text', 'image']


class adUpdateView(OwnerUpdateView):
    model = Ad
    fields = ['title', 'price','text', 'image']


class adDeleteView(OwnerDeleteView):
    model = Ad

# Comments:
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])

# Favorites:

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        a = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=a)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()


