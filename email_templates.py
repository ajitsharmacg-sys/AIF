from aif.models import AifStatusChoices


def get_aif_cc(aif, status):
    if status == AifStatusChoices.AWAITING_VALIDATION:
        return aif.email_cc or None
    if status == AifStatusChoices.PLANNED:
        return aif.email_cc or None
    if status == AifStatusChoices.COMMERCIALLY_APPROVED:
        return aif.meta_created_by.email
    if status == AifStatusChoices.INVALID:
        return aif.email_cc or None
    if status == AifStatusChoices.CLOSED:
        return aif.meta_created_by.email
    return None


def signature_user(name):
    return f"""
    Thanks,<br>
    Kind regards,<br>
    {name}
    """


ITCG_SIGNATURE = """
Thanks<br>
Kind regards,<br>
ITCG Rev Sales Operations
"""

AIF_FLOW_SIGNATURE = """
Thanks,<br>
Kind regards,<br>
AIF Flow
"""

REV_OPS_SIGNATURE = """
Thanks,<br>
Kind Regards,<br>
Rev Sales Ops Team
"""


def base_html_wrapper(content: str, signature: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; font-size:14px; color:#333;">
        {content}
        <br><br>
        {signature}
    </body>
    </html>
    """


def get_aif_email_subject(aif, status, closed_type=None):

    if status == AifStatusChoices.AWAITING_VALIDATION:
        return f"Promotion Ref:{aif.aif_id} Validation Request to {aif.meta_created_by.email}"

    if status == AifStatusChoices.PLANNED:
        return f"Promotion Ref:{aif.aif_id} is now with Commercial Planning Team"

    if status == AifStatusChoices.COMMERCIALLY_APPROVED:
        return f"Promotion Ref: {aif.aif_id} is now with Revenue Ops Team"

    if status == AifStatusChoices.INVALID:
        return f"Promotion Ref: {aif.aif_id} has been Rejected"

    if status == AifStatusChoices.CLOSED and closed_type == "validated":
        return f"Promotion Ref:{aif.aif_id} has been validated by {aif.meta_created_by.email}"

    if status == AifStatusChoices.CLOSED and closed_type == "completed":
        return f"Promotion Ref:{aif.aif_id} has been completed"

    return ""


def get_aif_email_body(aif, status, link: str, comment=None, closed_type=None):

    if status == AifStatusChoices.AWAITING_VALIDATION:
        content = f"""
            Dear {aif.meta_created_by.first_name},<br><br>

                Please validate your ONINVOICE promotion request
                within 48 hours.<br><br>

                Please click below link to view the promotion details:<br>
                <a href="{link}">
                    {link}
                </a>
                <br><br>

                Promotion Status: Closed<br>
                Validation Status: Pending<br><br>
        """
        return base_html_wrapper(content, REV_OPS_SIGNATURE)

    if status == AifStatusChoices.PLANNED:
        content = f"""
                Dear {aif.meta_created_by.first_name},<br><br>

                Your ONINVOICE promotion request has been submitted to the
                Commercial Planning Team for approval and is expected to be
                approved within 24 hours.<br><br>

                Please click the link below to review the promotion details:<br>
                <a href="{link}">
                    {link}
                </a>
                <br><br>
        """
        return base_html_wrapper(content, REV_OPS_SIGNATURE)

    if status == AifStatusChoices.COMMERCIALLY_APPROVED:
        content = f"""
        Dear {aif.meta_created_by.first_name},<br><br>

                Your ONINVOICE promotion request has received
                commercial approval and has been forwarded to the
                Revenue Ops Team. Oracle is expected to be updated
                within 48 hours.<br><br>

                Please click the link below to view the promotion details:<br>
                <a href="{link}">
                    {link}
                </a>
                <br><br>
        """
        return base_html_wrapper(content, REV_OPS_SIGNATURE)

    if status == AifStatusChoices.INVALID:
        content = f"""
            Dear {aif.meta_created_by.first_name},<br><br>

                Your ONINVOICE promotion request with reference
                {aif.aif_id} has been rejected.<br><br>

                Reason for Rejection: {comment or "-"}<br><br>

                Please click the link below to review the promotion details:<br>
                <a href="{link}">
                    {link}
                </a>
                <br><br>

                If required, you may amend the promotion and resubmit it
                for approval.<br><br>
        """
        return base_html_wrapper(content, AIF_FLOW_SIGNATURE)

    if status == AifStatusChoices.CLOSED and closed_type == "validated":
        content = f"""
        Dear Rev Ops Team,<br><br>

                Please be advised that {aif.meta_created_by.email} has
                validated the AIF.<br><br>

                Please click below link to view the promotion details:<br>
                <a href="{link}">
                    {link}
                </a>
                <br><br>

                Promotion Status: Closed<br>
                Validation Status: Validated<br><br>

        """
        return base_html_wrapper(
            content, signature_user(aif.meta_created_by.first_name)
        )

    # CLOSED - COMPLETED
    if status == AifStatusChoices.CLOSED and closed_type == "completed":
        content = f"""
        Dear Rev Ops Team,<br><br>

                The promotion request has been successfully completed.<br><br>
                Please click the link below to review the promotion details:<br>
                <a href="{link}">
                    {link}
                </a>
                <br><br>

                Please note that this promotion request is subject to
                SOX audit review.<br><br>

        """
        return base_html_wrapper(content, ITCG_SIGNATURE)

    return ""


def get_om_email_subject(aif):
    return f"AIF {aif.aif_id} - Open Orders Report"


def build_om_email_body(aif, link: str):

    customers_html = ""
    if aif.aif_customer_lines.exists():
        for cust in aif.aif_customer_lines.all():
            customers_html += f"""
            <tr>
                <td style="padding:6px;">{cust.oracle_cust_number}</td>
                <td style="padding:6px;">{cust.oracle_cust_name or ''}</td>
            </tr>
            """
    else:
        customers_html = """
        <tr>
            <td colspan="2" style="padding:6px; text-align:center;">
                All customers for selected NSO
            </td>
        </tr>
        """

    lines_html = ""
    for line in aif.aif_lines.all():
        lines_html += f"""
        <tr>
            <td style="padding:6px;">{line.product_group or ''}</td>
            <td style="padding:6px;">{line.mercury_code}</td>
            <td style="padding:6px;">{line.product_description or ''}</td>
            <td style="padding:6px; text-align:right;">{line.elp_eur}</td>
            <td style="padding:6px; text-align:right;">{line.elp}</td>
            <td style="padding:6px; text-align:right;">{line.promotional_elp}</td>
        </tr>
        """

    content = f"""
     <p>
        Dear OM Team,<br><br>

        Please be advised the ONINVOICE promotion request has been implemented in Oracle.<br><br>

        Kindly review the attached document for the list of impacted orders.<br><br>

        If an order was booked prior to the implementation date of the AIF,
        please refresh the order accordingly.<br><br>
    </p>

    <table width="100%" cellpadding="8" cellspacing="0"
           style="border:1px solid #ddd; border-collapse:collapse;">

        <tr>
            <td width="50%" valign="top" style="border-right:1px solid #ddd;">
                <strong>Customer Details</strong><br><br>
                <table width="100%">
                    <tr style="background:#f4f6f8;">
                        <th align="left">Customer No</th>
                        <th align="left">Customer Name</th>
                    </tr>
                    {customers_html}
                </table>
            </td>
            <td width="50%" valign="top">
                <strong>Promotion Period</strong><br><br>
                <strong>Start Date:</strong> {aif.start_date}<br>
                <strong>End Date:</strong> {aif.end_date}
            </td>        
        </tr>

        <tr>
            <td colspan="2" style="border-top:1px solid #ddd;">
                <br>
                <strong>Product Details</strong><br><br>
                <table width="100%">
                    <tr style="background:#f4f6f8;">
                        <th align="left">Product Group</th>
                        <th align="left">Mercury Code</th>
                        <th align="left">Product Description</th>
                        <th align="right">ELP (EUR)</th>
                        <th align="right">Local ELP</th>
                        <th align="right">Promo ELP</th>
                    </tr>
                    {lines_html}
                </table>
            </td>
        </tr>

    </table>
    <br><br>
    Note:Please view attachment for the orders details.
    """
    return base_html_wrapper(content, REV_OPS_SIGNATURE)
