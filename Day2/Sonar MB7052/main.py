import sonar
import time


while (1): # start endless loop
    distance_cm= sonar.get_sonar_dist()
    print ("Distance (cm)= %4.0f" %distance_cm)
    time.sleep(1)
