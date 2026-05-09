from .models import CompanyProfile


def company_profile(request):
    try:
        profile = CompanyProfile.objects.get(pk=1)
    except CompanyProfile.DoesNotExist:
        profile = None
    return {'company_profile': profile}
