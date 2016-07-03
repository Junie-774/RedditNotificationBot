class Command:

    possible_commands = ["addMe", "delMe"]

    def __init__(self, str, user):
        self.cmd_str = str
        self.user = user

