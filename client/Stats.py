import logging

class Stats:
    def __init__(self, output_path):
        self.output_path = output_path
        self.stats = {}

    def record_stat(self, stat_name, stat_value):
        self.stats[stat_name] = stat_value

    def dump(self):
        logging.info(f"Dumping {len(self.stats.items())} states to {self.output_path}")

        with open(self.output_path, "w") as stats_file:
            for stat_name, stat_value in self.stats.items():
                stats_file.write(f"{stat_name} {stat_value}\n")
