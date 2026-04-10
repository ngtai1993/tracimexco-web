from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.appearance.models import ColorToken, MediaAsset
from apps.appearance.services.appearance_cache_service import AppearanceCacheService


@receiver(post_save, sender=ColorToken)
def invalidate_on_token_save(sender, instance, **kwargs):
    AppearanceCacheService.invalidate_config()


@receiver(post_delete, sender=ColorToken)
def invalidate_on_token_delete(sender, instance, **kwargs):
    AppearanceCacheService.invalidate_config()


@receiver(post_save, sender=MediaAsset)
def invalidate_on_asset_save(sender, instance, **kwargs):
    AppearanceCacheService.invalidate_config()


@receiver(post_delete, sender=MediaAsset)
def invalidate_on_asset_delete(sender, instance, **kwargs):
    AppearanceCacheService.invalidate_config()
