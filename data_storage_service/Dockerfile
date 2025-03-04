FROM python:3.9-slim

WORKDIR /app

COPY data_storage_service/ /app/data_storage_service/
COPY protos/ /app/protos/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf redis

# Generate gRPC code
RUN mkdir -p /app/aggregator_pb2
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/aggregator.proto

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV REDIS_URL=redis://redis:6379/0
ENV OUTPUT_DIRECTORY=/app/output
ENV PORT=50053

CMD ["python", "data_storage_service/server.py"]

