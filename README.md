# Face Analysis System

A microservices-based system for detecting faces in images and analyzing them for age and gender information.

## Overview

This project implements a distributed system for face analysis using several microservices that communicate via gRPC. The system can detect faces in images, estimate age and gender, and aggregate the results.

![System Architecture](https://github.com/username/face-analysis-system/raw/main/docs/system_architecture.png)

## Features

- Face detection using Roboflow API
- Age and gender estimation using pre-trained models
- Microservices architecture with gRPC communication
- Redis for intermediate data storage
- Containerized deployment with Docker

## System Components

1. **Image Input Service** - Processes input images and sends them to appropriate analysis services
2. **Face Landmark Service** - Detects faces in images using Roboflow API
3. **Age Gender Service** - Estimates age and gender for detected faces
4. **Data Storage Service** - Aggregates and stores the final results
5. **Redis** - Used for intermediate data storage between services

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Internet connection for downloading models and dependencies

## Project Structure

```
face_analysis_system/
├── age_gender_service/
│   ├── Dockerfile
│   ├── server.py
│   └── requirements.txt
├── data_storage_service/
│   ├── Dockerfile
│   ├── server.py
│   └── requirements.txt
├── face_landmark_service/
│   ├── Dockerfile
│   ├── server.py
│   └── requirements.txt
├── image_input_service/
│   ├── Dockerfile
│   ├── server.py
│   └── requirements.txt
├── protos/
│   ├── age_gender.proto
│   ├── aggregator.proto
│   └── landmark_detection.proto
├── input/
│   └── (place your input images here)
├── output/
│   └── (processed results will appear here)
├── docker-compose.yml
└── README.md
```

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/username/face-analysis-system.git
cd face-analysis-system
```

### 2. Create input and output directories (if they don't exist)

```bash
mkdir -p input output
```

### 3. Set permissions for input and output directories

```bash
sudo chown -R 1000:1000 input/
sudo chown -R 1000:1000 output/
```

### 4. Place test images in the input directory

```bash
cp path/to/your/test/images/*.jpg input/
```

### 5. Build and start the system

```bash
sudo docker-compose build
sudo docker-compose up
```

## Usage

1. Place image files in the `input` directory
2. Start the system using Docker Compose
3. Check the `output` directory for processed results
4. Results will be saved as JSON files with the same base name as the input images

## Troubleshooting

### Port conflicts

If you see an error like "address already in use" for port 6379:

```bash
# Stop any existing Redis server
sudo systemctl stop redis-server

# Or find and kill the process using port 6379
sudo lsof -i :6379
sudo kill -9 [PID]

# Then restart the system
sudo docker-compose down
sudo docker-compose up
```

### Checking service status

```bash
sudo docker-compose ps
```

### Viewing logs

```bash
# All services
sudo docker-compose logs

# Specific service
sudo docker-compose logs image_input_service
```

## System Architecture

The system uses a microservices architecture with gRPC for inter-service communication:

1. **Image Input Service** reads images from the input directory and sends them to:
   - Face Landmark Service for face detection
   - Age Gender Service for age/gender estimation

2. **Face Landmark Service** uses the Roboflow API to detect faces in images and stores the results in Redis.

3. **Age Gender Service** uses pre-trained models to estimate age and gender for detected faces and stores the results in Redis.

4. **Data Storage Service** aggregates the results from Redis and saves them to the output directory.

## API Keys

The system uses the Roboflow API for face detection. The API key is included in the Docker Compose configuration. For production use, please replace it with your own API key.

## Example Output

```json
{
  "image_id": "test_image_1.jpg",
  "faces": [
    {
      "bbox": [100, 150, 200, 250],
      "confidence": 0.92,
      "age": "20-30",
      "age_confidence": 0.85,
      "gender": "Female",
      "gender_confidence": 0.91
    },
    {
      "bbox": [300, 150, 400, 250],
      "confidence": 0.89,
      "age": "30-40",
      "age_confidence": 0.78,
      "gender": "Male",
      "gender_confidence": 0.94
    }
  ],
  "processing_time": "2023-08-14T15:30:45.123456"
}
```

## Development

### Adding a new service

1. Create a new directory for your service
2. Define the service interface in a new proto file
3. Implement the service in Python
4. Add the service to the Docker Compose file
5. Update the necessary services to communicate with your new service

### Modifying existing services

1. Update the proto files if you need to change the service interfaces
2. Regenerate the gRPC code with protoc
3. Update the service implementations
4. Rebuild the Docker images

## License

This project is licensed under the Apache License - see the LICENSE file for details.

## Acknowledgments

- [Roboflow](https://roboflow.com/) for the face detection API
- [Hugging Face](https://huggingface.co/) for the age and gender models
- [gRPC](https://grpc.io/) for the RPC framework
