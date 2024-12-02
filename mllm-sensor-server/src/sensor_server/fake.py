import threading
import time
from collections import deque
from typing import Optional

from sensor_server.server import SERVER_IP

from .server import SensorServer


class FakeSensorServer(SensorServer):
    def __init__(self, update_interval=0.25) -> None:
        super().__init__(update_interval=update_interval)
        self.velocity_records = deque([0.0] * 10, maxlen=10)
        self.break_pressure_records = deque([0.0] * 10, maxlen=10)
        self.steering_angle_records = deque([0.0] * 10, maxlen=10)
        self.gear_status = "P"
        self.left_turn_signal = False
        self.right_turn_signal = False

        self.control_thread: Optional[threading.Thread] = None
        self.speed_target = 0.0
        self.speed_change = 0.0
        self.break_target = 0.0
        self.break_change = 0.0
        self.steering_target = 0.0
        self.steering_change = 0.0

    def _process_client_request(self, data: bytes) -> bytes:
        result = ""
        result += f"[Velocities]:{list(self.velocity_records)}\n"
        result += f"[Break Pressure]:{list(self.break_pressure_records)}\n"
        result += f"[Steering Angles]:{list(self.steering_angle_records)}\n"
        result += f"[Gear Status]:{self.gear_status}\n"
        result += f"[Left Turn Signal]:{self.left_turn_signal}\n"
        result += f"[Right Turn Signal]:{self.right_turn_signal}\n"
        return result.encode()

    def _change_status(self):
        while self.is_active:
            if self.speed_target != self.velocity_records[-1]:
                self.velocity_records.append(
                    self.velocity_records[-1] + self.speed_change
                )
                print(f"Speed: {self.velocity_records}")

            if self.break_target != self.break_pressure_records[-1]:
                self.break_pressure_records.append(
                    self.break_pressure_records[-1] + self.break_change
                )
                print(f"Break Pressure: {self.break_pressure_records}")

            if self.steering_target != self.steering_angle_records[-1]:
                self.steering_angle_records.append(
                    self.steering_angle_records[-1] + self.steering_change
                )
                print(f"Steering Angle: {self.steering_angle_records}")
            # else:
            #     if self.velocity_records[0] != self.velocity_records[-1]:
            #         self.velocity_records.append(self.velocity_records[-1])
            #         print(f"Speed: {self.velocity_records}")

            time.sleep(self.update_interval)

    def activate(self):
        super().activate()
        self.control_thread = threading.Thread(target=self._change_status)
        self.control_thread.start()

    def deactivate(self):
        super().deactivate()
        self.control_thread.join()


def activate_server():
    with FakeSensorServer() as server:
        while True:
            user_input = input("Enter 'q' to quit: ")
            user_input_key = user_input.split("=")[0]
            if len(user_input.split("=")) < 2:
                print("Invalid command")
                continue
            user_input_params = user_input.split("=")[1]
            user_input_params = user_input_params.split(",")
            multiplier = (
                float(user_input_params[1]) if len(user_input_params) > 1 else 1
            )
            if user_input == "q":
                break
            elif "speed" == user_input_key:
                server.speed_target = float(user_input_params[0])
                server.speed_change = (
                    (server.speed_target - server.velocity_records[-1])
                    * server.update_interval
                    / multiplier
                )
            elif "break" == user_input_key:
                server.break_target = float(user_input_params[0])
                server.break_change = (
                    (server.break_target - server.break_pressure_records[-1])
                    * server.update_interval
                    / multiplier
                )
            elif "steering" == user_input_key:
                server.steering_target = float(user_input_params[0])
                server.steering_change = (
                    (server.steering_target - server.steering_angle_records[-1])
                    * server.update_interval
                    / multiplier
                )
            elif "gear" == user_input_key:
                server.gear_status = user_input_params[0]
            elif "left" == user_input_key:
                server.left_turn_signal = True if user_input_params[0] == "1" else False
            elif "right" == user_input_key:
                server.right_turn_signal = (
                    True if user_input_params[0] == "1" else False
                )
            else:
                print("Invalid command")
    print("Server deactivated!")
