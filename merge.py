import re

app = 'deadline'
for line in open(app + '-lcs.txt'):
    args = line.strip().split(', ')
    bug_num = re.search('log_cat(\d+)_final', args[0]).group(1)
    scenario = '/'.join(args[1].split('/')[:-1])
    for line in open(app + '{}.txt'.format(bug_num)):
        a, b, c, d = line.strip().split(',')
        if str(bug_num) in a and b == scenario + '/record{}.log'.format(args[2][-9]):
            print ', '.join(args[:-1] + [c, d])
            break
