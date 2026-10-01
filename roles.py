from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from common.roles import create_default_role
from common.models import AccessProvider

NSO_USER = "AIF App NSO User"
PSBD_TEAM_USER = "AIF App PSBD User"
SALES_OPS_USER = "AIF App Sales Ops User"
ADMIN_ROLE = "AIF App Admin"
USER_ROLES = [NSO_USER, PSBD_TEAM_USER, SALES_OPS_USER]
ROLES = USER_ROLES + [ADMIN_ROLE]


def check_roles():
    """
    This function checks if all the roles in the ROLES list are present in the Group model.
    """
    all_roles_present: int = 0
    for role_name in ROLES:
        all_roles_present += int(Group.objects.filter(name=role_name).exists())

    return all_roles_present == len(ROLES)


def create_admin_role():
    """
    This function creates admin role with permission.
    """
    role_group, created = Group.objects.get_or_create(name=ADMIN_ROLE)
    print("create_admin_role")
    if created:
        for modelname in []:
            content_type = ContentType.objects.get_for_model(modelname)
            permissions = Permission.objects.filter(content_type=content_type)
            for permission in permissions:
                role_group.permissions.add(permission)


def create_user_roles():
    """
    This function creates user roles with permission.
    """
    for role_name in USER_ROLES:
        role_group, created = Group.objects.get_or_create(name=role_name)
        print("create_user_roles")
        if created:
            # view permissions
            for modelname in []:
                content_type = ContentType.objects.get_for_model(modelname)
                permissions = Permission.objects.filter(content_type=content_type)
                for permission in permissions:
                    if "view" in permission.codename:
                        role_group.permissions.add(permission)


def create_access_providers():
    for user_role_name in USER_ROLES:
        AccessProvider.objects.create(
            provider_group=Group.objects.get(name=ADMIN_ROLE),
            access_to_group=Group.objects.get(name=user_role_name),
        )


def create_roles_if_absent():
    create_default_role()
    if not check_roles():
        create_admin_role()
        create_user_roles()
        create_access_providers()


def has_access_to_app(user, roles):
    if user.groups.filter(name__in=roles).exists():
        return True

    return False
