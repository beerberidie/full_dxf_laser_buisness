"""
Communications Drafts Service for Laser OS Production Automation.

This module handles auto-generated client message drafts including:
- Quote follow-ups (QuotesAndApproval stage overdue)
- Pickup reminders (ReadyForPickup stage overdue)
- Draft management (list, send, delete)
"""

from datetime import datetime
from app import db
from app.models.business import OutboundDraft, Project


def get_pending_drafts(limit=50):
    """
    Get all pending (unsent) outbound drafts.
    
    Args:
        limit (int): Maximum number of drafts to return
        
    Returns:
        list: List of OutboundDraft objects
    """
    return OutboundDraft.query.filter_by(
        sent=False
    ).order_by(OutboundDraft.created_at.desc()).limit(limit).all()


def get_sent_drafts(limit=50):
    """
    Get all sent outbound drafts.
    
    Args:
        limit (int): Maximum number of drafts to return
        
    Returns:
        list: List of OutboundDraft objects
    """
    return OutboundDraft.query.filter_by(
        sent=True
    ).order_by(OutboundDraft.sent_at.desc()).limit(limit).all()


def get_drafts_for_project(project_id):
    """
    Get all drafts for a specific project.
    
    Args:
        project_id (int): Project ID
        
    Returns:
        list: List of OutboundDraft objects
    """
    return OutboundDraft.query.filter_by(
        project_id=project_id
    ).order_by(OutboundDraft.created_at.desc()).all()


def get_drafts_for_client(client_id):
    """
    Get all drafts for a specific client.
    
    Args:
        client_id (int): Client ID
        
    Returns:
        list: List of OutboundDraft objects
    """
    return OutboundDraft.query.filter_by(
        client_id=client_id
    ).order_by(OutboundDraft.created_at.desc()).all()


def mark_draft_as_sent(draft_id):
    """
    Mark a draft as sent.
    
    Args:
        draft_id (int): Draft ID
        
    Returns:
        bool: True if successful
    """
    draft = OutboundDraft.query.get(draft_id)
    if not draft:
        return False
    
    draft.sent = True
    draft.sent_at = datetime.utcnow()
    
    db.session.add(draft)
    db.session.commit()
    
    return True


def delete_draft(draft_id):
    """
    Delete a draft.
    
    Args:
        draft_id (int): Draft ID
        
    Returns:
        bool: True if successful
    """
    draft = OutboundDraft.query.get(draft_id)
    if not draft:
        return False
    
    db.session.delete(draft)
    db.session.commit()
    
    return True


def update_draft(draft_id, body_text=None, channel_hint=None):
    """
    Update a draft's content.
    
    Args:
        draft_id (int): Draft ID
        body_text (str): New body text (optional)
        channel_hint (str): New channel hint (optional)
        
    Returns:
        bool: True if successful
    """
    draft = OutboundDraft.query.get(draft_id)
    if not draft:
        return False
    
    if body_text is not None:
        draft.body_text = body_text
    
    if channel_hint is not None:
        draft.channel_hint = channel_hint
    
    db.session.add(draft)
    db.session.commit()
    
    return True


def create_manual_draft(project_id, client_id, body_text, channel_hint='whatsapp'):
    """
    Manually create a draft message.
    
    Args:
        project_id (int): Project ID
        client_id (int): Client ID
        body_text (str): Message body
        channel_hint (str): Preferred channel (default: 'whatsapp')
        
    Returns:
        OutboundDraft: Created draft
    """
    draft = OutboundDraft(
        project_id=project_id,
        client_id=client_id,
        channel_hint=channel_hint,
        body_text=body_text,
        sent=False
    )
    
    db.session.add(draft)
    db.session.commit()
    
    return draft


def get_draft_statistics():
    """
    Get statistics about drafts.
    
    Returns:
        dict: Statistics including pending count, sent count, etc.
    """
    pending_count = OutboundDraft.query.filter_by(sent=False).count()
    sent_count = OutboundDraft.query.filter_by(sent=True).count()
    
    # Get drafts by channel
    whatsapp_count = OutboundDraft.query.filter_by(
        sent=False,
        channel_hint='whatsapp'
    ).count()
    
    email_count = OutboundDraft.query.filter_by(
        sent=False,
        channel_hint='email'
    ).count()
    
    return {
        'pending_count': pending_count,
        'sent_count': sent_count,
        'total_count': pending_count + sent_count,
        'whatsapp_count': whatsapp_count,
        'email_count': email_count
    }

