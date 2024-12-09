#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Wondmagegn Rahmeto.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
import os
from datetime import datetime
from gnuradio import gr, blocks

class power_comparator_ff(gr.sync_block):
    """
    docstring for block power_comparator_ff
    """
    def __init__(self, sample_rate, center_frequency, vector_length, directory, mode, diff_fixed_dBm, diff_percentage):
        self.vlen = vector_length
        self.samp_rate = sample_rate
        self.center_freq = center_frequency
        self.freq_delta = sample_rate / (vector_length-1)
        self.directory = directory
        self.mode = mode
        self.diff_dBm = diff_fixed_dBm
        self.diff_percentage = diff_percentage
        gr.sync_block.__init__(self,
            name="power_comparator_ff",
            in_sig=[(numpy.float32,self.vlen)],
            out_sig=None)
            
    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
    
    def set_directory(self, directory):
        self.directory = directory
    
    def set_center_freq(self, center_frequency):
        self.center_freq = center_frequency
        
    def set_fft_size(self, fft_size):
        self.vlen = fft_size
    
    def set_mode(self, mode):
        self.mode = mode
        
    def set_diff_percentage(self, diff_percentage):
        print("set Diff %")
        print(diff_percentage)
        self.diff_percentage = diff_percentage
        
    def set_diff_dBm(self, diff_fixed_dBm):
        print("Set Diff dBm")
        print(diff_fixed_dBm)
        self.diff_fixed_dBm = diff_fixed_dBm
        self.diff_dBm = diff_fixed_dBm

    def work(self, input_items, output_items):
        #in0 = input_items[0]
        file_base_power = "power_%.0fMHz_%.0fMsps_%dFFT"%(self.center_freq // 1e6, self.samp_rate // 1e6, self.vlen)
        file_base_compare = "compare_%.0fMHz_%.0fMsps_%dFFT"% (self.center_freq // 1e6, self.samp_rate // 1e6, self.vlen)
        filename_power = "{dir}/{file_power}.txt".format(dir=self.directory, file_power=file_base_power)
        filename_result = "{dir}/{file_result}.txt".format(dir=self.directory, file_result=file_base_compare)
        filename_power_temp = "{dir}/{file_power}_tmp.txt".format(dir=self.directory, file_power=file_base_power)
        filename_result_temp = "{dir}/{file_result}_tmp.txt".format(dir=self.directory, file_result=file_base_compare)
        filename_log = "{dir}/log.txt".format(dir=self.directory)
        in0 = input_items[0]
        #print(in0)
        start_freq = self.center_freq - self.samp_rate / 2
        log_file = open(filename_log, 'a+')
        log_file.write(datetime.now().strftime('%Y%m%d %H:%M:%S:%f')+" ")
        log_file.write("files: " + filename_power+";" + filename_result + "\n")
        for i, value in enumerate(in0):
            iterator = numpy.nditer(value, flags=['f_index'])
            file_power_exists = False
            try:
                file_power = open(filename_power, 'r')
                file_power_exists = True
                
            except IOError:
                file_power = open(filename_power, 'w+')
                log_file.write(datetime.now().strftime('%Y%m%d %H:%M:%S:%f')+" ")
                log_file.write("No database file for {file}\n".format(file=file_base_power))
                return 0
                
            #iterator = numpy.nditer(value, flags=['f_index'])
              #we must read this value because is the first line of the file. not needed for processing.
            file_power_index = 0
            if file_power_exists:
                try:
                    file_power_index = float(file_power.readline()) #read number of values per row of powers
                except Exception:
                    #file_power_index = 0
                    log_file.write("file power exception\n")
                    
            temp_power_file = open(filename_power_temp, 'w+')
            temp_power_file.write("%f\n" % (file_power_index+1))
            file_result_exists = False
            try:
                file_result = open(filename_result, 'r')
                file_result_exists = True
            except IOError:
                file_result = open(filename_result, 'w+')
            file_result_index = 0
            if file_result_exists:
                try:
                    file_result_index = float(file_result.readline()) #read number of values per row of results
                except Exception:
                    file_result_index = 0
            temp_file = open(filename_result_temp, 'w+')
            temp_file.write("%.0f\n" % (file_result_index+1))
            while not iterator.finished:
                current_freq = (iterator.index * self.freq_delta) + start_freq
                cached_power = 1000
                if file_power_exists:
                    try:
                        line = file_power.readline()
                        cached_power = float(line.split("@")[0]) #read database power
                        print(cached_power)
                    except Exception:
                        #cached_power = 1000
                        log_file.write(datetime.now().strftime('%Y%m%d %H:%M:%S:%f')+" ")
                        log_file.write("cached_power exception\n")
                power = iterator[0]
                
                data = "default"
                exceeded_number = 0
                exceeded_average = 0
                exceeded_diff_min = 10000
                exceeded_diff_average = 0
                exceeded_diff_max = 0
                
                #if cached_power != 1000:
                #    power = ((cached_power * file_power_index) + power) / (file_power_index+1)
                #temp_power_file.write("%.2f@%.6f" % (power, current_freq/1e6))
                
                if file_result_exists:
                    try:
                        line = file_result.readline()
                        data = line.split("@")[0]
                        values = data.split(";")
                        exceeded_number = float(values[0])
                        exceeded_average = float(values[1])
                        exceeded_diff_min = float(values[2])
                        exceeded_diff_average = float(values[3])
                        exceeded_diff_max = float(values[4])
                    except Exception:
                        nodata = True
                exceeded_diff = 0
                if self.mode ==  1:  #percentage
                    threshold = cached_power*(1+self.diff_percentage/100)
                    
                else:  #fixed dBm
                    threshold = cached_power + self.diff_dBm
                if power > threshold:
                    exceeded_diff = power - cached_power
                    exceeded_diff_min = numpy.minimum(exceeded_diff_min, exceeded_diff)
                    exceeded_diff_average = ((exceeded_diff_average * exceeded_number) + exceeded_diff) / (exceeded_number+1)
                    exceeded_number = exceeded_number+1
                    exceeded_diff_max = numpy.maximum(exceeded_diff_max, exceeded_diff)
                
                exceeded_average = exceeded_number/(file_result_index+1)
                
                temp_power_file.write("%.2f@%.6f" % (power, current_freq/1e6))
                
                temp_file.write("%.0f;%.2f;%.2f;%.2f;%.2f@%.6f" % (exceeded_number, exceeded_average, exceeded_diff_min, exceeded_diff_average, exceeded_diff_max, current_freq/1e6))
                
                if (iterator.index != self.vlen-1):
                    temp_power_file.write("\n")
                    
                    temp_file.write("\n")
                
                iterator.iternext()
            file_power.close()
            file_result.close()
            temp_power_file.close()
            temp_file.close()
            os.remove(filename_power)
            os.remove(filename_result)
            os.rename(filename_power_temp, filename_power)
            os.rename(filename_result_temp, filename_result)
        log_file.close()
        return len(input_items[0])
