from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.models.optin import OptIn
from app.models.message import Message
from app.models.message_template import MessageTemplate
from app.models.contact import Contact
from app.models.consent import Consent

router = APIRouter()

@router.get("/dashboard/stats")
def get_dashboard_stats(
    days: Optional[int] = Query(30, description="Number of days to look back for time-based metrics"),
    db: Session = Depends(get_db)
):
    # Calculate time periods
    now = datetime.utcnow()
    period_start = now - timedelta(days=days)
    
    # Basic metrics from database
    users = db.query(AuthUser).count()
    
    # Count all OptIns and active OptIns separately
    total_optins = db.query(OptIn).count()
    active_optins = db.query(OptIn).filter(OptIn.status == 'active').count() if hasattr(OptIn, 'status') else total_optins
    
    # Count contacts
    total_contacts = db.query(Contact).count()
    new_contacts = db.query(Contact).filter(Contact.created_at >= period_start).count() if hasattr(Contact, 'created_at') else 0
    
    # Calculate consent metrics
    total_consents = db.query(Consent).count()
    active_consents = db.query(Consent).filter(Consent.status == 'opt-in').count() if hasattr(Consent, 'status') else 0
    opt_outs = db.query(Consent).filter(Consent.status == 'opt-out').count() if hasattr(Consent, 'status') else 0
    
    # Calculate verification metrics
    # In a real system, this would count verified vs unverified contacts
    # For now, we'll consider all active consents as verified
    total_verifications = total_consents
    successful_verifications = active_consents
    verification_rate = (successful_verifications / max(total_verifications, 1)) * 100 if total_verifications > 0 else 0
    
    # Calculate opt-in rate (percentage of contacts that have opted in)
    opt_in_rate = (active_consents / max(total_contacts, 1)) * 100 if total_contacts > 0 else 0
    opt_out_rate = (opt_outs / max(total_contacts, 1)) * 100 if total_contacts > 0 else 0
    
    # Channel distribution
    email_contacts = db.query(Contact).filter(Contact.contact_type == 'email').count() if hasattr(Contact, 'contact_type') else 0
    sms_contacts = db.query(Contact).filter(Contact.contact_type == 'phone').count() if hasattr(Contact, 'contact_type') else 0
    
    messages = db.query(Message).count()
    templates = db.query(MessageTemplate).count()
    
    # Get recent messages (within the specified time period)
    recent_messages = db.query(Message).filter(
        Message.created_at >= period_start
    ).count() if hasattr(Message, 'created_at') else 0
    
    # Get active users (who have logged in within the specified time period)
    active_users = db.query(AuthUser).filter(
        AuthUser.last_login >= period_start
    ).count() if hasattr(AuthUser, 'last_login') else 0
    
    # Get new opt-ins (created within the specified time period)
    new_optins = db.query(OptIn).filter(
        OptIn.created_at >= period_start
    ).count() if hasattr(OptIn, 'created_at') else 0
    
    # Get message status counts if the status field exists
    delivered_messages = db.query(Message).filter(Message.status == 'delivered').count() if hasattr(Message, 'status') else 0
    failed_messages = db.query(Message).filter(Message.status == 'failed').count() if hasattr(Message, 'status') else 0
    pending_messages = db.query(Message).filter(Message.status == 'pending').count() if hasattr(Message, 'status') else 0
    
    # Calculate delivery rate
    delivery_rate = (delivered_messages / max(messages, 1)) * 100 if messages > 0 else 0
    
    # Message volume trend (simplified - last 14 days)
    trend_days = min(14, days)
    message_trend_start = now - timedelta(days=trend_days)
    
    message_volume_trend = []
    if hasattr(Message, 'created_at'):
        for i in range(trend_days):
            day_date = message_trend_start + timedelta(days=i)
            next_day = day_date + timedelta(days=1)
            day_count = db.query(Message).filter(
                Message.created_at >= day_date,
                Message.created_at < next_day
            ).count()
            message_volume_trend.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "count": day_count
            })
    
    # Return a simplified dashboard data structure with only the data we can reliably get
    return {
        # Basic metrics
        "users": users,
        "optins": active_optins,  # Use active optins for the main count
        "messages": messages,
        "templates": templates,
        
        # Contact metrics
        "total_contacts": total_contacts,
        "new_contacts": new_contacts,
        "contact_growth_rate": 0,  # Placeholder for now
        "channel_distribution": {
            "sms": sms_contacts,
            "email": email_contacts
        },
        
        # Consent metrics
        "consent": {
            "total": total_consents,
            "active": active_consents,
            "opt_in_rate": round(opt_in_rate, 2),
            "opt_out_rate": round(opt_out_rate, 2)
        },
        
        # Verification metrics
        "verification": {
            "total": total_verifications,
            "successful": successful_verifications,
            "success_rate": round(verification_rate, 2)
        },
        
        # System metrics
        "system": {
            "users": {
                "total": users,
                "active": active_users
            },
            "templates": templates
        },
        
        # Opt-in metrics
        "optins": {
            "total": active_optins,  # Active optins count
            "all": total_optins,     # All optins count (including inactive)
            "new": new_optins,
            "top_performing": []
        },
        
        # Message metrics
        "messages": {
            "total": messages,
            "recent": recent_messages,
            "status": {
                "delivered": delivered_messages,
                "failed": failed_messages,
                "pending": pending_messages,
                "delivery_rate": round(delivery_rate, 2)
            },
            "volume_trend": message_volume_trend
        }
    }
