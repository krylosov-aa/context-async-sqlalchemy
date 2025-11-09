from http import HTTPStatus

from .context import get_db_session_from_context


async def auto_commit_by_status_code(status_code: int) -> None:
    """
    Implements automatic commit or rollback.
    It should be used, for example, in the middleware or anywhere else
        where you expect session lifecycle management.
    """
    session = get_db_session_from_context()

    if session and session.in_transaction():
        if status_code < HTTPStatus.BAD_REQUEST:
            await session.commit()
        else:
            await session.rollback()
