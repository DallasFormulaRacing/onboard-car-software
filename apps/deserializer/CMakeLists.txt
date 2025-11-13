cmake_minimum_required (VERSION 3.23)
project(onboard-can-deserializer)

set(CMAKE_CXX_STANDARD 20)

# Enabling this allows to generate compile_commands.json, useful for clangd LSP support
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(
    #../../libs/libsockcanpp/include/exceptions/
    #../../libs/libsockcanpp/include/can_errors/
    # ../../libs/libsockcanpp/include/
    ../../libs/
)

add_executable(onboard-can-deserializer src/main.cpp)


# Library: libsockcanpp for SocketCAN bindings
if (NOT TARGET sockcanpp)
    # -according to libsockcancpp README: this is only necessary if you *cannot* support C++20
    # -and we do so yay :)
    # IF you need C++11 support:
    # set(sockcanpp_CONCEPT_SUPPORT OFF CACHE BOOL "Force C++ standard back to 11")

    # add_subdirectory(${CMAKE_CURRENT_BUILD_DIR}/../lib/libsockcanpp ${CMAKE_CURRENT_BUILD_DIR}/libsockcanpp)
    add_subdirectory(../../libs/libsockcanpp ${CMAKE_CURRENT_BINARY_DIR}/libsockcanpp)
endif()


target_link_libraries(
    onboard-can-deserializer PRIVATE sockcanpp
)

add_compile_options(
    -Wall
    -Werror
    -Wpedantic
    -Wno-unknown-pragmas
)
