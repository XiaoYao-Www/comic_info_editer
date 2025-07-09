import threading
from typing import Any, Dict, Optional, Set, Callable

class _GlobalDataStore:
    """ 數據存儲類 """
    _lock = threading.Lock()
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._mutex = threading.Lock()
        self._callbacks: Set[Callable[[Dict[str, Any]], None]] = set()
    
    @property
    def data(self) -> Dict[str, Any]:
        """ 獲取數據的副本 """
        with self._mutex:
            return self._data.copy()
    
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """ 訂閱數據更新 """
        with self._mutex:
            self._callbacks.add(callback)
    
    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """ 取消訂閱 """
        with self._mutex:
            self._callbacks.discard(callback)
    
    def _notify(self, changes: Dict[str, Any]) -> None:
        """ 內部通知機制 """
        with self._mutex:
            callbacks = self._callbacks.copy()
        for callback in callbacks:
            try:
                callback(changes)
            except Exception:
                import traceback
                traceback.print_exc()
    
    def update(self, new_data: Dict[str, Any]) -> None:
        """ 批量更新數據 """
        with self._mutex:
            self._data.update(new_data)
        self._notify(new_data)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """ 獲取單個值 """
        with self._mutex:
            return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """ 設置單個值 """
        with self._mutex:
            self._data[key] = value
        self._notify({key: value})
    
    def clear(self) -> None:
        """ 清空所有數據 """
        with self._mutex:
            self._data.clear()
        self._notify({})

# 模組級全局實例
GLOBAL_DATA_STORE = _GlobalDataStore()