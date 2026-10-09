# Lab2: FastAPI 记账接口

实现一个简易记账 HTTP 服务，支持新增流水、查询流水、统计收支结余。

## 目录结构

```
lab2_fastapi/
├── main.py              # FastAPI 主程序
├── test_main.py         # pytest 测试用例
├── requirements.txt     # 依赖包
└── README.md            # 说明文档
```

## 接口说明

### 1. 新增流水

```bash
POST /records
```

请求体：

```json
{
  "amount": 100.0,
  "type": "收入",
  "category": "工资",
  "date": "2024-10-01"
}
```

校验规则：
- `amount` 必须大于 0
- `type` 只能是 `收入` 或 `支出`
- `date` 必须是 `YYYY-MM-DD` 格式

### 2. 查询流水

```bash
GET /records?type=收入&category=工资&start_date=2024-10-01&end_date=2024-10-31&page=1&page_size=10
```

支持筛选条件：
- `type`：按类型筛选
- `category`：按分类筛选
- `start_date` / `end_date`：按日期区间筛选
- `page` / `page_size`：分页

### 3. 统计收支

```bash
GET /summary?start_date=2024-10-01&end_date=2024-10-31
```

返回：

```json
{
  "start_date": "2024-10-01",
  "end_date": "2024-10-31",
  "income": 1000.0,
  "expense": 300.0,
  "balance": 700.0
}
```

## 运行方式

### 安装依赖

```bash
cd lab2_fastapi
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn main:app --reload
```

启动后访问：
- API 文档：http://127.0.0.1:8000/docs
- 备用文档：http://127.0.0.1:8000/redoc

### 运行测试

```bash
pytest test_main.py -v
```

## 并发安全说明

本项目使用内存存储，通过 `asyncio.Lock` 对写入操作和读取操作加锁，确保并发写入时：

1. **ID 自增安全**：每条记录 ID 唯一递增，不会出现重复或覆盖。
2. **数据一致性**：读写操作串行执行，避免数据竞争导致记录丢失或状态不一致。

如果后续需要更高并发性能，可以替换为 SQLite + SQLAlchemy，利用数据库事务和行级锁来保证并发安全。
