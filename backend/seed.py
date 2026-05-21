import os
from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from schemas import (
    ProviderSchema, ProviderScheduleSchema, ReviewSchema, BookingSchema, AgentTraceSchema,
    LocationSchema, WorkingHoursSchema, TimelineEntrySchema
)

# Initialize Firebase Admin
def init_firebase():
    if not firebase_admin._apps:
        # Use default credentials or GOOGLE_APPLICATION_CREDENTIALS from env
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    return firestore.client()

def clear_mock_data(db):
    print("Clearing existing mock data...")
    collections = ['providers', 'providerSchedules', 'reviews', 'bookings', 'agentTraces']
    for coll in collections:
        docs = db.collection(coll).where('isSynthetic', '==', True).stream()
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        print(f"Deleted {deleted_count} documents from {coll}.")

def seed_mock_data(db):
    print("Seeding mock data...")
    now = datetime.now(timezone.utc)

    # 1. Seed Providers
    providers = [
        ProviderSchema(
            id="prov_ac_1",
            name="Ali HVAC Services",
            category="AC Technician",
            specializations=["AC Installation", "AC Repair", "Maintenance"],
            basePrice=1500.0,
            rating=4.8,
            cancellationRate=0.05,
            reliabilityScore=0.92,
            distanceVectors=LocationSchema(lat=24.8607, lng=67.0011),
            reviewRecency=2.5,
            isSynthetic=True
        ),
        ProviderSchema(
            id="prov_elec_1",
            name="Kamran Electrician",
            category="Electrician",
            specializations=["Wiring", "Panel Upgrades", "Fault Finding"],
            basePrice=1200.0,
            rating=4.5,
            cancellationRate=0.1,
            reliabilityScore=0.88,
            distanceVectors=LocationSchema(lat=24.8500, lng=67.0100),
            reviewRecency=5.0,
            isSynthetic=True
        ),
        ProviderSchema(
            id="prov_plumb_1",
            name="Javed Plumbers",
            category="Plumber",
            specializations=["Leak Repair", "Pipe Installation", "Drain Unblocking"],
            basePrice=1000.0,
            rating=4.2,
            cancellationRate=0.15,
            reliabilityScore=0.80,
            distanceVectors=LocationSchema(lat=24.8700, lng=67.0200),
            reviewRecency=10.0,
            isSynthetic=True
        )
    ]

    for p in providers:
        db.collection('providers').document(p.id).set(p.model_dump())
    print(f"Seeded {len(providers)} providers.")

    # 2. Seed Schedules
    schedules = [
        ProviderScheduleSchema(
            id=f"sched_{p.id}",
            providerId=p.id,
            availableDates=[(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)],
            workingHours=WorkingHoursSchema(start="09:00", end="18:00"),
            isSynthetic=True
        ) for p in providers
    ]

    for s in schedules:
        db.collection('providerSchedules').document(s.id).set(s.model_dump())
    print(f"Seeded {len(schedules)} provider schedules.")

    # 3. Seed Reviews
    reviews = [
        ReviewSchema(
            id="rev_1",
            providerId="prov_ac_1",
            userId="user_123",
            rating=5.0,
            comment="Excellent AC repair, very punctual.",
            timestamp=now - timedelta(days=2),
            isSynthetic=True
        ),
        ReviewSchema(
            id="rev_2",
            providerId="prov_elec_1",
            userId="user_456",
            rating=4.0,
            comment="Good work but arrived late.",
            timestamp=now - timedelta(days=5),
            isSynthetic=True
        )
    ]

    for r in reviews:
        db.collection('reviews').document(r.id).set(r.model_dump())
    print(f"Seeded {len(reviews)} reviews.")

    # 4. Seed Bookings
    bookings = [
        BookingSchema(
            id="book_1",
            providerId="prov_ac_1",
            userId="user_789",
            status="completed",
            timeline=[
                TimelineEntrySchema(state="pending", timestamp=now - timedelta(days=1), agent="System"),
                TimelineEntrySchema(state="matched", timestamp=now - timedelta(hours=23), agent="Provider Matching Agent", reasoning="Best match based on distance and rating"),
                TimelineEntrySchema(state="completed", timestamp=now - timedelta(hours=20), agent="System")
            ],
            isSynthetic=True
        )
    ]

    for b in bookings:
        db.collection('bookings').document(b.id).set(b.model_dump())
    print(f"Seeded {len(bookings)} bookings.")

    # 5. Seed Agent Traces
    traces = [
        AgentTraceSchema(
            id="trace_1",
            bookingId="book_1",
            agentName="Provider Matching Agent",
            reasoning="Calculated 8-factor score: provider prov_ac_1 scored highest (0.95) due to proximity and high reliability.",
            confidence=0.96,
            timestamp=now - timedelta(hours=23),
            isSynthetic=True
        )
    ]

    for t in traces:
        db.collection('agentTraces').document(t.id).set(t.model_dump())
    print(f"Seeded {len(traces)} agent traces.")
    print("Mock data seeding completed successfully.")

if __name__ == "__main__":
    db = init_firebase()
    clear_mock_data(db)
    seed_mock_data(db)
