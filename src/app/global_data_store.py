from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker
from .signal_bus import SignalBus

class GlobalDataStore(QObject):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            QObject.__init__(cls._instance)
            cls._instance._data = {}
            cls._instance._mutex = QMutex()  # 添加互斥鎖保證線程安全
        return cls._instance
    
    def __init__(self):
        pass
    
    @property
    def data(self):
        """獲取數據的副本以避免直接修改內部數據"""
        with QMutexLocker(self._mutex):
            return self._data.copy()
    
    def update(self, new_data: dict):
        """線程安全的更新數據方法"""
        with QMutexLocker(self._mutex):
            self._data.update(new_data)
        SignalBus.dataUpdated.emit(new_data)  # 注意: 在鎖外發射信號
    
    def get(self, key, default=None):
        """線程安全的獲取單個值"""
        with QMutexLocker(self._mutex):
            return self._data.get(key, default)
    
    def set(self, key, value):
        """線程安全的設置單個值"""
        with QMutexLocker(self._mutex):
            self._data[key] = value
        SignalBus.dataUpdated.emit({key: value})
    
    def clear(self):
        """清空所有數據"""
        with QMutexLocker(self._mutex):
            self._data.clear()
        SignalBus.dataUpdated.emit({})