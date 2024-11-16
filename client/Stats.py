import logging


class Stats:
    """
    Class for keeping statistics related results. Keeps a dictionary to store stats. Stored stats are output to file to
    be processed after simulation.
    """

    def __init__(self, output_path: str) -> None:
        """
        Constructor for stats class

        Args:
            output_path: Path to output stats to
        """

        self.output_path = output_path
        self.stats = {}

    def record_stat(self, stat_name: str, stat_value: int) -> None:
        """
        Record a stat

        Args:
            stat_name: Name of stat
            stat_value: Value of stat
        """

        self.stats[stat_name] = stat_value

    def dump(self) -> None:
        """
        Dump stats to file
        """

        logging.info(f"Dumping {len(self.stats.items())} states to {self.output_path}")

        with open(self.output_path, "w") as stats_file:
            for stat_name, stat_value in self.stats.items():
                stats_file.write(f"{stat_name} {stat_value}\n")
