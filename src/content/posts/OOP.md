---
title: "物件導向程式設計：四大核心概念"
date: "2026年 01月 29日"
excerpt: "深入探討 OOP 的四大核心概念：封裝、繼承、多型、抽象。從基礎理論到實戰案例，搭配 Java、PHP、Python 範例，讓你真正掌握物件導向程式設計的精髓。"
tags: ["OOP", "Java", "PHP", "Python", "程式設計", "軟體工程"]
readTime: "25 min read"
slug: "oop-four-pillars"
---

## 什麼是物件導向程式設計?

**物件導向程式設計(Object-Oriented Programming, OOP)是一種以「物件」為核心的程式設計思維**。

簡單來說，OOP 讓我們可以把現實世界的概念直接對應到程式碼中:

- 一輛汽車是一個物件
- 一個銀行帳戶是一個物件
- 一個使用者是一個物件

每個物件都有:
- **屬性(Attributes)**: 描述物件的特徵(如汽車的顏色、型號)
- **方法(Methods)**: 物件能執行的動作(如汽車可以啟動、加速)

---

## 基礎概念:類別與物件

在深入四大核心之前,先理解這兩個基礎:

### 類別(Class)：物件的藍圖

```java
// Java 範例
public class Car {
    // 屬性
    private String color;
    private String model;
    
    // 建構函數
    public Car(String color, String model) {
        this.color = color;
        this.model = model;
    }
    
    // 方法
    public void startEngine() {
        System.out.println("引擎啟動!");
    }
}
```

### 物件(Object)：類別的實例

```java
// 建立物件
Car myCar = new Car("紅色", "Toyota");
Car yourCar = new Car("藍色", "Honda");

myCar.startEngine();  // 引擎啟動!
```

> 類比: 類別就像餅乾模具,物件就是用模具做出來的每一片餅乾。

---

## OOP 四大核心概念

### 一、封裝(Encapsulation)：保護你的資料

#### 核心概念

**將資料(屬性)和操作資料的方法(行為)綁定在一起,並隱藏內部實作細節。**

外部無法直接修改物件的內部狀態,只能透過公開的方法來存取,這提升了程式的安全性和可維護性。

#### 實戰案例：銀行帳戶系統

沒有封裝的危險:
```java
// 不良設計:屬性為 public
public class BankAccount {
    public double balance;  // 任何人都能直接改!
    
    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }
}

// 使用時
BankAccount account = new BankAccount(1000);
account.balance = -5000;  //  直接改成負數!沒人能阻止
System.out.println("餘額: " + account.balance);  // 餘額: -5000.0
```

使用封裝保護資料:
```java
public class BankAccount {
    private double balance;  // private: 外部無法直接存取
    private String accountNumber;
    
    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }
    
    // 透過公開方法控制存取
    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("金額必須大於 0");
        }
        if (amount > balance) {
            throw new IllegalArgumentException("餘額不足");
        }
        balance -= amount;
        System.out.println("提款成功,餘額: " + balance);
    }
    
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("金額必須大於 0");
        }
        balance += amount;
        System.out.println("存款成功,餘額: " + balance);
    }
    
    // Getter: 只允許讀取,不允許直接修改
    public double getBalance() {
        return balance;
    }
    
    public String getAccountNumber() {
        return accountNumber;
    }
}

// 使用
BankAccount account = new BankAccount("ACC001", 1000);
account.deposit(500);   //  存款成功,餘額: 1500.0
account.withdraw(300);  //  提款成功,餘額: 1200.0
// account.balance = -5000;  //  編譯錯誤!無法直接存取
```

#### PHP 範例

```php
<?php
class BankAccount {
    private $balance;
    private $accountNumber;
    
    public function __construct($accountNumber, $initialBalance) {
        $this->accountNumber = $accountNumber;
        $this->balance = $initialBalance;
    }
    
    public function withdraw($amount) {
        if ($amount <= 0) {
            throw new Exception("金額必須大於 0");
        }
        if ($amount > $this->balance) {
            throw new Exception("餘額不足");
        }
        $this->balance -= $amount;
        return "提款成功,餘額: {$this->balance}";
    }
    
    public function getBalance() {
        return $this->balance;
    }
}

$account = new BankAccount("ACC001", 1000);
echo $account->withdraw(300);  // 提款成功,餘額: 700
?>
```

#### Python 範例

