"""
 Version: 0.2.0
 Author: Nelio Goncalves Godoi
 E-mail: neliogodoi@yahoo.com.br
 Last Update: 20/03/2018
 Stylized According to PEP8: 18/01/2018
 Based on the work by author Joe Gutting (2014)
    (https://github.com/THP-JOE/Python_SI1145)
"""

import time
from ustruct import unpack

SI1145_PARAM_ADCCOUNTER_511CLK = 0x70
SI1145_PARAM_ADCMUX_LARGEIR = 0x03
SI1145_PARAM_ADCMUX_SMALLIR = 0x00
SI1145_PARAM_ALSIRADCGAIN = 0x1E
SI1145_PARAM_ALSIRADCMISC = 0x1F
SI1145_PARAM_ALSIRADCMISC_RANGE = 0x20
SI1145_PARAM_ALSIRADCMUX = 0x0E
SI1145_PARAM_ALSIRADCOUNTER = 0x1D
SI1145_PARAM_ALSVISADCGAIN = 0x11
SI1145_PARAM_ALSVISADCMISC = 0x12
SI1145_PARAM_ALSVISADCMISC_VISRANGE = 0x20
SI1145_PARAM_ALSVISADCOUNTER = 0x10
SI1145_PARAM_CHLIST = 0x01
SI1145_PARAM_CHLIST_ENALSIR = 0x20
SI1145_PARAM_CHLIST_ENALSVIS = 0x10
SI1145_PARAM_CHLIST_ENAUX = 0x40
SI1145_PARAM_CHLIST_ENPS1 = 0x01
SI1145_PARAM_CHLIST_ENUV = 0x80
SI1145_PARAM_PS1ADCMUX = 0x07
SI1145_PARAM_PSADCGAIN = 0x0B
SI1145_PARAM_PSADCMISC = 0x0C
SI1145_PARAM_PSADCMISC_PSMODE = 0x04
SI1145_PARAM_PSADCMISC_RANGE = 0x20
SI1145_PARAM_PSADCOUNTER = 0x0A
SI1145_PARAM_PSLED12SEL = 0x02
SI1145_PARAM_PSLED12SEL_PS1LED1 = 0x01
SI1145_PARAM_SET = 0xA0
SI1145_PSALS_AUTO = 0x0F
SI1145_REG_COMMAND = 0x18
SI1145_REG_HWKEY = 0x07
SI1145_REG_INTCFG = 0x03
SI1145_REG_INTCFG_INTOE = 0x01
SI1145_REG_IRQEN = 0x04
SI1145_REG_IRQEN_ALSEVERYSAMPLE = 0x01
SI1145_REG_IRQMODE1 = 0x05
SI1145_REG_IRQMODE2 = 0x06
SI1145_REG_IRQSTAT = 0x21
SI1145_REG_MEASRATE0 = 0x08
SI1145_REG_MEASRATE1 = 0x09
SI1145_REG_PARAMRD = 0x2E
SI1145_REG_PARAMWR = 0x17
SI1145_REG_PSLED21 = 0x0F
SI1145_REG_UCOEFF0 = 0x13
SI1145_REG_UCOEFF1 = 0x14
SI1145_REG_UCOEFF2 = 0x15
SI1145_REG_UCOEFF3 = 0x16
SI1145_RESET = 0x01
SI1145_ADDR = 0x60


