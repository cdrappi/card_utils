cmake_minimum_required(VERSION 3.12)
project(CardGames)

set(CMAKE_CXX_STANDARD 17)

# Collect source files into the SOURCES variable
file(GLOB SOURCES "CardGames.hpp" "src/deck/*.cpp" "src/gin/*.cpp")

add_library(CardGames ${SOURCES})

set_target_properties(CardGames PROPERTIES CXX_VISIBILITY_PRESET hidden)
