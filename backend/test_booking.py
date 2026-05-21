import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.schemas.booking import BookingRequestInput
from src.services.booking_service import BookingService, DoubleBookingError, normalize_time

def run_tests():
    bs = BookingService()

    # Test 1: same booking submitted twice
    print("\n--- Test 1: Same Booking Submitted Twice ---")
    req1 = BookingRequestInput(
        provider_id="PRO-1001",
        job_category="Plumber",
        scheduled_time="5:00 pm",
        dynamic_price=1000.0,
        customer_id="CUST-1",
        location_context="Clifton"
    )
    b1 = bs.create_booking(req1)
    print(f"Booking 1 Created: {b1['booking_id']}, Row: {b1['spreadsheet_row_id']}")
    
    b2 = bs.create_booking(req1)
    print(f"Booking 2 Result Status: {b2['current_status']}, Row: {b2.get('spreadsheet_row_id')}")
    assert b2["duplicate_detected"] == True, "Failed: Should be duplicate"
    assert b2["spreadsheet_row_id"] == b1["spreadsheet_row_id"], "Failed: Row ID should be the same"
    
    # Test 2: same provider and same time (different customer/category to bypass idempotency)
    print("\n--- Test 2: Same Provider, Same Time ---")
    req3 = BookingRequestInput(
        provider_id="PRO-1001",
        job_category="Electrician",
        scheduled_time="17:00",
        dynamic_price=1200.0,
        customer_id="CUST-2",
        location_context="DHA"
    )
    try:
        b3 = bs.create_booking(req3)
        print("FAILED: DoubleBookingError was not raised.")
    except DoubleBookingError as e:
        print(f"DoubleBookingError Raised correctly: {str(e)}")
        print(f"Alternate slots: {e.alternate_slots}")
        
    # Test 3: same request with "5 pm" and "17:00" is treated as duplicate
    print("\n--- Test 3: Duplicate using different time format ('5 pm' vs '17:00') ---")
    req4_a = BookingRequestInput(
        provider_id="PRO-1002",
        job_category="Plumber",
        scheduled_time="5 pm",
        dynamic_price=1000.0,
        customer_id="CUST-3",
        location_context="Clifton"
    )
    b4_a = bs.create_booking(req4_a)
    print(f"Booking A Created: {b4_a['booking_id']} with scheduled_time={req4_a.scheduled_time}")

    req4_b = BookingRequestInput(
        provider_id="PRO-1002",
        job_category="Plumber",
        scheduled_time="17:00",
        dynamic_price=1000.0,
        customer_id="CUST-3",
        location_context="Clifton"
    )
    b4_b = bs.create_booking(req4_b)
    print(f"Booking B Result Status: {b4_b['current_status']} with scheduled_time={req4_b.scheduled_time}")
    assert b4_b["duplicate_detected"] == True, "Failed: 5 pm and 17:00 should be duplicate"
    
    # Test 4: different time creates a new booking
    print("\n--- Test 4: Different time creates a new booking ---")
    req5 = BookingRequestInput(
        provider_id="PRO-1001", # same provider as Test 1
        job_category="Plumber",
        scheduled_time="8:00 pm", # different time
        dynamic_price=1000.0,
        customer_id="CUST-1",
        location_context="Clifton"
    )
    b5 = bs.create_booking(req5)
    print(f"Booking 5 Status: {b5['current_status']}, Row: {b5['spreadsheet_row_id']}")
    assert b5["duplicate_detected"] == False, "Failed: Should be a new booking"
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    run_tests()
