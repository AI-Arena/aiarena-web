import logging

from django.db.models import Max

from aiarena.core.models import Season, SeasonParticipation, Round

logger = logging.getLogger(__name__)


class Ladders:
    @staticmethod
    def get_season_ranked_participants(season: Season, amount=None):
        # only return SeasonParticipations that are included in the most recent round
        last_round = Ladders.get_most_recent_round(season)
        limit = f" LIMIT {amount}" if amount else ""
        query = "select distinct csp.id, elo, bot_id, win_perc, slug " \
                "from core_seasonparticipation csp " \
                "where season_id = %s and bot_id in (" \
                "select cmp.bot_id " \
                "from core_match cm " \
                "join core_matchparticipation cmp on cm.id = cmp.match_id " \
                "where cm.round_id = %s)" \
                " order by csp.elo desc " + limit
        return SeasonParticipation.objects.raw(query, (season.id, last_round.id,))

    @staticmethod
    def get_most_recent_round(season: Season):
        return Round.objects.only('id').get(season=season, number=Round.objects.filter(season=season).aggregate(Max('number'))['number__max'])
