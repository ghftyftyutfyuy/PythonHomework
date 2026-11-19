"""
FastAPI 记账接口的 pytest 测试用例。
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """提供测试客户端。"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_state():
    """每个测试用例前清空内存数据。"""
    from main import records_db, next_id
    records_db.clear()
    import main
    main.next_id = 1


class TestCreateRecord:
    """测试 POST /records 接口。"""

    def test_create_record_success(self, client):
        response = client.post("/records", json={
            "amount": 100.0,
            "type": "收入",
            "category": "工资",
            "date": "2024-10-01"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["amount"] == 100.0
        assert data["type"] == "收入"
        assert data["category"] == "工资"
        assert data["date"] == "2024-10-01"

    def test_create_record_invalid_amount_zero(self, client):
        response = client.post("/records", json={
            "amount": 0,
            "type": "收入",
            "category": "工资",
            "date": "2024-10-01"
        })
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_record_invalid_amount_negative(self, client):
        response = client.post("/records", json={
            "amount": -50,
            "type": "支出",
            "category": "餐饮",
            "date": "2024-10-01"
        })
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_record_invalid_type(self, client):
        response = client.post("/records", json={
            "amount": 50,
            "type": "转账",
            "category": "其他",
            "date": "2024-10-01"
        })
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_record_invalid_date(self, client):
        response = client.post("/records", json={
            "amount": 50,
            "type": "支出",
            "category": "餐饮",
            "date": "2024-13-01"
        })
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_record_missing_field(self, client):
        response = client.post("/records", json={
            "amount": 50,
            "type": "支出"
        })
        assert response.status_code == 422
        assert "detail" in response.json()


class TestListRecords:
    """测试 GET /records 接口。"""

    @pytest.fixture(autouse=True)
    def setup_data(self, client):
        records = [
            {"amount": 1000, "type": "收入", "category": "工资", "date": "2024-10-01"},
            {"amount": 200, "type": "支出", "category": "餐饮", "date": "2024-10-02"},
            {"amount": 300, "type": "支出", "category": "交通", "date": "2024-10-03"},
            {"amount": 500, "type": "收入", "category": "奖金", "date": "2024-10-05"},
        ]
        for r in records:
            client.post("/records", json=r)

    def test_list_all_records(self, client):
        response = client.get("/records")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_filter_by_type(self, client):
        response = client.get("/records?type=收入")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(r["type"] == "收入" for r in data)

    def test_filter_by_category(self, client):
        response = client.get("/records?category=餐饮")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "餐饮"

    def test_filter_by_date_range(self, client):
        response = client.get("/records?start_date=2024-10-02&end_date=2024-10-03")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_pagination(self, client):
        response = client.get("/records?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response = client.get("/records?page=2&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response = client.get("/records?page=3&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_invalid_date_format(self, client):
        response = client.get("/records?start_date=2024-10-99")
        assert response.status_code == 400

    def test_start_date_greater_than_end_date(self, client):
        response = client.get("/records?start_date=2024-10-05&end_date=2024-10-01")
        assert response.status_code == 400


class TestSummary:
    """测试 GET /summary 接口。"""

    @pytest.fixture(autouse=True)
    def setup_data(self, client):
        records = [
            {"amount": 1000, "type": "收入", "category": "工资", "date": "2024-10-01"},
            {"amount": 200, "type": "支出", "category": "餐饮", "date": "2024-10-02"},
            {"amount": 300, "type": "支出", "category": "交通", "date": "2024-10-03"},
            {"amount": 500, "type": "收入", "category": "奖金", "date": "2024-10-15"},
        ]
        for r in records:
            client.post("/records", json=r)

    def test_summary_all(self, client):
        response = client.get("/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["income"] == 1500
        assert data["expense"] == 500
        assert data["balance"] == 1000

    def test_summary_with_date_range(self, client):
        response = client.get("/summary?start_date=2024-10-01&end_date=2024-10-03")
        assert response.status_code == 200
        data = response.json()
        assert data["income"] == 1000
        assert data["expense"] == 500
        assert data["balance"] == 500

    def test_summary_invalid_date(self, client):
        response = client.get("/summary?start_date=invalid-date")
        assert response.status_code == 400


class TestConcurrency:
    """测试并发写入安全性。"""

    @pytest.mark.anyio
    async def test_concurrent_create(self, client):
        """并发创建 100 条记录，验证 ID 不重复、无数据丢失。"""
        import asyncio
        from httpx import AsyncClient, ASGITransport

        async def create_record(ac: AsyncClient, idx: int):
            response = await ac.post("/records", json={
                "amount": 1.0,
                "type": "收入",
                "category": "测试",
                "date": "2024-10-01"
            })
            return response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            tasks = [create_record(ac, i) for i in range(100)]
            responses = await asyncio.gather(*tasks)

        assert all(r.status_code == 201 for r in responses)

        ids = [r.json()["id"] for r in responses]
        assert len(ids) == len(set(ids))  # ID 不重复
        assert len(ids) == 100  # 无数据丢失
