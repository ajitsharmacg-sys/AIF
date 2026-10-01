from aif.models import (
    Aif,
    AifLines,
    AIFCustomerLines,
    AifApprover,
    NSOCurrencyOpUnitConfig,
    OMEmailsConfig,
)
from common.forms import EnhancedModelForm
from django.forms import Select, TextInput,NumberInput
from common.models import Pdh, Organization
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class AifForm(EnhancedModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        orgs = Organization.objects.exclude(
            organization_name__in=["CENV", "CEL"]
        ).values_list("organization_name", flat=True)
        org_choices = [("", "---------")] + [(org, org) for org in orgs]
        field = self.fields["nso"]
        field.choices = org_choices
        field.widget = Select(
            attrs={"class": "form-select form-select-sm", "required": field.required},
            choices=org_choices,
        )
        self.fields["promotion_category"].widget = Select(
            attrs={"class": "form-select form-select-sm"},
            choices=self.fields["promotion_category"].choices,
        )
        self.fields["promotion_category"].required = True
        self.fields["local_currency"].disabled = True

        self.fields["local_currency"].widget.attrs.update(
            {"placeholder": "Currency is derived from NSO Selection"}
        )
        self.fields["email_cc"].widget.attrs.update(
            {"rows": 3, "placeholder": "Enter CC emails, separated by semicolons(;)"}
        )
        self.fields["aif_cancel_numbers"].widget.attrs.update(
            {"rows": 3, "placeholder": "Enter AIF Number, separated by semicolons(;)"}
        )
        self.fields["promotion_campaign"].widget.attrs.update(
            {"rows": 2, "placeholder": "Enter Promotion Campaign Details"}
        )
        self.fields["promotion_activity"].widget.attrs.update(
            {"rows": 2, "placeholder": "Enter Promotion Activity Details"}
        )
        self.fields["exchange_rate"].widget.attrs.update(
            {"placeholder": "EUR is the Base Currency"}
        )
        self.fields["exchange_rate"].disabled = True

    class Meta:
        model = Aif
        fields = [
            "nso",
            "local_currency",
            "exchange_rate",
            "is_all_nso_enabled",
            "start_date",
            "end_date",
            "promotion_campaign",
            "promotion_category",
            "promotion_activity",
            "aif_cancel_numbers",
            "email_cc",
        ]


class AifCustomerLineForm(EnhancedModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["oracle_cust_number"].widget.attrs.update(
            {"placeholder": "Type Customer No", "class": "form-control form-control-sm"}
        )
        self.fields["oracle_cust_name"].widget.attrs.update(
            {
                "placeholder": "Type Customer Name",
                "class": "form-control form-control-sm",
                "autocomplete": "off",
            }
        )

    class Meta:
        model = AIFCustomerLines
        fields = ["oracle_cust_number", "oracle_cust_name"]

class AifLineForm(EnhancedModelForm):

    FIELD_CONFIG = {
        "product_group": {
            "readonly": True,
            "width": "60px",
        },
        "mercury_code": {
            "width": "90px",
        },
        "product_description": {
            "readonly": True,
            "width": "300px",
        },
        "elp": {
            "readonly": True,
            "width": "80px",
            "numeric": True,
        },
        "elp_eur": {
            "readonly": True,
            "width": "80px",
            "numeric": True,
        },
        "promotional_qty": {
            "width": "85px",
            "numeric": True,
        },
        "promotional_elp": {
            "width": "85px",
            "numeric": True,
        },
        "promotional_elp_eur": {
            "readonly": True,
            "width": "85px",
            "numeric": True,
        },
        "promotion_support": {
            "readonly": True,
            "width": "90px",
            "numeric": True,
        },
        "support_per_unit": {
            "readonly": True,
            "width": "90px",
            "numeric": True,
        },
        "promotion_support_eur": {
            "readonly": True,
            "width": "100px",
            "numeric": True,
        },
        "line_value": {
            "readonly": True,
            "width": "100px",
            "numeric": True,
        },
        "line_value_eur": {
            "readonly": True,
            "width": "100px",
            "numeric": True,
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, config in self.FIELD_CONFIG.items():
            if field_name not in self.fields:
                continue
            field = self.fields[field_name]
            attrs = {
                "style": f"width: {config['width']};",
            }
            css_class = "form-control form-control-sm"
            if config.get("numeric"):
                css_class += " text-end"
                field.widget = NumberInput(
                    attrs={
                        **attrs,
                        "class": css_class,
                        "step": "0.01",
                        "inputmode": "decimal",
                    }
                )
            else:
                field.widget = TextInput(
                    attrs={
                        **attrs,
                        "class": css_class,
                    }
                )

            if config.get("readonly"):
                field.disabled = True

    class Meta:
        model = AifLines
        fields = [
            "product_group",
            "mercury_code",
            "product_description",
            "elp_eur",
            "elp",
            "promotional_qty",
            "promotional_elp",
            "promotional_elp_eur",
            "promotion_support",
            "support_per_unit",
            "promotion_support_eur",
            "line_value",
            "line_value_eur",
        ]
class AifApproverAdminForm(EnhancedModelForm):
    class Meta:
        model = AifApprover
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "product_group" in self.fields:
            product_group_codes = (
                Pdh.objects.values("product_group")
                .distinct()
                .order_by("product_group")
                .values_list("product_group", flat=True)
            )
            self.fields["product_group"].widget = Select(
                attrs={"class": "form-select form-select-sm"},
                choices=[(None, "---")] + [(c, c) for c in product_group_codes],
            )


class NSOCurrencyOpUnitForm(EnhancedModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        orgs = Organization.objects.exclude(
            organization_name__in=["CENV", "CEL"]
        ).values_list("organization_name", flat=True)
        org_choices = [("", "---------")] + [(org, org) for org in orgs]
        field = self.fields["nso"]
        field.choices = org_choices
        field.widget = Select(
            attrs={"class": "form-select form-select-sm", "required": field.required},
            choices=org_choices,
        )
        self.fields["currency"].widget = Select(
            attrs={"class": "form-select form-select-sm"},
            choices=self.fields["currency"].choices,
        )

    class Meta:
        model = NSOCurrencyOpUnitConfig
        fields = "__all__"


class OMEmailsConfigForm(EnhancedModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        orgs = Organization.objects.exclude(
            organization_name__in=["CENV", "CEL"]
        ).values_list("organization_name", flat=True)
        org_choices = [("", "---------")] + [(org, org) for org in orgs]
        field = self.fields["nso"]
        field.choices = org_choices
        field.widget = Select(
            attrs={"class": "form-select form-select-sm", "required": field.required},
            choices=org_choices,
        )
        self.fields["om_emails"].widget.attrs.update(
            {"rows": 3, "placeholder": "Enter OM emails, separated by semicolons(;)"}
        )
        
    def clean_nso(self):
        nso = self.cleaned_data.get("nso")

        if OMEmailsConfig.objects.filter(nso=nso).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "A configuration already exists for this NSO."
            )

        return nso

    def clean_om_emails(self):
        value = self.cleaned_data.get("om_emails")
        if not value:
            return value

        emails = [email.strip() for email in value.split(";") if email.strip()]
        invalid_emails = []

        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                invalid_emails.append(email)

        if invalid_emails:
            raise forms.ValidationError(
                f"Invalid email(s): {', '.join(invalid_emails)}"
            )

        return ";".join(emails)

    class Meta:
        model = OMEmailsConfig
        fields = "__all__"
