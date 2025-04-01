from dataclasses import asdict, dataclass
import json


@dataclass
class MsgComplete:
    call_id: str
    result: dict

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
