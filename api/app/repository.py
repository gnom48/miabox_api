from fastapi import UploadFile
from .api.kpi_calculator import KpiCalculator
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
    async def get_config(cls) -> tuple:
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
            

    @classmethod
    async def get_supported_version(cls) -> int:
        async with new_session() as session:
            try:
                req = text("SELECT supported_version FROM versions;")
                result = await session.execute(req)
                version = result.scalars().first()
                return int(version)
            except:
                return 0

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
            summary = SummaryStatisticsWithLevelOrm()
            summary.user_id = new_user.id
            summary.deals_rent = 0
            summary.deals_sale = 0
            coefs = Repository.get_user_level_by_deals_count(0)
            summary.user_level = coefs[0]
            summary.base_percent = coefs[1]
            session.add(day_stats)
            session.add(week_stats)
            session.add(month_stats)
            session.add(summary)

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
                old_user.email = data.email
                await session.flush()
            except:
                return False
            await session.commit()
            return True


    @classmethod
    async def get_user_by_id(cls, id: str) -> UserOrm:
        async with new_session() as session:
            try:
                res = await session.get(UserOrm, id)
                return res
            except:
                return None


    @classmethod
    async def get_user_statistics(cls, id: str) -> StatisticsViaOrm:
        async with new_session() as session:
            try:
                res = await session.get(StatisticsViaOrm, id)
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
    async def get_all_notes_by_user_id(cls, user_id: str) -> list[NoteOrm]:
        async with new_session() as session:
            try:
                query = select(NoteOrm).where(NoteOrm.user_id == user_id)
                r = await session.execute(query)
                return r.scalars().all()
            except:
                return None


    @classmethod
    async def add_note(cls, data: Note) -> str:
        async with new_session() as session:
            try:
                new_note = NoteOrm(**data.model_dump())
                if new_note.id == "":
                    new_note.id = None
                session.add(new_note)
                await session.flush()
                note_id = new_note.id
                await session.commit()
                return note_id
            except:
                return None


    @classmethod
    async def del_note(cls, id: str) -> bool:
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
    async def get_all_tasks_by_user_id(cls, user_id: str, completed: bool) -> list[TaskOrm]:
        async with new_session() as session:
            try:
                query = select(TaskOrm).where(TaskOrm.user_id == user_id).where(TaskOrm.is_completed == completed)
                r = await session.execute(query)
                return r.scalars().all()
            except:
                return None


    @classmethod
    async def add_task(cls, data: Task) -> str:
        async with new_session() as session:
            try:
                new_task = TaskOrm(**data.model_dump())
                if new_task.id == "":
                    new_task.id = None
                new_task.work_type = data.work_type.name
                new_task.is_completed = False
                session.add(new_task)
                await session.flush()
                task_id = new_task.id
                await session.commit()
                return task_id
            except:
                return None


    @classmethod
    async def del_task(cls, id: str) -> bool:
        async with new_session() as session:
            try:
                task_to_del = await session.get(TaskOrm, id)
                task_to_del.is_completed = True
                if task_to_del.work_type != WorkTasksTypesOrm.OTHER:
                    await session.delete(task_to_del)
                await session.commit()
                return True
            except:
                return False
            

    # -------------------------- statistics --------------------------

    @classmethod
    def get_user_level_by_deals_count(cls, deals_count: int, top_flag: bool = False) -> tuple:
        if top_flag and deals_count >= 21:
            return (UserKpiLevelsOrm.TOP, 50)
        elif deals_count <= 3:
            return (UserKpiLevelsOrm.TRAINEE, 40)
        elif deals_count >= 3 and deals_count <= 20:
            return (UserKpiLevelsOrm.SPECIALIST, 43)
        elif deals_count > 21:
            return (UserKpiLevelsOrm.EXPERT, 45)
    

    @classmethod
    async def update_statistics(cls, user_id: str, statistic: str, addvalue: int) -> bool:
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
                    case WorkTasksTypesOrm.DEAL_RENT.value:
                        day_statistic_to_edit.deals_rent += addvalue
                        week_statistic_to_edit.deals_rent += addvalue
                        month_statistic_to_edit.deals_rent += addvalue
                        summary = await session.get(SummaryStatisticsWithLevelOrm, user_id)
                        summary.deals_rent = summary.deals_rent + addvalue
                        coefs = Repository.get_user_level_by_deals_count(int(summary.deals_sale) + int(summary.deals_rent))
                        summary.user_level = coefs[0]
                        summary.base_percent = coefs[1]
                    case WorkTasksTypesOrm.DEAL_SALE.value:
                        day_statistic_to_edit.deals_sale += addvalue
                        week_statistic_to_edit.deals_sale += addvalue
                        month_statistic_to_edit.deals_sale += addvalue
                        summary = await session.get(SummaryStatisticsWithLevelOrm, user_id)
                        summary.deals_sale = summary.deals_sale + addvalue
                        coefs = Repository.get_user_level_by_deals_count(int(summary.deals_sale) + int(summary.deals_rent))
                        summary.user_level = coefs[0]
                        summary.base_percent = coefs[1]
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
                    case WorkTasksTypesOrm.REGULAR_CONTRACT.value:
                        day_statistic_to_edit.regular_contracts += addvalue
                        week_statistic_to_edit.regular_contracts += addvalue
                        month_statistic_to_edit.regular_contracts += addvalue
                        month_statistic_to_edit.regular_contracts += addvalue
                    case WorkTasksTypesOrm.EXCLUSIVE_CONTRACT.value:
                        day_statistic_to_edit.exclusive_contracts += addvalue
                        week_statistic_to_edit.exclusive_contracts += addvalue
                        month_statistic_to_edit.exclusive_contracts += addvalue
                        month_statistic_to_edit.exclusive_contracts += addvalue
                    case WorkTasksTypesOrm.OTHER.value:
                        day_statistic_to_edit.others += addvalue
                        week_statistic_to_edit.others += addvalue
                        month_statistic_to_edit.others += addvalue
                await session.commit()
                return True
            except:
                return False
            
    
    @classmethod
    async def get_statistics_by_period(cls, user_id: str, period: str) -> StatisticsViaOrm:
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
    async def get_statistics_with_kpi(cls, user_id: str) -> LastMonthStatisticsWithKpiOrm:
        async with new_session() as session:
            try:
                return await session.get(LastMonthStatisticsWithKpiOrm, user_id)
            except:
                return None
                
    
    @classmethod
    async def get_current_kpi(cls, user: UserOrm) -> dict:
        async with new_session() as session:
            try:
                data = await session.get(MonthStatisticsOrm, user.id)
                coefs = await session.get(SummaryStatisticsWithLevelOrm, user.id)
                kpi_calc = KpiCalculator(coefs.base_percent, coefs.user_level, data.deals_rent, data.deals_sale, data.regular_contracts, data.exclusive_contracts, data.calls, data.meets, data.flyers, data.analytics, 0, user.type)
                return { "kpi": kpi_calc.calculate_kpi(), "level": coefs.user_level.value, "deals_rent": coefs.deals_rent, "deals_sale": coefs.deals_sale }
            except Exception as e:
                return None
            
                
    @classmethod
    async def update_kpi_level(cls, user_id: str, level: UserKpiLevels) -> StatisticsViaOrm:
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
                query = update(DayStatisticsOrm).values(flyers=0, calls=0, shows=0, meets=0, deals_rent=0, deals_sale = 0, deposits = 0, searches = 0, analytics = 0, others = 0, regular_contracts=0, exclusive_contracts=0)
                await session.execute(query)
                await session.commit()
                print(f"Обнуление ежедневной статистики")
            except Exception as e:
                print(f"Ошибка ежедневной работы: {e}")
                return

            
    @classmethod
    async def clear_week_statistics(cls):
        async with new_session() as session:
            try:
                query = update(WeekStatisticsOrm).values(flyers = 0, calls = 0, shows = 0, meets = 0, deals_rent = 0, deals_sale = 0, deposits = 0, searches = 0, analytics = 0, others = 0, regular_contracts=0, exclusive_contracts=0)
                await session.execute(query)
                await session.commit()
                print(f"Обнуление еженедельной статистики")
            except Exception as e:
                print(f"Ошибка еженедельной работы: {e}")
                return


    @classmethod
    async def clear_month_statistics(cls): 
        async with new_session() as session:
            try:
                res = await session.execute(select(MonthStatisticsOrm))
                month_select = list(res.scalars().all())
                for item in month_select:
                    cur_user_record = await session.get(LastMonthStatisticsWithKpiOrm, item.user_id)
                    cur_user = await session.get(UserOrm, item.user_id)
                    cur_user_record.flyers = item.flyers
                    cur_user_record.calls = item.calls
                    cur_user_record.shows = item.shows
                    cur_user_record.meets = item.meets
                    cur_user_record.deals_rent = item.deals_rent
                    cur_user_record.deals_sale = item.deals_sale
                    cur_user_record.deposits = item.deposits
                    cur_user_record.searches = item.searches
                    cur_user_record.analytics = item.analytics
                    cur_user_record.others = item.others
                    cur_user_record.regular_contracts = item.regular_contracts
                    cur_user_record.exclusive_contracts = item.exclusive_contracts
                    coefs = await session.get(SummaryStatisticsWithLevelOrm, item.user_id)
                    calc = KpiCalculator(coefs.base_percent, cur_user_record.user_level, item.deals_rent, item.deals_sale, item.regular_contracts, item.exclusive_contracts, item.calls, item.meets, item.flyers, item.shows, 0, cur_user.type)
                    cur_user_record.salary_percentage = calc.calculate_kpi()
                    await session.commit()
                print("Сбор для kpi")
            except Exception as e:
                print(f"Ошибка ежемесячной работы: {e}")

            try:
                query = update(MonthStatisticsOrm).values(flyers=0, calls=0, shows=0, meets=0, deals_rent=0, deals_sale=0, deposits=0, searches=0, analytics=0, others=0, regular_contracts=0, exclusive_contracts=0)
                await session.execute(query)
                print(f"Обнуление ежемесячной статистики")
                await session.commit()
            except Exception as e:
                print(f"Ошибка ежемесячной работы: {e}")
                return
            
    # -------------------------- teams --------------------------


    @staticmethod
    def __hide_password(u: UserOrm) -> UserOrm:
        u.password = "***"
        return u

    @classmethod
    async def get_all_teams_by_user_id(cls, user_id: str) -> list[TeamWithInfo]:
        async with new_session() as session:
            try:
                query = select(UserTeamOrm).where(UserTeamOrm.user_id == user_id)
                r = await session.execute(query)
                teams_user = list(r.scalars().all())
                res_teams = list[TeamWithInfo]()
                for t in teams_user:
                    team = await session.get(TeamOrm, t.team_id)
                    team_with_info = TeamWithInfo(team=team, members=[])
                    query_userteam = select(UserTeamOrm).where(UserTeamOrm.team_id == team.id)
                    r_userteam = await session.execute(query_userteam)
                    team_users__ = list(r_userteam.scalars().all())
                    team_with_info.members = [UserWithStats(
                        user=Repository.__hide_password(await session.get(UserOrm, i.user_id)),
                        statistics={j : await Repository.get_statistics_by_period(period=j, user_id=i.user_id) for j in [StatisticPeriods.DAY_STATISTICS_PERIOD, StatisticPeriods.WEEK_STATISTICS_PERIOD, StatisticPeriods.MONTH_STATISTICS_PERIOD]}, 
                        addresses=(await session.execute(select(AddresInfoOrm).where(AddresInfoOrm.user_id == i.user_id))).scalars().all(),
                        calls=(await session.execute(select(UsersCallsOrm).where(UsersCallsOrm.user_id == i.user_id))).scalars().all(),
                        kpi=await session.get(LastMonthStatisticsWithKpiOrm, i.user_id),
                        role=i.role.name) for i in team_users__]
                    res_teams.append(team_with_info)
                return res_teams
            except Exception as e:
                print(e)
                return None


    @classmethod
    async def add_team(cls, data: Team, user_id: str) -> str:
        async with new_session() as session:
            try:
                new_team = TeamOrm(**data.model_dump())
                if new_team.id == "":
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
    async def del_team(cls, id: str) -> bool:
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
    async def move_team_user_role(cls, team_id: str, user_id: str, role: UserStatuses) -> bool:
        async with new_session() as session:
            try:
                role_orm = UserStatusesOrm.OWNER
                if role == UserStatuses.USER:
                    role_orm = UserStatusesOrm.USER
                query = (
                    update(UserTeamOrm)
                    .where(UserTeamOrm.team_id == team_id)
                    .where(UserTeamOrm.user_id == user_id)
                    .values(role=role_orm)
                )
                await session.execute(query)
                await session.commit()
                return True
            except Exception as e:
                print(f"move_team_user_role error: {e}")
                return False


    @classmethod
    async def leave_team(cls, user_id: str, team_id: str) -> bool:
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
                address_info_orm = AddresInfoOrm(**data.model_dump())
                address_info_orm.record_id = data.record_id
                if address_info_orm.record_id == "":
                    address_info_orm.record_id = None
                session.add(address_info_orm)
                await session.flush()
                record_id = address_info_orm.record_id
                await session.commit()
                return record_id
            except:
                return None


    @classmethod
    async def get_address_info_by_user_id(cls, user_id: str, date_start: int | None = None, date_end: int | None = None) -> list[AddresInfoOrm]:
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


    # -------------------------- images --------------------------


    @classmethod
    async def add_image(cls, image: Image, to_user_id: str) -> str | None:
        async with new_session() as session:
            try:
                image_to_save = ImageOrm(**image.model_dump())
                if image_to_save.id == "":
                    image_to_save.id = None
                session.add(image_to_save)
                await session.flush()
                image_id = image_to_save.id
                to_user = await session.get(UserOrm, to_user_id)
                to_user.image = "1"
                await session.commit()

                await Repository.delete_image(to_user.image)
                to_user.image = image_id
                await session.commit()
                return image_id
            except Exception as e:
                print(f"Ошибка добавления картинки: {e}")
                return None

    
    @classmethod
    async def edit_image_file(cls, file: UploadFile, new_filename: str, to_user_id: str) -> str | None:
        async with new_session() as session:
            try:
                await file.seek(0)
                image = Image(id="", name=new_filename, data=bytearray(0))
                new_image_id = await Repository.add_image(image, to_user_id)
                return new_image_id
            except Exception as e:
                print(f"Ошибка загрузки картинки: {e}")
                return None
                

    @classmethod
    async def get_image(cls, user_id: str) -> ImageOrm | None:
        async with new_session() as session:
            try:
                user = await session.get(UserOrm, user_id)
                return await session.get(ImageOrm, user.image)
            except:
                return None
                
    
    @classmethod
    async def delete_image(cls, image_id: str) -> bool:
        async with new_session() as session:
            try:
                if image_id == "1":
                    return True
                image_to_delete = await session.get(ImageOrm, image_id)
                await session.delete(image_to_delete)
                await session.commit()
                return True
            except:
                return False


    # -------------------------- calls --------------------------


    @classmethod
    async def add_call_record_to_storage(cls, 
                                            user_id: str, file: UploadFile | None, new_filename: str, phone_number: str,
                                            contact_name: str, length_seconds: int, call_type: int,
                                            info: str, date_time: int, record_id: str | None) -> str | None:
        async with new_session() as session:
            try:
                if file is not None:
                    await file.seek(0)
                file_to_save = CallsRecordsOrm()
                if record_id == "" or record_id == None:
                    file_to_save.id = None
                else:
                    file_to_save.id = record_id
                file_to_save.name = new_filename
                file_to_save.data = None # await file.read()
                session.add(file_to_save)
                await session.flush()
                user_call = UsersCallsOrm()
                user_call.user_id = user_id
                user_call.date_time = date_time
                user_call.info = info
                user_call.phone_number = phone_number
                user_call.contact_name = contact_name
                user_call.call_type = call_type
                user_call.length_seconds = length_seconds
                user_call.transcription = None
                user_call.record_id = file_to_save.id
                session.add(user_call)
                await session.commit()
                return file_to_save.id
            except Exception as e:
                return None


    @classmethod
    async def get_all_info_user_calls(cls, user_id: str) -> list[UsersCallsOrm] | None:
        async with new_session() as session:
            try:
                query = select(UsersCallsOrm).where(UsersCallsOrm.user_id == user_id)
                r = await session.execute(query)
                return list(r.scalars().all())
            except:
                return None
                
                
    @classmethod
    async def get_all_user_call_records(cls, user_id: str) -> list[CallsRecordsOrm] | None:
        async with new_session() as session:
            try:
                calls: list[UsersCallsOrm] = await Repository.get_all_info_user_calls(user_id)
                records = [call.record_id for call in calls]
                query = select(CallsRecordsOrm)
                r = await session.execute(query)
                call_records = list(r.scalars().all())
                ret_val = []
                for i in call_records:
                    if i.id in records:
                        ret_val.append(i)
                return ret_val
            except:
                return None


    @classmethod
    async def get_call_record(cls, user_id: str, record_id: str) -> CallsRecordsOrm | None:
        async with new_session() as session:
            try:
                call_record = await session.execute(select(CallsRecordsOrm).where(CallsRecordsOrm.id == record_id))
                return call_record.scalars().first()
            except:
                return None
            

    @classmethod
    async def update_transcription(cls, user_id: str, record_id: str, transcription: str) -> bool | None:
        async with new_session() as session:
            try:
                req = await session.execute(select(UsersCallsOrm).where(UsersCallsOrm.user_id == user_id).where(UsersCallsOrm.record_id == record_id))
                user_call = req.scalars().first()
                user_call.transcription = transcription
                await session.commit()
                return True
            except:
                return False
            

    @classmethod
    async def get_filename(cls, user_id: str, record_id: str) -> str | None:
        async with new_session() as session:
            try:
                req = await session.execute(select(CallsRecordsOrm).where(CallsRecordsOrm.id == record_id))
                call = req.scalars().first()
                return call.name
            except:
                return None