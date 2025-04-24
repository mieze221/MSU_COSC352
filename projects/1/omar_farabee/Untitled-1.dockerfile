
FROM gcc:latest


WORKDIR /usr/src/omar_farabee


COPY . /usr/src/omar_farabee


RUN g++ -o app project352.cpp


CMD ["./app"]
