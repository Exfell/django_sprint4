from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.forms import UserCreationForm
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import render,redirect

handler403 = 'pages.views.forbidden'  # строка!
handler404 = 'pages.views.page_not_found'  # строка!
handler500 = 'pages.views.internal_server_error'  # строка!

def registration(request):
    template_name = 'registration/registration_form.html'
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('blog:index')
    context = {'form':form}
    return render(request, template_name, context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', registration, name='registration'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
