# Use an official lightweight Go runtime image
FROM golang:1.20

# Set the working directory inside the container
WORKDIR /app

# Copy the Go module files and download dependencies
COPY go.mod go.sum ./
RUN go mod tidy

# Copy the source code
COPY . .

# Build the Go application
RUN go build -o go-api

# Define the runtime command
CMD ["/app/go-api"]

# Expose the port the app runs on
EXPOSE 8080