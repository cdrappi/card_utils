cmake_minimum_required(VERSION 3.12)
project(CardGames)

set(CMAKE_CXX_STANDARD 17)

add_subdirectory(lib/pybind11)

file(GLOB LIBRARY_SOURCES "CardGames.hpp" "src/main.cpp" "src/deck/*.cpp" "src/gin/*.cpp")
add_library(CardGames ${LIBRARY_SOURCES})
set_target_properties(CardGames PROPERTIES CXX_VISIBILITY_PRESET hidden)

# Generate Python module.
file(GLOB PYBIND_SOURCES "CardGames.hpp" "src/deck/*.cpp" "src/gin/*.cpp")
pybind11_add_module(card_games ${PYBIND_SOURCES})
