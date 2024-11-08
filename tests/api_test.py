"""Module performs statisitcal testing of the API

If using a different deployment, change the url to the correct endpoint
"""
import matplotlib.pyplot as plt
import requests
import json
import numpy as np
import time
from pathlib import Path
import argparse
from collections import Counter, OrderedDict

# Load test data
data_path = Path.cwd().parent.joinpath("data")
with np.load(data_path.joinpath("mnist_test.npz"), allow_pickle=True) as f:
    x_test, y_test = f["x"], f["y"]

x_test = np.expand_dims(x_test, -1)
# normalize pixel values
x_test = x_test.astype("float32") / 255.0


def make_prediction(instances, url):
    data = json.dumps({"x": instances})
    headers = {"accept": "application/json", "content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    if json_response.status_code == 200:
        predictions = json.loads(json_response.text)["y"]
    else:
        raise Exception("Error: {}".format(json_response.status_code))
    return predictions


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--num_instances",
        type=int,
        help="Number of instances to predict",
        required=False,
        default=50,
    )
    parser.add_argument(
        "-p",
        "--plot",
        help="Show histogram of predictions [True/False]",
        required=False,
        default="False",
    )

    parser.add_argument(
        "-l", "--local", help="Test local deployment [True/False]", required=False, default="True"
    )

    args = parser.parse_args()
    i = args.num_instances

    if args.local == "True":
        url = "http://localhost:80/predict/batch"
    else:
        # AWS server
        url = (
            "http://clarity-api-advanced.eba-289rmxee.eu-west-1.elasticbeanstalk.com/predict/batch"
        )

    # Get a slice of the test data
    x, y = x_test[0:i].tolist(), y_test[0:i].tolist()
    # Make predictions and report time
    start = time.time()
    predictions = make_prediction(x, url)
    end = time.time()
    # Return the time and accuracy
    print("Time: {:.4f}s".format(end - start))
    accuracy = sum(p == t for p, t in zip(predictions, y)) / len(y)
    print("Accuracy: {:.2f}%".format(accuracy * 100))
    distribution = Counter(predictions)
    distribution = OrderedDict(sorted(distribution.items()))
    if args.plot == "True":
        labels, values = zip(*distribution.items())
        indexes = np.arange(len(labels))
        plt.bar(labels, values)
        plt.xticks(indexes, labels)
        plt.show()
    else:
        print("Prediction distribution: {}".format(distribution))
