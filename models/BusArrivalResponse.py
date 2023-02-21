from typing import List, Optional, Union

from pydantic import BaseModel, Field
import datetime


class ArrivalTime(BaseModel):
    hour: str
    minute: str
    second: str


class NextBusData(BaseModel):
    service_no: str
    estimated_arrival: list[str]

    def __str__(self) -> str:
        print(self.estimated_arrival)
        return f"Bus no: {self.service_no} | {' | '.join(self.estimated_arrival)}"


class BusStopData(BaseModel):
    bus_stop_code: str
    next_buses: list[NextBusData]

    def __str__(self):
        next_buses_text = "\n".join([str(i) for i in self.next_buses])
        return f"""Bus stop: {self.bus_stop_code}

{next_buses_text}"""
