import cv2
import serial
import time
from ultralytics import YOLO

# --- 1. CONNECT TO ARDUINO ---
try:
    arduino = serial.Serial('COM5', 9600, timeout=1)
    time.sleep(2)
    print("✅ Connected to Arduino!")
except:
    print("❌ Cannot find Arduino. Check COM port.")
    arduino = None

# --- 2. LOAD AI MODEL & CAMERA ---
model_path = r"ai_model\runs\detect\sortx_v1\weights\best.pt"
model = YOLO(model_path)

cap = cv2.VideoCapture(2)  

last_command_time = 0
cooldown = 2.5  

# --- ⚙️ SIZE THRESHOLD ---
WIDTH_THRESHOLD = 90

# --- 3. REAL-TIME LOOP ---
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 👉 Get the dimensions of your screen
    screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 👉 THE HORIZONTAL LINE: Placed 60% of the way down the screen
    tripwire_y = int(screen_height * 0.6) 

    results = model(frame, conf=0.80, verbose=False)
    current_time = time.time()

    if arduino and (current_time - last_command_time > cooldown):

        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            
            width = int(x2 - x1)
            
            # 👉 Get the BOTTOM edge of the tomato (y2)
            tomato_bottom_y = int(y2)

            # 👉 THE TRIPWIRE TRIGGER: If the bottom of the tomato crosses the horizontal line
            if tomato_bottom_y > tripwire_y:

                print(f"🔥 CROSSED THE LINE! Actual Pixel Width: {width}")
                
                if width < WIDTH_THRESHOLD:
                    print(f"🍅 SMALL CALIBRE (Crossed Line) → Sending '1'")
                    arduino.write(b'1')
                else:
                    print(f"🍅 BIG CALIBRE (Crossed Line) → Sending '2'")
                    arduino.write(b'2')

                last_command_time = current_time
                break  

    annotated_frame = results[0].plot()

    # 👉 Draw a visible GREEN HORIZONTAL LINE across the screen
    cv2.line(annotated_frame, (0, tripwire_y), (screen_width, tripwire_y), (0, 255, 0), 2)
    cv2.putText(annotated_frame, "TRIPWIRE (AI MEASURES HERE)", (10, tripwire_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("SortX - Live Dashboard", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()