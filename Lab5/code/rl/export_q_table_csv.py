import csv
import os
import pickle


def export_q_table_to_csv(
    input_path: str = "data/q_table.pkl",
    output_path: str = "data/q_table.csv",
):
    """Экспортирует Q-таблицу в CSV (state_index, action, q_value)."""
    base_dir = os.path.dirname(__file__)
    input_resolved = input_path if os.path.isabs(input_path) else os.path.join(base_dir, input_path)
    output_resolved = output_path if os.path.isabs(output_path) else os.path.join(base_dir, output_path)

    with open(input_resolved, "rb") as file:
        q_table = pickle.load(file)

    os.makedirs(os.path.dirname(output_resolved), exist_ok=True)
    with open(output_resolved, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["state_index", "action", "q_value"])
        for i, (state, actions) in enumerate(q_table.items()):
            for action, value in actions.items():
                writer.writerow([i, repr(action), value])

    return output_resolved


if __name__ == "__main__":
    path = export_q_table_to_csv()
    print(f"CSV сохранен: {path}")

