from django.conf import settings

from aiarena.core.models import User

BENEFITS_MAP = {
    "none": {
        "active_bots_limit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER,
        "requested_matches_limit": settings.MATCH_REQUEST_LIMIT_FREE_TIER,
        "can_request_match_via_api": False,
    },
    "bronze": {
        "active_bots_limit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_BRONZE_TIER,
        "requested_matches_limit": settings.MATCH_REQUEST_LIMIT_BRONZE_TIER,
        "can_request_match_via_api": True,
    },
    "silver": {
        "active_bots_limit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_SILVER_TIER,
        "requested_matches_limit": settings.MATCH_REQUEST_LIMIT_SILVER_TIER,
        "can_request_match_via_api": True,
    },
    "gold": {
        "active_bots_limit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_GOLD_TIER,
        "requested_matches_limit": settings.MATCH_REQUEST_LIMIT_GOLD_TIER,
        "can_request_match_via_api": True,
    },
    "platinum": {
        "active_bots_limit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_PLATINUM_TIER,
        "requested_matches_limit": settings.MATCH_REQUEST_LIMIT_PLATINUM_TIER,
        "can_request_match_via_api": True,
    },
    "diamond": {
        "active_bots_limit": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DIAMOND_TIER,
        "requested_matches_limit": settings.MATCH_REQUEST_LIMIT_DIAMOND_TIER,
        "can_request_match_via_api": True,
    },
}

class SupporterBenefits:
    @staticmethod
    def get_active_bots_limit(user: User):
        limit = BENEFITS_MAP[user.patreon_level]["active_bots_limit"]
        if limit is None:
            return None  # no limit
        else:
            return limit + user.extra_active_competition_participations

    @staticmethod
    def get_requested_matches_limit(user: User):
        return BENEFITS_MAP[user.patreon_level]["requested_matches_limit"] + user.extra_periodic_match_requests

    @staticmethod
    def get_active_competition_participations_limit_display(user: User):
        limit = SupporterBenefits.get_active_bots_limit(user)
        return "unlimited" if limit is None else limit

    @staticmethod
    def can_request_match_via_api(user: User) -> (bool, str):
        allowed = BENEFITS_MAP[user.patreon_level]["can_request_match_via_api"]
        return allowed, "You need to be a supporter to use this feature." if not allowed else None
