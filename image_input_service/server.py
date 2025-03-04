import os
import time
import uuid
import grpc
import logging
from concurrent import futures
import cv2
import numpy as np
import sys

# Add the project root to Python path for importing generated gRPC code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import landmark_detection_pb2
import landmark_detection_pb2_grpc
import age_gender_pb2
import age_gender_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('image_input_service')

# Get service addresses from environment variables
LANDMARK_SERVICE_ADDR = os.getenv('LANDMARK_SERVICE_ADDR', 'localhost:50051')
AGE_GENDER_SERVICE_ADDR = os.getenv('AGE_GENDER_SERVICE_ADDR', 'localhost:50052')

def process_image(image_path):
    """Process an image by sending it to landmark and age/gender services"""
    try:
        # Load image
        start_time = time.time()
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return False
        
        image_id = str(uuid.uuid4())
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()
        
        logger.info(f"Processing image {image_path} with ID {image_id}")
        
        # Send to landmark detection service
        landmark_result = send_to_landmark_service(image_bytes, image_id)
        
        # Send to age/gender estimation service
        age_gender_result = send_to_age_gender_service(image_bytes, image_id)
        
        end_time = time.time()
        logger.info(f"Image {image_id} processed in {end_time - start_time:.4f} seconds")
        
        return landmark_result and age_gender_result
        
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        return False

def send_to_landmark_service(image_bytes, image_id):
    """Send image to landmark detection service"""
    try:
        start_time = time.time()
        logger.info(f"Connecting to landmark service at {LANDMARK_SERVICE_ADDR}")
        
        # Create gRPC channel
        with grpc.insecure_channel(LANDMARK_SERVICE_ADDR) as channel:
            stub = landmark_detection_pb2_grpc.LandmarkDetectionStub(channel)
            
            # Create request
            request = landmark_detection_pb2.ImageRequest(
                image_data=image_bytes,
                image_id=image_id
            )
            
            # Send request
            response = stub.DetectLandmarks(request)
            
            end_time = time.time()
            logger.info(f"Landmark detection for {image_id} completed in {end_time - start_time:.4f} seconds")
            
            if not response.success:
                logger.error(f"Landmark detection failed: {response.error_message}")
                return False
                
            logger.info(f"Landmarks saved with Redis key: {response.redis_key}")
            return True
            
    except Exception as e:
        logger.error(f"Error in landmark detection: {str(e)}")
        return False

def send_to_age_gender_service(image_bytes, image_id):
    """Send image to age/gender estimation service"""
    try:
        start_time = time.time()
        logger.info(f"Connecting to age/gender service at {AGE_GENDER_SERVICE_ADDR}")
        
        # Create gRPC channel
        with grpc.insecure_channel(AGE_GENDER_SERVICE_ADDR) as channel:
            stub = age_gender_pb2_grpc.AgeGenderEstimationStub(channel)
            
            # Create request
            request = age_gender_pb2.ImageRequest(
                image_data=image_bytes,
                image_id=image_id
            )
            
            # Send request
            response = stub.EstimateAgeGender(request)
            
            end_time = time.time()
            logger.info(f"Age/Gender estimation for {image_id} completed in {end_time - start_time:.4f} seconds")
            
            if not response.success:
                logger.error(f"Age/Gender estimation failed: {response.error_message}")
                return False
                
            logger.info(f"Age/Gender data saved with Redis key: {response.redis_key}")
            return True
            
    except Exception as e:
        logger.error(f"Error in age/gender estimation: {str(e)}")
        return False

def process_directory(directory_path):
    """Process all images in a directory"""
    supported_extensions = ['.jpg', '.jpeg', '.png']
    
    for filename in os.listdir(directory_path):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in supported_extensions:
            image_path = os.path.join(directory_path, filename)
            logger.info(f"Processing {image_path}")
            process_image(image_path)

if __name__ == "__main__":
    # Get directory path from environment variable
    input_dir = os.getenv('INPUT_DIRECTORY', '/app/input')
    
    logger.info(f"Starting Image Input Service, monitoring directory: {input_dir}")
    
    # Check if directory exists
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        logger.info(f"Created directory: {input_dir}")
    
    # Process existing images
    process_directory(input_dir)
    
    # In a real system, you might implement a file watcher here
    logger.info("Initial processing complete. In a production system, this would watch for new files.")
