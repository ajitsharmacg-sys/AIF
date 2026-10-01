from collections import defaultdict
from aif.roles import (
    NSO_USER,
    PSBD_TEAM_USER,
    SALES_OPS_USER,
    ADMIN_ROLE,
)
from aif.models import (
    AifStatusChoices,
    AifLineStatusChoices,
)

AIF_STATUS_GRAPH = {
    AifStatusChoices.DRAFT: [
        AifStatusChoices.PLANNED,
    ],

    AifStatusChoices.PLANNED: [
        AifStatusChoices.COMMERCIALLY_APPROVED,
        AifStatusChoices.INVALID,
    ],

    AifStatusChoices.COMMERCIALLY_APPROVED: [
        AifStatusChoices.AWAITING_VALIDATION,
        AifStatusChoices.INVALID,
    ],

    AifStatusChoices.AWAITING_VALIDATION: [
        AifStatusChoices.CLOSED,
        AifStatusChoices.INVALID,
    ],

    AifStatusChoices.CLOSED: [],

    AifStatusChoices.INVALID: [
        AifStatusChoices.DRAFT,
    ],
}

AIF_LINE_STATUS_GRAPH = {
    AifLineStatusChoices.DRAFT: [
        AifLineStatusChoices.AWAITING_APPROVAL,
    ],

    AifLineStatusChoices.AWAITING_APPROVAL: [
        AifLineStatusChoices.APPROVED,
        AifLineStatusChoices.REJECTED,
    ],

    AifLineStatusChoices.APPROVED: [
        AifLineStatusChoices.AWAITING_VALIDATION,
        AifLineStatusChoices.REJECTED,
    ],

    AifLineStatusChoices.AWAITING_VALIDATION: [
        AifLineStatusChoices.CLOSED,
        AifLineStatusChoices.REJECTED,
    ],

    AifLineStatusChoices.CLOSED: [],

    AifLineStatusChoices.REJECTED: [
        AifLineStatusChoices.DRAFT,
    ],
}

AIF_STATUS_TO_ROLE = {
    AifStatusChoices.DRAFT: [
        NSO_USER,
        ADMIN_ROLE,
    ],

    AifStatusChoices.PLANNED: [
        PSBD_TEAM_USER,
        ADMIN_ROLE,
    ],

    AifStatusChoices.COMMERCIALLY_APPROVED: [
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],

    AifStatusChoices.AWAITING_VALIDATION: [
        NSO_USER,
        ADMIN_ROLE,
    ],

    AifStatusChoices.CLOSED: [
        NSO_USER,
        ADMIN_ROLE,
    ],

    AifStatusChoices.INVALID: [
        NSO_USER,
        PSBD_TEAM_USER,
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],
}

LINE_STATUS_TO_ROLE = {
    AifLineStatusChoices.DRAFT: [
        NSO_USER,
        ADMIN_ROLE,
    ],

    AifLineStatusChoices.AWAITING_APPROVAL: [
        PSBD_TEAM_USER,
        ADMIN_ROLE,
    ],

    AifLineStatusChoices.APPROVED: [
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],

    AifLineStatusChoices.AWAITING_VALIDATION: [
        NSO_USER,
        ADMIN_ROLE,
    ],

    AifLineStatusChoices.CLOSED: [
        NSO_USER,
        ADMIN_ROLE,
    ],

    AifLineStatusChoices.REJECTED: [
        NSO_USER,
        PSBD_TEAM_USER,
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],
}

def build_role_to_status_mapping(status_to_role):
    role_to_status = defaultdict(list)

    for status, roles in status_to_role.items():
        for role in roles:
            role_to_status[role].append(status)

    return dict(role_to_status)


ROLE_TO_AIF_STATUS = build_role_to_status_mapping(
    AIF_STATUS_TO_ROLE
)

ROLE_TO_LINE_STATUS = build_role_to_status_mapping(
    LINE_STATUS_TO_ROLE
)


def get_available_transitions(
    current_status,
    status_graph,
):
    return status_graph.get(
        current_status,
        [],
    )


def is_valid_transition(
    current_status,
    new_status,
    status_graph,
):
    allowed_statuses = get_available_transitions(
        current_status=current_status,
        status_graph=status_graph,
    )

    return new_status in allowed_statuses


def is_valid_aif_transition(
    current_status,
    new_status,
):
    return is_valid_transition(
        current_status=current_status,
        new_status=new_status,
        status_graph=AIF_STATUS_GRAPH,
    )


def is_valid_line_transition(
    current_status,
    new_status,
):
    return is_valid_transition(
        current_status=current_status,
        new_status=new_status,
        status_graph=AIF_LINE_STATUS_GRAPH,
    )


def is_role_allowed_for_status(
    user_roles,
    target_status,
    status_to_role,
):
    allowed_roles = status_to_role.get(
        target_status,
        []
    )

    return bool(
        set(user_roles).intersection(
            allowed_roles
        )
    )

def is_role_allowed_for_aif_status(
    user_roles,
    target_status,
):
    return is_role_allowed_for_status(
        user_roles=user_roles,
        target_status=target_status,
        status_to_role=AIF_STATUS_TO_ROLE,
    )


def is_role_allowed_for_line_status(
    user_roles,
    target_status,
):
    return is_role_allowed_for_status(
        user_roles=user_roles,
        target_status=target_status,
        status_to_role=LINE_STATUS_TO_ROLE,
    )
