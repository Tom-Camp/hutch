# Hutch Lights

## Micropython hutch (cabinet) lighting

A simple program to light a liquor cabinet using a [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/)
a [reed switch](https://www.explainthatstuff.com/howreedswitcheswork.html), and LEDs using
[Micropython](https://micropython.org/). The code uses the [Pico PIO](https://www.raspberrypi.com/news/what-is-pio/).
It probably doesn't need to, but, you know, why not? The light(s) willl go off if the door is closed,
but is also on a timer so the light(s) will go out after 60 seconds if the door is left open.

### Installing

- [Install Micropython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
- Once Micropython is installed copy the contents of the `main.py` to `main.py` on the Pico.
- Wire the reed switch GPIO pin 2.
  - Wire a 10k ohm pull up resistor from the 3.3V pin to pin 16
- Wire any LEDs to GPIO pin 6

That's it. Plug it in and call it good.

### Built with

- [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/)
- [Micropython](https://micropython.org/)
- [Reed switch](https://www.adafruit.com/product/375)
- [LEDs](https://www.adafruit.com/product/1622)

### Authors

- Tom Camp - _initial work_ - [Tom-Camp](https://github.com/Tom-Camp)

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
