from django.db import models
import uuid
from datetime import date
from django.db import models
from django.conf import settings
from aif.apps import AifConfig
from common.models import Organization


class MetaAbstract(models.Model):
    """
    Metadata Base Class, adds meta fields to the models.
    """

    meta_created_date = models.DateTimeField(
        auto_now=True, blank=True, verbose_name="Created At"
    )
    meta_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Created By",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )
    meta_edited_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Last Edit At"
    )
    meta_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Last Edit By",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_edited_by",
    )

    class Meta:
        abstract = True


class MetaCreatedAbstract(models.Model):
    """
    Metadata Base Class, adds meta fields to the models.
    """

    meta_created_date = models.DateTimeField(
        auto_now_add=True, blank=True, verbose_name="Created At"
    )
    meta_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Created By",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )

    class Meta:
        abstract = True


class MetaEditedAbstract(models.Model):
    """
    Metadata Base Class, adds meta fields to the models.
    """

    meta_edited_date = models.DateTimeField(null=True, blank=True)
    meta_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_edited_by",
    )

    class Meta:
        abstract = True


def generate_upload_path(nso: str, start_date: date, aif_id: str) -> str:
    """Sharepoint path generator to store AIF"""
    base_url = f"{AifConfig.site_address}{AifConfig.library}"
    return f"{base_url}/{nso}/{start_date.year}/{aif_id}"


class PromoCategoryChoices(models.TextChoices):
    PRODUCT_SUPPORT = ("Product Support", "Product Support")
    TENDER = ("Tender", "Tender")


class ResponsibilityChoices(models.TextChoices):
    PSBD = ("PSBD", "PSBD")
    TENDER = ("Tender", "Tender")


class CurrencyChoices(models.TextChoices):
    EUR = ("EUR", "EUR")
    GBP = ("GBP", "GBP")
    CHF = ("CHF", "CHF")
    SEK = ("SEK", "SEK")
    NOK = ("NOK", "NOK")
    DKK = ("DKK", "DKK")
    PLN = ("PLN", "PLN")
    HUF = ("HUF", "HUF")
    CZK = ("CZK", "CZK")
    RUB = ("RUB", "RUB")


class Aif(MetaAbstract):
    aif_id = models.BigAutoField(primary_key=True, verbose_name="AIF ID")
    nso = models.CharField(max_length=50, blank=False, null=False, verbose_name="NSO")
    local_currency = models.CharField(
        max_length=50, blank=False, null=False, verbose_name="Local Currency"
    )
    is_all_nso_enabled = models.BooleanField(
        default=False,
        verbose_name="All NSO Market",
        help_text="If enabled, this AIF applies to all customers for the selected NSO.",
    )
    start_date = models.DateField(blank=False, null=False, verbose_name="Start Date")
    end_date = models.DateField(blank=False, null=False, verbose_name="End Date")

    promotion_campaign = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Promo Campaign"
    )
    promotion_category = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        choices=PromoCategoryChoices,
        verbose_name="Promo Category",
    )
    promotion_activity = models.TextField(
        blank=True, null=True, verbose_name="Promo Activity"
    )
    aif_cancel_numbers = models.TextField(
        blank=True, null=True, verbose_name="AIF To Be Cancelled"
    )
    email_cc = models.TextField(
        max_length=1000, null=True, blank=True, verbose_name="Email CC"
    )
    link = models.URLField(max_length=3000, blank=True, null=True)

    exchange_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="FX Rate"
    )

    def __str__(self) -> str:
        return str(self.aif_id)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.link and self.start_date:
            self.link = generate_upload_path(
                nso=self.nso,
                start_date=self.start_date,
                aif_id=self.aif_id,
            )
            super().save(update_fields=["link"])


class AifStatusChoices(models.TextChoices):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    COMMERCIALLY_APPROVED = "COMMERCIALLY_APPROVED"
    INVALID = "INVALID"
    AWAITING_VALIDATION = "AWAITING_VALIDATION"
    CLOSED = "CLOSED"


class AifStatus(MetaCreatedAbstract):

    aif = models.ForeignKey(
        Aif,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="aif_status",
    )
    status = models.CharField(
        max_length=50,
        choices=AifStatusChoices,
        null=False,
        blank=False,
        default=AifStatusChoices.DRAFT,
    )
    comment = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.status}"

    class Meta:
        verbose_name_plural = "AIF Statuses"


class AIFCustomerLines(MetaAbstract):
    aif = models.ForeignKey(
        Aif,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="aif_customer_lines",
    )
    oracle_cust_number = models.CharField(max_length=50, verbose_name="Customer Number")
    oracle_cust_name = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Customer Name"
    )

    def __str__(self):
        return f"{self.oracle_cust_number} - {self.oracle_cust_name}"
    
    class Meta:
        unique_together = ("aif", "oracle_cust_number")


