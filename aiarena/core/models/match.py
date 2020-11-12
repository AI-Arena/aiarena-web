import logging
from enum import Enum

from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe


from .map import Map
from .mixins import LockableModelMixin, RandomManagerMixin
from .round import Round
from .user import User

logger = logging.getLogger(__name__)


# todo: structure for separate ladder types
class Match(models.Model, LockableModelMixin, RandomManagerMixin):
    """ Represents a match between 2 bots. Usually this is within the context of a round, but doesn't have to be. """
    map = models.ForeignKey(Map, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    started = models.DateTimeField(blank=True, null=True, editable=False, db_index=True)
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True,
                                     related_name='assigned_matches')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, blank=True, null=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='requested_matches')
    require_trusted_arenaclient = models.BooleanField(default=True)
    """Whether this match should require it be run on a trusted arena client"""

    def __str__(self):
        return self.id.__str__()

    @property
    def participant1(self):
        return self.matchparticipation_set.get(participant_number=1)

    @property
    def participant2(self):
        return self.matchparticipation_set.get(participant_number=2)

    @property
    def is_requested(self):
        return self.requested_by is not None

    @staticmethod
    def create(round, map, bot1, bot2, requested_by=None,
               bot1_use_data=None, bot1_update_data=None,
               bot2_use_data=None, bot2_update_data=None):
        with transaction.atomic():
            if bot1_use_data is None:
                bot1_use_data = bot1.bot_data_enabled
            if bot1_update_data is None:
                bot1_update_data = bot1.bot_data_enabled
            if bot2_use_data is None:
                bot2_use_data = bot2.bot_data_enabled
            if bot2_update_data is None:
                bot2_update_data = bot2.bot_data_enabled

            match = Match.objects.create(map=map, round=round, requested_by=requested_by)
            # create match participations
            from .match_participation import MatchParticipation  # avoid circular reference
            MatchParticipation.objects.create(match=match, participant_number=1, bot=bot1,
                                              use_bot_data=bot1_use_data, update_bot_data=bot1_update_data)
            MatchParticipation.objects.create(match=match, participant_number=2, bot=bot2,
                                              use_bot_data=bot2_use_data, update_bot_data=bot2_update_data)

            return match

    class CancelResult(Enum):
        SUCCESS = 1
        MATCH_DOES_NOT_EXIST = 3
        RESULT_ALREADY_EXISTS = 2

    def cancel(self, requesting_user):
        from . import Result
        with transaction.atomic():
            try:
                # do this to lock the record
                # select_related() for the round data
                match = Match.objects.select_related('round').select_for_update().get(pk=self.id)
            except Match.DoesNotExist:
                return Match.CancelResult.MATCH_DOES_NOT_EXIST  # should basically not happen, but just in case

            if Result.objects.filter(match=match).count() > 0:
                return Match.CancelResult.RESULT_ALREADY_EXISTS

            Result.objects.create(match=match, type='MatchCancelled', game_steps=0, submitted_by=requesting_user)

            if not match.started:
                match.started = timezone.now()
                match.save()

            if match.round is not None:
                match.round.update_if_completed()


    def get_absolute_url(self):
        return reverse('match', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')
