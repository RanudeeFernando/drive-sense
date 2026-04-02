import os
import time
import requests
import cv2
import numpy as np

# Cloud Server Configuration
CLOUD_SERVER_URL = "http://localhost:8001"

def create_mock_vehicle_image(filename="mock_vehicle.jpg"):
    """Generates a dummy image mimicking a captured camera frame."""
    print(f"[1/4] Generating mock hardware camera capture: {filename}")
    # Create an RGB image (BGR in OpenCV)
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:] = (255, 0, 0) # Solid blue square as a "vehicle"
    cv2.imwrite(filename, img)
    return filename

def run_test():
    print("==============================================")
    print("    DRIVESENSE: LOCAL CLOUD-EDGE LOOP TEST    ")
    print("==============================================\n")

    # Step A: Verify server is running
    print("[2/4] Verifying connection to local Cloud Server API...")
    try:
        res = requests.get(f"{CLOUD_SERVER_URL}/api/slots")
        if res.status_code == 200:
            print("      SUCCESS: Cloud server is UP and reachable.")
            print(f"      Initial Slots DB State: {res.json()}")
        else:
            print(f"      FAILED: Server returned {res.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("      FAILED: Could not connect to local Cloud Server.")
        print("      ACTION REQUIRED: Please start your Cloud Server first.")
        print("      Command: uvicorn api:app --host 0.0.0.0 --port 8001")
        return

    # Step B: Generate image
    image_path = create_mock_vehicle_image()
    
    # Step C: Send Payload
    print("\n[3/4] Transmitting mock image data to /api/detect_vehicle...")
    try:
        with open(image_path, "rb") as image_file:
            files = {"image": (os.path.basename(image_path), image_file, "image/jpeg")}
            start_time = time.time()
            response = requests.post(f"{CLOUD_SERVER_URL}/api/detect_vehicle", files=files)
            end_time = time.time()
            
        latency = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"      SUCCESS: Payload processed in {latency:.1f}ms")
            print(f"      Response Dictionary: {result}")
            
            if result.get("status") == "success":
                print("\n   => HW/SW INTEGRATION PASSED!")
                print(f"      AI Classified Vehicle: '{result.get('vehicle_type')}'")
                print(f"      Assigned Parking Slot: '{result.get('assigned_slot')}'")
                print(f"      Hardware Command:      '{result.get('command')}'")
            elif result.get("status") == "full":
                print("\n   => SYSTEM PARKING IS FULL.")
                print("      No open slot for this vehicle.")
            else:
                print(f"\n   => Error reported by API: {result}")
        else:
            print(f"      FAILED to process. HTTP Status {response.status_code}")
            print(f"      Details: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
         print(f"      FAILED: Connection Error during data transmission - {e}")

    # Step D: Final DB check
    print("\n[4/4] Verifying real-time updates pushed downstream...")
    try:
        res = requests.get(f"{CLOUD_SERVER_URL}/api/slots")
        if res.status_code == 200:
            print("      SUCCESS: Real-time Data state retrieved!")
            print(f"      Updated Slots DB State: {res.json()}")
    except Exception as e:
        print(f"      FAILED to retrieve final slot updates: {e}")
        
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)
    
    print("\n==============================================")
    print("                TEST FINISHED                 ")
    print("==============================================")

if __name__ == "__main__":
    run_test()
