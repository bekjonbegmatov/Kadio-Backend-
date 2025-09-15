from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.gamedification.models import GiveawayModel
from apps.gamedification.tasks import check_expired_giveaways

class Command(BaseCommand):
    help = 'Check and complete expired giveaways'

    def add_arguments(self, parser):
        parser.add_argument(
            '--giveaway-id',
            type=int,
            help='Complete specific giveaway by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        if options['giveaway_id']:
            self.complete_specific_giveaway(options['giveaway_id'], options['dry_run'])
        else:
            self.check_all_expired_giveaways(options['dry_run'])

    def complete_specific_giveaway(self, giveaway_id, dry_run):
        try:
            giveaway = GiveawayModel.objects.get(id=giveaway_id)
            
            if not giveaway.is_active:
                self.stdout.write(
                    self.style.WARNING(f'Giveaway "{giveaway.title}" is already completed')
                )
                return
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Would complete giveaway "{giveaway.title}" '
                        f'with {giveaway.participants.count()} participants'
                    )
                )
            else:
                old_winner = giveaway.winner
                giveaway.end_giveaway()
                
                if giveaway.winner:
                    winner = giveaway.winner
                    winner.coins += giveaway.prize_fond
                    winner.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Completed giveaway "{giveaway.title}". '
                            f'Winner: {winner.email}, Prize: {giveaway.prize_fond} coins'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Completed giveaway "{giveaway.title}" without participants'
                        )
                    )
                    
        except GiveawayModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Giveaway with ID {giveaway_id} not found')
            )

    def check_all_expired_giveaways(self, dry_run):
        now = timezone.now()
        
        expired_giveaways = GiveawayModel.objects.filter(
            is_active=True,
            end_date__lte=now
        )
        
        if not expired_giveaways.exists():
            self.stdout.write(
                self.style.SUCCESS('No expired giveaways found')
            )
            return
        
        self.stdout.write(
            f'Found {expired_giveaways.count()} expired giveaways:'
        )
        
        for giveaway in expired_giveaways:
            participants_count = giveaway.participants.count()
            
            if dry_run:
                self.stdout.write(
                    f'  - "{giveaway.title}" (ID: {giveaway.id}) '
                    f'with {participants_count} participants '
                    f'(ended: {giveaway.end_date})'
                )
            else:
                giveaway.end_giveaway()
                
                if giveaway.winner:
                    winner = giveaway.winner
                    winner.coins += giveaway.prize_fond
                    winner.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Completed "{giveaway.title}". '
                            f'Winner: {winner.email}, Prize: {giveaway.prize_fond} coins'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ✓ Completed "{giveaway.title}" without participants'
                        )
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully completed {expired_giveaways.count()} giveaways'
                )
            )