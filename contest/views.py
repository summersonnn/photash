from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from .models import Contest, Contender
from photo.models import Photo
from django.utils import timezone
from django.contrib import messages
from .forms import PhotoForm
from django.contrib.auth.decorators import permission_required
from home.views import set_session_for_language_according_to_IP

def contest_index(request):
    context = {}
    if request.GET.get('q'):
        context['query'] = request.GET['q']
    if request.GET.get('ongoing'):
        context['ongoing'] = request.GET['ongoing']
    if request.GET.get('finished'):
        context['finished'] = request.GET['finished']
    if request.GET.get('upcoming'):
        context['upcoming'] = request.GET['upcoming']

    if request.user.is_authenticated:
        if request.user.profile.languagePreference == "en":
            return render(request, "contest/index.html", context)
        else:
            return render(request, "contest/index-tr.html", context)

    # Guestler için session kontrolü
    # Session'da language belirlenmemiş ise önce belirleyelim
    if "language" not in request.session:
        set_session_for_language_according_to_IP(request)
    if (request.session['language'] == "tr"):
        return render(request, "contest/index-tr.html", context)
    else:
        return render(request, "contest/index.html", context)

def tag_search_list(request, slug):
    context = {'slug': slug}


    if request.user.is_authenticated:
        if request.user.profile.languagePreference == "en":
            return render(request, "contest/tag_search_results.html", context)
        else:
            return render(request, "contest/tag_search_results-tr.html", context)

    # Guestler için session kontrolü
    # Session'da language belirlenmemiş ise önce belirleyelim
    if "language" not in request.session:
        set_session_for_language_according_to_IP(request)
    if (request.session['language'] == "tr"):
        return render(request, "contest/tag_search_results-tr.html", context)
    else:
        return render(request, "contest/tag_search_results.html", context)



def contest_detail(request, slug):
    context = {'contest': Contest.objects.get(slug=slug)}

    if request.user.is_authenticated:
        if request.user.profile.languagePreference == "en":
            return render(request, "contest/detail.html", context)
        else:
            return render(request, "contest/detail-tr.html", context)
    else:
        messages.error(request, 'You logged in as a guest. Log in to your account in order to upload a photo or vote for photos',extra_tags="alert-warning")

    # Guestler için session kontrolü
    # Session'da language belirlenmemiş ise önce belirleyelim
    if "language" not in request.session:
        set_session_for_language_according_to_IP(request)
    if (request.session['language'] == "tr"):
        return render(request, "contest/detail-tr.html", context)
    else:
        return render(request, "contest/detail.html", context)

@permission_required('photo.ekle_photo')
def photo_upload(request, slug):
    # Fotoğrafın hangi contest'in pool'una gideceği bilgisini çektik.
    # Bu bilgi contest detail'indeki Join Contest butonu ile verilmişti.
    contest_record = Contest.objects.get(slug=slug)

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)

        if form.is_valid():  # valid captcha
            photo = form.save(commit=False)
            photo.contest = contest_record
            photo.ownername = request.user
            photo.isChecked = False
            photo.isDeleted = False
            photo.save()
            messages.success(request, "Successfully uploaded to photopool", extra_tags="alert-success" )

            # User'ın o conteste yükleyeceği İlk fotoğraf ise böyle contender objesi yoktur, o objeyi oluşturalım.
            if not Contender.objects.filter(user=request.user, contest=contest_record).exists():
                contender = Contender(user=request.user, contest=contest_record)
                contender.save()

            return HttpResponseRedirect(contest_record.get_absolute_url())

        else:  # user entered an invalid captcha
            messages.error(request, 'Big file size or Invalid Captcha.', extra_tags="alert-danger")
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

    else:  # GET
        if timezone.now() > contest_record.end_date:
            return render(request, 'contest/contest_ended.html')
        try:  # if there is not any Contender object, get() will raise an exception
            the_contender = Contender.objects.get(user=request.user, contest=contest_record)

            if the_contender.get_number_of_photos_uploaded() >= contest_record.max_photos_per_Reguser:
                return render(request, 'contest/maxreached.html')
        except Contender.DoesNotExist:
            pass

        form = PhotoForm()
        context = {
            'form': form,
        }

        if request.user.is_authenticated:
            if request.user.profile.languagePreference == "en":
                return render(request, 'photo/form.html', context)
            else:
                return render(request, 'photo/form-tr.html', context)

        # Guestler için session kontrolü
        # Session'da language belirlenmemiş ise önce belirleyelim
        if "language" not in request.session:
            set_session_for_language_according_to_IP(request)
        if (request.session['language'] == "tr"):
            return render(request, 'photo/form-tr.html', context)
        else:
            return render(request, 'photo/form.html', context)


def contest_photopool(request, slug):
    # O contest'e ait fotoğrafları contestid'sinden tanıyıp, ayrıştırıp öyle veriyoruz photo/index.html dosyasına.
    contest = Contest.objects.get(slug=slug)
    context = {'contest': contest}
    if request.GET.get('p'):
        query = request.GET.get('p')
        if int(query) in [photo.id for photo in Photo.objects.filter(contest=contest)]:
            context['query'] = query

    if request.user.is_authenticated:
        if request.user.profile.languagePreference == "en":
            return render(request, "contest/photopool.html", context)
        else:
            return render(request, "contest/photopool-tr.html", context)

    # Guestler için session kontrolü
    # Session'da language belirlenmemiş ise önce belirleyelim
    if "language" not in request.session:
        set_session_for_language_according_to_IP(request)
    if (request.session['language'] == "tr"):
        return render(request, "contest/photopool-tr.html", context)
    else:
        return render(request, "contest/photopool.html", context)


def contest_delete(request, id):
    contest = get_object_or_404(Contest, id=id)
    contest.delete()
    return redirect("contest:index")

def contest_rankings(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    context = {'contest': contest}

    if timezone.now() < contest.end_date:  # if contest is still in progress
        return render(request, "contest/contest_still_in_progress.html", context)

    if request.user.is_authenticated:
        if request.user.profile.languagePreference == "en":
            return render(request, "contest/rankings.html", context)
        else:
            return render(request, "contest/rankings-tr.html", context)

    # Guestler için session kontrolü
    # Session'da language belirlenmemiş ise önce belirleyelim
    if "language" not in request.session:
        set_session_for_language_according_to_IP(request)
    if (request.session['language'] == "tr"):
        return render(request, "contest/rankings-tr.html", context)
    else:
        return render(request, "contest/rankings.html", context)


