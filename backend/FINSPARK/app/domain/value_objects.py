import ipaddress
from datetime import datetime, time, timezone
from typing import Any


class IPAddress:
    """
    Value object representing a Client IP Address with CIDR check validation.
    """

    def __init__(self, ip_str: str):
        try:
            self._ip = ipaddress.ip_address(ip_str.strip())
        except ValueError as e:
            raise ValueError(f"Invalid IP address format: {ip_str}") from e

    @property
    def value(self) -> str:
        return str(self._ip)

    def is_in_subnet(self, subnet_cidr: str) -> bool:
        """
        Validates if the IP is part of a whitelist network block.
        """
        try:
            network = ipaddress.ip_network(subnet_cidr.strip(), strict=False)
            return self._ip in network
        except ValueError:
            return False

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IPAddress):
            return False
        return self._ip == other._ip

    def __repr__(self) -> str:
        return f"IPAddress({self.value})"


class TimeRange:
    """
    Value object representing a time window (e.g. core banking business hours).
    """

    def __init__(self, start: time, end: time):
        self.start = start
        self.end = end

    def contains(self, dt: datetime) -> bool:
        """
        Checks if the provided timestamp falls inside this time window (UTC).
        """
        # Convert dt to the target timezone or compare times directly in UTC
        check_time = dt.time()
        if self.start <= self.end:
            return self.start <= check_time <= self.end
        else:  # Handles wrap-around (overnight shifts)
            return check_time >= self.start or check_time <= self.end

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TimeRange):
            return False
        return self.start == other.start and self.end == other.end

    def __repr__(self) -> str:
        return f"TimeRange({self.start} - {self.end})"
