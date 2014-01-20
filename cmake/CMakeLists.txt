CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(hello)

SET(CMAKE_USE_RELATIVE_PATHS ON)
#SET(SRC_LIST "/src/*.cpp")
#AUX_SOURCE_DIRECTORY("src" SRC_LIST)
#AUX_SOURCE_DIRECTORY("src/3rd" SRC_LIST)
#SET(HED_LIST "include/*.h;src/*.h")

FILE(GLOB_RECURSE SRC_LIST "src/*.cpp")
FILE(GLOB_RECURSE HED_LIST1 "include/*.h")
FILE(GLOB_RECURSE HED_LIST2 "src/*.h")
SET(HED_LIST ${HED_LIST1} ${HED_LIST2})

MESSAGE(STATUS "This is BINARY dir ${PROJECT_BINARY_DIR}")
MESSAGE(STATUS "This is SOURCE dir ${PROJECT_SOURCE_DIR}")
MESSAGE(STATUS "SRC_LIST ${SRC_LIST}")
MESSAGE(STATUS "HED_LIST ${HED_LIST}")

INCLUDE_DIRECTORIES("/include/")
ADD_EXECUTABLE(hello ${SRC_LIST} ${HED_LIST})

################################
#…Ë÷√vs config
if(MSVC)
	set(CMAKE_CXX_FLAGS_DEBUG "/D_DEBUG /D_MBCS /MTd /Zi /Ob0 /Od /RTC1")
	set(CMAKE_CXX_FLAGS_RELEASE "/MT /O2 /Ob2 /D NDEBUG /D_MBCS")
endif()
if(CMAKE_CONFIGURATION_TYPES)
	set(CMAKE_CONFIGURATION_TYPES Debug Release)
	MESSAGE(STATUS "CMAKE_CONFIGURATION_TYPES ${CMAKE_CONFIGURATION_TYPES}")
endif()

MESSAGE(STATUS "CMAKE_CXX_FLAGS_DEBUG ${CMAKE_CXX_FLAGS_DEBUG}")
MESSAGE(STATUS "CMAKE_CXX_FLAGS_RELEASE ${CMAKE_CXX_FLAGS_RELEASE}")

################################
#…Ë÷√vs filter
macro(source_group_by_dir source_files)
    if(MSVC)
        set(sgbd_cur_dir ${CMAKE_CURRENT_SOURCE_DIR})
        foreach(sgbd_file ${${source_files}})
            string(REGEX REPLACE ${sgbd_cur_dir}/\(.*\) \\1 sgbd_fpath ${sgbd_file})
            string(REGEX REPLACE "\(.*\)/.*" \\1 sgbd_group_name ${sgbd_fpath})
            string(COMPARE EQUAL ${sgbd_fpath} ${sgbd_group_name} sgbd_nogroup)
            string(REPLACE "/" "\\" sgbd_group_name ${sgbd_group_name})
            if(sgbd_nogroup)
                set(sgbd_group_name "\\")
            endif(sgbd_nogroup)
            MESSAGE(STATUS "filter ${sgbd_group_name} - ${sgbd_file}")
            source_group(${sgbd_group_name} FILES ${sgbd_file})
        endforeach(sgbd_file)
    endif(MSVC)
endmacro(source_group_by_dir)

set(all_files ${SRC_LIST} ${HED_LIST})
source_group_by_dir(all_files)