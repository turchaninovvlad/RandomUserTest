from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..models.person import Person, PersonRead, PersonCreate
from typing import List, Optional

class PersonService:
    async def create_person(self, session: AsyncSession, person_data: PersonCreate) -> PersonRead:
        db_person = Person.from_orm(person_data)
        session.add(db_person)
        await session.commit()
        await session.refresh(db_person)
        return PersonRead.from_orm(db_person)

    async def get_person(self, session: AsyncSession, person_id: int) -> Optional[PersonRead]:
        result = await session.execute(select(Person).where(Person.id == person_id))
        db_person = result.scalar_one_or_none()
        return PersonRead.from_orm(db_person) if db_person else None

    async def get_all_persons(self, session: AsyncSession) -> List[PersonRead]:
        result = await session.execute(select(Person))
        persons = result.scalars().all()
        return [PersonRead.from_orm(p) for p in persons]