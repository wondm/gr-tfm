#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Wondmagegn Rahmeto.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from __future__ import division

from gnuradio import gr
from gnuradio import blocks
from gnuradio import fft as FFT_lib
import sys, math

try:
    from gnuradio import filter
except ImportError:
    sys.stderr.write('logpwrfft_win required gr-filter.\n')
    sys.exit(1)

class logpowerfft_win(gr.hier_block2):
    """
    docstring for block logpowerfft_win
    """
    def __init__(self,  sample_rate, fft_size, ref_scale, frame_rate):
        gr.hier_block2.__init__(self,
            "logpowerfft_win",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),          # Input signature
            gr.io_signature(1, 1, gr.sizeof_float * fft_size))    # Output signature
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.ref_scale = ref_scale
        self.frame_rate = frame_rate

            # Define blocks and connect them
           #self.connect()
        self._sd = blocks.stream_to_vector_decimator(item_size=gr.sizeof_gr_complex, 
                                    sample_rate=sample_rate,
                                    vec_rate=frame_rate,
                                    vec_len=fft_size)
       #if win is None:
        #win = window.hamming
        
        #sys.setrecursionlimit(5000)
        fft_window = FFT_lib.window.hamming(fft_size)
        fft = FFT_lib.fft_vcc(fft_size, True, fft_window, True)
        #print("eeeeeeeeeeeeeeeeeee",window.WIN_HAMMING)        
        window_power = sum([x * x for x in fft_window])
        
        c2magsq = blocks.complex_to_mag_squared(fft_size)
        self._avg = filter.single_pole_iir_filter_ff(1.0, fft_size)
        self._log = blocks.nlog10_ff(10, fft_size, 
                           -20*math.log10(fft_size)
                               -10*math.log10(float(window_power) / fft_size)
                               -20*math.log10(float(ref_scale) /2))
        self.connect(self, self._sd, fft, c2magsq, self._avg, self._log, self)
    def set_decimation(self, decim):
        self._sd.set_decimation(decim)
    
    def set_vec_rate(self, vec_rate):
        self._sd.set_vec_rate(vec_rate)
    
    def set_sample_rate(self, sample_rate):
        self._sd.set_sample_rate(sample_rate)
    
    def set_average(self, average):
        self._average = average
        if self._average:
            self._avg.set_taps(self._avg_alpha)
        else:
            self._avg.set_taps(1.0)
    
    def set_avg_alpha(self, avg_alpha):
        self._avg_alpha = avg_alpha
        self.set_average(self._average)
    
    def sample_rate(self):
        return self._sd.sample_rate()
    
    def decimation(self):
        return self._sd.decimation()
    
    def frame_rate(self):
        return self._sd.frame_rate()
    
    def average(self):
        return self._average
    
    def avg_alpha(self):
        return self._avg_alpha