```python
class BankAccount:
    def __init__(self, account_number, initial_balance):
        self.__balance = initial_balance  
        # __ 會觸發 name mangling（例如 _BankAccount__balance），
        # 用來避免外部誤用，而非真正的 private
        self.__account_number = account_number
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("金額必須大於 0")
        if amount > self.__balance:
            raise ValueError("餘額不足")
        self.__balance -= amount
        return f"提款成功,餘額: {self.__balance}"
    
    def get_balance(self):
        return self.__balance

account = BankAccount("ACC001", 1000)
print(account.withdraw(300))  # 提款成功,餘額: 700
```

#### ！封裝的核心價值！

**資料安全**: 防止無效或危險的資料被寫入  
**降低耦合**: 外部程式碼不依賴內部實作  
**易於維護**: 改變內部邏輯不影響使用者  
**提供驗證**: 所有修改都經過檢查  

---

### 二、繼承(Inheritance)：重用而非重複

#### 核心概念：**允許從已有的類別(父類別)建立新類別(子類別),子類別會繼承父類別的屬性和方法。**

子類別可以:
- 重用父類別的程式碼
- 新增自己的屬性和方法
- 覆寫(Override)父類別的方法

#### 實戰案例：動物分類

```java
// 父類別
public class Animal {
    protected String name;  // protected: 子類別可以存取
    protected int age;
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 共通方法
    public void eat() {
        System.out.println(name + " is eating.");
    }
    
    public void sleep() {
        System.out.println(name + " is sleeping.");
    }
    
    // 可被覆寫的方法
    public void sound() {
        System.out.println("Animal makes a sound.");
    }
}

// 子類別 1: Dog
public class Dog extends Animal {
    private String breed;
    
    public Dog(String name, int age, String breed) {
        super(name, age);  // 呼叫父類別建構函數
        this.breed = breed;
    }
    
    // 覆寫父類別方法
    @Override
    public void sound() {
        System.out.println(name + " barks: Woof! Woof!");
    }
    
    // 新增專屬方法
    public void fetch() {
        System.out.println(name + " is fetching the ball!");
    }
}

// 子類別 2: Cat
public class Cat extends Animal {
    private boolean isIndoor;
    
    public Cat(String name, int age, boolean isIndoor) {
        super(name, age);
        this.isIndoor = isIndoor;
    }
    
    @Override
    public void sound() {
        System.out.println(name + " meows: Meow~ Meow~");
    }
    
    public void scratch() {
        System.out.println(name + " is scratching the furniture!");
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        Dog myDog = new Dog("Buddy", 3, "Golden Retriever");
        myDog.eat();    // Buddy is eating. (繼承自 Animal)
        myDog.sound();  // Buddy barks: Woof! Woof! (覆寫)
        myDog.fetch();  // Buddy is fetching the ball! (Dog 專屬)
        
        Cat myCat = new Cat("Whiskers", 2, true);
        myCat.sleep();    // Whiskers is sleeping. (繼承自 Animal)
        myCat.sound();    // Whiskers meows: Meow~ Meow~ (覆寫)
        myCat.scratch();  // Whiskers is scratching the furniture! (Cat 專屬)
    }
}
```

#### PHP 範例

```php
<?php
class Animal {
    protected $name;
    protected $age;
    
    public function __construct($name, $age) {
        $this->name = $name;
        $this->age = $age;
    }
    
    public function eat() {
        echo "{$this->name} is eating.\n";
    }
    
    public function sound() {
        echo "Animal makes a sound.\n";
    }
}

class Dog extends Animal {
    private $breed;
    
    public function __construct($name, $age, $breed) {
        parent::__construct($name, $age);
        $this->breed = $breed;
    }
    
    public function sound() {
        echo "{$this->name} barks: Woof! Woof!\n";
    }
    
    public function fetch() {
        echo "{$this->name} is fetching!\n";
    }
}

$myDog = new Dog("Buddy", 3, "Golden Retriever");
$myDog->eat();     // Buddy is eating.
$myDog->sound();   // Buddy barks: Woof! Woof!
$myDog->fetch();   // Buddy is fetching!
?>
```

#### ⚠️ 避免繼承的濫用

```java
//  錯誤範例: 不合理的繼承關係
public class Radio {
    public void playMusic() {
        System.out.println("Playing music...");
    }
}

// 汽車不是一種收音機!這是錯誤的 is-a 關係
public class Car extends Radio {
    public void drive() {
        System.out.println("Driving...");
    }
}
```

** 正確做法:使用組合(Composition)**

