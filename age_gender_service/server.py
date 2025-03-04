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
from PIL import Image
from transformers import pipeline
import sys

# Add the project root to Python path for importing generated gRPC code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import age_gender_pb2
import age_gender_pb2_grpc
import aggregator_pb2
import aggregator_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('age_gender_service')

# Get service addresses from environment variables
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
AGGREGATOR_SERVICE_ADDR = os.getenv('AGGREGATOR_SERVICE_ADDR', 'localhost:50053')

# Initialize Redis client
redis_client = redis.from_url(REDIS_URL)

# Initialize age and gender models
logger.info("Loading age classification model...")
age_pipe = pipeline("image-classification", model="nateraw/vit-age-classifier")

logger.info("Loading gender classification model...")
gender_pipe = pipeline("image-classification", model="Leilab/gender_class")

class AgeGenderEstimationServicer(age_gender_pb2_grpc.AgeGenderEstimationServicer):
    def EstimateAgeGender(self, request, context):
        start_time = time.time()
        image_id = request.image_id
        
        logger.info(f"Received age/gender estimation request for image {image_id}")
        
        try:
            # Convert image bytes to numpy array
            np_arr = np.frombuffer(request.image_data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image for transformers
            pil_image = Image.fromarray(image_rgb)
            
            # Predict age
            age_start = time.time()
            age_result = age_pipe(pil_image)
            age_end = time.time()
            logger.info(f"Age prediction took {age_end - age_start:.4f} seconds")
            
            # Predict gender
            gender_start = time.time()
            gender_result = gender_pipe(pil_image)
            gender_end = time.time()
            logger.info(f"Gender prediction took {gender_end - gender_start:.4f} seconds")
            
            # Prepare results
            age_gender_data = {
                "age": {
                    "label": age_result[0]["label"],
                    "confidence": float(age_result[0]["score"])
                },
                "gender": {
                    "label": gender_result[0]["label"],
                    "confidence": float(gender_result[0]["score"])
                },
                "timestamp": time.time()
            }
            
            # Save to Redis
            redis_key = f"face:{image_id}"
            redis_client.hset(redis_key, "age_gender", json.dumps(age_gender_data))
            logger.info(f"Saved age/gender data to Redis with key {redis_key}")
            
            # Check if landmarks already exist
            if redis_client.hexists(redis_key, "landmarks"):
                logger.info(f"Landmarks already exist for {image_id}, sending to aggregator")
                self._send_to_aggregator(request.image_data, redis_key, image_id)
            
            end_time = time.time()
            logger.info(f"Age/gender estimation for {image_id} completed in {end_time - start_time:.4f} seconds")
            
            return age_gender_pb2.AgeGenderResponse(
                success=True,
                image_id=image_id,
                redis_key=redis_key
            )
            
        except Exception as e:
            logger.error(f"Error estimating age/gender: {str(e)}")
            return age_gender_pb2.AgeGenderResponse(
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
    age_gender_pb2_grpc.add_AgeGenderEstimationServicer_to_server(
        AgeGenderEstimationServicer(), server
    )
    
    port = os.getenv('PORT', '50052')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    logger.info(f"Age/Gender Estimation Service started on port {port}")
    
