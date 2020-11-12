from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from aiarena.core.models import Result


class Command(BaseCommand):
    help = "Cleanup and remove old replay files."

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
        self.stdout.write('Cleaning up replays starting from {0} days into the past...'.format(days))
        self.stdout.write('Cleaned up {0} replays.'.format(self.cleanup_replays(days, options['verbose'])))

    def cleanup_replays(self, days, verbose):
        self.stdout.write(f'Gathering records to clean...')
        results = Result.objects.exclude(replay_file='').filter(created__lt=timezone.now() - timedelta(days=days))
        self.stdout.write(f'{results.count()} records gathered.')
        for result in results:
            with transaction.atomic():
                result.lock_me()
                result.replay_file_has_been_cleaned = True
                result.replay_file.delete()
                result.save()
                if verbose:
                    self.stdout.write(f'Match {result.match_id} replay file deleted.')
        return results.count()
