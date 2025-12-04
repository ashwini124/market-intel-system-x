import matplotlib.pyplot as plt

def plot_sampled_signal(confidence, sample=50):
    if len(confidence) > sample:
        data = confidence[::len(confidence)//sample]
    else:
        data = confidence
    plt.figure(figsize=(10,4))
    plt.plot(data, marker='o')
    plt.title("Sampled Confidence Signal")
    plt.xlabel("Sample Index")
    plt.ylabel("Confidence")
    plt.show()
