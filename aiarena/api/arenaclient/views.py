import logging
from wsgiref.util import FileWrapper

from constance import config
from django.db import transaction
from django.db.models import Sum, F, Prefetch
from django.http import HttpResponse
from rest_framework import viewsets, serializers, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.fields import FileField, FloatField
from rest_framework.response import Response
from rest_framework.reverse import reverse

from aiarena import settings
from aiarena.api.arenaclient.exceptions import LadderDisabled
from aiarena.core.api import Bots, Matches
from aiarena.core.events import EVENT_MANAGER
from aiarena.core.events import MatchResultReceivedEvent
from aiarena.core.models import Bot, Map, Match, MatchParticipation, Result, SeasonParticipation
from aiarena.core.models.arena_client_status import ArenaClientStatus
from aiarena.core.permissions import IsArenaClientOrAdminUser, IsArenaClient
from aiarena.core.validators import validate_not_inf, validate_not_nan

logger = logging.getLogger(__name__)


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'
        ref_name = 'arenaclient'


class BotSerializer(serializers.ModelSerializer):
    # Dynamically regenerate bot_zip and bot_data urls to point to the API endpoints
    # Otherwise they will point to the front-end download views, which the API client won't
    # be authenticated for.
    bot_zip = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()

    def get_bot_zip(self, obj):
        p = MatchParticipation.objects.only('participant_number').get(bot=obj, match_id=self.root.instance.id)
        return reverse('match-download-zip', kwargs={'pk': self.root.instance.id, 'p_num': p.participant_number},
                       request=self.context['request'])

    def get_bot_data(self, obj):
        p = MatchParticipation.objects.select_related('bot')\
            .only('use_bot_data', 'bot__bot_data', 'participant_number')\
            .get(bot=obj, match_id=self.root.instance.id)
        if p.use_bot_data and p.bot.bot_data:
            return reverse('match-download-data', kwargs={'pk': self.root.instance.id, 'p_num': p.participant_number},
                           request=self.context['request'])
        else:
            return None

    class Meta:
        model = Bot
        fields = (
            'id', 'name', 'game_display_id', 'bot_zip', 'bot_zip_md5hash', 'bot_data', 'bot_data_md5hash', 'plays_race',
            'type')

        ref_name = "arenaclient"


class MatchSerializer(serializers.ModelSerializer):
    bot1 = BotSerializer(read_only=True)
    bot2 = BotSerializer(read_only=True)
    map = MapSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ('id', 'bot1', 'bot2', 'map')
        ref_name = 'arenaclient'


