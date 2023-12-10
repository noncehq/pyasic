# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field

from pyasic.config.base import MinerConfigOption, MinerConfigValue


@dataclass
class PowerScalingShutdownEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    duration: int = None

    def as_bosminer(self) -> dict:
        cfg = {"shutdown_enabled": True}

        if self.duration is not None:
            cfg["shutdown_duration"] = self.duration


@dataclass
class PowerScalingShutdownDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")

    def as_bosminer(self) -> dict:
        return {"shutdown_enabled": False}


class PowerScalingShutdown(MinerConfigOption):
    enabled = PowerScalingShutdownEnabled
    disabled = PowerScalingShutdownDisabled

    @classmethod
    def from_bosminer(cls, power_scaling_conf: dict):
        sd_enabled = power_scaling_conf.get("shutdown_enabled")
        if sd_enabled is not None:
            if sd_enabled:
                return cls.enabled(power_scaling_conf.get("shutdown_duration"))
            else:
                return cls.disabled()
        return None


@dataclass
class PowerScalingEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    power_step: int = None
    minimum_power: int = None
    shutdown_enabled: PowerScalingShutdown = None

    @classmethod
    def from_bosminer(cls, power_scaling_conf: dict):
        power_step = power_scaling_conf.get("power_step")
        min_power = power_scaling_conf.get("min_psu_power_limit")
        sd_mode = PowerScalingShutdown.from_bosminer(power_scaling_conf)

        return cls(
            power_step=power_step, minimum_power=min_power, shutdown_enabled=sd_mode
        )

    def as_bosminer(self) -> dict:
        cfg = {
            "enabled": True
        }
        if self.power_step is not None:
            cfg["power_step"] = self.power_step
        if self.minimum_power is not None:
            cfg["min_psu_power_limit"] = self.minimum_power

        if self.shutdown_enabled is not None:
            cfg = {**cfg, **self.shutdown_enabled.as_bosminer()}

        return {"power_scaling": cfg}

@dataclass
class PowerScalingDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")


class PowerScalingConfig(MinerConfigOption):
    enabled = PowerScalingEnabled
    disabled = PowerScalingDisabled

    @classmethod
    def default(cls):
        return cls.disabled()

    @classmethod
    def from_bosminer(cls, toml_conf: dict):
        power_scaling = toml_conf.get("power_scaling")
        if power_scaling is not None:
            enabled = power_scaling.get("enabled")
            if enabled is not None:
                if enabled:
                    return cls.enabled().from_bosminer(power_scaling)
                else:
                    return cls.disabled()

        return cls.default()