
import re
import subprocess

executable = './bin/AppGenerator'

# workflows = ['MONTAGE', 'CYBERSHAKE', 'GENOME', 'SIPHT']
workflows = ['GENOME']
# workflows = ['GENOME', 'SIPHT']

tasks = [50, 250, 500]

sequential_runtimes = [1800000, 3600000]
# tasks = [50]

# sequential_runtimes = [3600000]

avg_runtime_scaling = set(['MONTAGE', 'SIPHT'])

def generate_cmd(workflow, num_tasks, factor):
    return [executable, '-a', workflow, '-n', str(num_tasks), '-f', str(factor)]


def bsearch(workflow, num_tasks, target, low, high):
    # print("LOW: %f HIGH: %f" % (low, high))
    if low >= high:
        cmd = generate_cmd(workflow, num_tasks, high)
        runtime, out = execute_cmd(cmd)
        return high, runtime, out
    middle = (low + high) / 2.0
    cmd = generate_cmd(workflow, num_tasks, middle)
    runtime, out = execute_cmd(cmd)
    if abs(runtime - target) < 10000:
        return middle, runtime, out
    if runtime < target:
        return bsearch(workflow, num_tasks, target, middle, high)
    else:
        return bsearch(workflow, num_tasks, target, low, middle)


def execute_cmd(cmd):
    # print(cmd)
    res = subprocess.check_output(cmd)
    runtimes = re.findall('runtime=\"([-+]?\d*\.\d+|\d+)\"', res.decode('utf-8'))
    s = sum([float(x) for x in runtimes])
    # print("Tasks: %d Sequential runtime: %f" % (len(runtimes), s))
    return s, res

def find_upper_bound(workflow, num_tasks, runtime):
    f = 1
    time, _ = execute_cmd(generate_cmd(workflow, num_tasks, f))
    while time < runtime:
        f *= 2
        time, _ = execute_cmd(generate_cmd(workflow, num_tasks, f))
    return f

def decrease_factor(algorithm):
    if algorithm in avg_runtime_scaling:
        return 25
    return 0.25

def go_down(workflow, num_tasks, target, lower_bound, upper_bound):
    runtime, res = execute_cmd(generate_cmd(workflow, num_tasks, upper_bound))
    while abs(runtime - target) > 10000 and runtime > target and upper_bound >= lower_bound:
        upper_bound -= decrease_factor(workflow)
        runtime, res = execute_cmd(generate_cmd(workflow, num_tasks, upper_bound))
        # print("%f -> %f" % (upper_bound, runtime))
    print("found: %f -> %f" % (upper_bound, runtime))
    return upper_bound, runtime, res

def main():
    cases = []
    for algorithm in workflows:
        for num_tasks in tasks:
            for target in sequential_runtimes:
                group = (algorithm, num_tasks, target)
                cases.append(group)
    while cases:
        current = cases.pop()
        algorithm, num_tasks, target = current[0], current[1], current[2]
        print('%s, tasks=%d, target=%d' % (algorithm, num_tasks, target))
        u = find_upper_bound(algorithm, num_tasks, target)
        # print('lower bound: %f, upper bound: %f' % (u // 2, u))
        f, runtime, out = bsearch(algorithm, num_tasks, target, (u // 2), u)
        # f, runtime, out = go_down(algorithm, num_tasks, target, (u // 2), u)
        print("found: %f -> %f, diff=%f\n" % (f, runtime, (abs(target-runtime))))
        if abs(target-runtime) > 10000:
            cases.append(current)
        else:
            filename = algorithm + '_' + str(num_tasks) + '_' + str(target) + '.dax'
            file = open(filename, 'wb')
            file.write(out)
            file.close()


if __name__ == '__main__':
    main()
