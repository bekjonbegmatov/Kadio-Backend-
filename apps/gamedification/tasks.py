from celery import shared_task
from django.utils import timezone
from .models import GiveawayModel
from apps.api_auth.models import UserModel
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_expired_giveaways():
    """
    Проверяет и завершает истекшие конкурсы
    """
    now = timezone.now()
    
    # Находим все активные конкурсы, которые должны быть завершены
    expired_giveaways = GiveawayModel.objects.filter(
        is_active=True,
        end_date__lte=now
    )
    
    completed_count = 0
    
    for giveaway in expired_giveaways:
        try:
            # Завершаем конкурс
            giveaway.end_giveaway()
            
            # Если есть победитель, начисляем ему призовой фонд
            if giveaway.winner:
                winner = giveaway.winner
                winner.diamonds += giveaway.prize_fond
                winner.save()
                
                logger.info(
                    f"Giveaway '{giveaway.title}' completed. "
                    f"Winner: {winner.email}, Prize: {giveaway.prize_fond} diamonds"
                )
            
            # Собранные средства от участников идут организатору
            if giveaway.collected_funds > 0:
                giveaway.organizator.diamonds += giveaway.collected_funds
                giveaway.organizator.save()
                logger.info(f"Organizer {giveaway.organizator.username} received {giveaway.collected_funds} diamonds from participants")
            else:
                logger.info(
                    f"Giveaway '{giveaway.title}' completed without participants"
                )
            
            completed_count += 1
            
        except Exception as e:
            logger.error(
                f"Error completing giveaway '{giveaway.title}': {str(e)}"
            )
    
    if completed_count > 0:
        logger.info(f"Completed {completed_count} expired giveaways")
    
    return f"Processed {completed_count} expired giveaways"

@shared_task
def end_giveaway_by_id(giveaway_id):
    """
    Завершает конкретный конкурс по ID
    """
    try:
        giveaway = GiveawayModel.objects.get(id=giveaway_id, is_active=True)
        giveaway.end_giveaway()
        
        if giveaway.winner:
            winner = giveaway.winner
            winner.diamonds += giveaway.prize_fond
            winner.save()
            
            logger.info(
                f"Giveaway '{giveaway.title}' manually completed. "
                f"Winner: {winner.email}, Prize: {giveaway.prize_fond} diamonds"
            )
            return f"Giveaway completed. Winner: {winner.email}"
        
        # Собранные средства от участников идут организатору
        if giveaway.collected_funds > 0:
            giveaway.organizator.diamonds += giveaway.collected_funds
            giveaway.organizator.save()
            logger.info(f"Organizer {giveaway.organizator.username} received {giveaway.collected_funds} diamonds from participants")
        else:
            logger.info(
                f"Giveaway '{giveaway.title}' completed without participants"
            )
            return "Giveaway completed without participants"
            
    except GiveawayModel.DoesNotExist:
        logger.error(f"Giveaway with ID {giveaway_id} not found or already completed")
        return "Giveaway not found or already completed"
    except Exception as e:
        logger.error(f"Error completing giveaway {giveaway_id}: {str(e)}")
        return f"Error: {str(e)}"