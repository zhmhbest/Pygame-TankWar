import uuid


class Timer(object):
    """ 计时器，定时执行回调函数"""

    def __init__(self):
        self.timers = []

    def add(self, interval, f, repeat=-1):
        timer = {
            "interval": interval,  # 调用间隔，单位ms
            "callback": f,  # 回调函数
            "repeat": repeat,  # 重复调用次数
            "times": 0,  # 当前调用次数
            "time": 0,  # 计时
            "uuid": uuid.uuid4()  # 唯一id
        }
        self.timers.append(timer)
        return timer["uuid"]

    def destroy(self, uuid_nr):
        for timer in self.timers:
            if timer["uuid"] == uuid_nr:
                self.timers.remove(timer)
                return

    def update(self, time_passed):
        for timer in self.timers:
            timer["time"] += time_passed
            # 够间隔时间就调用回调函数并重新计时
            if timer["time"] >= timer["interval"]:
                timer["time"] -= timer["interval"]
                timer["times"] += 1
                # 调用次数满就移除该回调函数的计时器，否则调用该回调函数
                if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
                    self.timers.remove(timer)
                try:
                    timer["callback"]()
                except:
                    try:
                        self.timers.remove(timer)
                    except:
                        pass

# 全局计时器
gtimer = Timer()
