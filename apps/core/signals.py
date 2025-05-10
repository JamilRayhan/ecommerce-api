from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def invalidate_cache(sender, instance, **kwargs):
    """
    Invalidate cache for the given model instance
    """
    model_name = sender.__name__.lower()
    cache_key = f"{model_name}_{instance.pk}"
    cache.delete(cache_key)
    
    # Also invalidate list cache
    list_cache_key = f"{model_name}_list"
    cache.delete(list_cache_key)
    
    logger.debug(f"Cache invalidated for {cache_key} and {list_cache_key}")


def register_model_signals(model):
    """
    Register signals for the given model
    """
    post_save.connect(invalidate_cache, sender=model)
    post_delete.connect(invalidate_cache, sender=model)
