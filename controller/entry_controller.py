# core/entry_controller.py

class EntryController:

    def __init__(self, ultrasonic, camera, model, slot, ticket):
        self.ultrasonic = ultrasonic
        self.camera = camera
        self.model = model
        self.slot = slot
        self.ticket = ticket

    def process_vehicle(self):

        # Step 1: detect vehicle
        if self.ultrasonic.detect_slot_occupancy():

            print("🚘 Vehicle Arrived!")

            # Step 2: capture image
            img_path = self.camera.capture_image()

            # Step 3: classify vehicle
            vehicle_type = self.model.classify_vehicle(img_path)

            # Step 4: find available slot
            slot_id = self.slot.findAvailableSlot(vehicle_type)

            if slot_id:
                # Step 5: reserve slot
                self.slot.reserveSlot(slot_id)

                # Step 6: generate ticket
                ticket_id = self.ticket.generate_ticket(slot_id, vehicle_type)

                print(f"👉 Driver, go to Slot {slot_id}")
                return ticket_id

            else:
                print("❌ No slots available!")
                return None