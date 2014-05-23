import os
import collections

apps = 'calculator frex stickeroid gm-dice deadline units mirakel wikipedia'.split()

num_users = collections.defaultdict(lambda: 0)
num_scenarios = collections.defaultdict(lambda: 0)

for app in os.listdir('reran/results'):
    if app in apps:
        for user in os.listdir('reran/results/' + app):
            num_users[app] += 1
            for scenario in os.listdir('reran/results/' + app + '/' + user):
                num_scenarios[app] += 1

num_users = dict(num_users)
num_scenarios = dict(num_scenarios)

import pprint
pprint.pprint({
    'num_users': num_users,
    'num_scenarios': num_scenarios,
    'total_scenarios': sum(num_scenarios.values()),
    })
