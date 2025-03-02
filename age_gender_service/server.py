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
import age_gender_pb2
import age_gender_pb2_grpc
import aggregator_pb2
import aggregator_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
