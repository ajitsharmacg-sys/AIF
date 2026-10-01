from aif.models import (
    Aif,
    AifLines,
    AifStatus,
    AifLineStatus,
    AifApprover,
    MasterPricelist,
    AIFCustomerLines,
    ExchangeRates,
    CDHCustomer,
    NSOCurrencyOpUnitConfig,
    OMEmailsConfig,
)
from rest_framework import serializers
from common.serializers import CanonUserSimpleSerializer

class AifCustomerLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFCustomerLines
        fields = "__all__"
        read_only_fields = [
            "meta_created_by",
            "meta_created_date",
            "meta_edited_by",
            "meta_edited_date",
        ]

class AifLinesStatusSerializer(serializers.ModelSerializer):
    meta_created_by = serializers.StringRelatedField(many=False)

    class Meta:
        model = AifLineStatus
        fields = "__all__"
        read_only_fields = [
            "meta_created_by",
            "meta_created_date",
        ]


class AifLineReadSerializer(serializers.ModelSerializer):
    line_status = serializers.SerializerMethodField()
    meta_created_by = serializers.StringRelatedField(many=False)

    class Meta:
        model = AifLines
        fields = "__all__"
        read_only_fields = [
            "meta_created_date",
            "meta_created_by",
            "meta_edited_date",
            "meta_edited_by",
        ]

    def get_line_status(self, obj):
        latest = (
            obj.aif_line_status
            .order_by("-meta_created_date")
            .first()
        )

        return latest.status if latest else None
    
class AifLineWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AifLines
        fields = "__all__"
        read_only_fields = [
            "meta_created_date",
            "meta_created_by",
            "meta_edited_date",
            "meta_edited_by",
        ]

class AifReadSerializer(serializers.ModelSerializer):
    meta_created_by = serializers.StringRelatedField(many=False)
    aif_status = serializers.SerializerMethodField()
    aif_cancel_numbers_display = serializers.SerializerMethodField()
    class Meta:
        model = Aif
        fields = "__all__"
        read_only_fields = [
            "aif_id",
            "link",
            "meta_created_date",
            "meta_created_by",
            "meta_edited_date",
            "meta_edited_by",
        ]

    def get_aif_status(self, obj):
        latest = (
            obj.aif_status
            .order_by("-meta_created_date")
            .first()
        )

        return latest.status if latest else None

    def get_aif_cancel_numbers_display(self, obj):
        if not obj.aif_cancel_numbers:
            return ""

        return ", ".join(
            value.strip()
            for value in obj.aif_cancel_numbers.split(";")
            if value.strip()
        )


class AifWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aif
        exclude = [
            "meta_created_date",
            "meta_created_by",
            "meta_edited_date",
            "meta_edited_by",
        ]
        read_only_fields = [
            "link",
            "aif_id",
        ]

class AifStatusSerializer(serializers.ModelSerializer):
    meta_created_by = serializers.StringRelatedField(many=False)
    class Meta:
        model = AifStatus
        fields = "__all__"
        read_only_fields = [
            "meta_created_by",
            "meta_created_date",
        ]

class AifApproverSerializer(serializers.ModelSerializer):
    meta_edited_by = CanonUserSimpleSerializer(many=False, read_only=True)
    approver = CanonUserSimpleSerializer(many=False, read_only=True)

    class Meta:
        model = AifApprover
        fields = "__all__"

class MasterPriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterPricelist
        fields = [
            "item_code_1st_layer",
            "price_list_name",
            "price_start_date",
            "local_currency",
            "elp_eur",
        ]


class ExchangeRatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRates
        fields = [
            "from_currency",
            "to_currency",
            "record_date",
            "conversion_rate",
        ]


class CDHCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDHCustomer
        fields = "__all__"


class NSOCurrencyOpUnitConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NSOCurrencyOpUnitConfig
        fields = "__all__"


class OMEmailsConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OMEmailsConfig
        fields = "__all__"
