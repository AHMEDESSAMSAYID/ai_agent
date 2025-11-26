# ai_agent/tools/operations.py

from collections import Counter, defaultdict
from typing import List, Dict, Any
import asyncio
# داتا تجريبية (Mock) لحد ما توصلها بالـ DB الحقيقية
MOCK_SHIPMENTS = [
    {
        "tracking_number": "123",
        "city": "Jeddah",
        "area": "North",
        "driver": "Ahmed",
        "status": "delayed",
        "delay_hours": 2,
        "failure_reason": "Traffic",
        "date": "2025-11-20",
    },
    {
        "tracking_number": "888",
        "city": "Jeddah",
        "area": "West",
        "driver": "Ahmed",
        "status": "delayed",
        "delay_hours": 5,
        "failure_reason": "Driver issue",
        "date": "2025-11-19",
    },
    {
        "tracking_number": "456",
        "city": "Riyadh",
        "area": "Center",
        "driver": "Saad",
        "status": "delayed",
        "delay_hours": 3,
        "failure_reason": "Sorting center load",
        "date": "2025-11-20",
    },
    {
        "tracking_number": "321",
        "city": "Riyadh",
        "area": "East",
        "driver": "Omar",
        "status": "delivered",
        "delay_hours": 1,
        "failure_reason": None,
        "date": "2025-11-18",
    },
    {
        "tracking_number": "789",
        "city": "Dammam",
        "area": "South",
        "driver": "Khalid",
        "status": "delivered",
        "delay_hours": 0,
        "failure_reason": None,
        "date": "2025-11-18",
    },
]


def _matches_time_range(shipment: Dict[str, Any], time_range: str | None) -> bool:
    # حالياً هنطنّش الـ time_range (تقدر تطوّرها لاحقاً)
    await asyncio.sleep(0)
    return True


def get_delayed_shipments(
    city: str | None = None,
    driver: str | None = None,
    time_range: str | None = None,
) -> List[Dict[str, Any]]:
    """
    إرجاع كل الشحنات المتأخرة مع إمكانية التصفية بالمدينة / السائق / الفترة الزمنية
    """
    results = []
    for sh in MOCK_SHIPMENTS:
        if sh["status"] != "delayed":
            continue
        if city and sh["city"].lower() != city.lower():
            continue
        if driver and sh["driver"].lower() != driver.lower():
            continue
        if not _matches_time_range(sh, time_range):
            continue
        results.append(sh)
    await asyncio.sleep(0)
    return results


def get_city_summary(city: str) -> Dict[str, Any]:
    """
    ملخص مدينة: عدد الشحنات، المتأخرة، الناجحة، متوسط التأخير
    """
    city_shipments = [s for s in MOCK_SHIPMENTS if s["city"].lower() == city.lower()]
    total = len(city_shipments)
    delayed = [s for s in city_shipments if s["status"] == "delayed"]
    delivered = [s for s in city_shipments if s["status"] == "delivered"]
    avg_delay = (
        sum(s.get("delay_hours", 0) for s in delayed) / len(delayed)
        if delayed
        else 0
    )
    await asyncio.sleep(0)
    return {
        "city": city,
        "total_shipments": total,
        "delayed_shipments": len(delayed),
        "delivered_shipments": len(delivered),
        "avg_delay_hours": round(avg_delay, 2),
    }


def get_driver_performance(driver: str) -> Dict[str, Any]:
    """
    أداء سائق: عدد الشحنات، عدد المتأخرة، متوسط التأخير
    """
    driver_shipments = [
        s for s in MOCK_SHIPMENTS if s["driver"].lower() == driver.lower()
    ]
    total = len(driver_shipments)
    delayed = [s for s in driver_shipments if s["status"] == "delayed"]
    delivered = [s for s in driver_shipments if s["status"] == "delivered"]

    avg_delay = (
        sum(s.get("delay_hours", 0) for s in delayed) / len(delayed)
        if delayed
        else 0
    )
    await asyncio.sleep(0)
    return {
        "driver": driver,
        "total_shipments": total,
        "delayed_shipments": len(delayed),
        "delivered_shipments": len(delivered),
        "avg_delay_hours": round(avg_delay, 2),
        "sample_shipments": driver_shipments[:5],
    }


def list_shipments_by_status(
    status: str, city: str | None = None
) -> List[Dict[str, Any]]:
    """
    قائمة شحنات حسب الحالة (delayed / delivered / any status)
    مع إمكانية التصفية بالمدينة
    """
    status = status.lower()
    results = []
    for s in MOCK_SHIPMENTS:
        if city and s["city"].lower() != city.lower():
            continue
        if status != "any" and s["status"].lower() != status:
            continue
        results.append(s)
    await asyncio.sleep(0)
    return results


def get_area_heatmap(city: str | None = None) -> Dict[str, int]:
    """
    توزيع الشحنات على المناطق داخل المدينة (أو كل المدن لو city=None)
    """
    counter: Dict[str, int] = Counter()
    for s in MOCK_SHIPMENTS:
        if city and s["city"].lower() != city.lower():
            continue
        area = s.get("area") or "Unknown"
        counter[area] += 1
    await asyncio.sleep(0)
    return dict(counter)


def analyze_failure_reasons(
    city: str | None = None, time_range: str | None = None
) -> Dict[str, int]:
    """
    تحليل أسباب التأخير (failure_reason) حسب المدينة/الفترة الزمنية
    """
    counter: Dict[str, int] = Counter()
    for s in MOCK_SHIPMENTS:
        if s["status"] != "delayed":
            continue
        if city and s["city"].lower() != city.lower():
            continue
        if not _matches_time_range(s, time_range):
            continue
        reason = s.get("failure_reason") or "Unknown"
        counter[reason] += 1
    await asyncio.sleep(0)
    return dict(counter)
