import re
import sys
from argparse import ArgumentParser
from logging import error
from os import environ
from subprocess import run


def output_text(command):
    """
    Execute a system command and return the output as a list of strings.
    """
    result = run(command.split(" "), check=True, capture_output=True)
    return result.stdout.decode("utf-8").splitlines()


def check_subject_first_word(subject):
    """
    Check the first word in the subject.

    - Must be capitalized
    - Must be an imperative verb
    """
    if not re.match("^[A-Z][a-z]+ .*", subject):
        error("Invalid first word in subject: '{}'".format(subject))
        return 1
    first_word = subject.split()[0]
    for ending in ["ed", "ing"]:
        if first_word.endswith(ending):
            error("Invalid imperative in subject: '{}'".format(first_word))
            return 1
    return 0


def check_subject_length(subject):
    """
    Subject length is limited.
    """
    if len(subject) > 50:
        error("Subject is longer than 50 characters: '{}'".format(subject))
        return 1
    return 0


if __name__ == "__main__":
    parser = ArgumentParser(description="Run MR checks")
    parser.add_argument("--xlength", action="store_true", help="Exclude subject lenght check")
    parser.add_argument("--master", action="store_true", help="Use master branch")
    arguments = parser.parse_args()

    target_name = "main"
    if arguments.master:
        target_name = "master"
    output_text("git fetch --quiet origin {}".format(target_name))
    ancestor = output_text("git merge-base --octopus origin/{}".format(target_name))[0]
    subjects = output_text("git log --pretty=%s {}..".format(ancestor))

    errors = 0
    for subject in subjects:
        errors += check_subject_first_word(subject)
        if not arguments.xlength:
            errors += check_subject_length(subject)
    if errors:
        sys.exit("MR checks failed")
