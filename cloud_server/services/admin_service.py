# cloud_server/services/admin_service.py
from cloud_server.repositories.admin_repository import AdminRepository
from cloud_server.repositories.settings_repository import SettingsRepository


class AdminService:
    def __init__(self, light_manager_service):
        self.admin_repository = AdminRepository()
        self.settings_repository = SettingsRepository()
        self.light_manager_service = light_manager_service
        # Placeholder admin instance if needed for specific core logic
        # Admin(admin_id=1, username="admin", password="password")
        self.admin = None

    def login(self, username: str, password: str) -> dict:
        """Validate credentials against Firestore. Returns success or failure."""
        if self.admin_repository.verify_credentials(username, password):
            return {"success": True, "message": "Login successful."}
        return {"success": False, "message": "Invalid username or password."}

    def toggle_light(self, turn_on: bool):
        """Existing logic to control the light through the light controller."""
        if turn_on:
            self.light_manager_service.turn_on()
        else:
            self.light_manager_service.turn_off()

    def set_ldr_status(self, enabled: bool) -> dict:
        """Set the LDR enabled status in Firestore and update the lighting system accordingly."""
        self.settings_repository.set_ldr_enabled(enabled)
        
        # If disabling, ensure light is also turned off manually
        if not enabled:
            self.light_manager_service.turn_off()
            
        return {
            "success": True, 
            "message": f"Lighting system {'enabled' if enabled else 'disabled manually by admin'}"
        }

    def get_ldr_status(self) -> bool:
        """Return the current LDR enabled status."""
        return self.settings_repository.get_ldr_enabled()