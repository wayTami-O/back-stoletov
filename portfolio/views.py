from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

from .models import Project, SocialLinks
from .forms import ContactForm
from config.openapi import get_openapi_schema


class ProjectListView(ListView):
    model = Project
    template_name = 'portfolio/home.html'
    context_object_name = 'projects'


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact: ContactForm = form.save()
            # Send to Telegram
            token = settings.TELEGRAM_BOT_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID
            if token and chat_id:
                text = (
                    f"Новая заявка с формы:\n"
                    f"Имя: {contact.full_name}\n"
                    f"Email: {contact.email}\n"
                    f"Сообщение: {contact.message}"
                )
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id": chat_id, "text": text},
                        timeout=10,
                    )
                except Exception:
                    pass
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'portfolio/contact.html', {"form": form})


def _serialize_project(project: Project, request) -> dict:
    image_url = project.image.url if project.image else None
    if image_url:
        image_url = request.build_absolute_uri(image_url)
    return {
        "id": project.id,
        "name": project.name,
        "subtitle": project.subtitle,
        "description": project.description,
        "description_en": project.description_en,
        "category": project.category,
        "category_label": project.get_category_display(),
        "release_date": project.release_date.isoformat() if project.release_date else None,
        "work_period": {
            "start": project.work_start_date.isoformat() if project.work_start_date else None,
            "end": project.work_end_date.isoformat() if project.work_end_date else None,
        },
        "links": {
            "google_play": project.link_google_play,
            "rustore": project.link_rustore,
            "appstore": project.link_appstore,
            "github": project.link_github,
            "extra_social": project.extra_social_link,
        },
        "image": image_url,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        "created_at": project.created_at.isoformat() if project.created_at else None,
    }


def projects_api(request):
    projects = Project.objects.all()
    data = [_serialize_project(p, request) for p in projects]
    return JsonResponse(data, safe=False)


def project_detail_api(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    data = _serialize_project(project, request)
    return JsonResponse(data)


@csrf_exempt
def contact_api(request):
    if request.method != 'POST':
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    data = None
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body or b"{}")
        except Exception:
            data = {}
        form = ContactForm(data)
    else:
        form = ContactForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)
    contact = form.save()
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    if token and chat_id:
        text = (
            f"Новая заявка с формы (API):\n"
            f"Имя: {contact.full_name}\n"
            f"Email: {contact.email}\n"
            f"Сообщение: {contact.message}"
        )
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text},
                timeout=10,
            )
        except Exception:
            pass
    return JsonResponse({"ok": True})


@csrf_exempt
def social_links_api(request):
    if request.method == 'GET':
        obj = SocialLinks.objects.first()
        data = {
            "telegram": getattr(obj, 'telegram', ''),
            "github": getattr(obj, 'github', ''),
            "linkedin": getattr(obj, 'linkedin', ''),
        }
        return JsonResponse(data)
    if request.method == 'POST':
        # Simple token-based guard using Django admin session would be better,
        # but for simplicity accept a shared token via header X-Admin-Token
        token = request.headers.get('X-Admin-Token')
        expected = getattr(settings, 'SOCIAL_ADMIN_TOKEN', '')
        if not expected or token != expected:
            return JsonResponse({"detail": "Unauthorized"}, status=401)
        obj, _ = SocialLinks.objects.get_or_create(id=1)
        if request.content_type and 'application/json' in request.content_type:
            try:
                body = json.loads(request.body or b"{}")
            except Exception:
                body = {}
            obj.telegram = (body.get('telegram') or '').strip()
            obj.github = (body.get('github') or '').strip()
            obj.linkedin = (body.get('linkedin') or '').strip()
        else:
            obj.telegram = request.POST.get('telegram') or ''
            obj.github = request.POST.get('github') or ''
            obj.linkedin = request.POST.get('linkedin') or ''
        obj.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"detail": "Method not allowed"}, status=405)


def swagger_json(request):
    base_url = request.build_absolute_uri('/')[:-1]
    return JsonResponse(get_openapi_schema(base_url))

# Create your views here.
