n = 3
sum_val1 = 0
ref1 = 0
ref2 = 0
try:
    while n:
        # Enable and read from the first sensor
        set_gpio_state(xshut_pin_1, GPIO.HIGH)
        set_gpio_state(xshut_pin_2, GPIO.LOW)
        vl53l0x_1 = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)
        set_sensor_state(vl53l0x_1, True)
        distance_1 = vl53l0x_1.range
        sum_val1 += distance_1
        # Enable and read from the second sensor

        set_gpio_state(xshut_pin_1, GPIO.LOW)
        set_gpio_state(xshut_pin_2, GPIO.HIGH)
        vl53l0x_1 = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)
        set_sensor_state(vl53l0x_1, True)
        distance_2 = vl53l0x_1.range
        sum_val2 += distance_2

        n -= 1

        time.sleep(0.1)
    else:
        avg_val1 = sum_val1 // 3
        avg_val2 = sum_val2 // 3
        if (not plain_ref1(avg_val1)) or (not plain_ref2(avg_val2)):
            comp1 = avg_val1 - ref1
            comp2 = avg_val2 - ref2
            if comp1 < 0 or comp2 < 0:
                speak_text("elevation ahead")
                buzz(2)
            if comp1 > 0 or comp2 > 0:
                speak_text("depression ahead")
                buzz(2)