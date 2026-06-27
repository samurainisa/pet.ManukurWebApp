from django.db.utils import OperationalError, ProgrammingError

from users.models import UserProfile


def ensure_user_profile(user, role=UserProfile.Role.MASTER, client=None):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'role': role,
            'client': client,
        },
    )

    dirty = False
    if profile.role != role:
        profile.role = role
        dirty = True
    if client and profile.client_id != client.id:
        profile.client = client
        dirty = True

    if dirty and not created:
        profile.save(update_fields=['role', 'client', 'updated_at'])

    return profile


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    try:
        profile = getattr(user, 'profile', None)
    except (OperationalError, ProgrammingError):
        # DB might be not migrated yet; keep app usable for bootstrap commands.
        return UserProfile.Role.MASTER
    if profile:
        return profile.role

    if user.is_staff or user.is_superuser:
        ensure_user_profile(user, role=UserProfile.Role.MASTER)
        return UserProfile.Role.MASTER

    ensure_user_profile(user, role=UserProfile.Role.CLIENT)
    return UserProfile.Role.CLIENT
