################################
# 添加子工程
ADD_SUBDIRECTORY(lib_common)

################################
# 当前工程
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(pngtool)
MESSAGE(STATUS "======================")
MESSAGE(STATUS "pngtool start ...")
INCLUDE("CMakeMacro.txt")

################################
# 配置文件路径
SET(SRC_DIR "${PROJECT_SOURCE_DIR}/../Client/src/pngtools")
SET(GSLIB_LIB_DIR "${PROJECT_SOURCE_DIR}/../Client/lib/Debug")
SET(INCLUDE_DIRS
	"${PROJECT_SOURCE_DIR}/../Client/include/gslib"
	"${PROJECT_SOURCE_DIR}/../Client/include/lib_debug_new" 
	"${PROJECT_SOURCE_DIR}/../Client/include/lib_mapfile" 
	"${PROJECT_SOURCE_DIR}/../Client/src/httplib" 
	"${PROJECT_SOURCE_DIR}/../Client/src/httplib/include" 
	"${PROJECT_SOURCE_DIR}/../SHARECODE/include/lib_common"
	"${PROJECT_SOURCE_DIR}/../SHARECODE/include/lib_json"
	"${PROJECT_SOURCE_DIR}/../SHARECODE/include/STLport-5.2.1"
	"${PROJECT_SOURCE_DIR}/../SHARECODE/include/STLport-5.2.1/stlport"
)
normal_absolute(INCLUDE_DIRS)

################################
# 获取文件列表
FILE(GLOB_RECURSE DLG_SRC_LIST "${SRC_DIR}/Dlg*" "${SRC_DIR}/*Dlg*")
FILE(GLOB_RECURSE RES_SRC_LIST "${SRC_DIR}/*.ico" "${SRC_DIR}/*.png" "${SRC_DIR}/*.rc*" "${SRC_DIR}/*.bmp")
SET(DLG_SRC_LIST ${DLG_SRC_LIST} 
	"${SRC_DIR}/Timebar.cpp" "${SRC_DIR}/Timebar.h"
	"${SRC_DIR}/TimeLayer.cpp" "${SRC_DIR}/TimeLayer.h"
)
SET(FUNC_SRC_LIST
	"${SRC_DIR}/Globals.cpp" "${SRC_DIR}/Globals.h"
	"${SRC_DIR}/IniFile.cpp" "${SRC_DIR}/IniFile.h"
	"${SRC_DIR}/SmartClip.cpp" "${SRC_DIR}/SmartClip.h"
	"${SRC_DIR}/MyTimeBarMacro.h"
)
SET(RENDER_SRC_LIST "${SRC_DIR}/GSEView.cpp" "${SRC_DIR}/GSEView.h")
SET(SRC_LIST
	"${SRC_DIR}/gif89a.cpp" "${SRC_DIR}/gif89a.h"
	"${SRC_DIR}/MainFrm.cpp" "${SRC_DIR}/MainFrm.h"
	"${SRC_DIR}/pngtools.cpp" "${SRC_DIR}/pngtools.h"
	"${SRC_DIR}/pngtoolsDoc.cpp" "${SRC_DIR}/pngtoolsDoc.h"
	"${SRC_DIR}/pngtoolsView.cpp" "${SRC_DIR}/pngtoolsView.h"
	"${SRC_DIR}/stdafx.cpp" "${SRC_DIR}/stdafx.h"
	"${SRC_DIR}/Resource.h"
)

################################
# 路径信息输出
MESSAGE(STATUS "This is BINARY dir ${PROJECT_BINARY_DIR}")
MESSAGE(STATUS "This is SOURCE dir ${PROJECT_SOURCE_DIR}")
MESSAGE(STATUS "This is SRC_DIR ${SRC_DIR}")
MESSAGE(STATUS "This is INCLUDE_DIRS ${INCLUDE_DIRS}")

################################
# 初始化工程配置
# 生成VS文件过滤器
init_base_project()
source_group_by_dir(${SRC_DIR} "dlg" DLG_SRC_LIST)
source_group_by_dir(${SRC_DIR} "render" RENDER_SRC_LIST)
source_group_by_dir(${SRC_DIR} "func" FUNC_SRC_LIST)
source_group_by_dir(${SRC_DIR} "resource" RES_SRC_LIST)

################################
# 检查系统环境变量
IF($ENV{DXSDK_DIR})
	MESSAGE(WARNING "!!! 没有环境变量$DXSDK_DIR，请安装DirectX")
ENDIF($ENV{DXSDK_DIR})

################################
# 获取VS安装目录
if(MSVC)
	SET(VCINSTALLDIR "${CMAKE_LINKER}../../../")
	GET_FILENAME_COMPONENT(VCINSTALLDIR ${VCINSTALLDIR} ABSOLUTE)
	SET(VCINSTALLDIR "${VCINSTALLDIR}/include;${VCINSTALLDIR}/PlatformSDK/include")
endif(MSVC)
MESSAGE(STATUS "VCINSTALLDIR ${VCINSTALLDIR}")

################################
# 添加预处理器定义
ADD_DEFINITIONS(-DUSE_STATIC_LIB)

################################
# 使用静态MFC库
SET(CMAKE_MFC_FLAG 1)

################################
# 添加include和lib依赖目录
INCLUDE_DIRECTORIES(${VCINSTALLDIR})
INCLUDE_DIRECTORIES("$ENV{DXSDK_DIR}/Include" ${INCLUDE_DIRS})
LINK_DIRECTORIES("$ENV{DXSDK_DIR}/Lib/${BIT_FLAG}")
ADD_EXECUTABLE(pngtool WIN32 ${DLG_SRC_LIST} ${RENDER_SRC_LIST} ${FUNC_SRC_LIST} ${RES_SRC_LIST} ${SRC_LIST})
ADD_DEPENDENCIES(pngtool lib_common)
TARGET_LINK_LIBRARIES(pngtool lib_common)
TARGET_LINK_LIBRARIES(pngtool 
	d3dx9.lib
	d3d9.lib
	dxguid.lib
	winmm.lib
	Rpcrt4.lib
	debug "${PROJECT_SOURCE_DIR}/../Client/lib/Debug/gslib_d.lib"
	debug "${PROJECT_SOURCE_DIR}/../Client/lib/Debug/httpdownload_static_d.lib"
	debug "${PROJECT_SOURCE_DIR}/../SHARECODE/lib/Debug/stlportd_static.lib"
	debug "${PROJECT_SOURCE_DIR}/../SHARECODE/lib/Debug/lib_zlib_d.lib"
	debug "${PROJECT_SOURCE_DIR}/../SHARECODE/lib/Debug/lib_json_d.lib"
	optimized "${PROJECT_SOURCE_DIR}/../Client/lib/Release/gslib.lib"
	optimized "${PROJECT_SOURCE_DIR}/../Client/lib/Release/httpdownload_static.lib"
	optimized "${PROJECT_SOURCE_DIR}/../SHARECODE/lib/Release/stlport_static.lib"
	optimized "${PROJECT_SOURCE_DIR}/../SHARECODE/lib/Release/lib_zlib.lib"
	optimized "${PROJECT_SOURCE_DIR}/../SHARECODE/lib/Release/lib_json.lib"
)

################################
# 安装
INSTALL(TARGETS pngtool
	RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib/static
)
