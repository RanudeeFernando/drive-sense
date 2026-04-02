class Admin:
    def __init__(self, admin_id, username, password):
        self.admin_id = admin_id
        self.username = username
        self.password = password

    def get_admin_id(self):
        return self.admin_id

    def set_admin_id(self, admin_id):
        self.admin_id = admin_id

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    def login(self, input_username, input_password):
        return self.username == input_username and self.password == input_password

    def view_parking_logs(self, cloud_database):
        return cloud_database.retrieve()

    def view_slot_availability(self, slots):
        availability = []
        for slot in slots:
            availability.append({
                "slot_id": slot.slot_id,
                "slot_type": slot.slot_type,
                "occupied": slot.slot_status
            })
        return availability

    def control_lighting_system(self, lighting_controller, turn_on):
        if turn_on:
            return lighting_controller.turn_on()
        return lighting_controller.turn_off()