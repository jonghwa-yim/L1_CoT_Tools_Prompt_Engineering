import numpy as np
from scipy.spatial import cKDTree
from collections import Counter

class KNNClassifier:
    def __init__(self, k=3):
        self.k = k
        self.data = None
        self.labels = None
        self.tree = None

    def fit(self, data, labels):
        """Store the training data and labels, and build the KD Tree for faster nearest neighbor lookup."""
        self.data = data
        self.labels = labels
        self.tree = cKDTree(self.data)

    def predict(self, query):
        """Predict the label for one or multiple query points with improved performance."""
        outputs = []

        for point in query:
            # Use KD Tree query to find the nearest neighbors
            distances, indices = self.tree.query(point, k=self.k)
            nearest_labels = self.labels[indices]
            label_counts = Counter(nearest_labels)
            output = label_counts.most_common(1)[0][0]
            outputs.append(output)

        return np.array(outputs)


def large_test():
    # Create a larger, more realistic dataset for demonstration
    print("Generating a large dataset for demonstration...")
    np.random.seed(42)  # for reproducibility

    # Generate training data with two distinct clusters
    n_train_samples_per_class = 1000
    train_class0 = np.random.randn(n_train_samples_per_class, 2) + np.array([2, 2])
    train_class1 = np.random.randn(n_train_samples_per_class, 2) + np.array([8, 8])
    X_train = np.vstack((train_class0, train_class1))
    y_train = np.array([0] * n_train_samples_per_class + [1] * n_train_samples_per_class)

    # Generate test data from the same distributions
    n_test_samples_per_class = 200
    test_class0 = np.random.randn(n_test_samples_per_class, 2) + np.array([2, 2])
    test_class1 = np.random.randn(n_test_samples_per_class, 2) + np.array([8, 8])
    X_test = np.vstack((test_class0, test_class1))
    y_test_true = np.array([0] * n_test_samples_per_class + [1] * n_test_samples_per_class)

    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}\n")

    # Train and predict
    knn = KNNClassifier(k=5)
    knn.fit(X_train, y_train)
    import time
    start_time = time.time()
    predictions = knn.predict(X_test)
    end_time = time.time()
    print(f"Time taken for prediction on {len(X_test)} samples: {end_time - start_time:.6f} seconds")

    # Calculate and print accuracy to verify the model
    accuracy = np.mean(predictions == y_test_true)
    print(f"Model accuracy on the test set: {accuracy:.4f}")
    print(f"Predictions (first 10): {predictions[:10]}")
    print(f"True labels (first 10):   {y_test_true[:10]}")

# Example usage
if __name__ == "__main__":
    large_test()
    # # Sample data
    # X_train = np.array([[1, 2], [2, 3], [3, 1], [6, 5], [7, 7], [8, 6]])
    # y_train = np.array([0, 0, 0, 1, 1, 1])
    # X_test = np.array([[2, 2], [7, 6]])

    # # Train and predict
    # knn = KNNClassifier(k=4)
    # knn.fit(X_train, y_train)
    # import time
    # start_time = time.time()
    # predictions = knn.predict(X_test)
    # end_time = time.time()
    # print(f"Time taken: {end_time - start_time:.6f} seconds")

    # print(f"Predictions: {predictions}")