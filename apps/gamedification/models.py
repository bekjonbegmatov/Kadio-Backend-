from django.db import models
from apps.api_auth.models import UserModel

class GiveawayModel(models.Model):
    organizator = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='giveaways'
    )
    participants = models.ManyToManyField(
        UserModel,
        related_name='participated_giveaways'
    )

    title = models.CharField(
        max_length=255,
        verbose_name='Название розыгрыша'
    )
    description = models.TextField(
        verbose_name='Описание розыгрыша'
    )
    prize_fond = models.PositiveIntegerField(
        verbose_name='Сумма приза'
    )
    
    start_date = models.DateTimeField(
        verbose_name='Дата начала розыгрыша'
    )
    end_date = models.DateTimeField(
        verbose_name='Дата окончания розыгрыша'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    winner = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_giveaways'
    )
    
    giveaway_cost = models.PositiveIntegerField(
        verbose_name='Стоимость участия'
    )
    
    collected_funds = models.PositiveIntegerField(
        default=0,
        verbose_name='Собранные средства от участников'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_sum(self, sum: int):
        self.collected_funds += sum
        self.save()
    
    def __random_get_winner(self):
        return self.participants.order_by('?').first()
    
    def end_giveaway(self):
        self.is_active = False
        self.winner = self.__random_get_winner()
        
        # Если есть победитель, начисляем ему призовой фонд в diamonds
        if self.winner:
            self.winner.diamonds += self.prize_fond
            self.winner.save()
        
        # Собранные средства от участников идут организатору
        if self.collected_funds > 0:
            self.organizator.diamonds += self.collected_funds
            self.organizator.save()
        
        self.save()
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Giveaway'
        verbose_name_plural = 'Giveaways'
        ordering = ['-start_date']
        