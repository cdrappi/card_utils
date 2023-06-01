cmake_minimum_required(VERSION 3.12)
project(CardGames)

set(CMAKE_CXX_STANDARD 14)

add_subdirectory(pybind11)
pybind11_add_module(card_games main.cpp)
