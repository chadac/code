from dataclasses import dataclass


@dataclass
class Profile:
    name: str
    remote: str
    branch: str
