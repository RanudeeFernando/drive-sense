from cloud_server.repositories.settings_repository import SettingsRepository


class LightController:
    def __init__(self):
        self.settings_repository = SettingsRepository()
        self.settings_repository.initialize_default_light_settings()

    def process_light(self, resistance: float):
        settings = self.settings_repository.get_light_settings()

        if not settings:
            return {
                "status": "failed",
                "message": "Lighting settings not found",
                "light_on": False
            }

        mode = settings.get("mode", "AUTO")
        threshold = settings.get("threshold", 15)
        current_light_state = settings.get("light_on", False)

        # AUTO mode: decide based on resistance
        if mode == "AUTO":
            new_light_state = resistance > threshold

            self.settings_repository.update_light_settings({
                "light_on": new_light_state
            })

            return {
                "status": "success",
                "mode": "AUTO",
                "resistance": resistance,
                "threshold": threshold,
                "light_on": new_light_state,
                "message": "Light state updated automatically"
            }

        # MANUAL mode: ignore resistance, keep admin-set value
        elif mode == "MANUAL":
            return {
                "status": "success",
                "mode": "MANUAL",
                "resistance": resistance,
                "threshold": threshold,
                "light_on": current_light_state,
                "message": "Manual mode active, resistance ignored"
            }

        else:
            return {
                "status": "failed",
                "message": f"Invalid lighting mode: {mode}",
                "light_on": current_light_state
            }

    def set_manual_mode(self, light_on: bool):
        self.settings_repository.update_light_settings({
            "mode": "MANUAL",
            "light_on": light_on
        })

        return {
            "status": "success",
            "mode": "MANUAL",
            "light_on": light_on,
            "message": "Manual mode enabled"
        }

    def set_auto_mode(self):
        self.settings_repository.update_light_settings({
            "mode": "AUTO"
        })

        return {
            "status": "success",
            "mode": "AUTO",
            "message": "Auto mode enabled"
        }

    def update_threshold(self, threshold: float):
        self.settings_repository.update_light_settings({
            "threshold": threshold
        })

        return {
            "status": "success",
            "threshold": threshold,
            "message": "Threshold updated successfully"
        }

    def get_light_status(self):
        settings = self.settings_repository.get_light_settings()

        if not settings:
            return {
                "status": "failed",
                "message": "Lighting settings not found"
            }

        return {
            "status": "success",
            "mode": settings.get("mode", "AUTO"),
            "threshold": settings.get("threshold", 15),
            "light_on": settings.get("light_on", False)
        }