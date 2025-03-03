#!/bin/bash

# Create project directories
mkdir -p face_analysis_system/protos
mkdir -p face_analysis_system/image_input_service
mkdir -p face_analysis_system/face_landmark_service
mkdir -p face_analysis_system/age_gender_service
mkdir -p face_analysis_system/data_storage_service
mkdir -p face_analysis_system/input
mkdir -p face_analysis_system/output

cd face_analysis_system

# Create proto files
cat > protos/landmark_detection.proto << 'EOF'
syntax = "proto3";

package landmark_detection;

service LandmarkDetection {
  rpc DetectLandmarks (ImageRequest) returns (LandmarkResponse);
}

message ImageRequest {
  bytes image_data = 1;
  string image_id = 2;
}

message LandmarkResponse {
  bool success = 1;
  string image_id = 2;
  string redis_key = 3;
  string error_message = 4;
}
EOF

cat > protos/age_gender.proto << 'EOF'
syntax = "proto3";

package age_gender;

service AgeGenderEstimation {
  rpc EstimateAgeGender (ImageRequest) returns (AgeGenderResponse);
}

message ImageRequest {
  bytes image_data = 1;
  string image_id = 2;
}

message AgeGenderResponse {
  bool success = 1;
  string image_id = 2;
  string redis_key = 3;
  string error_message = 4;
}
EOF

cat > protos/aggregator.proto << 'EOF'
syntax = "proto3";

package aggregator;

service DataAggregator {
  rpc AggregateData (AggregateRequest) returns (AggregateResponse);
}

message AggregateRequest {
  bytes image_data = 1;
  string redis_key = 2;
  string image_id = 3;
}

message AggregateResponse {
  bool success = 1;
  string message = 2;
  string saved_path = 3;
}
EOF

echo "Proto files created successfully."

