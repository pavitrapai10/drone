import serial
ser = serial.Serial('COM15', 9600, timeout=1)
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            # print(line)
            
            # Split the line into key and value based on ':'
            key_value = line.split(':')
            
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                
                # Assign variables based on key
                if key == 'Battery Voltage':
                    battery_voltage = float(value)
                    print(f"Battery Voltage: {battery_voltage}")
                elif key == 'Roll':
                    roll = float(value)
                    print(f"Roll: {roll}")
                elif key == 'Pitch':
                    pitch = float(value)
                    print(f"Pitch: {pitch}")
                elif key == 'Heading':
                    heading = float(value)
                    print(f"Heading: {heading}")
                elif key == 'Number of Satellites':
                    num_satellites = int(value)
                    print(f"Number of Satellites: {num_satellites}")
                elif key == 'Main Mode':
                    mainmode = str(value)
                    print(f"Mode: {mainmode}")
                elif key == 'Sub Mode':
                    submode = str(value)
                    print(f"Mode: {submode}")
                elif key == 'Error':
                    error = int(value)
                    print(f"Error: {error}")
                elif key == 'GPS':
                    gps = bool(value)
                    print(f"GPS Status: {gps}")
                elif key == 'Latitude':
                    latitude = float(value)
                    print(f"Latitude: {latitude}")
                elif key == 'Longitude':
                    longitude = float(value)
                    print(f"Longitude: {longitude}")
                elif key == 'Altitude':
                    altitude = float(value)
                    print(f"Altitude: {altitude}")
                elif key == 'Distance Right':
                    distance_right = int(value)
                    print(f"Distance Right: {distance_right}")
                elif key == 'Distance Left':
                    distance_left = int(value)
                    print(f"Distance Left: {distance_left}")
                elif key == 'Distance Upper':
                    distance_upper = int(value)
                    print(f"Distance Upper: {distance_upper}")
                elif key == 'Armed or Not':  
                    armed = str(value)
                    print(f"Armed or Not: {armed}")
                     
                    
except KeyboardInterrupt:
    print("Exiting program")
finally:
    ser.close()
    

