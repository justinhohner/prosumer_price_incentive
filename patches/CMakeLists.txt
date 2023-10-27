option(SAM_SKIP_TOOLS "Skip generating sdktool" OFF)
option(SAM_SKIP_TESTS "Skip building GTest files" OFF)
option(SAMAPI_EXPORT "Export SSC binaries to SAM_api folder for PySAM" ON)
option(SAM_SKIP_AUTOGEN "Skip generating SAMAPI from export_config for PySAM" OFF)
option(SAMPRIVATE "Build NREL version of SAM" OFF)

cmake_minimum_required(VERSION 3.24)

set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")
if (UNIX AND NOT CMAKE_C_COMPILER)
    set(CMAKE_C_COMPILER gcc)
    set(CMAKE_CXX_COMPILER g++)
endif()

if(MSVC)
    set(CMAKE_CONFIGURATION_TYPES "Debug;Release" CACHE STRING "Debug and Release Builds Configured" FORCE)
endif()

Project(system_advisor_model VERSION 1.0.0)

add_subdirectory(lk)
add_subdirectory(wex)
add_subdirectory(ssc)
add_subdirectory(SAM)
if (SAMPRIVATE)
    add_subdirectory(SAM-private)
    add_subdirectory(SAM-private/webupd)
endif()