```java
public class Car {
    private Radio radio;  // 汽車「擁有」收音機
    
    public Car() {
        this.radio = new Radio();
    }
    
    public void drive() {
        System.out.println("Driving...");
    }
    
    public void playMusic() {
        radio.playMusic();  // 委派給收音機
    }
}
```

> **設計原則**: "優先使用組合而非繼承" - Gang of Four

#### 繼承的核心價值

**程式碼重用**: 避免重複撰寫相同邏輯  
**建立層級**: 清楚的 is-a 關係  
**統一介面**: 維持一致的方法簽名  
**易於擴展**: 新增功能不影響父類別  

---

### 三、多型(Polymorphism)：相同介面，不同行為

#### 核心概念：**允許使用相同的介面(或方法名稱)來執行不同的行為。**

多型可以通過:
- **方法覆寫（Override）**  
  子類別重新定義父類別的方法（Java / Python / PHP 皆支援）

- **方法多載（Overload）**  
  相同方法名稱但參數不同  
  - Java 支援編譯期方法多載  
  - Python 不支援傳統意義上的編譯期多載，但可透過：
    - 預設參數
    - `*args` / `**kwargs`
    - `functools.singledispatch`
    達成類似效果

#### 實戰案例：動物叫聲系統

```java
public class Animal {
    protected String name;
    
    public Animal(String name) {
        this.name = name;
    }
    
    public void sound() {
        System.out.println("Animal makes a sound.");
    }
}

public class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }
    
    @Override
    public void sound() {
        System.out.println(name + " barks: Woof! Woof!");
    }
}

public class Cat extends Animal {
    public Cat(String name) {
        super(name);
    }
    
    @Override
    public void sound() {
        System.out.println(name + " meows: Meow~ Meow~");
    }
}

public class Cow extends Animal {
    public Cow(String name) {
        super(name);
    }
    
    @Override
    public void sound() {
        System.out.println(name + " moos: Moo~ Moo~");
    }
}

// 多型的威力:統一處理
public class AnimalShelter {
    // 接受 Animal 類型,但實際執行會根據物件類型而不同
    public void makeAllAnimalsSpeak(Animal[] animals) {
        for (Animal animal : animals) {
            animal.sound();  // 多型!每個動物發出不同聲音
        }
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        Animal[] animals = {
            new Dog("Buddy"),
            new Cat("Whiskers"),
            new Cow("Bessie"),
            new Dog("Max")
        };
        
        AnimalShelter shelter = new AnimalShelter();
        shelter.makeAllAnimalsSpeak(animals);
        
        /* 輸出:
         * Buddy barks: Woof! Woof!
         * Whiskers meows: Meow~ Meow~
         * Bessie moos: Moo~ Moo~
         * Max barks: Woof! Woof!
         */
    }
}
```

#### 實戰案例：支付系統

```java
// 定義支付介面
interface PaymentMethod {
    void process(double amount);
}

// 實作 1: 信用卡支付
class CreditCardPayment implements PaymentMethod {
    private String cardNumber;
    
    public CreditCardPayment(String cardNumber) {
        this.cardNumber = cardNumber;
    }
    
    @Override
    public void process(double amount) {
        System.out.println("信用卡支付 $" + amount);
        System.out.println("卡號: " + cardNumber);
    }
}

// 實作 2: PayPal 支付
class PayPalPayment implements PaymentMethod {
    private String email;
    
    public PayPalPayment(String email) {
        this.email = email;
    }
    
    @Override
    public void process(double amount) {
        System.out.println("PayPal 支付 $" + amount);
        System.out.println("帳號: " + email);
    }
}

// 實作 3: 加密貨幣支付
class CryptoPayment implements PaymentMethod {
    private String walletAddress;
    
    public CryptoPayment(String walletAddress) {
        this.walletAddress = walletAddress;
    }
    
    @Override
    public void process(double amount) {
        System.out.println("加密貨幣支付 $" + amount);
        System.out.println("錢包: " + walletAddress);
    }
}

// 核心處理邏輯:完全不需要知道具體類型!
class CheckoutService {
    public void checkout(PaymentMethod payment, double amount) {
        System.out.println("=== 開始結帳 ===");
        payment.process(amount);  // 多型!根據傳入的物件執行不同邏輯
        System.out.println("=== 支付完成 ===\n");
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        CheckoutService checkout = new CheckoutService();
        
        checkout.checkout(new CreditCardPayment("1234-5678-9012-3456"), 100);
        checkout.checkout(new PayPalPayment("user@example.com"), 200);
        checkout.checkout(new CryptoPayment("0x742d35Cc..."), 50);
        
        //  新增 Apple Pay? 只要新增類別,不用改 CheckoutService!
        class ApplePayPayment implements PaymentMethod {
            public void process(double amount) {
                System.out.println("Apple Pay 支付 $" + amount);
            }
        }
        
        checkout.checkout(new ApplePayPayment(), 150);
    }
}
```

