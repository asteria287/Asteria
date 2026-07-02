"""
缓存工具 - 文件缓存 + 内存缓存
"""
import json
import hashlib
import time
from pathlib import Path
from functools import wraps
from config import CACHE_DIR


# 内存缓存（快速访问）
_memory_cache: dict = {}


def _hash_key(key: str) -> str:
    """生成缓存键的哈希"""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def cache_get(key: str) -> dict | None:
    """
    获取缓存数据
    先查内存，再查文件
    """
    hashed = _hash_key(key)

    # 内存缓存
    if hashed in _memory_cache:
        entry = _memory_cache[hashed]
        if entry["expires_at"] > time.time():
            return entry["data"]
        else:
            del _memory_cache[hashed]

    # 文件缓存
    cache_file = CACHE_DIR / f"{hashed}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                entry = json.load(f)
            if entry["expires_at"] > time.time():
                _memory_cache[hashed] = entry
                return entry["data"]
            else:
                cache_file.unlink()
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink()

    return None


def cache_set(key: str, data: dict, ttl: int = 3600):
    """
    设置缓存数据
    同时写入内存和文件
    """
    hashed = _hash_key(key)
    entry = {
        "data": data,
        "expires_at": time.time() + ttl,
        "created_at": time.time()
    }

    # 内存缓存
    _memory_cache[hashed] = entry

    # 文件缓存
    cache_file = CACHE_DIR / f"{hashed}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, default=str)
    except Exception:
        pass  # 文件写入失败不影响内存缓存


def cache_clear(key: str = None):
    """清除缓存"""
    if key:
        hashed = _hash_key(key)
        _memory_cache.pop(hashed, None)
        cache_file = CACHE_DIR / f"{hashed}.json"
        if cache_file.exists():
            cache_file.unlink()
    else:
        _memory_cache.clear()
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
