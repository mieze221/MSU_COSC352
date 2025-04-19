FROM golang:1.21 AS builder

WORKDIR /app

COPY go.mod ./ COPY go.sum ./ RUN go mod download

COPY . . RUN go build -o extract_tables extract_tables.go

FROM gcr.io/distroless/base COPY --from=builder /app/extract_tables /app/ COPY --from=builder /app/data /app/data WORKDIR /app CMD ["./extract_tables"]
