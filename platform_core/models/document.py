from django.db import models
from django.utils import timezone
from django.db import transaction
from .base import OrgScopedModel


class DocumentStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    POSTED = 'posted', 'Проведён'
    CANCELLED = 'cancelled', 'Отменён'


class Document(OrgScopedModel):
    """
    Абстрактный Документ.

    Ключевое свойство — проведение (posting):
    - Черновик: данные не влияют на регистры
    - Проведён: движения записаны в регистры, документ защищён от изменений
    - Отменён: движения откатываются

    Модули переопределяют _make_movements() и _reverse_movements().
    """
    number = models.CharField(max_length=50, blank=True, verbose_name='Номер')
    date = models.DateField(verbose_name='Дата')
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
        db_index=True,
        verbose_name='Статус',
    )
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата проведения')
    posted_by = models.ForeignKey(
        'platform_core.Employee',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Провёл',
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        abstract = True
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.__class__.__name__} №{self.number} от {self.date}'

    @property
    def is_posted(self):
        return self.status == DocumentStatus.POSTED

    @transaction.atomic
    def post(self, user):
        """Провести документ — записать движения в регистры."""
        if self.status == DocumentStatus.POSTED:
            raise ValueError('Документ уже проведён')
        if self.status == DocumentStatus.CANCELLED:
            raise ValueError('Отменённый документ нельзя провести')
        self._make_movements()
        self.status = DocumentStatus.POSTED
        self.posted_at = timezone.now()
        self.posted_by = user
        self.save()

    @transaction.atomic
    def unpost(self, user):
        """Отменить проведение — откатить движения в регистрах."""
        if self.status != DocumentStatus.POSTED:
            raise ValueError('Документ не проведён')
        self._reverse_movements()
        self.status = DocumentStatus.DRAFT
        self.posted_at = None
        self.posted_by = None
        self.save()

    def _make_movements(self):
        """Переопределить в модуле: создать записи в регистрах."""
        pass

    def _reverse_movements(self):
        """Переопределить в модуле: удалить записи в регистрах по этому документу."""
        pass
