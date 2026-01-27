---
title: "Race Condition"
date: "2025年 09月 12日"
excerpt: "深入了解 Race Condition 的原因、危險和解決方案。"
tags: ["Threading", "Python", "並發編程"]
readTime: "12 min read"
slug: "race-condition"
---

## 什麼是 Race Condition？

Race Condition 是指多個執行緒同時訪問共享資源，但沒有適當的同步機制，導致結果不可預測的現象。

簡單比喻：想像兩個人同時從銀行帳戶提款。如果沒有鎖機制，可能都能提出超過帳戶餘額的金額。

### 最簡單的例子

```python
# 不安全的程式碼
counter = 0

def increment():
    global counter
    counter += 1

# 用 100 個執行緒各加 1000 次
# 預期結果：100,000
# 實際結果：通常是 20,000 ~ 80,000（不確定）
```

### 為什麼？

因為 `counter += 1` 實際上不是原子操作（atomic operation）。它被編譯成三個步驟：

```assembly
LOAD counter into register    # 讀取值
ADD 1 to register            # 加 1
STORE register back to counter # 存回
```

如果兩個執行緒同時執行，可能會互相覆蓋彼此的結果。

---

## Race Condition 的三個必要條件

要發生 Race Condition，必須同時滿足以下三個條件：

### 1. 多個執行緒/進程訪問共享資源

```python
shared_resource = {"balance": 1000}
# 多個執行緒都想修改這個字典
```

### 2. 至少有一個執行緒進行寫入操作

```python
# 只有讀取是安全的
# 但只要有寫入，就可能出問題
balance = shared_resource["balance"]  # 讀（安全）
shared_resource["balance"] -= 100     # 寫（危險）
```

### 3. 沒有同步機制控制訪問順序

```python
# 沒有鎖、沒有信號量、沒有原子操作
# = Race Condition 的溫床
```

---

## 實戰案例 1：銀行轉帳系統

### 問題程式碼

```python
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
    
    def transfer(self, amount):
        """不安全的轉帳"""
        if self.balance >= amount:
            self.balance -= amount
            print(f"轉帳 {amount}，剩餘 {self.balance}")

account = BankAccount(1000)

def withdraw_many_times():
    for _ in range(100):
        account.transfer(10)

threads = [threading.Thread(target=withdraw_many_times) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"最終餘額：{account.balance}")
```

### 為什麼會出問題？

| 時間 | 執行緒 A | 執行緒 B | account.balance |
|------|---------|---------|-----------------|
| 1    | 讀: 1000|         | 1000            |
| 2    |         | 讀: 1000| 1000            |
| 3    | 寫: 990 |         | 990             |
| 4    |         | 寫: 990 | 990 (應該是 980!)    |

執行緒 B 覆蓋了執行緒 A 的操作。

### 解決方案：Mutex Lock（互斥鎖）

```python
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()
    
    def transfer(self, amount):
        """安全的轉帳"""
        with self.lock:
            if self.balance >= amount:
                self.balance -= amount
                print(f"轉帳 {amount}，剩餘 {self.balance}")

account = BankAccount(1000)

def withdraw_many_times():
    for _ in range(100):
        account.transfer(10)

threads = [threading.Thread(target=withdraw_many_times) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"最終餘額：{account.balance}")  # 現在一定是 0
```

**原理：** 鎖確保同一時間只有一個執行緒能進入臨界區。

---

## 實戰案例 2：生產者-消費者問題

### 問題程式碼

```python
import threading
import time

class Buffer:
    def __init__(self):
        self.items = []
    
    def produce(self, item):
        self.items.append(item)
        print(f"生產: {item}")
    
    def consume(self):
        if self.items:
            item = self.items.pop(0)
            print(f"消費: {item}")

buffer = Buffer()

def producer():
    for i in range(100):
        buffer.produce(f"item-{i}")
        time.sleep(0.01)

def consumer():
    for _ in range(100):
        buffer.consume()
```

### 解決方案：Condition Variable

