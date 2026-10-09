"""
考题二：FastAPI 记账接口
实现一个简易记账 HTTP 服务，数据使用内存存储，并通过 asyncio.Lock 保证并发写入安全。
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator


# 内存数据存储
records_db: List[dict] = []
record_lock = asyncio.Lock()
next_id = 1


# 数据模型
class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="金额，必须大于 0")
    type: Literal["收入", "支出"] = Field(..., description="类型：收入或支出")
    category: str = Field(..., min_length=1, description="分类")
    date: str = Field(..., description="日期，格式 YYYY-MM-DD")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式错误，请使用 YYYY-MM-DD")
        return v


class Record(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: str


class Summary(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    income: float
    expense: float
    balance: float


class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[List[dict]] = None


# 异常处理：将 Pydantic 校验错误转换为结构化 4xx 响应
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", ""),
            "type": err.get("type", "")
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "请求参数校验失败", "errors": errors}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时清空内存数据（方便测试重复运行）
    global records_db, next_id
    records_db.clear()
    next_id = 1
    yield


app = FastAPI(title="FastAPI 记账接口", lifespan=lifespan)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


def _filter_records(
    type_: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """按条件过滤记录（非线程安全，调用方需自行加锁）。"""
    result = records_db[:]

    if type_:
        result = [r for r in result if r["type"] == type_]
    if category:
        result = [r for r in result if r["category"] == category]
    if start_date:
        result = [r for r in result if r["date"] >= start_date]
    if end_date:
        result = [r for r in result if r["date"] <= end_date]

    return result


@app.post("/records", response_model=Record, status_code=201)
async def create_record(record: RecordCreate):
    """新增一条流水记录。"""
    global next_id

    async with record_lock:
        new_record = {
            "id": next_id,
            "amount": record.amount,
            "type": record.type,
            "category": record.category,
            "date": record.date,
        }
        records_db.append(new_record)
        next_id += 1

    return new_record


@app.get("/records", response_model=List[Record])
async def list_records(
    type: Optional[str] = Query(None, description="按类型筛选：收入/支出"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数")
):
    """查询流水记录，支持筛选和分页。"""
    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date 格式错误，请使用 YYYY-MM-DD")
    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date 格式错误，请使用 YYYY-MM-DD")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能大于 end_date")

    async with record_lock:
        filtered = _filter_records(type, category, start_date, end_date)
        total = len(filtered)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        result = filtered[start_idx:end_idx]

    return result


@app.get("/summary", response_model=Summary)
async def get_summary(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """返回指定日期区间内的收入合计、支出合计与结余。"""
    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date 格式错误，请使用 YYYY-MM-DD")
    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date 格式错误，请使用 YYYY-MM-DD")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能大于 end_date")

    async with record_lock:
        filtered = _filter_records(start_date=start_date, end_date=end_date)
        income = sum(r["amount"] for r in filtered if r["type"] == "收入")
        expense = sum(r["amount"] for r in filtered if r["type"] == "支出")

    return Summary(
        start_date=start_date,
        end_date=end_date,
        income=income,
        expense=expense,
        balance=income - expense
    )
