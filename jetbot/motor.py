import atexit
import traitlets
from traitlets.config.configurable import Configurable

import sys

sys.path.append('/opt/nvidia/jetson-gpio/lib/python')
sys.path.append('/opt/nvidia/jetson-gpio/lib/python/Jetson/GPIO')
sys.path.append('/home/nvidia/repositories/nano_gpio/gpio_env/lib/python2.7/site-packages/periphery/')

class Motor(Configurable):

    value = traitlets.Float()
    
    # config
    alpha = traitlets.Float(default_value=1.0).tag(config=True)
    beta = traitlets.Float(default_value=0.0).tag(config=True)

    def __init__(self, driver, channel, *args, **kwargs):
        super(Motor, self).__init__(*args, **kwargs)  # initializes traitlets

        self._motor = driver
        self._channel = channel
        atexit.register(self._release)
        
    @traitlets.observe('value')
    def _observe_value(self, change):
        self._write_value(change['new'])

    def _write_value(self, value):
        """Sets motor value between [-1, 1]"""
        mapped_value = int(255.0 * (self.alpha * value + self.beta))

        if mapped_value < 0:    # 306=パルス幅1.5ms(stop),204=パルス幅1.0ms(forward),408=パルス幅2.0ms(backward)
            self._motor.set_pwm(self._channel,round(306-102*abs(value)))
        else:
            self._motor.set_pwm(self._channel,round(306+102*abs(value)))

    def _release(self):
        """Stops motor by releasing control"""
        self._motor.set_pwm(0,306)
        self._motor.set_pwm(1,306)
