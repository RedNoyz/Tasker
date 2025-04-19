import os
import sys
import logging
import functools
import inspect

IS_DEBUG_BUILD = (not getattr(sys, "frozen", False)) or (os.getenv("TASKER_DEBUG") == "1")

if IS_DEBUG_BUILD:
    logging.basicConfig(
        level=logging.DEBUG,
        filename="tasker.log",
        format="%(asctime)s %(levelname)s %(module)s:%(funcName)s:%(lineno)d %(message)s"
    )
else:
    root = logging.getLogger()
    root.addHandler(logging.NullHandler())
    logging.disable(logging.CRITICAL)

logger = logging.getLogger("tasker")

def log_call(func):
    if not IS_DEBUG_BUILD:
        return func
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
