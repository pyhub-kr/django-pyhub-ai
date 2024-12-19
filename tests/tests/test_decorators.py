import pytest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.test import AsyncClient, RequestFactory
from django.urls import path

from pyhub_ai.decorators import acsrf_exempt, alogin_required, arequire_POST


@arequire_POST
async def async_post_only_view(request):
    return HttpResponse("OK")


@acsrf_exempt
@arequire_POST
async def async_post_only_exempt_view(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    return HttpResponse("OK")


urlpatterns = [
    path("test-post/", async_post_only_view),
    path("test-post-exempt/", async_post_only_exempt_view),
]


@pytest.mark.asyncio
@pytest.mark.urls(__name__)
class TestAsyncCsrfExempt:
    @pytest.mark.it("CSRF 토큰이 없는 POST 요청은 403 오류를 발생시켜야 합니다.")
    async def test_post_without_csrf_token(self, csrf_async_client: AsyncClient):
        # AsyncClient에서는 디폴트로 enforce_csrf_checks=False 설정으로 CSRF 체크가 비활성화되어있습니다.
        # csrf_async_client는 enforce_csrf_checks=True 설정으로 CSRF 체크가 강제 활성화됩니다.
        response = await csrf_async_client.post("/test-post/")
        assert response.status_code == HttpResponseForbidden.status_code

    @pytest.mark.it("async_csrf_exempt 장식자가 적용된 뷰는 CSRF 토큰 없이도 POST 요청이 가능해야 합니다.")
    async def test_post_with_csrf_exempt(self, csrf_async_client: AsyncClient):
        response = await csrf_async_client.post("/test-post-exempt/")
        assert response.status_code == 200
        assert response.content.decode() == "OK"


@pytest.mark.asyncio
class TestALoginRequired:
    @pytest.mark.it("로그인하지 않은 사용자는 로그인 페이지로 리다이렉트되어야 합니다.")
    async def test_anonymous_user_redirected(self, settings):
        @alogin_required
        async def protected_view(request):
            return HttpResponse("OK")

        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        response = await protected_view(request)
        assert isinstance(response, HttpResponseRedirect)
        assert settings.LOGIN_URL in response.url

    @pytest.mark.it("로그인한 사용자는 보호된 뷰에 접근할 수 있어야 합니다.")
    async def test_authenticated_user_allowed(self, create_user):
        @alogin_required
        async def protected_view(request):
            return HttpResponse("OK")

        request = RequestFactory().get("/")
        request.user = create_user
        response = await protected_view(request)
        assert response.status_code == 200
        assert response.content.decode() == "OK"