class AifLines(MetaAbstract):
    aif = models.ForeignKey(
        Aif, on_delete=models.CASCADE, blank=False, null=False, related_name="aif_lines"
    )
    product_group = models.CharField(
        max_length=2, null=True, blank=True, verbose_name="Product Group"
    )
    mercury_code = models.CharField(
        max_length=10, blank=False, null=True, verbose_name="Mercury Code"
    )
    product_description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Product Description"
    )
    elp = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Local ELP"
    )
    elp_eur = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="ELP (EUR)"
    )
    promotional_qty = models.PositiveIntegerField(default=0, verbose_name="Promo Qty")
    promotional_elp = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Promo ELP"
    )
    promotion_support = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Promo Support"
    )
    support_per_unit = models.DecimalField( 
        max_digits=5, decimal_places=2, default=0, verbose_name="Support Per Unit (%)",
    )
    line_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Line Value"
    )
    promotional_elp_eur = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Promo ELP (EUR)",
    )
    promotion_support_eur = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Promo Support (EUR)",
    )
    line_value_eur = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Line Value (EUR)",
    )
    
    def __str__(self) -> str:
        return self.aif_id


class AifLineStatusChoices(models.TextChoices):
    DRAFT = "DRAFT"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    AWAITING_VALIDATION = "AWAITING_VALIDATION"
    CLOSED = "CLOSED"


class AifLineStatus(MetaCreatedAbstract):
    aif_line = models.ForeignKey(
        AifLines,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="aif_line_status",
    )
    status = models.CharField(
        max_length=50,
        choices=AifLineStatusChoices,
        null=False,
        blank=False,
        default=AifLineStatusChoices.DRAFT,
    )
    comment = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        verbose_name = "Aif Line Status"
        verbose_name_plural = "Aif Line Statuses"


class AifApprover(MetaEditedAbstract):
    product_group = models.CharField(
        max_length=2, null=True, blank=True, verbose_name="Product Group"
    )
    responsibility = models.CharField(max_length=20, choices=ResponsibilityChoices)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approver",
        verbose_name="AIF Approver",
    )

    def __str__(self):
        return f"{self.product_group} - {self.responsibility}"

    class Meta:
        verbose_name = "AIF Approver"
        verbose_name_plural = "AIF Approver(PSBD)"


