CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(lib_common)

SET(SRC_DIR "${PROJECT_SOURCE_DIR}/../../SHARECODE/src/lib_common")
SET(HED_DIR "${PROJECT_SOURCE_DIR}/../../SHARECODE/include/lib_common")
GET_FILENAME_COMPONENT(SRC_DIR ${SRC_DIR} ABSOLUTE)
GET_FILENAME_COMPONENT(HED_DIR ${HED_DIR} ABSOLUTE)

FILE(GLOB_RECURSE SRC_LIST "${SRC_DIR}/*.cpp")
FILE(GLOB_RECURSE HED_LIST "${HED_DIR}/*.h")

MESSAGE(STATUS "This is BINARY dir ${PROJECT_BINARY_DIR}")
MESSAGE(STATUS "This is SOURCE dir ${PROJECT_SOURCE_DIR}")
MESSAGE(STATUS "This is SRC_DIR ${SRC_DIR}")
MESSAGE(STATUS "This is HED_DIR ${HED_DIR}")
MESSAGE(STATUS "SRC_LIST ${SRC_LIST}")
MESSAGE(STATUS "HED_LIST ${HED_LIST}")

INCLUDE_DIRECTORIES(${HED_DIR})
ADD_LIBRARY(lib_common STATIC ${SRC_LIST} ${HED_LIST})

################################
#设置vs 使用相对路径
IF(CMAKE_USE_RELATIVE_PATHS)
	SET(CMAKE_USE_RELATIVE_PATHS ON CACHE BOOL ON FORCE)
ELSE(CMAKE_USE_RELATIVE_PATHS)
	SET(CMAKE_USE_RELATIVE_PATHS ON)
ENDIF(CMAKE_USE_RELATIVE_PATHS)
MESSAGE(STATUS "CMAKE_USE_RELATIVE_PATHS ${CMAKE_USE_RELATIVE_PATHS}")

################################
#设置vs compile config
if(MSVC)
	set(CMAKE_CXX_FLAGS_DEBUG "/D_DEBUG /D_MBCS /MTd /Zi /Ob0 /Od /RTC1")
	set(CMAKE_CXX_FLAGS_RELEASE "/MT /O2 /Ob2 /D NDEBUG /D_MBCS")
endif()
MESSAGE(STATUS "CMAKE_CXX_FLAGS_DEBUG ${CMAKE_CXX_FLAGS_DEBUG}")
MESSAGE(STATUS "CMAKE_CXX_FLAGS_RELEASE ${CMAKE_CXX_FLAGS_RELEASE}")

################################
#设置vs config
if(CMAKE_CONFIGURATION_TYPES)
	set(CMAKE_CONFIGURATION_TYPES Debug Release)
	MESSAGE(STATUS "CMAKE_CONFIGURATION_TYPES ${CMAKE_CONFIGURATION_TYPES}")
endif()

################################
#设置vs filter
macro(source_group_by_dir sgbd_cur_dir prefix_group source_files)
    if(MSVC)
		MESSAGE(STATUS "----------------------")
        MESSAGE(STATUS "根目录 ${sgbd_cur_dir}")
        foreach(sgbd_file ${${source_files}})
            string(REGEX REPLACE ${sgbd_cur_dir}/\(.*\) \\1 sgbd_fpath ${sgbd_file})
            string(REGEX REPLACE "\(.*\)/.*" \\1 sgbd_group_name ${sgbd_fpath})
            string(COMPARE EQUAL ${sgbd_fpath} ${sgbd_group_name} sgbd_nogroup)
            string(REPLACE "/" "\\" sgbd_group_name ${sgbd_group_name})
            if(sgbd_nogroup)
                set(sgbd_group_name "")
            endif(sgbd_nogroup)
            set(sgbd_group_name "${prefix_group}\\${sgbd_group_name}")
            MESSAGE(STATUS "filter ${sgbd_group_name} - ${sgbd_file}")
            source_group(${sgbd_group_name} FILES ${sgbd_file})
        endforeach(sgbd_file)
    endif(MSVC)
endmacro(source_group_by_dir)

source_group_by_dir(${SRC_DIR} "source" SRC_LIST)
source_group_by_dir(${HED_DIR} "header" HED_LIST)