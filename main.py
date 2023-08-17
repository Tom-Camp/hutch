from machine import Pin, Timer
from rp2 import PIO, StateMachine, asm_pio
import time


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock).side(0)
    mov(x, osr)  # Keep most recent pull data stashed in X, for recycling by noblock
    mov(y, isr)  # ISR must be preloaded with PWM count max
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop().side(1)
    label("skip")
    jmp(y_dec, "pwmloop")


class PIOPWM:

    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(sm_id, pwm_prog, freq=2 * count_freq, sideset_base=Pin(pin))
        # Use exec() to load max count into ISR
        self._sm.put(max_count)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count

    def set(self, value):
        # Minimum value is -1 (completely turn off), 0 actually still produces narrow pulse
        value = max(value, -1)
        value = min(value, self._max_count)
        self._sm.put(value)


class Lighting:

    def __init__(self):
        self.light_status: bool = False
        self.timeout: bool = False
        self.pwm = PIOPWM(0, 15, max_count=(1 << 16) - 1, count_freq=10_000_000)
        self.light_timer = Timer()

    def light_on(self):
        for i in range(256):
            self.pwm.set(i ** 2)
            time.sleep(0.01)
        self.set_status(True)
        self.light_timer.init(mode=Timer.ONE_SHOT, period=10000, callback=light.light_off)

    def light_off(self, timer: Timer):
        print("off")
        self.set_timeout(True)
        self.pwm.set(-1)
        self.set_status(False)

    def set_timeout(self, value: bool):
        self.timeout = value

    def set_status(self, value: bool):
        self.light_status = value


door = Pin(16, mode=Pin.IN, pull=Pin.PULL_UP)
light = Lighting()
while True:
    if door.value() > 0 and not light.timeout and not light.light_status:
        light.light_on()
    else:
        light.light_timer.deinit()
        light.set_timeout(False)
        light.pwm.set(-1)
    time.sleep(1)
