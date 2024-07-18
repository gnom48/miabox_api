from .models import UserKpiLevels


class RealEstateAgentKPI:
    def __init__(self, level: UserKpiLevels, deals: int, exclusive_contracts: int, regular_contracts: int, cold_calls: int, meetings: int, flyers: int, shows: int, leed_crm: int):
        self.level = level
        self.deals = deals
        self.exclusive_contracts = exclusive_contracts
        self.regular_contracts = regular_contracts
        self.cold_calls = cold_calls
        self.meetings = meetings
        self.flyers = flyers
        self.shows = shows
        self.leed_crm = leed_crm

    def calculate_kpi(self):
        if self.level == UserKpiLevels.TRAINEE:
            base_percent = 0.4
            bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
            if self.deals > 3:
                return 0
            if self.cold_calls < 200 or self.meetings < 84 or self.flyers < 1200 or self.shows < 80 or self.leed_crm < 0.9:
                return 0
            return base_percent + bonus_percent * self.deals

        elif self.level == UserKpiLevels.SPECIALIST:
            base_percent = 0.4
            bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
            if self.deals > 20:
                return 0
            if self.cold_calls < 90 or self.meetings < 40 or self.flyers < 1000 or self.leed_crm < 0.9:
                return 0
            extra_deals = max(0, self.deals - 1)
            extra_percent = extra_deals * 0.025
            if self.cold_calls > 90:
                extra_percent += 0.02
            if self.meetings > 40:
                extra_percent += 0.02
            if self.flyers > 1000:
                extra_percent += 0.01
            return base_percent + bonus_percent * self.deals + extra_percent

        elif self.level == UserKpiLevels.EXPERT:
            base_percent = 0.45
            bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
            if self.deals <= 20:
                return 0
            if self.cold_calls < 60 or self.meetings < 30 or self.flyers < 500 or self.shows < 80 or self.leed_crm < 0.9:
                return 0
            extra_deals = max(0, self.deals - 1)
            extra_percent = extra_deals * 0.025
            if self.cold_calls > 60:
                extra_percent += 0.02
            if self.meetings > 30:
                extra_percent += 0.02
            if self.flyers > 500:
                extra_percent += 0.01
            return base_percent + bonus_percent * self.deals + extra_percent

        elif self.level == UserKpiLevels.TOP:
            base_percent = 0.5
            bonus_percent = 0.005 if self.exclusive_contracts else 0.0025
            if self.deals <= 20:
                return 0
            if self.cold_calls < 50 or self.meetings < 20 or self.flyers < 500 or self.shows < 80 or self.leed_crm < 0.9:
                return 0
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
