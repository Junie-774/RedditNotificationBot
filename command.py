class Command:

    possible_commands = ["addMe", "delMe"]

    def __init__(self, string, user):
        self.cmd_str = string
        self.user = user

