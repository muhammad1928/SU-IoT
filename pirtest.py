from gpiozero import MotionSensor

pir = MotionSensor(12, hold_time=2)  # Define the GPIO pin number for the PIR sensor

while True:
    print("Scanning for motions...")
    if pir.motion_detected:
        print("Motion detected! Lamp is on.")
    else:
        print("No motion detected. Lamp is off.")
        
    



# import time
# import RPi.GPIO as GPIO
# from actuator import turnOn, turnOff

# GPIO.setmode(GPIO.BCM)  # Set the GPIO mode to BCM (Broadcom SOC channel)
# PIR_PIN = 7  # Define the GPIO pin number for the PIR sensor
# GPIO.setup(PIR_PIN, GPIO.IN)  # Set the PIR_PIN as an input pin

# motion_detected = False
# last_motion_time = 0

# try:
#     while True:
#         if GPIO.input(PIR_PIN):  # Check if the PIR sensor detects motion
#             if not motion_detected:
#                 print("Motion Detected!")
#                 turnOn()  # Call the function to turn on the device
#                 motion_detected = True
#             last_motion_time = time.time()
#         else:
#             if motion_detected and (time.time() - last_motion_time > 5):
#                 print("No Motion for 30 seconds, turning off.")
#                 turnOff()  # Call the function to turn off the device
#                 motion_detected = False
#         time.sleep(1)  # Wait for 1 second before checking again
# except KeyboardInterrupt: # press control + c to stop the program
#     print("Quit")
#     GPIO.cleanup()  # Clean up the GPIO settings