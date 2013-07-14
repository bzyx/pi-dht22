TARGET = dht_reader
LIBS = -lbcm2835
CC = gcc
CFLAGS = -g -Wall	-std=c99	 

.PHONY: clean all default

default: $(TARGET)
all: default

OBJECTS = $(patsubst %.c, %.o, $(wildcard *.c))
HEADERS = $(wildcard *.h)

%.o: %.c $(HEADERS)
	$(CC)	$(CFLAGS)	-c	$<	-o	$@		

.PRECIOUS: $(TARGET) $(OBJECTS)

$(TARGET): $(OBJECTS)
	$(CC)	$(OBJECTS)	-Wall	$(LIBS)	-o	$@	

clean:
	-rm	-f	*.o	
	-rm	-f	$(TARGET)	
