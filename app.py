import time
import requests
import os
from dotenv import load_dotenv
from sensors.camera_sensor import CameraSensor
from sensors.light_sensor import LightSensor
from sensors.ultrasonic_sensor import UltrasonicSensor
from core.lighting_controller import LightingController

# Load .env for local dev; on Raspberry Pi, set the var in the shell or a systemd service file
load_dotenv(override=False)

# Switch between local testing and live EC2 by changing this in your .env — no code change needed!
CLOUD_SERVER_URL = os.environ.get("CLOUD_SERVER_URL", "http://localhost:8001/api/detect_vehicle")

def main():
    # Only physical hardware sensors remain on the Edge!
    # No AI or Database logic exists here anymore.
    camera = CameraSensor(sensor_id=1, camera_index=0)
    light_sensor = LightSensor(sensor_id=2, threshold=300)
    ultrasonic_sensor = UltrasonicSensor(sensor_id=3, mock_mode=True)
    lighting = LightingController()

    print("=== DriveSense EDGE NODE Running ===")
    print(f"Connected to Cloud Server: {CLOUD_SERVER_URL}")
    print("Monitoring physical entrance...\n")

    while True:
        try:
            time.sleep(2)
            
            # 1. Hardware Sensor: Ultrasonic detects presence
            if ultrasonic_sensor.detect_slot_occupancy():
                print("\n[+] EDGE HARDWARE: Vehicle Detected at Entrance!")
                
                # Hardware Sensor: Check ambient lighting physically
                if light_sensor.is_dark():
                    lighting.turn_on()
                
                # 2. Hardware Sensor: Capture Visual Data
                image_path = camera.capture_image()
                
                if os.path.exists(image_path) and image_path != "dummy_vehicle_image.jpg":
                    # 3. EDGE/CLOUD COLLABORATION: Transmit captured data!
                    print(">>> Transmitting sensor image payload to Cloud Server for AI classification...")
                    try:
                        with open(image_path, "rb") as image_file:
                            files = {"image": (os.path.basename(image_path), image_file, "image/jpeg")}
                            response = requests.post(CLOUD_SERVER_URL, files=files)
                            
                        if response.status_code == 200:
                            result = response.json()
                            
                            # 4. REMOTE CONTROL: Execute Cloud Server Commands
                            if result.get("status") == "success":
                                slot = result.get("assigned_slot")
                                vtype = result.get("vehicle_type")
                                print(f"<<< CLOUD RESPONSE: AI Classified vehicle as '{vtype}'!")
                                print(f"    COMMAND RECEIVED: {result.get('command')}")
                                print(f"    PHYSICAL ACTION: Activating barrier motor... Proceeding to Slot {slot}!")
                            
                            elif result.get("status") == "full":
                                print("<<< CLOUD COMMAND: DISPLAY_FULL_MESSAGE")
                                print("    PHYSICAL ACTION: Turning on 'Parking Full' LED Screen.")
                            else:
                                print(f"Cloud Server reported an internal error: {result}")
                        else:
                            print(f"Cloud Transmit Failed! HTTP Code: {response.status_code}")
                            
                    except requests.exceptions.ConnectionError:
                        print(f"FATAL: Could not connect to Cloud Server at {CLOUD_SERVER_URL}!")
                        print("Please ensure api.py is running in another terminal tab acting as your Cloud Server.")
                else:
                    print("Error: Edge failed to capture image.")
                    
                # Hardware Cooldown
                print("\nWaiting 10 seconds before polling next vehicle...")
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\nShutting down physical edge node...")
            break

if __name__ == "__main__":
    main()