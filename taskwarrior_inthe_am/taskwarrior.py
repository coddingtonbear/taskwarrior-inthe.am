from taskw.taskrc import TaskRc


def get_taskwarrior_config(path):
    try:
        return TaskRc(path)
    except IOError:
        return {}
