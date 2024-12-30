'''
  * author 冯自立
  * created at : 2024-12-30 23:07:10
  * description: 实现一个按照日期设置限制的工具类
'''
import datetime


class DailyLimitationManager:
    def __init__(self, dateLimitationStr: str, dailyLimitation=5):
        if dateLimitationStr:
            self.dateStr, timeStr = dateLimitationStr.split(',')
            self.timeCount = int(timeStr)
        else:
            self.dateStr = datetime.datetime.now().strftime('%Y-%m-%d')
            self.timeCount = 0
        self.dailyLimitation = dailyLimitation

    def autoReset(self):
        todayStr = datetime.datetime.now().strftime('%Y-%m-%d')
        if todayStr != self.dateStr:
            self.dateStr = todayStr
            self.timeCount = 0

    @property
    def reachedDailyLimitation(self):
        self.autoReset()
        return (self.timeCount + 1) >= self.dailyLimitation

    def use(self, timeCount=1):
        self.autoReset()
        self.timeCount += timeCount
        return self.dailyLimitation - self.timeCount

    def getRemainingTime(self):
        self.autoReset()
        return self.dailyLimitation - self.timeCount

    def toString(self):
        self.autoReset()
        return f"{self.dateStr},{self.timeCount}"