#### Python 範例

```python
# Python 的多型不需要明確的介面
class Dog:
    def speak(self):
        return "Woof! Woof!"

class Cat:
    def speak(self):
        return "Meow~ Meow~"

class Cow:
    def speak(self):
        return "Moo~ Moo~"

# 多型的威力:相同方法名稱,不同行為
def make_animal_speak(animal):
    print(animal.speak())

# 使用
animals = [Dog(), Cat(), Cow(), Dog()]
for animal in animals:
    make_animal_speak(animal)

# 輸出:
# Woof! Woof!
# Meow~ Meow~
# Moo~ Moo~
# Woof! Woof!
```

#### 多型的核心價值

**消除條件判斷**: 不再需要一堆 `if-else`  
**開放封閉原則**: 對擴展開放,對修改封閉  
**提高可測試性**: 每個類別可獨立測試  
**靈活擴展**: 新增功能不影響既有程式碼  

---

### 四、抽象(Abstraction)：隱藏複雜性

#### 核心概念：**將類別或方法中的非必要細節隱藏,只暴露必要的介面給使用者。**<p>


抽象可以透過:
- **抽象類別(Abstract Class)**: 不能被實例化,用來定義共通結構
- **介面(Interface)**: 定義類別必須實現的行為契約

#### 抽象 vs 封裝的區別

| 概念 | 目的 | 重點 |
|------|------|------|
| **封裝** | 保護資料 | 隱藏「實作細節」,控制存取 |
| **抽象** | 簡化使用 | 隱藏「複雜性」,只暴露必要介面 |

#### 實戰案例：圖形系統(使用抽象類別)

```java
// 抽象類別:不能被實例化
abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 抽象方法:子類別必須實作
    public abstract double calculateArea();
    public abstract double calculatePerimeter();
    
    // 具體方法:子類別可以直接使用
    public void displayInfo() {
        System.out.println("顏色: " + color);
        System.out.println("面積: " + calculateArea());
        System.out.println("周長: " + calculatePerimeter());
    }
}

// 子類別 1: 圓形
class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double calculatePerimeter() {
        return 2 * Math.PI * radius;
    }
}

// 子類別 2: 矩形
class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double calculateArea() {
        return width * height;
    }
    
    @Override
    public double calculatePerimeter() {
        return 2 * (width + height);
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        // Shape shape = new Shape("紅色");  //  錯誤!抽象類別不能實例化
        
        Shape circle = new Circle("紅色", 5);
        circle.displayInfo();
        // 輸出:
        // 顏色: 紅色
        // 面積: 78.53981633974483
        // 周長: 31.41592653589793
        
        Shape rectangle = new Rectangle("藍色", 4, 6);
        rectangle.displayInfo();
        // 輸出:
        // 顏色: 藍色
        // 面積: 24.0
        // 周長: 20.0
        
        // 使用者不需要知道面積如何計算,只需要呼叫方法
        // 這就是抽象的威力!
    }
}
```

#### 實戰案例：資料庫系統(使用介面)

```java
// 定義資料庫操作介面
interface DatabaseOperations {
    void connect();
    void disconnect();
    void executeQuery(String query);
}

// 實作 1: MySQL 資料庫
class MySQLDatabase implements DatabaseOperations {
    private String host;
    
    public MySQLDatabase(String host) {
        this.host = host;
    }
    
    @Override
    public void connect() {
        System.out.println("連接到 MySQL: " + host);
    }
    
    @Override
    public void disconnect() {
        System.out.println("中斷 MySQL 連線");
    }
    
    @Override
    public void executeQuery(String query) {
        System.out.println("執行 MySQL 查詢: " + query);
    }
}

// 實作 2: PostgreSQL 資料庫
class PostgreSQLDatabase implements DatabaseOperations {
    private String host;
    
    public PostgreSQLDatabase(String host) {
        this.host = host;
    }
    
    @Override
    public void connect() {
        System.out.println("連接到 PostgreSQL: " + host);
    }
    
    @Override
    public void disconnect() {
        System.out.println("中斷 PostgreSQL 連線");
    }
    
    @Override
    public void executeQuery(String query) {
        System.out.println("執行 PostgreSQL 查詢: " + query);
    }
}

// 應用程式:不需要知道是哪種資料庫
class Application {
    private DatabaseOperations db;
    
    public Application(DatabaseOperations db) {
        this.db = db;
    }
    
    public void run() {
        db.connect();
        db.executeQuery("SELECT * FROM users");
        db.disconnect();
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        // 輕鬆切換資料庫,不需要改 Application 的程式碼
        Application app1 = new Application(new MySQLDatabase("localhost"));
        app1.run();
        
        Application app2 = new Application(new PostgreSQLDatabase("192.168.1.100"));
        app2.run();
    }
}
```

