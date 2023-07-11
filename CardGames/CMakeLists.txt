cmake_minimum_required(VERSION 3.12)
project(CardGames)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

add_subdirectory(lib/pybind11)
include_directories(/opt/homebrew/include)
link_directories(/opt/homebrew/lib)

file(GLOB LIBRARY_SOURCES "CardGames.hpp" "src/btree/*.cpp" "src/deck/*.cpp" "src/gin/*.cpp")
add_library(CardGames ${LIBRARY_SOURCES})
set_target_properties(CardGames PROPERTIES CXX_VISIBILITY_PRESET hidden)

# Generate Python module.
file(GLOB PYBIND_SOURCES "src/main.cpp" "src/btree/*.cpp" "src/deck/*.cpp" "src/gin/*.cpp")
pybind11_add_module(card_games ${PYBIND_SOURCES})
target_link_libraries(card_games PRIVATE -lprofiler)
