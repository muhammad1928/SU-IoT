from gpiozero import MotionSensor

pir = MotionSensor(12)

while True:
    print("Scanning for motions...")
    pir.wait_for_motion()

    print("Motion detected!")
    pir.wait_for_no_motion()
    


    print("no motion detected.")