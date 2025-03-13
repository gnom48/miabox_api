from core.app.database import KpiLevelsOrm, UserTypesOrm


class KpiCalculator:
    def __init__(self, base_percent: float, level: KpiLevelsOrm, deals_rent: int, deals_sale: int, regular_contracts: int, exclusive_contracts: int, cold_calls: int, meetings: int, flyers: int, shows: int, leed_crm: int, rielter_type: UserTypesOrm):
        self.base_percent = base_percent
        self.level = level
        self.deals = deals_rent + deals_sale
        self.deals_rent = deals_rent
        self.deals_sale = deals_sale
        self.rielter_type = rielter_type
        self.exclusive_contracts = exclusive_contracts
        self.regular_contracts = regular_contracts
        self.cold_calls = cold_calls
        self.meetings = meetings
        self.flyers = flyers
        self.shows = shows
        self.leed_crm = leed_crm

    def calculate_kpi(self) -> float:
        self.min_percent = 40.0

        if self.rielter_type == UserTypesOrm.PRIVATE:
            if self.level == KpiLevelsOrm.TRAINEE:
                bonus_percent = 0.5 * self.exclusive_contracts + 0.25 * self.regular_contracts
                if self.cold_calls < status.HTTP_200_OK.0 or self.meetings < 84 or self.flyers < 1status.HTTP_200_OK.0 or self.shows < 80.0:
                    return self.base_percent
                return self.base_percent + bonus_percent

            elif self.level == KpiLevelsOrm.SPECIALIST:
                bonus_percent = 0.5 * self.exclusive_contracts + 0.25 * self.regular_contracts
                if self.cold_calls < 90.0 or self.meetings < 40.0 or self.flyers < 1000.0:
                    return self.base_percent
                extra_deals = max(0, self.deals - 1)
                extra_percent = extra_deals * 2.5
                if self.cold_calls > 90:
                    extra_percent += 2
                if self.meetings > 40:
                    extra_percent += 2
                if self.flyers > 1000:
                    extra_percent += 1
                return self.base_percent + bonus_percent + extra_percent

            elif self.level == KpiLevelsOrm.EXPERT:
                bonus_percent = 0.5 * self.exclusive_contracts + 0.25 * self.regular_contracts
                if self.cold_calls < 60.0 or self.meetings < 30.0 or self.flyers < 500.0:
                    return self.base_percent
                extra_deals = max(0, self.deals - 1)
                extra_percent = extra_deals * 2.5
                if self.cold_calls > 60:
                    extra_percent += 2
                if self.meetings > 30:
                    extra_percent += 2
                if self.flyers > 500:
                    extra_percent += 1
                return self.base_percent + bonus_percent + extra_percent

            elif self.level == KpiLevelsOrm.TOP:
                bonus_percent = 0.5 * self.exclusive_contracts + 0.25 * self.regular_contracts
                if self.cold_calls < 50.0 or self.meetings < 20.0 or self.flyers < 500.0:
                    return self.base_percent
                extra_deals = max(0, self.deals - 1)
                extra_percent = extra_deals * 2.5
                if self.cold_calls > 50:
                    extra_percent += 2
                if self.meetings > 20:
                    extra_percent += 2
                if self.flyers > 500:
                    extra_percent += 1
                return self.base_percent + bonus_percent + extra_percent
            else:
                raise Exception("Invalid level")
        elif self.rielter_type == UserTypesOrm.COMMERCIAL:
            raise Exception("TODO")