class MasterPricelist(models.Model):
    """
    Read-only model for [ELP_PriceList].[dbo].[1_MasterPricelist]
    """

    item_code_1st_layer = models.CharField(
        db_column="Item_Code_1st_Layer",
        primary_key=True,
        max_length=255,
        blank=True,
        null=False,
    )

    price_list_name = models.CharField(
        db_column="Price_List_Name", max_length=255, blank=True, null=True
    )
    pg_group_number = models.CharField(
        db_column="PG_Group_Number", max_length=255, blank=True, null=True
    )
    pg_type_group = models.CharField(
        db_column="PG_Type_Group", max_length=255, blank=True, null=True
    )
    item_description = models.CharField(
        db_column="Item_Description", max_length=255, blank=True, null=True
    )
    item_group = models.CharField(
        db_column="Item_Group", max_length=255, blank=True, null=True
    )
    product_group = models.CharField(
        db_column="Product_Group", max_length=255, blank=True, null=True
    )
    product_series = models.CharField(
        db_column="Product_Series", max_length=255, blank=True, null=True
    )
    product_group_subgroup = models.CharField(
        db_column="Product_Group_Subgroup", max_length=255, blank=True, null=True
    )
    item_code = models.CharField(
        db_column="Item_Code", max_length=255, blank=True, null=True
    )
    item_status = models.CharField(
        db_column="Item_Status", max_length=255, blank=True, null=True
    )
    ean_end_product = models.CharField(
        db_column="EAN_End_Product", max_length=255, blank=True, null=True
    )
    country_of_origin = models.CharField(
        db_column="Country_OF_Origin", max_length=255, blank=True, null=True
    )
    unit_gross_weight = models.DecimalField(
        db_column="Unit_Gross_Weight",
        max_digits=12,
        decimal_places=3,
        blank=True,
        null=True,
    )
    uom_length = models.DecimalField(
        db_column="UOM_Length", max_digits=12, decimal_places=3, blank=True, null=True
    )
    uom_width = models.DecimalField(
        db_column="UOM_Width", max_digits=12, decimal_places=3, blank=True, null=True
    )
    uom_height = models.DecimalField(
        db_column="UOM_Height", max_digits=12, decimal_places=3, blank=True, null=True
    )
    pro_item = models.CharField(
        db_column="PRO_Item", max_length=255, blank=True, null=True
    )
    niche_item = models.CharField(
        db_column="NICHE_Item", max_length=255, blank=True, null=True
    )
    ct_qty = models.DecimalField(
        db_column="CT_Qty", max_digits=12, decimal_places=3, blank=True, null=True
    )
    pt_qty = models.DecimalField(
        db_column="PT_Qty", max_digits=12, decimal_places=3, blank=True, null=True
    )
    cp_qty = models.DecimalField(
        db_column="CP_Qty", max_digits=12, decimal_places=3, blank=True, null=True
    )
    bp_qty = models.DecimalField(
        db_column="BP_Qty", max_digits=12, decimal_places=3, blank=True, null=True
    )
    ep_qty = models.DecimalField(
        db_column="EP_Qty", max_digits=12, decimal_places=3, blank=True, null=True
    )
    recommended_street_price = models.DecimalField(
        db_column="Recommended_Street_Price",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    elp_eur = models.DecimalField(
        db_column="ELP_EUR", max_digits=12, decimal_places=2, blank=True, null=True
    )
    price_start_date = models.DateTimeField(
        db_column="Price_Start_Date", blank=True, null=True
    )
    carton_price_unit_eur = models.DecimalField(
        db_column="Carton_Price_Unit_EUR",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    pallet_price_unit_eur = models.DecimalField(
        db_column="Pallet_Price_Unit_EUR",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    truck_price_unit_eur = models.DecimalField(
        db_column="Truck_Price_Unit_EUR",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    local_currency = models.CharField(
        db_column="Local_Currency", max_length=10, blank=True, null=True
    )
    elp_local = models.DecimalField(
        db_column="ELP_Local", max_digits=12, decimal_places=2, blank=True, null=True
    )
    carton_price_unit_local = models.DecimalField(
        db_column="Carton_Price_Unit_Local",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    pallet_price_unit_local = models.DecimalField(
        db_column="Pallet_Price_Unit_Local",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    truck_price_unit_local = models.DecimalField(
        db_column="Truck_Price_Unit_Local",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    copy_tax_category_code = models.CharField(
        db_column="Copy_Tax_Category_Code",
        max_length=50,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )
    copy_tax_printed_tax_code = models.CharField(
        db_column="Copy_Tax_Printed_Tax_Code",
        max_length=50,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )
    copy_tax_code_name = models.CharField(
        db_column="Copy_Tax_Code_Name",
        max_length=100,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )
    copy_tax_code_amount = models.DecimalField(
        db_column="Copy_Tax_Code_Amount",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    environment_tax_category_code = models.CharField(
        db_column="Environment_Tax_Category_Code",
        max_length=50,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )
    environment_tax_printed_tax_code = models.CharField(
        db_column="Environment_Tax_Printed_Tax_Code",
        max_length=50,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )
    environment_tax_code_name = models.CharField(
        db_column="Environment_Tax_Code_Name",
        max_length=100,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )
    environment_tax_code_amount = models.DecimalField(
        db_column="Environment_Tax_Code_Amount",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "1_MasterPricelist"


class CDHCustomer(models.Model):
    party_number = models.CharField(
        db_column="PARTY_NUMBER",
        primary_key=True,
        max_length=10,
        db_collation="Latin1_General_CI_AS",
        blank=True,
    )
    customer_name = models.CharField(
        db_column="CUSTOMER_NAME",
        max_length=100,
        db_collation="Latin1_General_CI_AS",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "CDH_Customer"

    def __str__(self):
        return f"{self.party_number} - {self.customer_name}"


class ExchangeRates(models.Model):
    from_currency = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="FROM_CURRENCY",
        db_collation="Latin1_General_CI_AS",
    )

    to_currency = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="TO_CURRENCY",
        db_collation="Latin1_General_CI_AS",
    )

    conversion_date = models.DateTimeField(
        null=True, blank=True, db_column="CONVERSION_DATE"
    )

    conversion_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="CONVERSION_TYPE",
        db_collation="Latin1_General_CI_AS",
    )

    conversion_rate = models.DecimalField(
        max_digits=22,
        decimal_places=7,
        null=True,
        blank=True,
        db_column="CONVERSION_RATE",
    )

    record_date = models.DateTimeField(null=True, blank=True, db_column="Record_date")

    source_file = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="Source_File",
        db_collation="Latin1_General_CI_AS",
    )

    datasource = models.CharField(
        max_length=10,
        primary_key=True,
        blank=True,
        db_column="DATASOURCE",
        db_collation="Latin1_General_CI_AS",
    )

    class Meta:
        managed = False
        db_table = "Exchange_Rates"

    def __str__(self):
        return f"{self.from_currency} → {self.to_currency} ({self.conversion_date})"


class NSOCurrencyOpUnitConfig(models.Model):
    nso = models.CharField(max_length=50, blank=False, null=False, verbose_name="NSO")
    currency = models.CharField(
        max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.EUR
    )

    operation_unit_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nso} - {self.currency}"

    class Meta:
        verbose_name = "NSO Currency"
        verbose_name_plural = "NSO Currency"


class OMEmailsConfig(models.Model):
    nso = models.CharField(max_length=50, blank=False, null=False, verbose_name="NSO")
    om_emails = models.TextField(
        max_length=1000, null=True, blank=True, verbose_name="OM Emails"
    )

    def __str__(self):
        return f"{self.om_emails}"

    class Meta:
        verbose_name = "OM Emails"
        verbose_name_plural = "OM Emails"

    