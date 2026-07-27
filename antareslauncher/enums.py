from enum import IntEnum, StrEnum


class Modes(IntEnum):
    antares = 1
    xpansion_r = 2
    xpansion_cpp = 3
    xpansion_trajectory = 4


class XpansionMode(StrEnum):
    NOT_XPANSION = ""
    R = "r"
    CPP = "cpp"
    TRAJECTORY = "trajectory"

    def to_run_mode(self) -> Modes:
        if self == XpansionMode.NOT_XPANSION:
            return Modes.antares
        elif self == XpansionMode.R:
            return Modes.xpansion_r
        elif self == XpansionMode.CPP:
            return Modes.xpansion_cpp
        elif self == XpansionMode.TRAJECTORY:
            return Modes.xpansion_trajectory
        else:
            raise ValueError(f"Unknown Xpansion mode: {self}")
