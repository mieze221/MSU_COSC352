
FROM golang:1.21


WORKDIR /app


COPY go.mod go.sum ./
RUN go mod download


COPY extract_tables.go ./
COPY data/ ./data/


RUN go build -o extract_tables extract_tables.go


CMD ["./extract_tables"]
