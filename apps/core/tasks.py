from celery import shared_task
import logging

logger = logging.getLogger('apps')

@shared_task
def sample_task(name, count=1):
    """
    A sample task to demonstrate Celery functionality.
    """
    logger.info(f"Running sample task with name: {name}, count: {count}")
    for i in range(count):
        logger.info(f"Sample task {name} - iteration {i+1}/{count}")
    return f"Completed {count} iterations for task {name}"
