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


def light_on():
    for i in range(256):
        pwm.set(i ** 2)
        time.sleep(0.01)
    light_status = True


def light_off(timer: Timer):
    print("off")
    timeout = True
    pwm.set(-1)
    light_status = False


pwm = PIOPWM(0, 15, max_count=(1 << 16) - 1, count_freq=10_000_000)

light_status: bool = False
timeout: bool = False
light_on_timer = Timer()

door = Pin(16, mode=Pin.IN, pull=Pin.PULL_UP)
while True:
    if door.value() > 0 and not timeout:
        print("Open")
        light_on()
        light_on_timer.init(mode=Timer.ONE_SHOT, period=10000, callback=light_off)
        print(light_status)
        print(timeout)
    else:
        light_on_timer.deinit()
        timeout = False
        pwm.set(-1)
    time.sleep(1)
