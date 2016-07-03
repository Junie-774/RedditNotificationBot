import praw
import time
import command

USERNAME = "balloonbooperbot"

PW_FILE = open("pw.txt", "r")

PASSWORD = PW_FILE.read()

read_submissions_file = open("read_subs.txt", "r")
read_mailing_list_file = open("mailing_list.txt", "r")

user_agent = "Windows 10:BalloonBooper:v0.2 (By /u/chickengod37)"

interactor = praw.Reddit(user_agent)
interactor.login(USERNAME, PASSWORD, disable_warning = True)

tagged_submissions = []

subreddits = []
mailing_list = []
mailing_list.append(interactor.get_redditor("chickengod37"))
keywords = ["balloon"]

subreddits.append(interactor.get_subreddit("balloonswithhats"))
subreddits.append(interactor.get_subreddit("balloons"))
subreddits.append(interactor.get_subreddit("test"))

read_submissions = []
commands_to_process = []

for line in read_submissions_file:
    if line[:len(line) - 1] not in read_submissions:
        read_submissions.append(line[:len(line) - 1]) #cut off the '\n' after each line

for line in read_mailing_list_file:
    if line[:len(line) - 1] not in mailing_list:
        mailing_list.append(interactor.get_redditor(line[:len(line) - 1])) #again, cut off the '\n' after each line


read_submissions_file.close()
read_mailing_list_file.close()


def find_command(text, user):
    cmd_in_text = False
    cmd_index = -1
    cmd_len = -1
    for cmd in command.Command.possible_commands:
        if cmd in text:
            cmd_in_text = True
            cmd_index = text.find(cmd)
            cmd_len = len(cmd)

    if not cmd_in_text:
        return command.Command("NULL", None)

    cmd_str = text[cmd_index:(cmd_index + cmd_len)]

    return command.Command(cmd_str, user)


# returns new tagged submissions
def get_new_tagged_submissions(desired_subreddit):
    taggable_submissions = []
    all_submissions = desired_subreddit.get_new(limit=20)
    for submission in all_submissions:
        title = submission.title.lower()
        has_keyword = any(string in title for string in keywords)
        if has_keyword and submission.id not in read_submissions:
            print(submission.id)
            taggable_submissions.append(submission)
            read_submissions.append(submission.id)
    return taggable_submissions


def get_new_command_comments():
    commands = []
    for msg in interactor.get_unread():
        msg_txt = msg.body
        command = find_command(msg_txt, msg.author)
        print("FOUND NEW COMMAND")
        commands.append(command)
        msg.mark_as_read()

    return commands


def process_command(cmd_to_process):
    if cmd_to_process.cmd_str == "addMe":
        if cmd_to_process.user not in mailing_list:
            mailing_list.append(cmd_to_process.user)
    elif cmd_to_process.cmd_str == "delMe":
        if cmd_to_process.user in mailing_list:
            mailing_list.remove(cmd_to_process.user)

        print("DELETING USER " + cmd_to_process.user.name)


while True:
    commands_to_process = get_new_command_comments()
    for cmd in commands_to_process:
        process_command(cmd)
        commands_to_process.remove(cmd)

    for subreddit in subreddits:

        tagged_submissions = get_new_tagged_submissions(subreddit)

        for submission in tagged_submissions:
            write_submissions_file = open("read_subs.txt", "a")
            for user in mailing_list:
                print("sending message to {name}. Title: {title}".format(name=user.name, title=submission.title))
                msg_body = "Title: {title}. \n\nLink: {link}.".format(title = submission.title, link = submission.short_link)
                interactor.send_message(user.name, "A new post with balloons has happened", msg_body)
            write_submissions_file.write(submission.id + "\n")
            write_submissions_file.close()

    time.sleep(20)

write_mailing_list_file = open("mailing_list.txt", "w")
for user in mailing_list:
    write_mailing_list_file.write(user + "\n")



