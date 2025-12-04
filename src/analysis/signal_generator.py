import numpy as np

def generate_signals(X):
    n = X.shape[0]
    np.random.seed(42)
    buy = np.random.randint(0, 2, size=n).tolist()
    sell = [1-b for b in buy]
    confidence = np.random.rand(n).tolist()
    return {
        'buy': buy,
        'sell': sell,
        'confidence': confidence
    }
