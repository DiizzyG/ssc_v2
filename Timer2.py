import threading
import types

class ResettableTimer:
    def __init__(self, timeout, on_timeout):
        self.timeout = timeout
        self.on_timeout = on_timeout
        self._reset_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            if not self._reset_event.wait(self.timeout):
                self.on_timeout()
                break
            self._reset_event.clear()

    def reset(self):
        self._reset_event.set()

    def cancel(self):
        self._stop_event.set()
        self._reset_event.set()



class LifecycleObject:
    def __init__(self, key, registry, timeout=30, *args, **kwargs):
        self._key = key
        self._registry = registry
        self._timeout = timeout
        self._timer = ResettableTimer(timeout, self._on_expire)

    def _on_expire(self):
        print(f"[{self._key}] 超时未使用，正在销毁...")
        self._registry.remove(self._key)
        self._timer = None

    def __getattribute__(self, name):
        # 内部属性正常访问
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        attr = object.__getattribute__(self, name)

        if callable(attr):
            def wrapped(*args, **kwargs):
                self._reset_timer()
                return attr(*args, **kwargs)
            return wrapped
        else:
            self._reset_timer()
            return attr

    def _reset_timer(self):
        if self._timer:
            self._timer.reset()

    def cleanup(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

class ObjectRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._objects = {}

    def __getitem__(self, key):
        with self._lock:
            return self._objects[key]

    def __setitem__(self, key, obj):
        with self._lock:
            self._objects[key] = obj

    def __delitem__(self, key):
        with self._lock:
            obj = self._objects.pop(key, None)
            if obj:
                obj.cleanup()

    def __contains__(self, key):
        with self._lock:
            return key in self._objects

    def __len__(self):
        with self._lock:
            return len(self._objects)

    def __iter__(self):
        with self._lock:
            return iter(self._objects.copy())  # 拷贝防止迭代期间被修改

    def keys(self):
        return list(iter(self))

    def values(self):
        with self._lock:
            return list(self._objects.values())

    def items(self):
        with self._lock:
            return list(self._objects.items())

    def remove(self, key):
        # 手动销毁某个 key（对象自己也会回调这里）
        self.__delitem__(key)


# import time

# class MyWorker(LifecycleObject):
#     def work(self):
#         print(f"[{self._key}] 正在工作...")

# registry = ObjectRegistry()

# # 添加对象
# for i in range(3):
#     worker = MyWorker(i, registry, timeout=5)
#     registry.add(i, worker)

# # 模拟调用
# registry.get(0).work()  # 只调用了第一个
# time.sleep(2)
# registry.get(0).work()
# time.sleep(6)  # 第二个和第三个被清理了

# print("剩下的 keys:", registry.keys())  # 只剩下 0