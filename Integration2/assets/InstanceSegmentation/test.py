
# import cv2
# from detectron2 import model_zoo
# from detectron2.engine import DefaultPredictor
# from detectron2.config import get_cfg
# from detectron2.utils.visualizer import Visualizer
# from detectron2.data import MetadataCatalog

# # Load a pre-trained model
# cfg = get_cfg()
# cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
# cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Set threshold for this model
# cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")

# # Set device to CPU
# cfg.MODEL.DEVICE = 'cpu'

# # Initialize Detectron2 predictor
# predictor = DefaultPredictor(cfg)

# # Load an image
# image_path = "../test13.jpg"
# image = cv2.imread(image_path)

# # Perform inference
# outputs = predictor(image)
# instances = outputs["instances"]
# # Get class names from metadata
# class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes
# if instances.has("pred_boxes") and instances.has("pred_classes"):
#     classes = instances.pred_classes.cpu().numpy()
#     scores = instances.scores.cpu().numpy()
#     for cls, score in zip(classes, scores):
#         class_name = class_names[cls]  # Convert index to a readable class name
#         print(f"Class: {class_name}, Confidence Score: {score*100:.2f}%")


# # Visualize the results
# v = Visualizer(image[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
# out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
# cv2.imshow("Detectron2 Output", out.get_image()[:, :, ::-1])
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# from detectron2.data import MetadataCatalog

# # Retrieve the COCO metadata
# # This assumes you are using the COCO dataset; the key might be different if you've set it up differently
# coco_metadata = MetadataCatalog.get("coco_2017_train")

# # Print all the class names
# for idx, class_name in enumerate(coco_metadata.thing_classes):
#     print(f"{idx + 0}: {class_name}")

import cv2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
import os


# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Find the index of the "Integration2" part in the path
integration2_index = current_file_path.find("Integration2")

# Extract up to the end of "Integration2\\" (note the addition to include the folder name itself)
default_path = current_file_path[:integration2_index] + "Integration2\\"

cost_summary= f'{default_path}assets\\InstanceSegmentation\\costsummary.txt'

# Function to read costs from file
def read_costs(filename):
    costs = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split('-') 
            if len(parts) == 2:
                costs[parts[0].strip()] = float(parts[1])
    return costs

# Load a pre-trained model
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Set threshold for this model
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
cfg.MODEL.DEVICE = 'cpu'  # Set device to CPU

# Initialize Detectron2 predictor
predictor = DefaultPredictor(cfg)

# Load an image
image_path = f"{default_path}\images\\Object_ROI_.jpg"
# image_path = f"{default_path}\images\\original_ROI_.jpg"
image = cv2.imread(image_path)

# Perform inference
outputs = predictor(image)
instances = outputs["instances"]

# Get class names from metadata
class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes

# Load the cost data
costs = read_costs(f'{default_path}assets\\InstanceSegmentation\\cost.txt')  # Path to your cost file
total_cost = 0
write_cost = ""




if instances.has("pred_boxes") and instances.has("pred_classes"):
    classes = instances.pred_classes.cpu().numpy()
    scores = instances.scores.cpu().numpy()
    for cls, score in zip(classes, scores):
        class_name = class_names[cls]  # Convert index to a readable class name
        print(f"Class: {class_name}, Confidence Score: {score*100:.2f}%")
        # Add to total cost if the class name exists in costs dictionary
        if class_name in costs:
            print(class_name," : Rs ",costs[class_name])
            write_cost = write_cost + f"{class_name} : Rs {costs[class_name]}\n"
            total_cost += costs[class_name]

# Print total estimated damage cost
print(f"Total Estimated Damage Cost: INR {total_cost}")
write_cost = write_cost + f"Total Estimated Damage Cost: INR {total_cost}\n"

with open(cost_summary, 'w') as file:
    file.write(write_cost)

# Visualize the results
v = Visualizer(image[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
cv2.imshow("Detectron2 Output", out.get_image()[:, :, ::-1])
cv2.waitKey(0)
cv2.destroyAllWindows()
