from .models import UserKpiLevels
from api.app.database import UserKpiLevelsOrm, UserTypesOrm


class KpiCalculator:
    def __init__(self, level: UserKpiLevelsOrm, deals: int, exclusive_contracts: int, regular_contracts: int, cold_calls: int, meetings: int, flyers: int, shows: int, leed_crm: int, rielter_type: UserTypesOrm = UserTypesOrm.PRIVATE):
        self.level = level
        self.deals = deals
        self.rielter_type = rielter_type
        self.exclusive_contracts = exclusive_contracts
        self.regular_contracts = regular_contracts
        self.cold_calls = cold_calls
        self.meetings = meetings
        self.flyers = flyers
        self.shows = shows
        self.leed_crm = leed_crm

    # TODO: добавить для коммерческого 
    # TODO: переписать 
    def calculate_kpi(self) -> float:
        if self.rielter_type == UserTypesOrm.PRIVATE:
            if self.level == UserKpiLevelsOrm.TRAINEE:
                base_percent = 0.4
                bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
                if self.deals > 3:
                    return 0.0
                if self.cold_calls < 200.0 or self.meetings < 84 or self.flyers < 1200.0 or self.shows < 80.0 or self.leed_crm < 0.9:
                    return 0.0
                return base_percent + bonus_percent * self.deals

            elif self.level == UserKpiLevelsOrm.SPECIALIST:
                base_percent = 0.4
                bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
                if self.deals > 20:
                    return 0.0
                if self.cold_calls < 90.0 or self.meetings < 40.0 or self.flyers < 1000.0 or self.leed_crm < 0.9:
                    return 0.0
                extra_deals = max(0, self.deals - 1)
                extra_percent = extra_deals * 0.025
                if self.cold_calls > 90:
                    extra_percent += 0.02
                if self.meetings > 40:
                    extra_percent += 0.02
                if self.flyers > 1000:
                    extra_percent += 0.01
                return base_percent + bonus_percent * self.deals + extra_percent

            elif self.level == UserKpiLevelsOrm.EXPERT:
                base_percent = 0.45
                bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
                if self.deals <= 20:
                    return 0.0
                if self.cold_calls < 60.0 or self.meetings < 30.0 or self.flyers < 500.0 or self.shows < 80.0 or self.leed_crm < 0.9:
                    return 0.0
                extra_deals = max(0, self.deals - 1)
                extra_percent = extra_deals * 0.025
                if self.cold_calls > 60:
                    extra_percent += 0.02
                if self.meetings > 30:
                    extra_percent += 0.02
                if self.flyers > 500:
                    extra_percent += 0.01
                return base_percent + bonus_percent * self.deals + extra_percent

            elif self.level == UserKpiLevelsOrm.TOP:
                base_percent = 0.5
                bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
                if self.deals <= 20:
                    return 0.0
                if self.cold_calls < 50.0 or self.meetings < 20.0 or self.flyers < 500.0 or self.shows < 80.0 or self.leed_crm < 0.9:
                    return 0.0
                extra_deals = max(0, self.deals - 1)
                extra_percent = extra_deals * 0.025
                if self.cold_calls > 50:
                    extra_percent += 0.02
                if self.meetings > 20:
                    extra_percent += 0.02
                if self.flyers > 500:
                    extra_percent += 0.01
                return base_percent + bonus_percent * self.deals + extra_percent
            else:
                raise Exception("Invalid level")
        elif self.rielter_type == UserTypesOrm.COMMERCIAL:
            raise Exception("TODO")

