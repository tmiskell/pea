#
# Generic rules tested @Linux ubuntu 3.8.0-29-generic #42~precise1-Ubuntu
#

TARGET	= quasar
CC	= gcc
CFLAGS	= -g -O2 -Wall -pthread -rdynamic
LIBS	= -lrt

HEADERS = $(wildcard *.h)
OBJECTS = $(patsubst %.c, %.o, $(wildcard *.c))

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	-rm -f $(OBJECTS)
	-rm -f $(TARGET)
