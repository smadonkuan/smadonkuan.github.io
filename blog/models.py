# ===== 匯入必要的套件 =====
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import markdown  # 用來轉換 Markdown 成 HTML
import re  # 用來做正規表達式替換（加入標題 id）


# ===== 部落格文章模型 =====
class Post(models.Model):
    """
    代表一篇部落格文章
    包含標題、內容、標籤等資訊
    """
    
    # ===== 必填欄位 =====
    # 文章標題（最多 200 字）
    title = models.CharField(max_length=200)
    
    # URL 友善的標題
    # 例如：「深入理解 Race Condition」→「race-condition」
    # blank=True 表示可以留空（會自動從 title 生成）
    slug = models.SlugField(unique=True, blank=True)
    
    # 文章主要內容（Markdown 格式）
    # TextField = 可以存放很長的文字
    content = models.TextField()
    
    # 文章摘要（最多 300 字）
    # 用在列表頁面展示
    excerpt = models.CharField(max_length=300)
    
    # ===== 選填欄位 =====
    # 文章配圖 URL（可不填）
    image_url = models.URLField(blank=True, null=True)
    
    # 發布時間
    # default=timezone.now 表示新增時自動設為現在時間
    created_at = models.DateTimeField(default=timezone.now)
    
    # 更新時間
    # auto_now=True 表示每次存檔都自動更新為現在時間
    updated_at = models.DateTimeField(auto_now=True)
    
    # 標籤（逗號分隔）
    # 例如：「Python, Django, 並發程式設計」
    tags = models.CharField(max_length=200)
    
    # 是否發布
    # True = 在網站上顯示
    # False = 草稿（不顯示）
    published = models.BooleanField(default=True)
    
    # ===== 模型設定 =====
    class Meta:
        # 按建立時間倒序（最新的在前）
        ordering = ['-created_at']
    
    # ===== 自動生成 slug =====
    def save(self, *args, **kwargs):
        """
        存檔前的處理
        如果沒有 slug，就從 title 自動產生
        """
        if not self.slug:
            # slugify 會把「深入理解 Race Condition」轉成「shen-ru-li-jie-race-condition」
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    # ===== 處理標籤 =====
    def get_tags(self):
        """
        把標籤字串拆成陣列
        例如：「Python, Django, 並發」
        → [「Python」, 「Django」, 「並發」]
        """
        return [tag.strip() for tag in self.tags.split(',')]
    
    # ===== 將 Markdown 轉成 HTML =====
    def get_content_html(self):
        """
        將 Markdown 格式的內容轉成 HTML
        同時給所有標題加上 id（讓目錄可以跳轉）
        """
        
        # 第一步：轉換 Markdown → HTML
        html = markdown.markdown(
            self.content,
            extensions=[
                'fenced_code',      # 支援 ```python``` 這種代碼塊
                'tables',           # 支援表格 | 欄位 |
                'toc',              # 支援目錄
                'codehilite',       # 代碼高亮（著色）
                'nl2br',            # 換行支援（Enter 換行）
                'sane_lists',       # 列表支援（1. 2. 3. 或 - 項目）
            ]
        )
        
        # 第二步：給 h2 標題加 id
        # 目的：讓目錄可以點擊跳轉
        # 例如：<h2>什麼是 Race Condition？</h2>
        # 變成：<h2 id="race-condition">什麼是 Race Condition？</h2>
        html = re.sub(
            r'<h2>(.*?)</h2>',  # 找出所有 <h2> 標籤
            lambda m: f'<h2 id="{m.group(1).lower().replace(" ", "-").replace("？", "").replace("?", "")}">{m.group(1)}</h2>',
            html
        )
        # 流程說明：
        # m.group(1) = 標籤內的文字
        # .lower() = 轉小寫
        # .replace(" ", "-") = 空格改成破折號
        # .replace("？", "") = 移除問號
        # .replace("?", "") = 移除英文問號
        
        # 第三步：給 h3 標題加 id（同理）
        html = re.sub(
            r'<h3>(.*?)</h3>',  # 找出所有 <h3> 標籤
            lambda m: f'<h3 id="{m.group(1).lower().replace(" ", "-").replace("。", "").replace(".", "")}">{m.group(1)}</h3>',
            html
        )
        
        return html
    
    # ===== 字串表示 =====
    def __str__(self):
        """
        在 Django Admin 後台顯示的名稱
        例如：「深入理解 Race Condition」
        """
        return self.title