#### PHP 範例

```php
<?php
// 抽象類別
abstract class Animal {
    protected $name;
    
    public function __construct($name) {
        $this->name = $name;
    }
    // 抽象方法
    abstract public function sound();
    // 具體方法
    public function sleep() {
        echo "{$this->name} is sleeping.\n";
    }
}

class Dog extends Animal {
    public function sound() {
        echo "{$this->name} barks.\n";
    }
}

$dog = new Dog("Buddy");
$dog->sound();  // Buddy barks.
$dog->sleep();  // Buddy is sleeping.
?>
```

#### Python 範例

```python
from abc import ABC, abstractmethod

# 抽象類別
class Shape(ABC):
    def __init__(self, color):
        self.color = color
    
    @abstractmethod
    def calculate_area(self):
        """子類別必須實作"""
        pass
    
    @abstractmethod
    def calculate_perimeter(self):
        """子類別必須實作"""
        pass
    
    def display_info(self):
        print(f"顏色: {self.color}")
        print(f"面積: {self.calculate_area()}")
        print(f"周長: {self.calculate_perimeter()}")

class Circle(Shape):
    def __init__(self, color, radius):
        super().__init__(color)
        self.radius = radius
    
    def calculate_area(self):
        return 3.14159 * self.radius ** 2
    
    def calculate_perimeter(self):
        return 2 * 3.14159 * self.radius

# 使用
circle = Circle("紅色", 5)
circle.display_info()
```

#### 抽象的核心價值

**簡化使用**: 使用者不需要知道內部複雜性  
**強制規範**: 確保子類別實作必要方法  
**提升可讀性**: 清楚的介面定義  
**降低耦合**: 依賴抽象而非具體實作  

---

## 四大核心概念總結

| 概念 | 核心目的 | 主要技術 | 實務價值 |
|------|---------|---------|---------|
| **封裝** | 保護資料 | private/protected + getter/setter | 資料安全、降低耦合 |
| **繼承** | 重用程式碼 | extends | 避免重複,建立層級 |
| **多型** | 統一介面 | 覆寫(Override) + 介面 | 消除 if-else,易於擴展 |
| **抽象** | 隱藏複雜性 | 抽象類別 + 介面 | 簡化使用,強制規範 |

### 四者如何協同運作?

讓我們用一個完整範例展示:

```java
// 抽象:定義支付的抽象概念
abstract class Payment {
    protected double amount;
    protected String transactionId;
    
    public Payment(double amount) {
        this.amount = amount;
        this.transactionId = generateTransactionId();
    }
    
    // 抽象方法
    public abstract boolean processPayment();
    public abstract void sendReceipt();
    
    // 封裝:保護交易 ID 的生成邏輯
    private String generateTransactionId() {
        return "TXN-" + System.currentTimeMillis();
    }
    
    // 具體方法
    public void displayTransaction() {
        System.out.println("交易編號: " + transactionId);
        System.out.println("金額: $" + amount);
    }
}

// 繼承:信用卡支付繼承 Payment
class CreditCardPayment extends Payment {
    private String cardNumber;  // 封裝:私有屬性
    
    public CreditCardPayment(double amount, String cardNumber) {
        super(amount);
        this.cardNumber = maskCardNumber(cardNumber);  // 封裝
    }
    
    // 封裝:隱藏卡號遮罩邏輯
    private String maskCardNumber(String cardNumber) {
        return "****-****-****-" + cardNumber.substring(cardNumber.length() - 4);
    }
    
    // 多型:覆寫抽象方法
    @Override
    public boolean processPayment() {
        System.out.println("處理信用卡支付...");
        return true;
    }
    
    @Override
    public void sendReceipt() {
        System.out.println("發送信用卡支付收據");
    }
}

// 繼承:PayPal 支付繼承 Payment
class PayPalPayment extends Payment {
    private String email;
    
    public PayPalPayment(double amount, String email) {
        super(amount);
        this.email = email;
    }
    
    // 多型:不同的實作
    @Override
    public boolean processPayment() {
        System.out.println("處理 PayPal 支付...");
        return true;
    }
    
    @Override
    public void sendReceipt() {
        System.out.println("發送 PayPal 收據到: " + email);
    }
}

// 多型的應用
class PaymentProcessor {
    // 接受抽象類型,實際執行依據具體物件
    public void process(Payment payment) {
        payment.displayTransaction();
        if (payment.processPayment()) {
            payment.sendReceipt();
            System.out.println("支付成功!\n");
        }
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        PaymentProcessor processor = new PaymentProcessor();
        
        // 多型:用相同的方式處理不同的支付方式
        processor.process(new CreditCardPayment(100, "1234567890123456"));
        processor.process(new PayPalPayment(200, "user@example.com"));
    }
}
```

