cmake_minimum_required(VERSION 3.12)
project(CardGames)

set(CMAKE_CXX_STANDARD 14)

add_subdirectory(pybind11)

add_library(card_games MODULE
    src/main.cpp
    src/deck/card.cpp
    src/gin/gin.cpp
    src/gin/gin_rummy.cpp
)

target_include_directories(card_games PRIVATE src)

target_link_libraries(card_games PRIVATE pybind11::module)

set_target_properties(card_games PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
                                         SUFFIX "${PYTHON_MODULE_EXTENSION}")
