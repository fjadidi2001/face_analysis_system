FROM python:3.9-slim

WORKDIR /app

COPY image_input_service/ /app/image_input_service/
COPY protos/ /app/protos/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf

# Generate gRPC code
RUN mkdir -p /app/landmark_detection_pb2
RUN mkdir -p /app/age_gender_pb2
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/landmark_detection.proto
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/age_gender.proto

# Create input directory
RUN mkdir -p /app/input

# Set environment variables
ENV INPUT_DIRECTORY=/app/input
ENV LANDMARK_SERVICE_ADDR=face_landmark_service:50051
ENV AGE_GENDER_SERVICE_ADDR=age_gender_service:50052

CMD ["python", "image_input_service/server.py"]
