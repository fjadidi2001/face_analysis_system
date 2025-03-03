# face_analysis_system/image_input_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY image_input_service/ /app/image_input_service/
COPY protos/ /app/protos/
COPY *.py /app/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf

# Generate gRPC code
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/landmark_detection.proto
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/age_gender.proto

# Create input directory
RUN mkdir -p /app/input

# Set environment variables
ENV INPUT_DIRECTORY=/app/input
ENV LANDMARK_SERVICE_ADDR=face_landmark_service:50051
ENV AGE_GENDER_SERVICE_ADDR=age_gender_service:50052

CMD ["python", "image_input_service/server.py"]

# face_analysis_system/face_landmark_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY face_landmark_service/ /app/face_landmark_service/
COPY protos/ /app/protos/
COPY *.py /app/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf redis inference-sdk

# Generate gRPC code
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/landmark_detection.proto
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/aggregator.proto

# Set environment variables
ENV REDIS_URL=redis://redis:6379/0
ENV AGGREGATOR_SERVICE_ADDR=data_storage_service:50053
ENV PORT=50051

CMD ["python", "face_landmark_service/server.py"]

# face_analysis_system/age_gender_service/Dockerfile
FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-runtime

WORKDIR /app

COPY age_gender_service/ /app/age_gender_service/
COPY protos/ /app/protos/
COPY *.py /app/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf redis transformers Pillow

# Generate gRPC code
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/age_gender.proto
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/aggregator.proto

# Set environment variables
ENV REDIS_URL=redis://redis:6379/0
ENV AGGREGATOR_SERVICE_ADDR=data_storage_service:50053
ENV PORT=50052

CMD ["python", "age_gender_service/server.py"]

# face_analysis_system/data_storage_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY data_storage_service/ /app/data_storage_service/
COPY protos/ /app/protos/
COPY *.py /app/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf redis

# Generate gRPC code
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/aggregator.proto

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV REDIS_URL=redis://redis:6379/0
ENV OUTPUT_DIRECTORY=/app/output
ENV PORT=50053

CMD ["python", "data_storage_service/server.py"]
