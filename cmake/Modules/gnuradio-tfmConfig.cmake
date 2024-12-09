find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_TFM gnuradio-tfm)

FIND_PATH(
    GR_TFM_INCLUDE_DIRS
    NAMES gnuradio/tfm/api.h
    HINTS $ENV{TFM_DIR}/include
        ${PC_TFM_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_TFM_LIBRARIES
    NAMES gnuradio-tfm
    HINTS $ENV{TFM_DIR}/lib
        ${PC_TFM_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-tfmTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_TFM DEFAULT_MSG GR_TFM_LIBRARIES GR_TFM_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_TFM_LIBRARIES GR_TFM_INCLUDE_DIRS)
