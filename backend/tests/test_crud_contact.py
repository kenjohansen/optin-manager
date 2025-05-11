"""
tests/test_crud_contact.py

Tests for CRUD operations on the Contact model.
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.crud.contact import (
    get_contact, 
    get_contact_by_value, 
    create_contact, 
    update_contact, 
    delete_contact, 
    list_contacts,
    list_contacts_with_filters,
    get_masked_contact_value
)
from app.models.contact import Contact, ContactTypeEnum
from app.models.consent import Consent, ConsentStatusEnum, ConsentChannelEnum
from app.core.encryption import generate_deterministic_id
from app.schemas.contact import ContactCreate, ContactUpdate

class TestContactCrud:
    """Test suite for Contact CRUD operations."""
    
    def test_get_contact(self, db_session: Session):
        """Test retrieving a contact by ID."""
        # Create a test contact
        email = "test-get@example.com"
        contact_id = generate_deterministic_id(email)
        
        contact = Contact(
            id=contact_id,
            encrypted_value="encrypted_email_value",
            contact_type=ContactTypeEnum.email.value
        )
        db_session.add(contact)
        db_session.commit()
        
        # Test retrieval
        retrieved_contact = get_contact(db_session, contact_id)
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact_id
        assert retrieved_contact.contact_type == ContactTypeEnum.email.value
        
        # Test retrieval with non-existent ID
        non_existent_contact = get_contact(db_session, "non-existent-id")
        assert non_existent_contact is None
    
    def test_get_contact_by_value(self, db_session: Session):
        """Test retrieving a contact by value."""
        # Create a test contact
        email = "test-by-value@example.com"
        contact_id = generate_deterministic_id(email)
        
        # Check if contact already exists
        existing = db_session.query(Contact).filter(Contact.id == contact_id).first()
        if existing is None:
            contact = Contact(
                id=contact_id,
                encrypted_value=f"encrypted_value_{contact_id}",  # Use unique value
                contact_type=ContactTypeEnum.email.value
            )
            db_session.add(contact)
            db_session.commit()
        
        # Test retrieval by value - should work by generating the same deterministic ID
        retrieved_contact = get_contact_by_value(db_session, email)
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact_id
        
        # Test with explicit contact type
        retrieved_contact = get_contact_by_value(db_session, email, "email")
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact_id
        
        # Test with non-existent value
        non_existent_contact = get_contact_by_value(db_session, "non-existent@example.com")
        assert non_existent_contact is None
    
    def test_create_contact(self, db_session: Session):
        """Test creating a new contact."""
        # Create schema
        email = "test-create@example.com"
        contact_create = ContactCreate(
            contact_value=email,
            contact_type="email",
            status="active",
            comment="Test comment"
        )
        
        # Create contact
        created_contact = create_contact(db_session, contact_create)
        assert created_contact is not None
        assert created_contact.id == generate_deterministic_id(email)
        assert created_contact.contact_type == ContactTypeEnum.email.value
        assert created_contact.status == "active"
        assert created_contact.comment == "Test comment"
        
        # Check that it was saved to the database
        db_contact = db_session.query(Contact).filter(Contact.id == created_contact.id).first()
        assert db_contact is not None
        assert db_contact.id == created_contact.id
    
    def test_update_contact(self, db_session: Session):
        """Test updating an existing contact."""
        # Create a test contact
        email = "test-update@example.com"
        contact_id = generate_deterministic_id(email)
        
        # Check if contact already exists
        contact = db_session.query(Contact).filter(Contact.id == contact_id).first()
        if contact is None:
            contact = Contact(
                id=contact_id,
                encrypted_value=f"encrypted_value_{contact_id}",  # Use unique value
                contact_type=ContactTypeEnum.email.value,
                status="active",
                comment="Original comment"
            )
            db_session.add(contact)
            db_session.commit()
        
        # Update schema
        contact_update = ContactUpdate(
            status="inactive",
            comment="Updated comment"
        )
        
        # Update contact
        updated_contact = update_contact(db_session, contact, contact_update)
        assert updated_contact.status == "inactive"
        assert updated_contact.comment == "Updated comment"
        
        # Check that it was saved to the database
        db_contact = db_session.query(Contact).filter(Contact.id == contact_id).first()
        assert db_contact.status == "inactive"
        assert db_contact.comment == "Updated comment"
    
    def test_delete_contact(self, db_session: Session):
        """Test deleting a contact."""
        # Create a test contact
        email = "test-delete@example.com"
        contact_id = generate_deterministic_id(email)
        
        # First check and delete if it already exists to avoid unique constraint errors
        existing = db_session.query(Contact).filter(Contact.id == contact_id).first()
        if existing:
            db_session.delete(existing)
            db_session.commit()
            
        contact = Contact(
            id=contact_id,
            encrypted_value=f"encrypted_value_{contact_id}",  # Ensure unique value
            contact_type=ContactTypeEnum.email.value
        )
        db_session.add(contact)
        db_session.commit()
        
        # Delete the contact
        delete_contact(db_session, contact)
        
        # Verify it's gone
        deleted_contact = db_session.query(Contact).filter(Contact.id == contact_id).first()
        assert deleted_contact is None
    
    def test_list_contacts(self, db_session: Session):
        """Test listing contacts with pagination."""
        # Create multiple test contacts
        for i in range(5):
            email = f"test-list-{i}@example.com"
            contact_id = generate_deterministic_id(email)
            
            contact = Contact(
                id=contact_id,
                encrypted_value=f"encrypted_email_value_{i}",
                contact_type=ContactTypeEnum.email.value
            )
            db_session.add(contact)
        
        db_session.commit()
        
        # Test listing with default pagination
        all_contacts = list_contacts(db_session)
        # We should have at least the 5 contacts we created
        assert len(all_contacts) >= 5
        
        # Test pagination - first page with 2 items
        page1 = list_contacts(db_session, skip=0, limit=2)
        assert len(page1) == 2
        
        # Second page with 2 items
        page2 = list_contacts(db_session, skip=2, limit=2)
        assert len(page2) == 2
        
        # Verify the pages contain different contacts
        assert page1[0].id != page2[0].id
        
    def test_list_contacts_with_filters(self, db_session: Session):
        """Test listing contacts with filters."""
        # Check the actual enum values to make sure we're using the correct ones
        from app.models.consent import ConsentStatusEnum
        
        # Create test contacts with different properties
        # Contact 1: Email, opted in, recent
        email1 = "test-filter-1@example.com"
        contact_id1 = generate_deterministic_id(email1)
        
        # Check if contact already exists and remove if needed
        existing1 = db_session.query(Contact).filter(Contact.id == contact_id1).first()
        if existing1:
            db_session.delete(existing1)
            db_session.commit()
            
        contact1 = Contact(
            id=contact_id1,
            encrypted_value=f"encrypted_email_{contact_id1}",  # Ensure unique value
            contact_type=ContactTypeEnum.email.value,
            updated_at=datetime.utcnow()
        )
        db_session.add(contact1)
        db_session.commit()
        
        # Add consent record for contact 1
        existing_consent1 = db_session.query(Consent).filter(Consent.id == f"{contact_id1}-product1").first()
        if existing_consent1:
            db_session.delete(existing_consent1)
            db_session.commit()
            
        consent1 = Consent(
            id=f"{contact_id1}-product1",
            user_id=contact_id1,
            optin_id="product1",  # Using optin_id instead of product_id
            channel=ConsentChannelEnum.email.value,  # Add required channel field
            status=ConsentStatusEnum.opt_in.value  # Use correct enum name
        )
        db_session.add(consent1)
        db_session.commit()
        
        # Contact 2: Phone, opted out, recent
        phone = "+12065551234"
        contact_id2 = generate_deterministic_id(phone)
        
        # Check if contact already exists and remove if needed
        existing2 = db_session.query(Contact).filter(Contact.id == contact_id2).first()
        if existing2:
            db_session.delete(existing2)
            db_session.commit()
            
        contact2 = Contact(
            id=contact_id2,
            encrypted_value=f"encrypted_phone_{contact_id2}",  # Ensure unique value
            contact_type=ContactTypeEnum.phone.value,
            updated_at=datetime.utcnow()
        )
        db_session.add(contact2)
        db_session.commit()
        
        # Add consent record for contact 2
        existing_consent2 = db_session.query(Consent).filter(Consent.id == f"{contact_id2}-product1").first()
        if existing_consent2:
            db_session.delete(existing_consent2)
            db_session.commit()
            
        consent2 = Consent(
            id=f"{contact_id2}-product1",
            user_id=contact_id2,
            optin_id="product1",  # Using optin_id instead of product_id
            channel=ConsentChannelEnum.sms.value,  # Add required channel field 
            status=ConsentStatusEnum.opt_out.value  # Use correct enum name
        )
        db_session.add(consent2)
        db_session.commit()
        
        # Contact 3: Email, no consent, older
        email3 = "test-filter-3@example.com"
        contact_id3 = generate_deterministic_id(email3)
        
        # Check if contact already exists and remove if needed
        existing3 = db_session.query(Contact).filter(Contact.id == contact_id3).first()
        if existing3:
            db_session.delete(existing3)
            db_session.commit()
            
        contact3 = Contact(
            id=contact_id3,
            encrypted_value=f"encrypted_email_{contact_id3}",  # Ensure unique value
            contact_type=ContactTypeEnum.email.value,
            updated_at=datetime.utcnow() - timedelta(days=30)
        )
        db_session.add(contact3)
        db_session.commit()
        
        # Test: Filter by time window (recent contacts)
        recent_contacts = list_contacts_with_filters(db_session, time_window=7)
        # Should include contact1 and contact2, but not contact3
        recent_ids = [c.id for c in recent_contacts]
        assert contact_id1 in recent_ids
        assert contact_id2 in recent_ids
        assert contact_id3 not in recent_ids
        
        # Test: Filter by consent status (opted in)
        opted_in_contacts = list_contacts_with_filters(db_session, consent="opted_in")
        opted_in_ids = [c.id for c in opted_in_contacts]
        assert contact_id1 in opted_in_ids
        assert contact_id2 not in opted_in_ids
        
        # Test: Filter by consent status (opted out)
        opted_out_contacts = list_contacts_with_filters(db_session, consent="opted_out")
        opted_out_ids = [c.id for c in opted_out_contacts]
        assert contact_id1 not in opted_out_ids
        assert contact_id2 in opted_out_ids
    
    @pytest.mark.skip(reason="Requires encryption keys setup for decryption to work")
    def test_get_masked_contact_value(self, db_session: Session):
        """Test getting masked contact value."""
        # This test is skipped because it requires proper encryption key setup
        # that might not be available in the test environment.
        # The masking function relies on being able to decrypt values first.
        
        # Create a test contact (email)
        email_contact = Contact(
            id="email-mask-test",
            encrypted_value="encrypted_email",
            contact_type=ContactTypeEnum.email.value
        )
        
        # Create a test contact (phone)
        phone_contact = Contact(
            id="phone-mask-test",
            encrypted_value="encrypted_phone",
            contact_type=ContactTypeEnum.phone.value
        )
        
        # Test masking
        # In a proper environment, these would work with real encryption keys
        email_masked = get_masked_contact_value(email_contact)
        assert email_masked is not None
        
        phone_masked = get_masked_contact_value(phone_contact)
        assert phone_masked is not None
