from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Quantum Position Engine"
    VERSION: str = "3.0.0"
    # 汇率缓存时间 (秒)，默认5分钟
    CACHE_TTL: int = 300

settings = Settings()
