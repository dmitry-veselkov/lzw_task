from pydantic import BaseModel


class Password(BaseModel):
    has_password: bool
    password: bytes | None
    salt: bytes


class MetaInfo(BaseModel):
    password: Password
    files: dict[str, int]

    @property
    def has_many_files(self) -> bool:
        return len(self.files) > 1
