import logging
from contextvars import ContextVar
from typing import Optional
from uuid import UUID

# Define context variables for job_id and task_id with default values.
job_id_context: ContextVar[Optional[UUID]] = ContextVar("job_id", default=None)
task_id_context: ContextVar[Optional[UUID]] = ContextVar("task_id", default=None)


class ContextFilter(logging.Filter):
    """
    A logging filter that injects job_id and task_id from contextvars
    into the log record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Adds job_id and task_id to the log record.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            bool: True to process the record, False to discard it.
        """
        job_id = job_id_context.get()
        task_id = task_id_context.get()

        # Format the context string to be included in the log message.
        if task_id:
            record.context_info = f"[{job_id}|{task_id}] "
        elif job_id:
            record.context_info = f"[{job_id}] "
        else:
            record.context_info = ""

        return True