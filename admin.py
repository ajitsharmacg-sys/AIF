from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import (
    AifApprover,
    NSOCurrencyOpUnitConfig,
    OMEmailsConfig,
)
from .forms import AifApproverAdminForm,NSOCurrencyOpUnitForm,OMEmailsConfigForm
from aif.roles import ADMIN_ROLE, PSBD_TEAM_USER


@admin.register(AifApprover)
class AifApproverAdmin(admin.ModelAdmin):
    save_as = True
    form = AifApproverAdminForm

    list_display = (
        "id",
        "product_group",
        "responsibility",
        "approver_email",
        "meta_edited_date",
    )

    list_filter = ("product_group", "responsibility")

    search_fields = (
        "approver__username",
        "approver__email",
        "product_group",
    )

    readonly_fields = (
        "meta_edited_date",
        "meta_edited_by",
    )

    exclude = ("meta_edited_by",)

    def save_model(self, request, obj, form, change):
        obj.meta_edited_by = request.user
        obj.meta_edited_date = timezone.now()

        super().save_model(request, obj, form, change)

        psbd_group, _ = Group.objects.get_or_create(name=PSBD_TEAM_USER)
        if not obj.approver.groups.filter(name=PSBD_TEAM_USER).exists():
            obj.approver.groups.add(psbd_group)

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def approver_email(self, obj):
        return obj.approver.email

    approver_email.short_description = "Approver Email"


@admin.register(NSOCurrencyOpUnitConfig)
class NSOCurrencyOpUnitAdmin(admin.ModelAdmin):
    save_as = True
    form = NSOCurrencyOpUnitForm

    list_display = (
        "id",
        "nso",
        "currency",
        "operation_unit_code",
    )
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()
    
    
@admin.register(OMEmailsConfig)
class OMEmailsConfigAdmin(admin.ModelAdmin):
    save_as = True
    form = OMEmailsConfigForm 

    list_display = (
        "id",
        "nso",
        "om_emails", 
    )
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name=ADMIN_ROLE).exists()
