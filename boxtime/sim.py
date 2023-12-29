import json
import random
import pytz
from copy import deepcopy
from datetime import datetime, timedelta

import numpy as np


with open("./assets/events/primary_2023-12-01_2023-12-31_False_False.bak", "r") as f:
    real_events = json.load(f)


def main():
    mock_events = []
    color_ids = [str(i) for i in range(1, 12)]
    probs = np.zeros(11)
    probs[0] = 0.1
    probs[1] = 0.1
    probs[2] = 0.01
    probs[3] = 0.01
    probs[4] = 0.16
    probs[5] = 0.1
    probs[6] = 0.01
    probs[7] = 0.1
    probs[8] = 0.01
    probs[9] = 0.2
    probs[10] = 0.2

    print("probs", sum(probs))

    for i in range(365):
        current_date = datetime(2023, 1, 1) + timedelta(days=i + 1 - 1)

        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        n = random.randint(4, 10)
        selected_objects = deepcopy(random.sample(real_events, n))

        for i, obj in enumerate(selected_objects):
            start_dt = current_date.replace(
                hour=9 + i, minute=0, second=0, microsecond=0, tzinfo=pytz.utc
            )

            end_dt = start_dt + timedelta(hours=1)

            obj["start"]["dateTime"] = start_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
            obj["end"]["dateTime"] = end_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
            selected_color_id = np.random.choice(color_ids, p=probs)
            obj["colorId"] = selected_color_id

            mock_events.append(obj)
        current_date += timedelta(days=1)

    with open("./assets/events/primary_2023-12-01_2023-12-31_False_False", "w") as f:
        json.dump(mock_events, f)


if __name__ == "__main__":
    main()
