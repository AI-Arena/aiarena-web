from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import Match


class Command(BaseCommand):
    help = 'Registers a MatchCancelled result for all current matches.'

    def add_arguments(self, parser):
        parser.add_argument('match_ids', nargs='+', type=int, help="A space separated list of match ids to cancel.")

    def handle(self, *args, **options):
        for match_id in options['match_ids']:
            try:
                with transaction.atomic():
                    match = Match.objects.select_for_update().get(pk=match_id)
                    result = match.cancel(None)
                    if result == Match.CancelResult.MATCH_DOES_NOT_EXIST:  # should basically not happen, but just in case
                        raise CommandError('Match "%s" does not exist' % match_id)
                    elif result == Match.CancelResult.RESULT_ALREADY_EXISTS:
                        raise CommandError('A result already exists for match "%s"' % match_id)

                self.stdout.write(self.style.SUCCESS('Successfully marked match "%s" with MatchCancelled' % match_id))
            except Match.DoesNotExist:
                raise CommandError('Match "%s" does not exist' % match_id)
