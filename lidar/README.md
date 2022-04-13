# Showcase Code - LiDAR

Todos:

* [ ] Sensor
  * [ ] Figure out how negative numbers are represented and implement in driver
  * [ ] Configure sensor: set detection speed to 1kHz, possibly raise baudrate
* [ ] Servos
  * [x] Write/figure out servo driver
* [ ] Integration
  * [ ] Set up LiDAR driver that controls both sensor and servos
    * [ ] Redo scanning process so that no delay is needed
    * [ ] Add option to scan in different axis order
  * [x] Establish interface for sending data
  * [x] Receive data on the processing end
