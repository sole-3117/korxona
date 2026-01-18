import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_action(user_id, action, details):
    logger.info(f"User {user_id}: {action} - {details}")