class MatchViewSet(viewsets.GenericViewSet):
    """
    MatchViewSet implements a POST method with no field requirements, which will create a match and return the JSON.
    No reading of models is implemented.
    """
    serializer_class = MatchSerializer
    permission_classes = [IsArenaClientOrAdminUser]
    throttle_scope = 'arenaclient'

    def create_new_match(self, requesting_user):
        match = Matches.start_next_match(requesting_user)

        match.bot1 = MatchParticipation.objects.select_related('bot').only('bot')\
            .get(match_id=match.id, participant_number=1).bot
        match.bot2 = MatchParticipation.objects.select_related('bot').only('bot')\
            .get(match_id=match.id, participant_number=2).bot

        serializer = self.get_serializer(match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        if config.LADDER_ENABLED:
            try:
                if config.REISSUE_UNFINISHED_MATCHES:
                    # Check for any unfinished matches assigned to this user. If any are present, return that.
                    unfinished_matches = Match.objects.only('id', 'map')\
                        .filter(started__isnull=False, assigned_to=request.user,
                                result__isnull=True).order_by(F('round_id').asc())
                    if unfinished_matches.count() > 0:
                        match = unfinished_matches[0]  # todo: re-set started time?

                        match.bot1 = MatchParticipation.objects.select_related('bot').only('bot')\
                            .get(match_id=match.id, participant_number=1).bot
                        match.bot2 = MatchParticipation.objects.select_related('bot').only('bot')\
                            .get(match_id=match.id, participant_number=2).bot

                        serializer = self.get_serializer(match)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return self.create_new_match(request.user)
                else:
                    return self.create_new_match(request.user)
            except Exception as e:
                logger.exception("Exception while processing request for match.")
                raise
        else:
            raise LadderDisabled()

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=['GET'], name='Download a participant\'s zip file', url_path='(?P<p_num>\d+)/zip')
    def download_zip(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs['pk'], participant_number=kwargs['p_num'])
        response = HttpResponse(FileWrapper(p.bot.bot_zip), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename="{0}.zip"'.format(p.bot.name)
        return response

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=['GET'], name='Download a participant\'s data file', url_path='(?P<p_num>\d+)/data')
    def download_data(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs['pk'], participant_number=kwargs['p_num'])
        response = HttpResponse(FileWrapper(p.bot.bot_data), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename="{0}_data.zip"'.format(p.bot.name)
        return response


class SubmitResultResultSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        instance = SubmitResultResultSerializer.Meta.model(**attrs)
        instance.clean()  # enforce model validation
        return attrs

    class Meta:
        model = Result
        fields = 'match', 'type', 'replay_file', 'game_steps', 'submitted_by', 'arenaclient_log'


class SubmitResultBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = 'bot_data',


class SubmitResultParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipation
        fields = 'avg_step_time', 'match_log', 'result', 'result_cause'


# Front facing serializer used by the view. Combines the other serializers together.
class SubmitResultCombinedSerializer(serializers.Serializer):
    # Result
    match = serializers.IntegerField()
    type = serializers.ChoiceField(choices=Result.TYPES)
    replay_file = serializers.FileField(required=False)
    game_steps = serializers.IntegerField()
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    arenaclient_log = FileField(required=False)
    # Bot
    bot1_data = FileField(required=False)
    bot2_data = FileField(required=False)
    # Participant
    bot1_log = FileField(required=False)
    bot2_log = FileField(required=False)
    bot1_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])
    bot2_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """
    serializer_class = SubmitResultCombinedSerializer
    permission_classes = [IsArenaClientOrAdminUser]
    # Don't throttle result submissions - we can never have "too many" result submissions.
    # throttle_scope = 'arenaclient'

    def create(self, request, *args, **kwargs):
        if config.LADDER_ENABLED:
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                match_id = serializer.validated_data['match']

                if config.DEBUG_LOGGING_ENABLED:
                    logger.info(f"Result submission. "
                                 f"match: {serializer.validated_data.get('match')} "
                                 f"type: {serializer.validated_data.get('type')} "
                                 f"replay_file: {serializer.validated_data.get('replay_file')} "
                                 f"game_steps: {serializer.validated_data.get('game_steps')} "
                                 f"submitted_by: {serializer.validated_data.get('submitted_by')} "
                                 f"arenaclient_log: {serializer.validated_data.get('arenaclient_log')} "
                                 f"bot1_avg_step_time: {serializer.validated_data.get('bot1_avg_step_time')} "
                                 f"bot1_log: {serializer.validated_data.get('bot1_log')} "
                                 f"bot1_data: {serializer.validated_data.get('bot1_data')} "
                                 f"bot2_avg_step_time: {serializer.validated_data.get('bot2_avg_step_time')} "
                                 f"bot2_log: {serializer.validated_data.get('bot2_log')} "
                                 f"bot2_data: {serializer.validated_data.get('bot2_data')} "
                                 )

                with transaction.atomic():
                    match = Match.objects.prefetch_related(
                        Prefetch('matchparticipation_set', MatchParticipation.objects.all().select_related('bot'))
                    ).get(id=match_id)

                    # validate result
                    result = SubmitResultResultSerializer(data={'match': match_id,
                                                                'type': serializer.validated_data['type'],
                                                                'replay_file': serializer.validated_data.get('replay_file'),
                                                                'game_steps': serializer.validated_data['game_steps'],
                                                                'submitted_by': serializer.validated_data['submitted_by'].pk,
                                                                'arenaclient_log': serializer.validated_data.get(
                                                                'arenaclient_log')})
                    result.is_valid(raise_exception=True)

                    # validate participants
                    p1_instance = match.matchparticipation_set.get(participant_number=1)
                    result_cause = p1_instance.calculate_result_cause(serializer.validated_data['type'])
                    participant1 = SubmitResultParticipationSerializer(instance=p1_instance, data={
                        'avg_step_time': serializer.validated_data.get('bot1_avg_step_time'),
                        'match_log': serializer.validated_data.get('bot1_log'),
                        'result': p1_instance.calculate_relative_result(serializer.validated_data['type']),
                        'result_cause': result_cause},
                                                                       partial=True)
                    participant1.is_valid(raise_exception=True)

                    p2_instance = match.matchparticipation_set.get(participant_number=2)
                    participant2 = SubmitResultParticipationSerializer(instance=p2_instance, data={
                        'avg_step_time': serializer.validated_data.get('bot2_avg_step_time'),
                        'match_log': serializer.validated_data.get('bot2_log'),
                        'result': p2_instance.calculate_relative_result(serializer.validated_data['type']),
                        'result_cause': result_cause},
                                                                       partial=True)
                    participant2.is_valid(raise_exception=True)

                    # validate bots

                    if not p1_instance.bot.is_in_match(match_id):
                        logger.warning(f"A result was submitted for match {match_id}, "
                                       f"which Bot {p1_instance.bot.name} isn't currently in!")
                        raise APIException('Unable to log result: Bot {0} is not currently in this match!'
                                           .format(p1_instance.bot.name))

                    if not p2_instance.bot.is_in_match(match_id):
                        logger.warning(f"A result was submitted for match {match_id}, "
                                       f"which Bot {p2_instance.bot.name} isn't currently in!")
                        raise APIException('Unable to log result: Bot {0} is not currently in this match!'
                                           .format(p2_instance.bot.name))

                    bot1 = None
                    bot2 = None

                    match_is_requested = match.is_requested
                    # should we update the bot data?
                    if p1_instance.use_bot_data and p1_instance.update_bot_data and not match_is_requested:
                        bot1_data = serializer.validated_data.get('bot1_data')
                        # if we set the bot data key to anything, it will overwrite the existing bot data
                        # so only include bot1_data if it isn't none
                        # Also don't update bot data if it's a requested match.
                        if bot1_data is not None and not match_is_requested:
                            bot1_dict = {'bot_data': bot1_data}
                            bot1 = SubmitResultBotSerializer(instance=p1_instance.bot,
                                                             data=bot1_dict, partial=True)
                            bot1.is_valid(raise_exception=True)

                    if p2_instance.use_bot_data and p2_instance.update_bot_data and not match_is_requested:
                        bot2_data = serializer.validated_data.get('bot2_data')
                        # if we set the bot data key to anything, it will overwrite the existing bot data
                        # so only include bot2_data if it isn't none
                        # Also don't update bot data if it's a requested match.
                        if bot2_data is not None and not match_is_requested:
                            bot2_dict = {'bot_data': bot2_data}
                            bot2 = SubmitResultBotSerializer(instance=p2_instance.bot,
                                                             data=bot2_dict, partial=True)
                            bot2.is_valid(raise_exception=True)

                    # save models
                    result = result.save()
                    participant1 = participant1.save()
                    participant2 = participant2.save()
                    # save these after the others so if there's a validation error,
                    # then the bot data files don't need reverting to match their hashes.
                    # This could probably be done more fool-proof by actually rolling back the files on a transaction fail.
                    if bot1 is not None:
                        bot1.save()
                    if bot2 is not None:
                        bot2.save()

                    # Only do these actions if the match is part of a round
                    if result.match.round is not None:
                        result.match.round.update_if_completed()

                        # Update and record ELO figures
                        p1_initial_elo, p2_initial_elo = result.get_initial_elos
                        result.adjust_elo()

                        initial_elo_sum = p1_initial_elo + p2_initial_elo

                        # Calculate the change in ELO
                        # the bot elos have changed so refresh them
                        # todo: instead of having to refresh, return data from adjust_elo and apply it here
                        sp1, sp2 = result.get_season_participants
                        participant1.resultant_elo = sp1.elo
                        participant2.resultant_elo = sp2.elo
                        participant1.elo_change = participant1.resultant_elo - p1_initial_elo
                        participant2.elo_change = participant2.resultant_elo - p2_initial_elo
                        participant1.save()
                        participant2.save()

                        resultant_elo_sum = participant1.resultant_elo + participant2.resultant_elo
                        if initial_elo_sum != resultant_elo_sum:
                            logger.critical(f"Initial and resultant ELO sum mismatch: "
                                            f"Result {result.id}. "
                                            f"initial_elo_sum: {initial_elo_sum}. "
                                            f"resultant_elo_sum: {resultant_elo_sum}. "
                                            f"participant1.elo_change: {participant1.elo_change}. "
                                            f"participant2.elo_change: {participant2.elo_change}")

                        if config.ENABLE_ELO_SANITY_CHECK:
                            if config.DEBUG_LOGGING_ENABLED:
                                logger.info("ENABLE_ELO_SANITY_CHECK enabled. Performing check.")

                            # test here to check ELO total and ensure no corruption
                            match_season = result.match.round.season
                            expected_elo_sum = settings.ELO_START_VALUE * SeasonParticipation.objects.filter(season=match_season).count()
                            actual_elo_sum = SeasonParticipation.objects.filter(season=match_season).aggregate(
                                Sum('elo'))

                            if actual_elo_sum['elo__sum'] != expected_elo_sum:
                                logger.critical(
                                    "ELO sum of {0} did not match expected value of {1} upon submission of result {2}".format(
                                        actual_elo_sum['elo__sum'], expected_elo_sum, result.id))
                            elif config.DEBUG_LOGGING_ENABLED:
                                logger.info("ENABLE_ELO_SANITY_CHECK passed!")

                        elif config.DEBUG_LOGGING_ENABLED:
                            logger.info("ENABLE_ELO_SANITY_CHECK disabled. Skipping check.")

                        if result.is_crash_or_timeout:
                            run_consecutive_crashes_check(result.get_causing_participant_of_crash_or_timeout_result)

                EVENT_MANAGER.broadcast_event(MatchResultReceivedEvent(result))

                headers = self.get_success_headers(serializer.data)
                return Response({'result_id': result.id}, status=status.HTTP_201_CREATED, headers=headers)
            except Exception as e:
                logger.exception("Exception while processing result submission")
                raise
        else:
            raise LadderDisabled()

    # todo: use a model form
    # todo: avoid results being logged against matches not owned by the submitter


class SetArenaClientStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArenaClientStatus
        fields = ('status',)


class SetArenaClientStatusViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    SetArenaClientStatusViewSet implements a POST method to record an arena client's status.
    No reading of models is implemented.
    """
    serializer_class = SetArenaClientStatusSerializer
    permission_classes = [IsArenaClient]

    def perform_create(self, serializer):
        serializer.save(arenaclient=self.request.user.arenaclient)


def run_consecutive_crashes_check(triggering_participant: MatchParticipation):
    """
    Checks to see whether the last X results for a participant are crashes and, if so, disables the bot
    and sends an alert to the bot author
    :param triggering_participant: The participant who triggered this check and whose bot we should run the check for.
    :return:
    """

    if config.BOT_CONSECUTIVE_CRASH_LIMIT < 1:
        return  # Check is disabled

    if not triggering_participant.bot.active:
        return  # No use running the check - bot is already inactive.

    # Get recent match participation records for this bot
    recent_participations = MatchParticipation.objects.filter(bot=triggering_participant.bot,
                                                              match__result__isnull=False).order_by(
        '-match__result__created')[:config.BOT_CONSECUTIVE_CRASH_LIMIT]

    # if there's not enough participations yet, then exit without action
    if recent_participations.count() < config.BOT_CONSECUTIVE_CRASH_LIMIT:
        return

    # if any of the previous results weren't a crash, then exit without action
    for recent_participation in recent_participations:
        if not recent_participation.crashed:
            return

    # If we get to here, all the results were crashes, so take action
    Bots.disable_and_send_crash_alert(triggering_participant.bot)
