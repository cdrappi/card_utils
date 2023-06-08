cmake_minimum_required(VERSION 3.12)
project(CardGames)

set(CMAKE_CXX_STANDARD 17)

# add_subdirectory(lib/pybind11)

# Collect source files into the SOURCES variable
file(GLOB SOURCES "src/CardGames.h" "src/deck/*.cpp" "src/gin/*.cpp")

# Add a library target
# pybind11_add_module(card_games ${SOURCES})

add_library(CardGames ${SOURCES})
