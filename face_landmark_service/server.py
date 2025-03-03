import os
import time
import uuid
import grpc
import logging
import json
import numpy as np
import cv2
import redis
from concurrent import futures
from inference_sdk import InferenceHTTPClient
import sys

# Add the project root to Python path for importing generated gRPC code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import landmark_detection_pb2
import landmark_detection_pb2_grpc
import aggregator_pb2
import aggregator_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('landmark_detection_service')

# Get service addresses from environment variables
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
AGGREGATOR_SERVICE_ADDR = os.getenv('AGGREGATOR_SERVICE_ADDR', 'localhost:50053')
API_KEY = os.getenv('ROBOFLOW_API_KEY', '2IGtFaicFMGaMwb2mX8A')

# Initialize Redis client
redis_client = redis.from_url(REDIS_URL)

# Initialize face detection client
face_detector = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
)

class LandmarkDetectionServicer(landmark_detection_pb2_grpc.LandmarkDetectionServicer):
    def DetectLandmarks(self, request, context):
        start_time = time.time()
        image_id = request.image_id
        
        logger.info(f"Received landmark detection request for image {image_id}")
        
        try:
            # Convert image bytes to numpy array
            np_arr = np.frombuffer(request.image_data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Save temporary image for Roboflow API
            temp_path = f"/tmp/{image_id}.jpg"
            cv2.imwrite(temp_path, image)
            
            # Detect faces using Roboflow API
            face_detection_start = time.time()
            result = face_detector.infer(temp_path, model_id="face-detection-mik1i/21")
            face_detection_end = time.time()
            
            logger.info(f"Face detection took {face_detection_end - face_detection_start:.4f} seconds")
            
            # Process the results
            landmarks = []
            if "predictions" in result:
                for face in result["predictions"]:
                    confidence = face.get("confidence", 0)
                    
                    # Extract bounding box coordinates
                    x = face.get("x", face.get("x_center", None))
                    y = face.get("y", face.get("y_center", None))
                    w = face.get("width", face.get("w", None))
                    h = face.get("height", face.get("h", None))
                    
                    if all([x is not None, y is not None, w is not None, h is not None]):
                        x1 = int(x - w/2)
                        y1 = int(y - h/2)
                        x2 = int(x + w/2)
                        y2 = int(y + h/2)
                        
                        landmarks.append({
                            "confidence": confidence,
                            "bbox": [x1, y1, x2, y2]
                        })
            
            # Generate Redis key and save landmarks
            redis_key = f"face:{image_id}"
            landmark_data = {
                "landmarks": landmarks,
                "timestamp": time.time()
            }
            
            redis_client.hset(redis_key, "landmarks", json.dumps(landmark_data))
            logger.info(f"Saved landmarks to Redis with key {redis_key}")
            
            # Check if age/gender data already exists
            if redis_client.hexists(redis_key, "age_gender"):
                logger.info(f"Age/gender data already exists for {image_id}, sending to aggregator")
                self._send_to_aggregator(request.image_data, redis_key, image_id)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            end_time = time.time()
            logger.info(f"Landmark detection for {image_id} completed in {end_time - start_time:.4f} seconds")
            
            return landmark_detection_pb2.LandmarkResponse(
                success=True,
                image_id=image_id,
                redis_key=redis_key
            )
            
        except Exception as e:
            logger.error(f"Error detecting landmarks: {str(e)}")
            return landmark_detection_pb2.LandmarkResponse(
                success=False,
                image_id=image_id,
                error_message=str(e)
            )
    
    def _send_to_aggregator(self, image_data, redis_key, image_id):
        """Send data to the aggregator service"""
        try:
            with grpc.insecure_channel(AGGREGATOR_SERVICE_ADDR) as channel:
                stub = aggregator_pb2_grpc.DataAggregatorStub(channel)
                
                request = aggregator_pb2.AggregateRequest(
                    image_data=image_data,
                    redis_key=redis_key,
                    image_id=image_id
                )
                
                response = stub.AggregateData(request)
                
                if response.success:
                    logger.info(f"Data aggregated successfully: {response.saved_path}")
                else:
                    logger.error(f"Data aggregation failed: {response.message}")
                    
        except Exception as e:
            logger.error(f"Error sending to aggregator: {str(e)}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    landmark_detection_pb2_grpc.add_LandmarkDetectionServicer_to_server(
        LandmarkDetectionServicer(), server
    )
    
    port = os.getenv('PORT', '50051')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    logger.info(f"Landmark Detection Service started on port {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        server.stop(0)

if __name__ == "__main__":
    serve()
