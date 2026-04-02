# SPOORTHY QUANTUM OS — Employees API
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from uuid import UUID

from ....db.session import get_db
from ....repositories.repositories import EmployeeRepository
from ....models.models import EmployeeSchema, EmployeeCreateSchema, Employee

router = APIRouter()

@router.post("/", response_model=EmployeeSchema, status_code=201)
async def create_employee(
    employee: EmployeeCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    repo = EmployeeRepository(db)
    db_emp = await repo.create(**employee.model_dump())
    return EmployeeSchema.model_validate(db_emp)

@router.get("/", response_model=List[EmployeeSchema])
async def list_employees(
    entity_id: UUID,
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    repo = EmployeeRepository(db)
    if active_only:
        employees = await repo.get_active_by_entity(entity_id)
    else:
        employees = await repo.get_all(skip=skip, limit=limit, filters={"entity_id": entity_id})
    return [EmployeeSchema.model_validate(e) for e in employees]

@router.get("/{employee_id}", response_model=EmployeeSchema)
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Employee).where(Employee.employee_id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeSchema.model_validate(emp)

@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: UUID,
    employee_update: EmployeeCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        update(Employee).where(Employee.employee_id == employee_id)
        .values(**employee_update.model_dump(exclude_unset=True))
        .returning(Employee)
    )
    await db.commit()
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeSchema.model_validate(emp)

@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(delete(Employee).where(Employee.employee_id == employee_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
