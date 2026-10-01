from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from common.apps import CommonConfig
from common.views import forbidden_page
from common.models import ContactOrLink
from aif.forms import AifCustomerLineForm, AifForm, AifLineForm
from django.contrib.auth import get_user_model
from aif.roles import ROLES, NSO_USER, SALES_OPS_USER, PSBD_TEAM_USER, ADMIN_ROLE
from aif.apps import AifConfig
from aif.workflow import (
    AIF_STATUS_GRAPH,
    AIF_LINE_STATUS_GRAPH,
    LINE_STATUS_TO_ROLE,
    ROLE_TO_LINE_STATUS,
)
from aif.workflow import AIF_STATUS_TO_ROLE, ROLE_TO_AIF_STATUS

UserModel = get_user_model()


def has_access_to_aifmgm(user):
    if user.groups.filter(name__in=ROLES).exists():
        return True

    return False


def get_default_context(request):
    app_prefix = "AIF App"
    users = UserModel.objects.filter(
        groups__name__in=[PSBD_TEAM_USER, SALES_OPS_USER, ADMIN_ROLE]
    ).distinct()
    users_to_display = []
    for user in users:
        u = {}
        u["email"] = user.email
        u["first_name"] = user.first_name
        u["last_name"] = user.last_name
        u["roles"] = []
        for group in user.groups.all():
            if app_prefix in group.name:
                u["roles"].append(group.name)

        u["roles"] = ", ".join(u["roles"])
        users_to_display.append(u)

    context = {
        "aif_form": AifForm(),
        "aif_line_form": AifLineForm(),
        "aif_customer_line_form": AifCustomerLineForm(),
        "site_address": AifConfig.site_address,
        "library": AifConfig.library,
        "sharepoint_upload_endpoint": settings.AZURE_SECRETS[
            "SharepointUploadEndpoint"
        ],
        "users_to_display": users_to_display,
        "links": ContactOrLink.objects.filter(related_to_app=AifConfig.name),
        "feedback_site_address": CommonConfig.feedback_site_address,
        "feedback_library": CommonConfig.feedback_library,
        "app_name":AifConfig.name,
    }
    return context


@login_required
def aif_index(request, context=None):
    if not has_access_to_aifmgm(UserModel.objects.get(id=request.user.id)):
        return forbidden_page(request, ROLES)

    default_context = get_default_context(request)
    if not context:
        context = default_context
    else:
        context = context | default_context

    return render(request, "aif/app.html", context=context)


@login_required
def aif_view(request, aif_id):
    return aif_index(request, context={"aif_id": aif_id, "start_screen": "aif_view"})


@login_required
def workflow(request):
    workflow = {
        "AIF_STATUS_GRAPH": AIF_STATUS_GRAPH,
        "AIF_LINE_STATUS_GRAPH": AIF_LINE_STATUS_GRAPH,
        "LINE_STATUS_TO_ROLE": LINE_STATUS_TO_ROLE,
        "ROLE_TO_LINE_STATUS": ROLE_TO_LINE_STATUS,
        "ROLE_TO_AIF_STATUS": ROLE_TO_AIF_STATUS,
        "AIF_STATUS_TO_ROLE": AIF_STATUS_TO_ROLE,
        "ROLES": ROLES,
        "ADMIN_ROLE": ADMIN_ROLE,
    }
    return JsonResponse(workflow)
