import config
import bot_db

def parse_command(message, n_arguments=None):
    """
    Splits a message into its command's components. A command has the structure:

    ```
    !<name>[ <argument>]*
    ```

    So for example `!hello`, `!hello a` or `!hello a b`.

    If we know we only have `n_arguments`, we can collapse the superfluous arguments into one
    string. This is useful for example when we have `!add_tag hello Hello everyone!`. Parsing
    this with `n_arguments = 2` yields `['add_tag', 'hello', 'Hello everyone!']`.
    """
    splits = message[1:].split(' ')
    if len(splits) - 1 < n_arguments:
        raise ValueError(
            'Too few arguments. Expected {} and got {}.'.format(n_arguments, len(splits) - 1)
        )
    if n_arguments is None:
        return splits
    else:
        return splits[:n_arguments] + [' '.join(splits[n_arguments:])]

def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if len(a_set.intersection(b_set)) > 0:
        return(True)
    return(False)

def is_admin(user):
    if(common_member([r['name'] for r in bot_db.get_all_admin_roles()], [roles.name for roles in user.roles])):
        return(True)
    return(False)