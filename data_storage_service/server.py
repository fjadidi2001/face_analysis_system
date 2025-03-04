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
import sys

# Add the project root to Python path for importing generated gRPC code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import aggregator_pb2
import aggregator_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('data_storage_service')

# Get service addresses from environment variables
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
OUTPUT_DIR = os.getenv('OUTPUT_DIRECTORY', '/app/output')

# Initialize Redis client
redis_client = redis.from_url(REDIS_URL)

class DataAggregatorServicer(aggregator_pb2_grpc.DataAggregatorServicer):
    def AggregateData(self, request, context):
        start_time = time.time()
        image_id = request.image_id
        redis_key = request.redis_key
        
        logger.info(f"Received data aggregation request for image {image_id} with key {redis_key}")
        
        try:
            # Create output directory if it doesn't exist
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
                logger.info(f"Created output directory: {OUTPUT_DIR}")
            
            # Get data from Redis
            landmarks_json = redis_client.hget(redis_key, "landmarks")
            age_gender_json = redis_client.hget(redis_key, "age_gender")
            
            if not landmarks_json or not age_gender_json:
                error_msg = f"Missing data in Redis for key {redis_key}"
                logger.error(error_msg)
                return aggregator_pb2.AggregateResponse(
                    success=False,
                    message=error_msg
                )
            
            # Parse JSON data
            landmark_data = json.loads(landmarks_json)
            age_gender_data = json.loads(age_gender_json)
            
            # Combine data
            combined_data = {
                "image_id": image_id,
                "landmarks": landmark_data,
                "age_gender": age_gender_data,
                "timestamp": time.time()
            }
            
            # Save image
            np_arr = np.frombuffer(request.image_data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            image_path = os.path.join(OUTPUT_DIR, f"{image_id}.jpg")
            cv2.imwrite(image_path, image)
            
            # Save JSON data
            json_path = os.path.join(OUTPUT_DIR, f"{image_id}.json")
            with open(json_path, 'w') as f:
                json.dump(combined_data, f, indent=4)
            
            end_time = time.time()
            logger.info(f"Data aggregation for {image_id} completed in {end_time - start_time:.4f} seconds")
            
            return aggregator_pb2.AggregateResponse(
                success=True,
                message="Data aggregated successfully",
                saved_path=json_path
            )
            
        except Exception as e:
            error_msg = f"Error aggregating data: {str(e)}"
            logger.error(error_msg)
            return aggregator_pb2.AggregateResponse(
                success=False,
                message=error_msg
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    aggregator_pb2_grpc.add_DataAggregatorServicer_to_server(
        DataAggregatorServicer(), server
    )
    
    port = os.getenv('PORT', '50053')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    logger.info(f"Data Storage Service started on port {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        server.stop(0)

if __name__ == "__main__":
    serve()
