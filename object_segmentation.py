import os
import cv2
import pandas as pd
import numpy as np
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from detectron2.data import MetadataCatalog

import ast

def preprocess_gaze_data(gaze_df):
    def safe_parse(value):
        if pd.isna(value):
            return (np.nan, np.nan)
        if isinstance(value, tuple) or isinstance(value, list):
            return value
        try:
            return ast.literal_eval(str(value))
        except Exception:
            return (np.nan, np.nan)

    # Parse into two numeric columns
    gaze_df[['x_norm', 'y_norm']] = gaze_df['left_gaze_point_on_display_area'] \
        .apply(safe_parse).apply(pd.Series)

    # Screen dimensions (16:9)
    screen_w, screen_h = 1920, 1080
    gaze_df['x_screen'] = gaze_df['x_norm'] * screen_w
    gaze_df['y_screen'] = gaze_df['y_norm'] * screen_h

    # Image mapping (800x800 centered)
    offset_x = (screen_w - screen_h) // 2   # 420 px black bars
    offset_y = 0
    scale = screen_h / 800                  # 1080 / 800 = 1.35

    gaze_df['x_gaze'] = (gaze_df['x_screen'] - offset_x) / scale
    gaze_df['y_gaze'] = (gaze_df['y_screen'] - offset_y) / scale

    return gaze_df

# --- 1. CONFIGURATION ---
IMAGE_DIR = './current_images'
GAZE_DATA_DIR = './data'
OUTPUT_RESULTS_PATH = 'analysis_results.csv'

CONFIG_FILE = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"

# --- 2. SET UP DETECTRON2 PREDICTOR ---
print("Initializing Detectron2 model...")

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file(CONFIG_FILE))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(CONFIG_FILE)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5

predictor = DefaultPredictor(cfg)
metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])

print("Model loaded successfully.")

# --- 3. DATA PROCESSING PIPELINE ---
all_results = []

# Get lists of image and gaze files
image_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
gaze_data_files = sorted([f for f in os.listdir(GAZE_DATA_DIR) if f.lower().endswith('.csv')])

if not image_files:
    print(f"No image files found in '{IMAGE_DIR}'. Please check your path.")
    exit()

if not gaze_data_files:
    print(f"No gaze data files found in '{GAZE_DATA_DIR}'. Please check your path.")
    exit()

# Loop over images
for image_filename in image_files:
    print(f"\nProcessing image: {image_filename}")
    image_path = os.path.join(IMAGE_DIR, image_filename)

    img = cv2.imread(image_path)
    if img is None:
        print(f"Warning: Could not read image at {image_path}. Skipping.")
        continue

    outputs = predictor(img)
    instances = outputs["instances"]

    if len(instances.pred_classes) == 0:
        print("No objects detected in this image. Skipping gaze analysis.")
        continue

    pred_masks = instances.pred_masks.to('cpu').numpy()
    pred_classes = instances.pred_classes.to('cpu').numpy()

    image_stem = os.path.splitext(image_filename)[0]

    # Match gaze data files by name
    for gaze_data_filename in gaze_data_files:
        if image_stem in gaze_data_filename:
            print(f"  Analyzing gaze data from: {gaze_data_filename}")
            gaze_data_path = os.path.join(GAZE_DATA_DIR, gaze_data_filename)
            gaze_df = pd.read_csv(gaze_data_path)

            if gaze_df.empty:
                print(f"    Warning: Gaze data file is empty. Skipping.")
                continue

            gaze_df = preprocess_gaze_data(gaze_df)

            fixation_count_per_object = {}

            # --- 4. POINT-IN-MASK CHECK ---
            for _, row in gaze_df.iterrows():
                if pd.isna(row['x_gaze']) or pd.isna(row['y_gaze']):
                    continue

                gaze_x = int(round(row['x_gaze']))
                gaze_y = int(round(row['y_gaze']))

                for mask_idx, mask in enumerate(pred_masks):
                    if 0 <= gaze_y < mask.shape[0] and 0 <= gaze_x < mask.shape[1]:
                        if mask[gaze_y, gaze_x]:
                            object_class_id = pred_classes[mask_idx]
                            object_instance_id = mask_idx

                            key = f"{object_class_id}_{object_instance_id}"
                            fixation_count_per_object[key] = fixation_count_per_object.get(key, 0) + 1
                            break

            # --- 5. AGGREGATE RESULTS ---
            for key, count in fixation_count_per_object.items():
                object_class_id, object_instance_id = key.split('_')
                object_class_id = int(object_class_id)

                class_name = metadata.thing_classes[object_class_id]

                results = {
                    'image_filename': image_filename,
                    'participant_id': gaze_data_filename.split('_')[0],
                    'object_class_id': object_class_id,
                    'object_class_name': class_name,
                    'object_instance_id': int(object_instance_id),
                    'fixation_count': count
                }
                all_results.append(results)

# --- 6. SAVE RESULTS ---
if all_results:
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(OUTPUT_RESULTS_PATH, index=False)
    print(f"\nAnalysis complete. Results saved to '{OUTPUT_RESULTS_PATH}'.")
else:
    print("\nNo analysis results to save. Please check your data and paths.")

