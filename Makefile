config=debug
CC=g++
CFLAGS :=
ifeq ($(config), debug)
	CFLAGS+=-g
else
	ifeq ($(config), release)
		CFLAGS+=-O3
	endif
endif


CFLAGS+=-c -Wall -Wall
LDFLAGS=
SOURCES=main.cpp Test.cpp
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=$(config)/hello

all: prepare $(SOURCES) $(EXECUTABLE)
    
$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) $(config)-obj/$(OBJECTS) -o $@ # BUG: only first element has correct directory to object file (.o)

prepare:
	@mkdir -p $(config)
	@mkdir -p $(config)-obj

.cpp.o:
	$(CC) $(CFLAGS) $< -o $(config)-obj/$@

clean:
	@echo -ne "Cleaning"
	@rm -rf $(EXECUTABLE)
	@echo -ne "."
	@rm -rf $(config)
	@echo -ne "."
	@rm -rf $(config)-obj
	@echo -ne "."
	@echo "Done"

clean-all: 
	@echo -ne "Cleaning"
	@rm -rf $(EXECUTABLE)
	@echo -ne "."
	@rm -rf debug
	@echo -ne "."
	@rm -rf debug-obj
	@echo -ne "."
	@rm -rf release
	@echo -ne "."
	@rm -rf release-obj
	@echo -ne "."
	@echo "Done"