class SI1145(object):
    """Driver for SI1145 sensor"""

    def __init__(self, i2c=None, addr=SI1145_ADDR):
        if i2c is None:
            raise ValueError('An I2C object is required.')
        self._i2c = i2c
        self._addr = addr
        self._reset()
        self._load_calibration()

    def _read8(self, register):
        result = unpack(
            'B',
            self._i2c.readfrom_mem(
                self._addr, register, 1)
        )[0] & 0xFF
        return result

    def _read16(self, register, little_endian=True):
        result = unpack('BB', self._i2c.readfrom_mem(self._addr, register, 2))
        result = ((result[1] << 8) | (result[0] & 0xFF))
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def _write8(self, register, value):
        value = value & 0xFF
        self._i2c.writeto_mem(self._addr, register, bytes([value]))

    def _reset(self):
        """Device reset"""
        self._write8(SI1145_REG_MEASRATE0, 0x00)
        self._write8(SI1145_REG_MEASRATE1, 0x00)
        self._write8(SI1145_REG_IRQEN, 0x00)
        self._write8(SI1145_REG_IRQMODE1, 0x00)
        self._write8(SI1145_REG_IRQMODE2, 0x00)
        self._write8(SI1145_REG_INTCFG, 0x00)
        self._write8(SI1145_REG_IRQSTAT, 0xFF)
        self._write8(SI1145_REG_COMMAND, SI1145_RESET)
        time.sleep(.01)
        self._write8(SI1145_REG_HWKEY, 0x17)
        time.sleep(.01)

    def _write_param(self, parameter, value):
        self._write8(SI1145_REG_PARAMWR, value)
        self._write8(SI1145_REG_COMMAND, parameter | SI1145_PARAM_SET)
        param_val = self._read8(SI1145_REG_PARAMRD)
        return param_val

    def _load_calibration(self):
        self._write8(SI1145_REG_UCOEFF0, 0x7B)
        self._write8(SI1145_REG_UCOEFF1, 0x6B)
        self._write8(SI1145_REG_UCOEFF2, 0x01)
        self._write8(SI1145_REG_UCOEFF3, 0x00)
        self._write_param(
            SI1145_PARAM_CHLIST,
            SI1145_PARAM_CHLIST_ENUV |
            SI1145_PARAM_CHLIST_ENAUX |
            SI1145_PARAM_CHLIST_ENALSIR |
            SI1145_PARAM_CHLIST_ENALSVIS |
            SI1145_PARAM_CHLIST_ENPS1)
        self._write8(SI1145_REG_INTCFG, SI1145_REG_INTCFG_INTOE)
        self._write8(SI1145_REG_IRQEN, SI1145_REG_IRQEN_ALSEVERYSAMPLE)
        self._i2c.writeto_mem(SI1145_ADDR, SI1145_REG_PSLED21, b'0x03')
        self._write_param(
            SI1145_PARAM_PS1ADCMUX,
            SI1145_PARAM_ADCMUX_LARGEIR)
        self._write_param(
            SI1145_PARAM_PSLED12SEL,
            SI1145_PARAM_PSLED12SEL_PS1LED1)
        self._write_param(SI1145_PARAM_PSADCGAIN, 0)
        self._write_param(
            SI1145_PARAM_PSADCOUNTER,
            SI1145_PARAM_ADCCOUNTER_511CLK)
        self._write_param(
            SI1145_PARAM_PSADCMISC,
            SI1145_PARAM_PSADCMISC_RANGE |
            SI1145_PARAM_PSADCMISC_PSMODE)
        self._write_param(
            SI1145_PARAM_ALSIRADCMUX,
            SI1145_PARAM_ADCMUX_SMALLIR)
        self._write_param(SI1145_PARAM_ALSIRADCGAIN, 0)
        self._write_param(
            SI1145_PARAM_ALSIRADCOUNTER,
            SI1145_PARAM_ADCCOUNTER_511CLK)
        self._write_param(
            SI1145_PARAM_ALSIRADCMISC,
            SI1145_PARAM_ALSIRADCMISC_RANGE)
        self._write_param(SI1145_PARAM_ALSVISADCGAIN, 0)
        self._write_param(
            SI1145_PARAM_ALSVISADCOUNTER,
            SI1145_PARAM_ADCCOUNTER_511CLK)
        self._write_param(
            SI1145_PARAM_ALSVISADCMISC,
            SI1145_PARAM_ALSVISADCMISC_VISRANGE)
        self._write8(SI1145_REG_MEASRATE0, 0xFF)
        self._write8(SI1145_REG_COMMAND, SI1145_PSALS_AUTO)

    @property
    def read_uv(self):
        """Returns the UV index"""
        return self._read16(0x2C, little_endian=True) / 100

    @property
    def read_visible(self):
        """Returns visible + IR light levels"""
        return self._read16(0x22, little_endian=True)

    @property
    def read_ir(self):
        """Returns IR light levels"""
        return self._read16(0x24, little_endian=True)

    @property
    def read_prox(self):
        """Returns "Proximity" - assumes an IR LED is attached to LED"""
        return self._read16(0x26, little_endian=True)
