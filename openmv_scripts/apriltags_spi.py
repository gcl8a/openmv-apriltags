# AprilTags Pixy I2C Emulation Script
#
# This script allows your OpenMV Cam to transmit AprilTag detection data like
# a Pixy (CMUcam5) tracking colors in I2C mode. This script allows you to
# easily replace a Pixy (CMUcam5) color tracking sensor with an OpenMV Cam
# AprilTag tracking sensor. Note that this only runs on the OpenMV Cam M7.
#
# P4 = SCL
# P5 = SDA
#
# Note: The tag family is TAG36H11. Additionally, in order to for the
#       signature value of a tag detection to be compatible with pixy
#       interface libraries all tag ids have 8 added to them in order
#       to move them in the color code signature range. Finally, tags
#       are all reported as color code blocks...

# Comm Parameters ############################################################

max_blocks = 255
max_blocks_per_id = 255

##############################################################################

###
# Changed to using rpc.put_bytes, which has a little more control
# Plan is to make it report back the number
###

import image, math, pyb, sensor, struct, time
from rpc import rpc_slave

class rpc_spi_peripheral(rpc_slave):
    def __init__(self, cs_pin="P3", clk_polarity=0, clk_phase=0, spi_bus=2):  # private
        self.__pin = pyb.Pin(cs_pin, mode = pyb.Pin.IN, pull = pyb.Pin.PULL_UP)
        self.__polarity = clk_polarity
        self.__clk_phase = clk_phase
        self.__spi = pyb.SPI(spi_bus)
        rpc_slave.__init__(self)
        self._stream_writer_queue_depth_max = 1

    def get_bytes(self, buff, timeout_ms):  # protected
        self._get_short_timeout = self._get_short_timeout_reset
        start = pyb.millis()
        while self.__pin.value():
            if pyb.elapsed_millis(start) >= self._get_short_timeout:
                return None
        self.__spi.init(pyb.SPI.SLAVE, polarity=self.__polarity, phase=self.__clk_phase)
        try:
            self.__spi.send_recv(buff, buff, timeout=timeout_ms)  # SPI.recv() is broken.
        except OSError:
            buff = None
        self.__spi.deinit()
        return buff

    def put_bytes(self, data, timeout_ms):  # protected
        self._put_short_timeout = self._put_short_timeout_reset
        start = pyb.millis()
        while self.__pin.value():
            if pyb.elapsed_millis(start) >= self._put_short_timeout:
                return
        self.__spi.init(pyb.SPI.SLAVE, polarity=self.__polarity, phase=self.__clk_phase)
        try:
            self.__spi.send(data, timeout=timeout_ms)
        except OSError:
            pass
        self.__spi.deinit()



# Camera Setup

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 1000)

# Link Setup

interface = rpc_spi_peripheral()

# Helper Stuff

def checksum(data):
    checksum = 0
    for i in range(0, len(data), 2):
        checksum += ((data[i+1] & 0xFF) << 8) | ((data[i+0] & 0xFF) << 0)
    return checksum & 0xFFFF

def to_object_block_format(tag):
    angle = int((tag.rotation() * 180) / math.pi)
    temp = struct.pack("<hhhhhh", tag.id(), tag.cx(), tag.cy(), tag.w(), tag.h(), angle)
    return struct.pack("<hh12s", 0xAA56, checksum(temp), temp)

# Main Loop

clock = time.clock()
while(True):
    clock.tick()
    img = sensor.snapshot()
    tags = img.find_apriltags(families=image.TAG16H5) # default TAG16H5 family

    # Transmit Tags #

    dat_buf = struct.pack("<b", len(tags))
    interface.put_bytes(dat_buf, timeout_ms = 200)

    if tags and (max_blocks > 0) and (max_blocks_per_id > 0): # new frame

        # sort biggest to smallest
        for tag in sorted(tags, key = lambda x: x.h() * x.w(), reverse = True)[0:max_blocks]:

            dat_buf = to_object_block_format(tag)
            img.draw_rectangle(tag.rect())
            img.draw_cross(tag.cx(), tag.cy())

            # dat_buf += struct.pack("<h", 0x0000)
            # write(dat_buf) # write all data in one packet...
            interface.put_bytes(dat_buf, timeout_ms = 200)

    num_tags = min(len(tags), max_blocks)
    print("%d tags(s) found - FPS %f" % (num_tags, clock.fps()))
