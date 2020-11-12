from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from aiarena.core.models import MatchParticipation


class Command(BaseCommand):
    help = "Cleanup and remove old match logfiles."

    _DEFAULT_DAYS_LOOKBACK = 30

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int,
                            help="Number of days into the past to start cleaning from. Default is {0}.".format(
                                self._DEFAULT_DAYS_LOOKBACK))
        parser.add_argument('--verbose', action='store_true', help="Output information with each action.")

    def handle(self, *args, **options):
        if options['days'] is not None:
            days = options['days']
        else:
            days = self._DEFAULT_DAYS_LOOKBACK
        self.stdout.write('Cleaning up match logfiles starting from {0} days into the past...'.format(days))
        self.stdout.write('Cleaned up {0} logfiles.'.format(self.cleanup_logfiles(days, options['verbose'])))

    def cleanup_logfiles(self, days, verbose):
        self.stdout.write(f'Gathering records to clean...')
        participants = MatchParticipation.objects.exclude(match_log='')\
            .filter(match__result__created__lt=timezone.now() - timedelta(days=days))
        self.stdout.write(f'{participants.count()} records gathered.')
        for participant in participants:
            with transaction.atomic():
                participant.lock_me()
                participant.match_log_has_been_cleaned = True
                participant.match_log.delete()
                participant.save()
                if verbose:
                    self.stdout.write(f'Participant {participant.id} match log deleted.')
        return participants.count()
