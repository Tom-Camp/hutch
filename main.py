import time

from machine import Pin, Timer
from rp2 import PIO, StateMachine, asm_pio


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock).side(0)  # noqa F821
    mov(x, osr)  # noqa F821
    mov(y, isr)  # noqa F821
    label("pwmloop")  # noqa F821
    jmp(x_not_y, "skip")  # noqa F821
    nop().side(1)  # noqa F821
    label("skip")  # noqa F821
    jmp(y_dec, "pwmloop")  # noqa F821


class PIOPWM:
    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(
            sm_id, pwm_prog, freq=2 * count_freq, sideset_base=Pin(pin)
        )
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
        self.status: bool = False
        self.timeout: bool = False
        self.pwm = PIOPWM(0, 15, max_count=(1 << 16) - 1, count_freq=10_000_000)

    def light_on(self):
        for i in range(256):
            self.pwm.set(i**2)
            time.sleep(0.01)
        self.set_status(True)

    def off(self):
        self.set_status(False)
        for i in reversed(range(256)):
            self.pwm.set(i**2)
            time.sleep(0.01)
        self.pwm.set(-1)

    def light_off(self):
        self.set_timeout(False)
        self.off()

    def light_timeout(self, timer: Timer):
        self.set_timeout(True)
        self.off()

    def set_timeout(self, value: bool):
        self.timeout = value

    def set_status(self, value: bool):
        self.status = value


door = Pin(16, mode=Pin.IN, pull=Pin.PULL_UP)
light = Lighting()
lit = Timer()
while True:
    if door.value() > 0 and not light.status:
        if not light.timeout:
            print("Door opened. Turning light on")
            light.light_on()
            lit.init(mode=Timer.ONE_SHOT, period=20000, callback=light.light_timeout)
            print(lit)
    elif door.value() == 0:
        light.set_timeout(False)
        if light.status:
            print("Door closed. Turning light off")
            lit.deinit()
            light.light_off()
    time.sleep(0.5)
