# ----------------------------------------------------------------------------
PROJECT(pySpline LANGUAGES Fortran C)
# ----------------------------------------------------------------------------
CMAKE_MINIMUM_REQUIRED(VERSION 3.14)

# -- I/O
# Build type
IF(NOT CMAKE_BUILD_TYPE)
    SET(CMAKE_BUILD_TYPE "Release" CACHE STRING 
         "Choose the type of build, options are: None Debug Release RelWithDebInfo MinSizeRel."
         FORCE)
ENDIF(NOT CMAKE_BUILD_TYPE)

# -- Fortran
# Compile/Link flags
IF(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
    SET(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -fdefault-real-8 -fPIC -std=f2008")
    IF(NOT APPLE)
        SET(CMAKE_SHARED_LINKER_FLAGS "-fPIC -shared")
    ELSE()
        SET(CMAKE_SHARED_LINKER_FLAGS "-fPIC -dynamiclib -single_module -undefined dynamic_lookup -multiply_defined suppress")
    ENDIF()
ELSEIF(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
    IF(NOT WIN32)
        SET(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -r8 -fPIC -stand f08")
        SET(CMAKE_SHARED_LINKER_FLAGS "-fPIC -shared")
    ELSE()
        SET(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} /4R8 /stand:f08")
    ENDIF()
ELSE()
    MESSAGE(FATAL_ERROR "No definitions found for CMAKE_Fortran_COMPILER_ID=${CMAKE_Fortran_COMPILER_ID}")
ENDIF()

# -- C
# Standard
SET(CMAKE_C_STANDARD 11)
SET(CMAKE_C_STANDARD_REQUIRED ON)
# Compile flags
IF(CMAKE_C_COMPILER_ID MATCHES "GNU")
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC -Wall")
ELSEIF(CMAKE_C_COMPILER_ID MATCHES "MSVC")
	ADD_DEFINITIONS(-D_USE_MATH_DEFINES) # otherwise M_PI is undefined
	SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /MP") # parallel build
ENDIF()

# -- DEPENDENCIES
# Python
# use Python3_ROOT_DIR if wrong python found (e.g. anaconda)
FIND_PACKAGE(Python COMPONENTS Interpreter Development NumPy)

# -- OUTPUT
# Copy files for f2py and get include dirs
CONFIGURE_FILE("${CMAKE_SOURCE_DIR}/src/f2py/f2py_f2cmap.ref" "${CMAKE_CURRENT_BINARY_DIR}/.f2py_f2cmap" COPYONLY)
CONFIGURE_FILE("${CMAKE_SOURCE_DIR}/src/f2py/pyspline.pyf" "${CMAKE_CURRENT_BINARY_DIR}/pyspline.pyf" COPYONLY)
CONFIGURE_FILE("${CMAKE_SOURCE_DIR}/src/f2py/importTest.py" "${CMAKE_CURRENT_BINARY_DIR}/importTest.py" COPYONLY)
EXECUTE_PROCESS(COMMAND "${Python_EXECUTABLE}" -c "import numpy.f2py; print(numpy.f2py.get_include())" OUTPUT_VARIABLE F2PY_INCLUDE_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
STRING(REPLACE "\\" "/" F2PY_INCLUDE_DIR "${F2PY_INCLUDE_DIR}")
# Compile static library from source
FILE(GLOB SRCS src/*.f90 src/*.F90)
ADD_LIBRARY(spline STATIC ${SRCS})
# Execute f2py
ADD_CUSTOM_TARGET(f2py)
ADD_CUSTOM_COMMAND(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/libsplinemodule.c" "${CMAKE_CURRENT_BINARY_DIR}/libspline-f2pywrappers2.f90" COMMAND ${Python_EXECUTABLE} -m "numpy.f2py" "${CMAKE_CURRENT_BINARY_DIR}/pyspline.pyf")
# Compile shared library from f2py output and link to static lib
ADD_LIBRARY(libspline SHARED "${CMAKE_CURRENT_BINARY_DIR}/libsplinemodule.c" "${CMAKE_CURRENT_BINARY_DIR}/libspline-f2pywrappers2.f90" "${F2PY_INCLUDE_DIR}/fortranobject.c")
IF(WIN32)
    TARGET_COMPILE_DEFINITIONS(libspline PUBLIC UPPERCASE_FORTRAN NO_APPEND_FORTRAN)
	SET_TARGET_PROPERTIES(libspline PROPERTIES SUFFIX .pyd)
ELSE()
	SET_TARGET_PROPERTIES(libspline PROPERTIES PREFIX "")
ENDIF()
TARGET_INCLUDE_DIRECTORIES(libspline PRIVATE ${F2PY_INCLUDE_DIR})
TARGET_LINK_LIBRARIES(libspline spline Python::NumPy)
INSTALL(TARGETS libspline DESTINATION ${PROJECT_SOURCE_DIR}/pyspline)
# Test
ADD_CUSTOM_TARGET(test ALL DEPENDS libspline)
ADD_CUSTOM_COMMAND(TARGET test POST_BUILD COMMAND ${Python_EXECUTABLE} "importTest.py")

# -- PRINT
MESSAGE(STATUS "PROJECT: ${CMAKE_PROJECT_NAME}")
MESSAGE(STATUS "* SYSTEM NAME=\"${CMAKE_SYSTEM_NAME}\"")
MESSAGE(STATUS "* FORTRAN COMPILER: ${CMAKE_Fortran_COMPILER_ID}")
MESSAGE(STATUS "* CXX COMPILER: ${CMAKE_CXX_COMPILER_ID}")
MESSAGE(STATUS "* CXX STANDARD: ${CMAKE_CXX_STANDARD}")
MESSAGE(STATUS "* BUILD TYPE: ${CMAKE_BUILD_TYPE}")
