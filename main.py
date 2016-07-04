import praw
import time
import command


USERNAME = "balloonbooperbot"


PASSWORD = ""

try:
    with open("pw.txt", "r") as PW_FILE:
        PASSWORD = PW_FILE.read()
except FileNotFoundError as err:
    print("ERROR: Password file was not found. \n")


read_submissions = []

user_agent = "Windows 10:BalloonBooper:v0.2 (By /u/chickengod37). "

info_message = "^^I'm ^^a ^^bot ^^created ^^by ^^/u/chickengod37. "
info_message += "^^[Github](https://github.com/chickengod37/RedditBalloonBot)"

Reddit = praw.Reddit(user_agent)
Reddit.login(USERNAME, PASSWORD, disable_warning=True)


subreddits = []
mailing_list = []


subreddits.append(Reddit.get_subreddit("balloonswithhats"))
subreddits.append(Reddit.get_subreddit("balloons"))
subreddits.append(Reddit.get_subreddit("test"))

search_keywords = ["balloon"]

try:
    with open("read_subs.txt", "r") as read_submissions_file:
        for line in read_submissions_file:
            if line[:len(line) - 1] not in read_submissions:
                read_submissions.append(line[:len(line) - 1])  # Cut off the '\n' after each line
except FileNotFoundError:
    pass
except EOFError as e:
    print(e)

try:
    with open("mailing_list.txt", "r") as read_mailing_list_file:
        for line in read_mailing_list_file:
            if line[:len(line) - 1] not in mailing_list:
                mailing_list.append(Reddit.get_redditor(line[:len(line) - 1]))  # See above
except FileNotFoundError:
    pass
except EOFError as e:
    print(e)


def find_command(text, usr):
    cmd_in_text = False
    cmd_index = -1
    cmd_len = -1
    for possible_cmd in command.Command.possible_commands:
        if possible_cmd in text:
            cmd_in_text = True
            cmd_index = text.find(possible_cmd)
            cmd_len = len(possible_cmd)

    if not cmd_in_text:
        return command.Command("NULL", None)

    cmd_str = text[cmd_index:(cmd_index + cmd_len)]

    return command.Command(cmd_str, usr)


# returns new tagged submissions
def get_new_tagged_submissions(desired_subreddit):
    taggable_submissions = []
    all_submissions = desired_subreddit.get_new(limit=20)
    for sub in all_submissions:
        title = sub.title.lower()
        has_keyword = any(string in title for string in search_keywords)
        if has_keyword and sub.id not in read_submissions:
            print(sub.id)
            taggable_submissions.append(sub)
            read_submissions.append(sub.id)
    return taggable_submissions


def get_new_command_comments():
    commands = []
    for msg in Reddit.get_unread():
        msg_txt = msg.body
        new_cmd = find_command(msg_txt, msg.author)
        print("FOUND NEW COMMAND")
        commands.append(new_cmd)
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

################
# Main Program #
################
print("Mailing list:")
for user in mailing_list:
    print("    " + user.name)

while True:
    commands_to_process = get_new_command_comments()
    for cmd in commands_to_process:
        process_command(cmd)
        commands_to_process.remove(cmd)

    for subreddit in subreddits:

        tagged_submissions = get_new_tagged_submissions(subreddit)
        if not tagged_submissions:
            print("No new submissions in /r/" + subreddit.display_name + " right now.")
        for submission in tagged_submissions:
            for user in mailing_list:
                print("sending message to {name}. Title: {title}".format(name=user.name, title=submission.title))
                msg_body = "Hello {name}! Someone has recently posted about balloons!\n\n\n\n".format(name=user.name)
                msg_body += "Subreddit: /r/{sub}\n\n".format(sub=subreddit.display_name)
                msg_body += "Title: {title}\n\n".format(title=submission.title)
                msg_body += "Link: {link}\n\n".format(link=submission.short_link)
                msg_body += "*****\n\n"
                msg_body += info_message
                Reddit.send_message(user.name, "A new post with balloons has happened", msg_body)

            write_submissions_file = open("read_subs.txt", "a")
            write_submissions_file.write(submission.id + "\n")
            write_submissions_file.close()

    # Write mailing list to file
    write_mailing_list_file = open("mailing_list.txt", "w")
    for user in mailing_list:
        if user.name not in mailing_list:
            write_mailing_list_file.write(user.name + "\n")
    write_mailing_list_file.close()

    time.sleep(20)
