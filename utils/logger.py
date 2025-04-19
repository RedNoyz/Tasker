import logging
import functools
import inspect
import sys

# configure logging once
logging.basicConfig(
    level=logging.DEBUG,
    filename="tasker.log",
    format="%(asctime)s %(levelname)s %(module)s:%(funcName)s:%(lineno)d %(message)s"
)
logger = logging.getLogger("tasker")

if getattr(sys, "frozen", False):
    logging.disable(logging.DEBUG)

def log_call(func):
    """Decorator that logs every call, including its caller."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        caller = inspect.stack()[1]
        logger.debug(
            f"CALL {func.__module__}.{func.__name__} "
            f"(from {caller.filename}:{caller.lineno})",
            stack_info=True,
            stacklevel=2
        )
        return func(*args, **kwargs)
    return wrapper