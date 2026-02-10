"""
AI Mentor Chat History API - Phase 3

Provides endpoints for managing chat conversations and messages:
- List chat conversations
- Create new conversation
- Get conversation details
- Update conversation title
- Delete conversation
- Get conversation messages

Path: /api/v3/tutor/ai/chat
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.models.database import ChatConversation, ChatMessage, User
from src.api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Models and Schemas
# =============================================================================


class ChatMessageResponse(BaseModel):
    """Chat message response."""
    id: str
    role: str
    content: str
    created_at: str
    extra_data: Optional[dict] = None


class ChatConversationResponse(BaseModel):
    """Chat conversation response."""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


class ChatConversationDetail(BaseModel):
    """Chat conversation with messages."""
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessageResponse]


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    title: str = Field(default="New Chat", max_length=255)


class UpdateConversationRequest(BaseModel):
    """Request to update conversation title."""
    title: str = Field(..., max_length=255)


class CreateMessageRequest(BaseModel):
    """Request to add a message to conversation."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=10000)
    extra_data: Optional[dict] = None


# =============================================================================
# Helper Functions
# =============================================================================


async def get_user_chats(db: AsyncSession, user_id: UUID) -> List[ChatConversation]:
    """Get all chat conversations for a user."""
    result = await db.execute(
        select(ChatConversation)
        .where(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.updated_at.desc())
        .options(selectinload(ChatConversation.messages))
    )
    return list(result.scalars().all())


async def get_conversation_by_id(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[ChatConversation]:
    """Get a specific conversation by ID."""
    result = await db.execute(
        select(ChatConversation)
        .where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user_id
        )
        .options(selectinload(ChatConversation.messages))
    )
    return result.scalar_one_or_none()


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/conversations", response_model=List[ChatConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all chat conversations for a user.

    Returns conversations ordered by most recently updated.

    **Authentication**: Required - Users must be logged in to view their conversations.
    """
    try:
        conversations = await get_user_chats(db, current_user.id)

        response = []
        for conv in conversations:
            response.append(ChatConversationResponse(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                message_count=len(conv.messages)
            ))

        return response

    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.post("/conversations", response_model=ChatConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new chat conversation.

    Creates a new empty conversation with the given title.

    **Authentication**: Required - Users must be logged in to create conversations.
    """
    try:
        # Create conversation
        conversation = ChatConversation(
            user_id=current_user.id,
            title=request.title
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return ChatConversationResponse(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            message_count=0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/conversations/{conversation_id}", response_model=ChatConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a conversation with all its messages.

    Returns the conversation details and all messages ordered by creation time.

    **Authentication**: Required - Users can only view their own conversations.
    """
    try:
        conversation = await get_conversation_by_id(db, conversation_id, current_user.id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        messages = [
            ChatMessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
                extra_data=msg.extra_data
            )
            for msg in sorted(conversation.messages, key=lambda m: m.created_at)
        ]

        return ChatConversationDetail(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=messages
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.put("/conversations/{conversation_id}", response_model=ChatConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    request: UpdateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update conversation title.

    Updates the title of an existing conversation.

    **Authentication**: Required - Users can only update their own conversations.
    """
    try:
        conversation = await get_conversation_by_id(db, conversation_id, current_user.id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        conversation.title = request.title
        await db.commit()
        await db.refresh(conversation)

        return ChatConversationResponse(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            message_count=len(conversation.messages)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation"
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.

    Permanently removes the conversation and all associated messages.

    **Authentication**: Required - Users can only delete their own conversations.
    """
    try:
        # Verify conversation belongs to user
        conversation = await get_conversation_by_id(db, conversation_id, current_user.id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Delete conversation (cascade will delete messages)
        await db.execute(
            delete(ChatConversation).where(ChatConversation.id == conversation_id)
        )
        await db.commit()

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def create_message(
    conversation_id: UUID,
    request: CreateMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a message to a conversation.

    Adds a new message to the specified conversation and updates the updated_at timestamp.

    **Authentication**: Required - Users can only add messages to their own conversations.
    """
    try:
        # Verify conversation belongs to user
        conversation = await get_conversation_by_id(db, conversation_id, current_user.id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Create message
        message = ChatMessage(
            conversation_id=conversation_id,
            role=request.role,
            content=request.content,
            extra_data=request.extra_data
        )
        db.add(message)

        # Update conversation timestamp
        from sqlalchemy import func
        await db.execute(
            select(ChatConversation).where(ChatConversation.id == conversation_id)
        )
        conversation.updated_at = func.now()

        await db.commit()
        await db.refresh(message)

        return ChatMessageResponse(
            id=str(message.id),
            role=message.role,
            content=message.content,
            created_at=message.created_at.isoformat(),
            extra_data=message.extra_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating message: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message"
        )