```python
import threading
import time

class Buffer:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
    
    def produce(self, item):
        with self.condition:
            self.items.append(item)
            print(f"生產: {item}")
            self.condition.notify()
    
    def consume(self):
        with self.condition:
            while not self.items:
                self.condition.wait()
            item = self.items.pop(0)
            print(f"消費: {item}")

buffer = Buffer()

def producer():
    for i in range(100):
        buffer.produce(f"item-{i}")
        time.sleep(0.01)

def consumer():
    for _ in range(100):
        buffer.consume()

threads = [
    threading.Thread(target=producer),
    threading.Thread(target=consumer),
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

---

## Race Condition 的常見類型

### 1. 資料競爭（Data Race）

```python
x = 0
# 執行緒 A: x = x + 1
# 執行緒 B: x = x + 1
# 結果：x = 1（而不是 2）
```

### 2. 檢查-執行問題（Check-Then-Act）

```python
if file_exists(filename):
    # 執行緒 B 在這裡可能刪除了檔案
    data = open("data.txt")  # 錯誤！
```

### 3. 讀-修改-寫

```python
# 執行緒 A: temp = counter; temp++; counter = temp
# 執行緒 B: temp = counter; temp++; counter = temp
# 結果：counter 只 +1（而不是 +2）
```

---

## 解決方案總結

| 方案 | 優點 | 缺點 | 使用場景 |
|------|------|------|---------|
| Mutex Lock | 簡單，適用大多數情況 | 可能死鎖 | 一般共享資源 |
| Condition Variable | 能有效等待事件 | 複雜度高 | 生產者-消費者 |
| Semaphore | 能控制資源數量 | 容易出錯 | 有限資源池 |
| RWLock | 允許多個讀者 | 實現複雜 | 讀多寫少 |
| Atomic Operations | 無鎖，高效 | 只支援簡單操作 | 計數器、標誌 |
| Message Passing | 避免共享狀態 | 效能開銷 | 複雜互動 |

### Python 範例：使用 Lock

```python
import threading
from threading import Lock

class Counter:
    def __init__(self):
        self._value = 0
        self._lock = Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
    
    def get_value(self):
        with self._lock:
            return self._value
```

---

## 偵測 Race Condition 的方法

### 1. 壓力測試

```python
for _ in range(1000):
    thread = threading.Thread(target=risky_function)
    thread.start()
    thread.join()
```

### 2. ThreadSanitizer（TSan）

```bash
gcc -fsanitize=thread -g program.c
```

### 3. 工具和框架

- **Java**: JCStress, ThreadSafety Checker
- **Python**: ThreadSanitizer, pytest-xdist
- **Go**: race detector

---

## Race Condition 的最佳實踐

### ✅ 要做的事

#### 1. 最小化臨界區

```python
# 好
with lock:
    result = expensive_computation()

# 不好
with lock:
    result = expensive_computation()
    other_work()
```

#### 2. 使用高層次抽象

```python
from queue import Queue
q = Queue()  # 內部已經線程安全
```

#### 3. 加入日誌和監控

```python
import logging
with lock:
    logging.debug(f"Thread {threading.current_thread().name} 進入臨界區")
```

#### 4. 使用不可變物件

```python
data = (1, 2, 3)  # tuple 是不可變的
```

### ❌ 不要做的事

#### 1. 過度鎖定

```python
with lock:
    for i in range(1000000):
        do_expensive_operation()  # 太慢了
```

#### 2. 嵌套鎖（容易死鎖）

```python
with lock1:
    with lock2:
        pass  # 危險！
```

#### 3. 忘記同步

```python
with lock:
    part1 = data
part2 = data  # 沒有鎖！
```

---

## 總結

Race Condition 是多執行緒程式設計中最常見也最隱蔽的 bug。

**核心重點：**

1. **識別共享資源** - 找出哪些資料被多個執行緒訪問
2. **新增同步機制** - Lock、Condition Variable、Atomic 等
3. **測試徹底** - 壓力測試揭示 Race Condition
4. **設計簡潔** - 儘量減少同步的複雜性

理解 Race Condition 不只是寫出更好的程式碼，也是理解作業系統底層如何調度執行緒的第一步。