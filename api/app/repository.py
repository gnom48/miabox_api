from fastapi import UploadFile
from .api.kpi_calculator import RealEstateAgentKPI
from .database.orm import new_session
from sqlalchemy.sql import text
from .database.models import *
from .api.models import *
import time
from sqlalchemy import select, update, delete, and_


class Repository:
    """Класс репозиторий для работы с базой данных как с объектом"""

    # -------------------------- config --------------------------

    @classmethod
    async def get_config(cls) -> str:
        async with new_session() as session:
            try:
                req = text("SELECT version() AS db_version;")
                result = await session.execute(req)
                version = result.scalars().first()
                req = text("SELECT now() AS db_datetime;")
                result = await session.execute(req)
                ntime = result.scalars().first()
                return (version, ntime)
            except:
                return None

    # -------------------------- users --------------------------


    @classmethod
    async def registrate_user(cls, data: User) -> bool:
        async with new_session() as session:
            new_user_id = -1
            try:
                new_user = UserOrm(**data.model_dump())
                new_user.type = UserTypesOrm[data.type.name]
                new_user.reg_date = int(time.time())
                new_user.id = None
                session.add(new_user)
                await session.flush()
                new_user_id = new_user.id
            except:
                return new_user_id
            
            day_stats = DayStatisticsOrm()
            day_stats.user_id = new_user.id
            week_stats = WeekStatisticsOrm()
            week_stats.user_id = new_user.id
            month_stats = MonthStatisticsOrm()
            month_stats.user_id = new_user.id
            session.add(day_stats)
            session.add(week_stats)
            session.add(month_stats)

            await session.commit()
            return new_user_id
        

    @classmethod
    async def edit_user(cls, data: User) -> bool:
        async with new_session() as session:
            try:
                old_user = await session.get(UserOrm, data.id)
                old_user.type = UserTypesOrm[data.type.name]
                old_user.birthday = data.birthday
                old_user.gender = data.gender
                old_user.login = data.login
                old_user.password = data.password
                old_user.name = data.name
                old_user.phone = data.phone
                old_user.photo = data.photo
                await session.flush()
            except:
                return False
            await session.commit()
            return True
        

    @classmethod
    async def get_user_by_id(cls, id: int) -> UserOrm:
        async with new_session() as session:
            try:
                res = await session.get(UserOrm, id)
                return res
            except:
                return None
                
                
    @classmethod
    async def get_user_statistics(cls, id: int) -> StatisticsOrm:
        async with new_session() as session:
            try:
                res = await session.get(StatisticsOrm, id)
                return res
            except:
                return None
                
                
    @classmethod
    async def get_user_by_login(cls, login: str, password: str) -> UserOrm:
        async with new_session() as session:
            try:
                query = select(UserOrm).where(UserOrm.login == login).where(UserOrm.password == password)
                r = await session.execute(query)
                return r.scalar()
            except:
                return None
                

    # -------------------------- notes --------------------------

                
    @classmethod
    async def get_all_notes_by_user_id(cls, user_id: int) -> list[NoteOrm]:
        async with new_session() as session:
            try:
                query = select(NoteOrm).where(NoteOrm.user_id == user_id)
                r = await session.execute(query)
                return r.scalars().all()
            except:
                return None


    @classmethod
    async def add_note(cls, data: Note) -> int:
        async with new_session() as session:
            try:
                new_note = NoteOrm(**data.model_dump())
                new_note.id = None
                session.add(new_note)
                await session.flush()
                note_id = new_note.id
                await session.commit()
                return note_id
            except:
                return None


    @classmethod
    async def del_note(cls, id: int) -> bool:
        async with new_session() as session:
            try:
                note_to_del = await session.get(NoteOrm, id)
                await session.delete(note_to_del)
                await session.commit()
                return True
            except:
                return False
                
    
    @classmethod
    async def edit_note(cls, data: Note) -> bool:
        async with new_session() as session:
            try:
                note_to_edit = await session.get(NoteOrm, data.id)
                note_to_edit.title = data.title
                note_to_edit.desc = data.desc
                note_to_edit.date_time = data.date_time
                await session.commit()
                return True
            except:
                return False


    # -------------------------- tasks --------------------------

                
    @classmethod
    async def get_all_tasks_by_user_id(cls, user_id: int) -> list[TaskOrm]:
        async with new_session() as session:
            try:
                query = select(TaskOrm).where(TaskOrm.user_id == user_id)
                r = await session.execute(query)
                return r.scalars().all()
            except:
                return None


    @classmethod
    async def add_task(cls, data: Task) -> int:
        async with new_session() as session:
            try:
                new_task = TaskOrm(**data.model_dump())
                new_task.id = None
                new_task.work_type = data.work_type.name
                session.add(new_task)
                await session.flush()
                task_id = new_task.id
                await session.commit()
                return task_id
            except:
                return None


    @classmethod
    async def del_task(cls, id: int) -> bool:
        async with new_session() as session:
            try:
                task_to_del = await session.get(TaskOrm, id)
                await session.delete(task_to_del)
                await session.commit()
                return True
            except:
                return False
            

    # -------------------------- statistics --------------------------
    

    @classmethod
    async def update_statistics(cls, user_id: int, statistic: str, addvalue: int) -> bool:
        async with new_session() as session:
            try:
                day_statistic_to_edit: DayStatisticsOrm = await session.get(DayStatisticsOrm, user_id)
                week_statistic_to_edit: WeekStatisticsOrm = await session.get(WeekStatisticsOrm, user_id)
                month_statistic_to_edit: MonthStatisticsOrm = await session.get(MonthStatisticsOrm, user_id)
                match statistic:
                    case WorkTasksTypesOrm.FLYERS.value:
                        day_statistic_to_edit.flyers += addvalue
                        week_statistic_to_edit.flyers += addvalue
                        month_statistic_to_edit.flyers += addvalue
                    case WorkTasksTypesOrm.CALLS.value:
                        day_statistic_to_edit.calls += addvalue
                        week_statistic_to_edit.calls += addvalue
                        month_statistic_to_edit.calls += addvalue
                    case WorkTasksTypesOrm.SHOW.value:
                        day_statistic_to_edit.shows += addvalue
                        week_statistic_to_edit.shows += addvalue
                        month_statistic_to_edit.shows += addvalue
                    case WorkTasksTypesOrm.MEET.value:
                        day_statistic_to_edit.meets += addvalue
                        week_statistic_to_edit.meets += addvalue
                        month_statistic_to_edit.meets += addvalue
                    case WorkTasksTypesOrm.DEAL.value:
                        day_statistic_to_edit.deals += addvalue
                        week_statistic_to_edit.deals += addvalue
                        month_statistic_to_edit.deals += addvalue
                    case WorkTasksTypesOrm.DEPOSIT.value:
                        day_statistic_to_edit.deposits += addvalue
                        week_statistic_to_edit.deposits += addvalue
                        month_statistic_to_edit.deposits += addvalue
                    case WorkTasksTypesOrm.SEARCH.value:
                        day_statistic_to_edit.searches += addvalue
                        week_statistic_to_edit.searches += addvalue
                        month_statistic_to_edit.searches += addvalue
                    case WorkTasksTypesOrm.ANALYTICS.value:
                        day_statistic_to_edit.analytics += addvalue
                        week_statistic_to_edit.analytics += addvalue
                        month_statistic_to_edit.analytics += addvalue
                    case _:
                        day_statistic_to_edit.others += addvalue
                        week_statistic_to_edit.others += addvalue
                        month_statistic_to_edit.others += addvalue
                await session.commit()
                return True
            except:
                return False
            
    
    @classmethod
    async def get_statistics_by_period(cls, user_id: int, period: str) -> StatisticsOrm:
        async with new_session() as session:
            try:
                match period:
                    case StatisticPeriods.DAY_STATISTICS_PERIOD:
                        return await session.get(DayStatisticsOrm, user_id)
                    case StatisticPeriods.WEEK_STATISTICS_PERIOD:
                        return await session.get(WeekStatisticsOrm, user_id)
                    case StatisticPeriods.MONTH_STATISTICS_PERIOD:
                        return await session.get(MonthStatisticsOrm, user_id)
                    case _:
                        return None
            except:
                return None
                
                
    @classmethod
    async def get_statistics_with_kpi(cls, user_id: int) -> LastMonthStatisticsWithKpiOrm:
        async with new_session() as session:
            try:
                return await session.get(LastMonthStatisticsWithKpiOrm, user_id)
            except:
                return None
            
                
    @classmethod
    async def update_kpi_level(cls, user_id: int, level: UserKpiLevels) -> StatisticsOrm:
        async with new_session() as session:
            try:
                var = await session.get(LastMonthStatisticsWithKpiOrm, user_id)
                var.user_level = UserKpiLevelsOrm[level.name]
                await session.commit()
            except:
                return None
            

    @classmethod
    async def clear_day_statistics(cls):
        async with new_session() as session:
            try:
                day_select = await session.execute(select(WeekStatisticsOrm)).scalars().all()
                for item in day_select:
                    item.flyers = 0
                    item.calls = 0
                    item.shows = 0
                    item.meets = 0
                    item.deals = 0
                    item.deposits = 0
                    item.searches = 0
                    item.analytics = 0
                    item.others = 0
                    await session.flush()
                await session.commit()
            except Exception as e:
                print(f"Ошибка ежедневной работы: {e}")
                return

            
    @classmethod
    async def clear_week_statistics(cls):
        async with new_session() as session:
            try:
                week_select = await session.execute(select(WeekStatisticsOrm)).scalars().all()
                for item in week_select:
                    item.flyers = 0
                    item.calls = 0
                    item.shows = 0
                    item.meets = 0
                    item.deals = 0
                    item.deposits = 0
                    item.searches = 0
                    item.analytics = 0
                    item.others = 0
                    await session.flush()
                await session.commit()
            except Exception as e:
                print(f"Ошибка еженедельной работы: {e}")
                return


    @classmethod
    async def clear_month_statistics(cls): 
        async with new_session() as session:
            try:
                month_select = await session.execute(select(MonthStatisticsOrm)).scalars().all()
                for item in month_select:
                    cur_user_record = await session.get(LastMonthStatisticsWithKpiOrm, item.user_id)
                    cur_user_record.flyers = item.flyers
                    cur_user_record.calls = item.calls
                    cur_user_record.shows = item.shows
                    cur_user_record.meets = item.meets
                    cur_user_record.deals = item.deals
                    cur_user_record.deposits = item.deposits
                    cur_user_record.searches = item.searches
                    cur_user_record.analytics = item.analytics
                    cur_user_record.others = item.others
                    calc = RealEstateAgentKPI(cur_user_record.user_level, item.deals, 0, 0, item.calls, item.meets, item.flyers, item.shows)
                    cur_user_record.salary_percentage = calc.calculate_kpi()
                    await session.flush()
                await session.commit()
            except Exception as e:
                print(f"Ошибка ежемесячной работы: {e}")

            try:
                for item in month_select:
                    item.flyers = 0
                    item.calls = 0
                    item.shows = 0
                    item.meets = 0
                    item.deals = 0
                    item.deposits = 0
                    item.searches = 0
                    item.analytics = 0
                    item.others = 0
                await session.commit()
            except Exception as e:
                print(f"Ошибка ежемесячной работы: {e}")
                return
            
    # -------------------------- teams --------------------------

    @classmethod
    async def get_all_teams_by_user_id(cls, user_id: int) -> list[TeamWithInfo]:
        async with new_session() as session:
            try:
                query = select(UserTeamOrm).where(UserTeamOrm.user_id == user_id)
                r = await session.execute(query)
                teams_user = list(r.scalars().all())
                res_teams = list[TeamWithInfo]()
                for t in teams_user:
                    team = await session.get(TeamOrm, t.team_id)
                    team_with_info = TeamWithInfo(team=team, members=[])
                    query__ = select(UserTeamOrm).where(UserTeamOrm.team_id == team.id)
                    r__ = await session.execute(query__)
                    team_users__ = list(r__.scalars().all())
                    team_with_info.members = [UserWithStats(user=await session.get(UserOrm, i.user_id), statistics={j : await Repository.get_statistics_by_period(period=j, user_id=i.user_id) for j in [StatisticPeriods.DAY_STATISTICS_PERIOD, StatisticPeriods.WEEK_STATISTICS_PERIOD, StatisticPeriods.MONTH_STATISTICS_PERIOD]}, role=i.role.name) for i in team_users__]
                    res_teams.append(team_with_info)
                return res_teams
            except:
                return None


    @classmethod
    async def add_team(cls, data: Team, user_id: int) -> int:
        async with new_session() as session:
            try:
                new_team = TeamOrm(**data.model_dump())
                new_team.id = None
                session.add(new_team)
                await session.flush()
                team_id = new_team.id
                await session.commit()

                user_team = UserTeamOrm()
                user_team.role = UserStatusesOrm.OWNER
                user_team.team_id = team_id
                user_team.user_id = user_id
                await Repository.join_to_team(user_team)

                return team_id
            except:
                return None


    @classmethod
    async def del_team(cls, id: int) -> bool:
        async with new_session() as session:
            try:
                team_to_del = await session.get(TeamOrm, id)
                await session.delete(team_to_del)
                await session.commit()
                return True
            except:
                return False
                
    
    @classmethod
    async def edit_team(cls, data: Team) -> bool:
        async with new_session() as session:
            try:
                team_to_edit = await session.get(TeamOrm, data.id)
                team_to_edit.name = data.name
                await session.commit()
                return True
            except:
                return False
            

    @classmethod
    async def join_to_team(cls, data: UserTeamOrm) -> bool:
        async with new_session() as session:
            try:
                session.add(data)
                await session.commit()
                return True
            except:
                return False


    @classmethod
    async def leave_team(cls, user_id: int, team_id: int) -> bool:
        async with new_session() as session:
            try:
                query = select(UserTeamOrm).where(UserTeamOrm.user_id == user_id).where(UserTeamOrm.team_id == team_id)
                r = await session.execute(query)
                user_team_to_del = r.scalars().first()
                await session.delete(user_team_to_del)
                await session.commit()
                return True
            except:
                return False


    # -------------------------- addresses --------------------------


    @classmethod
    async def add_address_info(cls, data: AddresInfo) -> bool:
        async with new_session() as session:
            try:
                addres_info_orm = AddresInfoOrm(**data.model_dump())
                addres_info_orm.record_id = None
                session.add(addres_info_orm)
                await session.flush()
                record_id = addres_info_orm.record_id
                await session.commit()
                return record_id
            except:
                return None


    @classmethod
    async def get_address_info_by_user_id(cls, user_id: int, date_start: int | None = None, date_end: int | None = None) -> list[AddresInfoOrm]:
        async with new_session() as session:
            try:
                query = None
                if date_start is not None and date_end is not None:
                    query = select(AddresInfoOrm).where(AddresInfoOrm.date_time >= date_start).where(AddresInfoOrm.date_time <= date_end).where(AddresInfoOrm.user_id == user_id)
                else:
                    query = select(AddresInfoOrm).where(AddresInfoOrm.user_id == user_id)
                r = await session.execute(query)
                addresses = r.scalars().all()
                return list(addresses)
            except:
                return None


    @classmethod
    async def get_address_info_for_team(cls, team_id: int) -> dict | None:
        async with new_session() as session:
            try:
                query_users = select(UserTeamOrm).where(UserTeamOrm.team_id == team_id)
                r = await session.execute(query_users)
                teams_user = list(r.scalars().all())
                user_addreses_by_team: dict = {}
                for ut in teams_user:
                    query_addresses = select(AddresInfoOrm).where(AddresInfoOrm.user_id == ut.user_id)
                    r = await session.execute(query_addresses)
                    addresses = r.scalars().all()
                    user_addreses_by_team[ut.user_id] = list(addresses)
                return user_addreses_by_team
            except:
                return None


    # -------------------------- images --------------------------


    @classmethod
    async def add_image(cls, image: Image, to_user_id: int) -> int | None:
        async with new_session() as session:
            try:
                image_to_save = ImageOrm(**image.model_dump())
                image_to_save.id = None
                session.add(image_to_save)
                await session.flush()
                image_id = image_to_save.id
                to_user = await session.get(UserOrm, to_user_id)
                to_user.image = image_id
                await session.commit()
                return image_id
            except:
                return None
            
            
    @classmethod
    async def edit_image(cls, image: Image, to_user_id: int) -> int | None:
        async with new_session() as session:
            try:
                new_image_id = await Repository.add_image(image, to_user_id)
                if new_image_id is not None:
                    user = await session.get(UserOrm, to_user_id)
                    old_img = user.image
                    user.image = new_image_id
                    await session.commit()
                    await Repository.delete_image(old_img)
                    return new_image_id
                else:
                    raise Exception
            except:
                return None
                

    @classmethod
    async def get_image(cls, user_id: int) -> ImageOrm | None:
        async with new_session() as session:
            try:
                user = await session.get(UserOrm, user_id)
                return await session.get(ImageOrm, user.image)
            except:
                return None
                
    
    @classmethod
    async def delete_image(cls, image_id: int) -> bool:
        async with new_session() as session:
            try:
                image_to_delete = await session.get(ImageOrm, image_id)
                await session.delete(image_to_delete)
                await session.commit()
                return True
            except:
                return False


    # -------------------------- calls --------------------------


    @classmethod
    async def add_call_record_to_storage(cls, user_id: int, file: UploadFile, phone_number: str, info: str, date_time: int) -> int | None:
        async with new_session() as session:
            try:
                file_to_save = CallsRecordsOrm()
                file_to_save.id = None
                file_to_save.name = file.filename
                file_to_save.data = await file.read()
                session.add(file_to_save)
                await session.flush()
                user_call = UsersCallsOrm()
                user_call.user_id = user_id
                user_call.date_time = date_time
                user_call.info = info
                user_call.phone_number = phone_number
                user_call.transcription = None
                user_call.record_id = file_to_save.id
                session.add(user_call)
                await session.commit()
                return file_to_save.id
            except:
                return None


    @classmethod
    async def get_all_info_user_calls(cls, user_id: int) -> list[UsersCallsOrm] | None:
        async with new_session() as session:
            try:
                query = select(UsersCallsOrm).where(UsersCallsOrm.user_id == user_id)
                r = await session.execute(query)
                return list(r.scalars().all())
            except:
                return None


    @classmethod
    async def get_call_record_from_storage(cls, user_id: int, record_id: int) -> bytes | None:
        async with new_session() as session:
            try:
                call_record = await session.execute(select(CallsRecordsOrm).where(CallsRecordsOrm.id == record_id))
                call_record = call_record.scalars().first()
                if call_record:
                    return call_record.data
                else:
                    return None
            except:
                return None
            

    @classmethod
    async def update_transcription(cls, user_id: int, record_id: int, transcription: str) -> int | None:
        async with new_session() as session:
            try:
                req = await session.execute(select(UsersCallsOrm).where(UsersCallsOrm.user_id == user_id).where(UsersCallsOrm.user_id == user_id))
                user_call = req.scalars().first()
                user_call.transcription = transcription
                await session.commit()
                return True
            except:
                return False