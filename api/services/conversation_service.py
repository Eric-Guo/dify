import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Account
from models.model import App, Conversation, EndUser
from services.errors.conversation import ConversationNotExistsError
from tasks.collect_agent_resources_task import enqueue_agent_resource_collection

logger = logging.getLogger(__name__)


class ConversationService:
    @classmethod
    def get_conversation(
        cls, app_model: App, conversation_id: str, user: Account | EndUser | None, *, session: Session
    ):
        conversation = session.scalar(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.app_id == app_model.id,
                Conversation.from_source == ("api" if isinstance(user, EndUser) else "console"),
                Conversation.from_end_user_id == (user.id if isinstance(user, EndUser) else None),
                Conversation.from_account_id == (user.id if isinstance(user, Account) else None),
                Conversation.is_deleted.is_(False),
            )
            .limit(1)
        )

        if not conversation:
            raise ConversationNotExistsError()

        return conversation

    @staticmethod
    def enqueue_delete_cleanup(*, tenant_id: str, conversation_id: str, retired_workspace_ids: tuple[str, ...]) -> None:
        """Dispatch resource collection only after the lifecycle transaction commits."""
        if retired_workspace_ids:
            enqueue_agent_resource_collection(
                tenant_id=tenant_id,
                workspace_ids=retired_workspace_ids,
            )
