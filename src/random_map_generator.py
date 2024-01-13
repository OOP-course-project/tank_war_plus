import random
import json


class generate_map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bricks = []
        self.irons = []
        self.map_data = {"bricks": self.bricks, "irons": self.irons}

    def randomly_generate_map(self):
        total_cells = self.width * self.height
        total_obstacles = random.randint(total_cells // 4, total_cells // 3)

        # Reserve a position for the tank at the bottom
        tank_position = {"x": self.width // 2, "y": self.height - 1}
        self.bricks.append(tank_position)

        # Generate irons, the maximum number of irons is 8
        iron_rows = set()
        iron_cols = set()
        for _ in range(15):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(9, 17)
                if (
                    (x == tank_position["x"] and y == tank_position["y"])
                    or (len(iron_rows) == 9 and y in iron_rows)
                    or (len(iron_cols) == self.width and x in iron_cols)
                    or (
                        abs(x - tank_position["x"]) <= 1
                        and abs(y - tank_position["y"]) <= 1
                    )
                ):
                    continue
                self.irons.append({"x": x, "y": y})
                iron_rows.add(y)
                iron_cols.add(x)
                break

        # Generate bricks, the maximum number of bricks is total_obstacles - 8
        obstacle_positions = set()
        while len(self.bricks) + len(self.irons) < total_obstacles:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (
                (x == tank_position["x"] and y == tank_position["y"])
                or (y < 2 or y > 23)
                or (x, y) in obstacle_positions
            ):
                continue
            self.bricks.append({"x": x, "y": y})
            obstacle_positions.add((x, y))

        self.map_data = {"bricks": self.bricks, "irons": self.irons}

    def to_json(self):
        return json.dumps(self.map_data, indent=4)

    def save_map(self, filename):
        # 保存地图数据到文件
        with open(filename, "w") as file:
            json.dump(self.map_data, file, indent=4)  # 将地图数据以 JSON 格式写入文件


if __name__ == "__main__":
    map = generate_map(26, 26)
    map.randomly_generate_map()
    map_data = map.to_json()
    map.save_map("../maps/test_map.json")
