from dataclasses import asdict, dataclass
import json


@dataclass
class MsgQueued:
    call_id: str
    file_path: str
    object_name: str
    bucket_name: str

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
