# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT tfm_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT tfm_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND tfm_python_files
    python_bindings.cc)

GR_PYBIND_MAKE_OOT(tfm
   ../../..
   gr::tfm
   "${tfm_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(TARGET tfm_python POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:tfm_python>
    ${PROJECT_BINARY_DIR}/test_modules/gnuradio/tfm/
)

install(TARGETS tfm_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/tfm COMPONENT pythonapi)
