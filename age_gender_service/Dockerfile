FROM python:3.9-slim

WORKDIR /app

COPY age_gender_service/ /app/age_gender_service/
COPY protos/ /app/protos/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf redis transformers torch torchvision Pillow

# Generate gRPC code
RUN mkdir -p /app/age_gender_pb2
RUN mkdir -p /app/aggregator_pb2
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/age_gender.proto
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/aggregator.proto

# Set environment variables
ENV REDIS_URL=redis://redis:6379/0
ENV AGGREGATOR_SERVICE_ADDR=data_storage_service:50053
ENV PORT=50052

CMD ["python", "age_gender_service/server.py"]
