import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
import os

def read_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            if "conf_thresh" in line:
                parts = line.split(',')
                conf_thresh = float(parts[0].split('=')[1].strip())
                TP = int(parts[1].split('=')[1].strip())
                FP = int(parts[2].split('=')[1].strip())
                FN = int(parts[3].split('=')[1].strip())
                data.append((conf_thresh, TP, FP, FN))
    return data

def calculate_metrics(data):
    results = []
    for conf_thresh, TP, FP, FN in data:
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        results.append((conf_thresh, recall, precision, f1_score))
    return results

def calculate_auc(results):
    # Extract recalls and precisions for AUC calculation
    recalls = [r[0] for r in results]
    precisions = [r[1] for r in results]
    return metrics.auc(recalls, precisions)

def generate_pr_curve(results, image_size, auc):
    recalls = [r[1] for r in results]
    precisions = [r[2] for r in results]
    plt.figure()
    plt.plot(recalls, precisions, marker='o', label='Precision-Recall Curve')
    plt.title(f'Precision-Recall Curve - Image Size {image_size} - AUC {auc:4f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'results/precision_recall_{image_size}.png')
    plt.close()

def main():
    image_sizes = [512, 608, 800]
    final_results = {}

    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    for size in image_sizes:
        file_path = f'data/{size}_yolov4_5000_cell_data.txt'
        data = read_file(file_path)
        results = calculate_metrics(data)
        auc = calculate_auc(results)
        generate_pr_curve(results, size, auc)

        # Find the best threshold based on F1-Score
        best_threshold = max(results, key=lambda x: x[3])  # Max F1-Score

        # Store results
        final_results[size] = {
            'auc': auc,
            'best_threshold': best_threshold
        }

    best_size = max(final_results, key=lambda size: final_results[size]['auc'])
    best_info = final_results[best_size]

    # Save the best configuration to a text file
    with open('results/best_configuration.txt', 'w') as file:
        file.write("================ \n")
        file.write(f"Best Image Size: {best_size}\n")
        file.write(f"AUC: {best_info['auc']:.4f}\n")
        file.write(f"Best Threshold: {best_info['best_threshold'][0]}\n")
        file.write(f"Recall: {best_info['best_threshold'][1]:.4f}\n")
        file.write(f"Precision: {best_info['best_threshold'][2]:.4f}\n")
        file.write(f"F1-Score: {best_info['best_threshold'][3]:.4f}\n")
        file.write("================ \n")
        file.write("\n## Resume Images Configurations:\n")
        file.write("\n")
        for size, info in final_results.items():
            file.write(f"Image Size: {size}\n")
            file.write(f"AUC: {info['auc']:.4f}\n")
            file.write(f"Best Threshold: {info['best_threshold'][0]}\n")
            file.write(f"Recall: {info['best_threshold'][1]:.4f}\n")
            file.write(f"Precision: {info['best_threshold'][2]:.4f}\n")
            file.write(f"F1-Score: {info['best_threshold'][3]:.4f}\n")
            file.write("\n")


if __name__ == "__main__":
    main()
