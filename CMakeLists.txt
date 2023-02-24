cmake_minimum_required(VERSION 3.1.3)
project(sciunit2-deps NONE)

include(ExternalProject)

set_directory_properties(PROPERTIES EP_BASE build)
set(_LIBEXEC_DIR ${CMAKE_BINARY_DIR}/sciunit2/libexec)
set(_FILES_DIR ${CMAKE_SOURCE_DIR}/files)

ExternalProject_Add(
  ptu
  GIT_REPOSITORY "https://github.com/depaul-dice/provenance-to-use"
  CMAKE_ARGS -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} -DBUILD_TESTING=OFF
  INSTALL_COMMAND install -s <BINARY_DIR>/ptu ${_LIBEXEC_DIR}
)

ExternalProject_Add(
  scripter
  GIT_REPOSITORY "https://github.com/depaul-dice/scripter"
  CMAKE_ARGS -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
  INSTALL_COMMAND install -s <BINARY_DIR>/scripter ${_LIBEXEC_DIR}
)

ExternalProject_Add(
  vvpkg
  GIT_REPOSITORY "https://github.com/depaul-dice/sciunit-dedup"
  GIT_TAG "1234d4c"
  PATCH_COMMAND ${GIT_EXECUTABLE} apply ${_FILES_DIR}/vv-report-size.patch
  CMAKE_ARGS -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
  INSTALL_COMMAND install -s <BINARY_DIR>/demo/vv ${_LIBEXEC_DIR}
  TEST_COMMAND <BINARY_DIR>/tests/run
)

ExternalProject_Add_Step(vvpkg before_stash
  COMMAND git config user.email "zhihao.yuan@depaul.edu"
  COMMAND git config user.name "Zhihao Yuan"
  DEPENDEES download
  DEPENDERS update
  WORKING_DIRECTORY <SOURCE_DIR>
)
