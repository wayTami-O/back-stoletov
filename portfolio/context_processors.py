from .models import SocialLinks


def social_links(_request):
    link_obj = SocialLinks.objects.first()
    links = []
    if link_obj:
        links = [
            {"label": "Telegram", "url": link_obj.telegram or ''},
            {"label": "GitHub", "url": link_obj.github or ''},
            {"label": "LinkedIn", "url": link_obj.linkedin or ''},
        ]
    return {"social_links": links}

