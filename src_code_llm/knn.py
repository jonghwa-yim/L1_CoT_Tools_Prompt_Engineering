import numpy as np


class KNNClassifier:
    def __init__(self, k=3):
        self.k = k
        self.data = None
        self.labels = None

    def fit(self, data, labels):
        """Store the training data and labels."""
        self.data = data
        self.labels = labels

    def predict(self, query):
        """Predict the label for a single query point."""
        
        outputs = []

        for point in query:
            distances = 0
            for data_, pnt_ in zip(self.data, point):
                distances += (data_ - pnt_) ** 2
            indices = np.argsort(distances)[:self.k]
            nearest_labels = self.labels[indices] # [0, 0, 1]
            labels, counts = np.unique(nearest_labels, return_counts=True)
            output = labels[np.argmax(counts)]
            outputs.append(output)
            print("nearest_labels:", nearest_labels)
        return np.array(outputs)

# Example usage
if __name__ == "__main__":
    # Sample data
    X_train = np.array([[1, 2], [2, 3], [3, 1], [6, 5], [7, 7], [8, 6]])
    y_train = np.array([0, 0, 0, 1, 1, 1])
    
    X_test = np.array([[2, 2], [7, 6]])
    
    # Train and predict
    knn = KNNClassifier(k=4)
    knn.fit(X_train, y_train)
    import time
    start_time = time.time()
    predictions = knn.predict(X_test)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.6f} seconds")
    
    print(f"Predictions: {predictions}")
