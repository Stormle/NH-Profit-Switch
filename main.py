import argparse
import sys
import asyncio
from plugController import MinerPlug
from profitTracker import Tracker
from threads import RepeatTimer, asyncWithMaxLaps, thread_with_exception

# !!!!!!!!!THIS PROGRAM NEEDS NMAP INSTALLED ON THE SYSTEM!!!!!!!!!
task_repeat_time_in_minutes = 15
status_check_interval_in_minutes = 5
pc_power_use_in_watts = 349
electricity_cost_per_kw = 0.1
ipMask = '192.168.1.0/24'
hashrates = {
    "speeds": {"DAGGERHASHIMOTO": 96, "KAWPOW": 46, "BEAMV3": 47.2, "GRINCUCKATOO32": 0.845, "CUCKOOCYCLE": 11.5,
               "ZHASH": 146.6, "OCTOPUS": 73.2, "AUTOLYKOS": 195, "ZELHASH": 78}}


async def init():
    p100_1 = MinerPlug("5C:A6:E6:FF:00:76", ipMask, args.email, args.password)
    success = False
    while success == False:
        success = p100_1.initializeConnection()
    testvar = p100_1.plug_status
    profit_tracker = Tracker(pc_power_use_in_watts, electricity_cost_per_kw, hashrates)
    status_checker = RepeatTimer(status_check_interval_in_minutes * 60, p100_1.refreshPlugStatus, {})
    status_checker.start()
    p110_1_timer = RepeatTimer(task_repeat_time_in_minutes * 60, reoccurring_task, [p100_1, profit_tracker])
    p110_1_timer.start()

def reoccurring_task(plug, profit_tracker):
    profit_tracker.refresh()
    profit = profit_tracker.get_profitability()
    print("plug status: " + str(plug.plug_status))
    if profit >= 0 and not plug.plug_status:
        plug.plug_desired_status = True
        plug.refreshPlugStatus()
    if profit < 0 and plug.plug_status:
        plug.plug_desired_status = False
        plug.refreshPlugStatus()
args = ""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NH-Profit-Switch')
    parser.add_argument('--email', help="Your TP-link Tapo email")
    parser.add_argument('--password', help="Your TP-link Tapo password")
    args = parser.parse_args(sys.argv[1:])
    asyncio.run(init())
