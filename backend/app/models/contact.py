"""
models/contact.py

SQLAlchemy model for the Contact entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base
import enum

class UserStatusEnum(str, enum.Enum):
    """
    Enumeration for contact status values.
    
    These status values track whether a contact is currently active in the system.
    This is important for filtering contacts in reports and determining whether
    communications should be sent, independent of specific consent status.
    """
    active = "active"      # Contact is active and can receive communications if consented
    inactive = "inactive"  # Contact is inactive and should not receive communications

class ContactTypeEnum(str, enum.Enum):
    """
    Enumeration for contact type values.
    
    Different contact types require different validation, encryption, and masking
    approaches. This enumeration allows the system to handle various contact methods
    while applying the appropriate business logic and regulatory requirements to each.
    """
    email = "email"  # Email address contact method
    phone = "phone"  # Phone number contact method

class Contact(Base):
    """
    SQLAlchemy model for contact records (opt-in/consent, no authentication).
    
    The Contact model represents individuals who may provide consent for communications.
    This model stores contact information in an encrypted format to protect personally
    identifiable information (PII) while still allowing the system to manage consent.
    Using deterministic IDs derived from the contact value enables lookups without
    decrypting the data, balancing security with functionality.
    
    This model is distinct from AuthUser, which represents authenticated system users
    with roles and permissions. Contacts are the subjects of consent management, while
    AuthUsers are the operators of the system.
    
    Attributes:
        id (String): Primary key - deterministic ID generated from contact value,
                   enabling lookups without decrypting PII.
        encrypted_value (str): Encrypted contact value (email or phone), protecting
                             PII while storing necessary contact information.
        contact_type (str): Type of contact (email/phone), determining how the
                          system validates, encrypts, and communicates with the contact.
        created_at (datetime): Creation timestamp for audit and reporting purposes.
        updated_at (datetime): Last update timestamp for tracking changes over time.
        status (str): Contact status (active/inactive), controlling whether the
                    contact should receive communications independent of consent.
        is_admin (bool): Whether the contact has admin privileges, legacy field
                       maintained for backward compatibility.
        is_staff (bool): Whether the contact has staff privileges, legacy field
                       maintained for backward compatibility.
        comment (str): Stores opt-out comment from contact, capturing the reason
                     for opt-out which is important for compliance and reporting.
    """
    __tablename__ = "contacts"
    id = Column(String, primary_key=True)  # Deterministic ID from contact value
    """
    Unique identifier for the contact, generated deterministically from the contact value.
    Using a deterministic ID allows the system to find contacts without decrypting their
    information, which is essential for privacy and security while maintaining functionality.
    """
    
    encrypted_value = Column(String, nullable=False, unique=True)  # Encrypted email or phone
    """
    Encrypted representation of the contact's email or phone number.
    Storing this data in encrypted form protects PII while still allowing the system to
    maintain necessary contact information for communications and consent management.
    """
    
    contact_type = Column(String, nullable=False)  # 'email' or 'phone'
    """
    The type of contact information stored (email or phone).
    Different contact types require different validation, encryption, masking, and
    communication approaches, so tracking the type is essential for proper handling.
    """
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    """
    Timestamp when the contact record was created.
    This is important for audit trails, reporting, and understanding the contact's
    history in the system.
    """
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    """
    Timestamp when the contact record was last updated.
    This helps track changes to contact information over time and is useful for
    filtering recent changes in reports.
    """
    
    status = Column(String, default=UserStatusEnum.active.value)
    """
    Current status of the contact (active or inactive).
    This status controls whether the contact should receive communications at all,
    independent of specific consent status for individual opt-in programs.
    """
    
    is_admin = Column(Boolean, default=False)
    """
    Legacy field indicating whether the contact has admin privileges.
    This field is maintained for backward compatibility but is not actively used
    in the current system architecture, which separates contacts from authenticated users.
    """
    
    is_staff = Column(Boolean, default=False)
    """
    Legacy field indicating whether the contact has staff privileges.
    This field is maintained for backward compatibility but is not actively used
    in the current system architecture, which separates contacts from authenticated users.
    """
    
    comment = Column(String, nullable=True)  # Stores opt-out comment from contact
    """
    Optional comment provided by the contact when opting out.
    Capturing the reason for opt-out is valuable for improving services and
    understanding user concerns, as well as for compliance reporting.
    """
