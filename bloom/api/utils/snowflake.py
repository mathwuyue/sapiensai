import time

class Snowflake:
    def __init__(
        self,
        worker_id: int = 1,
        datacenter_id: int = 1,
        sequence: int = 0,
        twepoch: int = 1704067200000
    ):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.twepoch = twepoch

        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)

        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        self.last_timestamp = -1

    def _til_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._time_gen()
        while timestamp <= last_timestamp:
            timestamp = self._time_gen()
        return timestamp

    def _time_gen(self) -> int:
        return int(time.time() * 1000)

    def generate_id(self) -> int:
        timestamp = self._time_gen()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards!")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return (
            ((timestamp - self.twepoch) << self.timestamp_left_shift) |
            (self.datacenter_id << self.datacenter_id_shift) |
            (self.worker_id << self.worker_id_shift) |
            self.sequence
        )
