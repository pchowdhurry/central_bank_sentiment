CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 `pkg-config --cflags poppler-cpp`
LDFLAGS = `pkg-config --libs poppler-cpp`

TARGET = app
SRCS = main.cpp text_extract.cpp
OBJS = $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f *.o $(TARGET) text_extract 

run: ./$(TARGET)