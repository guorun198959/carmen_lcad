include ../Makefile.conf

# Module name and description
MODULE_NAME = ROBOSENSE
MODULE_COMMENT = ROBOSENSE LIDAR Module for variable_message

LINK = g++

CFLAGS += -std=c11
CXXFLAGS += -std=c++11

# Application specific include directories.

IFLAGS += -I$(CARMEN_HOME)/sharedlib/librobosense
IFLAGS += -I$(CARMEN_HOME)/sharedlib/libtf/src -I/usr/local/include/bullet/
LFLAGS += -L$(CARMEN_HOME)/sharedlib/librobosense
LFLAGS += -L$(CARMEN_HOME)/sharedlib/libtf/src

# Required default libraries to comunicate with Carmen Core.
LFLAGS += -lipc -lglobal -lparam_interface -lvelodyne_interface
LFLAGS += -ltf -lBulletCollision -lBulletDynamics -lBulletSoftBody -lLinearMath -lboost_thread-mt -lrt -lboost_signals -lboost_system -pthread
CFLAGS += -Wall

# Source code files (.c, .cpp) 
SOURCES = robosense.cpp

# Public headers, linked to 'carmen/include/carmen/'.
PUBLIC_INCLUDES =

# Public libraries, linked to 'carmen/lib'.
PUBLIC_LIBRARIES =

# Public binaries, your application specific module laucher, copied to 'carmen/bin'.
PUBLIC_BINARIES = robosense

TARGETS = robosense librobosense.a
PUBLIC_LIBRARIES_SO = 
#
#ifndef NO_PYTHON
#TARGETS += libvelodyne_interface.so.1
#endif

# If you set graphics support in configure (only for GTK).
ifndef NO_GRAPHICS
FLAGS += `$(GTK_CONFIG) --cflags` 
LFLAGS += `pkg-config --libs gtk+-2.0`
#Source code file (.c)
TARGETS +=
SOURCES += 
endif

librobosense.a: 
	$(MAKE) -C $(CARMEN_HOME)/sharedlib/librobosense 
#libvelodyne_transforms.a: velodyne_transforms.o tf_helper.o
#libvelodyne_interface.a: velodyne_interface.o
#libvelodyne_interface.a: velodyne_interface.o tf_helper.o

#libvelodyne_interface.so.1:	velodyne_interface.o 
#libvelodyne_transforms.so.1:  velodyne_transforms.o tf_helper.o

robosense: robosense.o $(CARMEN_HOME)/sharedlib/librobosense/librobosense.a $(CARMEN_HOME)/src/velodyne/libvelodyne_interface.a

clean: clean_librobosense

clean_librobosense:
	$(MAKE) clean -C $(CARMEN_HOME)/sharedlib/librobosense/


# rules

include ../Makefile.rules