---

## OOP 的實務建議

### 1. 何時使用封裝?

 **總是使用**: 封裝是 OOP 的基本原則  
 **屬性設為 private**: 除非有充分理由  
 **提供 getter/setter**: 但不是每個屬性都需要；其目的在於保護物件的不變條件（invariant），而非單純暴露欄位。

### 2. 何時使用繼承?

 **有明確的 is-a 關係**: Dog is an Animal  
 **共享大量共通邏輯**: 避免重複程式碼  
 **避免深層繼承**: 超過 3 層就要重新思考  
 **優先考慮組合**: "has-a" 關係用組合  

### 3. 何時使用多型?

 **消除大量 if-else**: 用多型取代條件判斷  
 **需要擴展性**: 未來可能新增類型  
 **統一處理**: 用相同方式處理不同物件  

### 4. 何時使用抽象?

 **定義契約**: 確保子類別實作特定方法  
 **提供框架**: 部分實作 + 部分抽象  
 **隱藏複雜性**: 簡化使用者介面  

---

## 常見誤區

###  誤區 1: 過度設計

```java
// 不要為了用 OOP 而用 OOP
class Calculator {
    private int result;
    
    public void add(int a, int b) {
        this.result = a + b;
    }
    
    public int getResult() {
        return result;
    }
}

// 簡單的計算,用函數就好
public static int add(int a, int b) {
    return a + b;
}
```

###  誤區 2: 濫用繼承

```java
// 錯誤:為了共用程式碼而繼承
class Utils {
    public void log(String message) {
        System.out.println(message);
    }
}

class MyClass extends Utils {  //  MyClass 不是一種 Utils
    // ...
}

// 正確:用組合或靜態方法
class MyClass {
    private Logger logger = new Logger();
    
    public void doSomething() {
        logger.log("Doing something");
    }
}
```

###  誤區 3: Getter/Setter 陷阱

```java
// 這不是真正的封裝!
class User {
    private List<String> roles;
    
    public List<String> getRoles() {
        return roles;  //  返回內部可變物件
    }
}

// 外部可以直接修改
user.getRoles().clear();  //  破壞封裝!

// 正確做法
public List<String> getRoles() {
    return new ArrayList<>(roles);  // 返回副本
}
```

---

## 總結

OOP 的四大核心概念不是孤立的,而是互相配合:

1. **封裝**保護資料
2. **繼承**重用程式碼
3. **多型**提供彈性
4. **抽象**簡化使用

掌握這四個概念,你就能寫出:
-  更安全的程式碼(封裝)
-  更容易維護的系統(繼承 + 抽象)
-  更容易擴展的架構(多型)
-  更容易理解的介面(抽象)


## 延伸：OOP 四大概念與 SOLID 原則的對應關係
- 封裝（Encapsulation） → SRP / ISP  
  封裝幫助類別只關注單一責任，並避免對外暴露不必要的細節。
- 多型（Polymorphism） → OCP  
  透過多型新增行為時，不需要修改既有程式碼。
- 抽象（Abstraction） → DIP  
  高階模組依賴抽象，而非具體實作。
- 組合優於繼承（Composition over Inheritance） → LSP  
  避免因不當繼承破壞可替換性。


> #### **Happy Coding!**