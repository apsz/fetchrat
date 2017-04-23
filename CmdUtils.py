#!/usr/bin/python3


# wrapper for unittest
def get_input(text):
    return input(text)


def get_str(msg, input_type='string', valid=None, default=None, min_len=0, max_len=30):
    msg += ' [{}]:'.format(default) if default else ': '
    while True:
        user_input = get_input(msg)
        if not user_input:
            if default:
                return default
            print('{} cannot be empty.'.format(input_type))
            continue
        user_string_len = len(user_input)
        if ((not min_len or min_len <= user_string_len) and
                (not max_len or max_len >= user_string_len)):
            if valid:
                if user_input in valid:
                    return user_input
                print('Not in valid range.')
                continue
            return user_input
        else:
            print('{} must be between {} and {} long.'.format(input_type, min_len, max_len))


def get_int(msg, input_type='integer', default=None, min_val=0, max_val=100):
    msg += ' [{}]:'.format(default) if default else ': '
    while True:
        try:
            user_input = get_input(msg)
            if not user_input and default:
                return default
            user_input = int(user_input)
            if ((not min_val or min_val <= user_input) and
                    (not max_val or max_val >= user_input)):
                return user_input
            print('{} must be between {} and {}.'.format(input_type, min_val, max_val))
        except ValueError:
            print('Not an integer.')
