import re, json

from random import randint

from decorators import db_session
from .users import is_admin_user
from models import Command
from models import RestrictedCommand
from models import RestrictedCommandGrant
from models import ConfigItem
from models import SmackPatrick
from models import ThrowJoey
from models import Blaymon
from models import HackThePlanet
from models import Shanty
from models import Stapler
from models import Weapoj
from models import User
from models import Ship
from models import Pirate
from models import PirateName
from models import Plank

from sprinkles import get_db_session

prefixes = [
    '~'
]
pfx = f"({'|'.join(prefixes)})"

__pirate_channel = 'CC06WLNA1'

def parse(message):
    if is_admin_user(message.get('user')):
        for c in commands:
            if c.enabled and c.pattern.match(message['text']):
                return c
    else:
        return None

def shutdown(message, command):
    return {'shutdown' : True}

@db_session
def new_blaymon(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_message = match.group(1)

    db_session.add(Blaymon(message=new_message))
    db_session.commit()

    return f"New potential response for !blaymon added: '{new_message}'"

@db_session
def new_hack_the_planet(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_message = match.group(1)

    db_session.add(HackThePlanet(message=new_message))
    db_session.commit()

    return f"New potential response for !hackThePlanet added: '{new_message}'"

@db_session
def new_stapler(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_message = match.group(1)

    db_session.add(Stapler(message=new_message))
    db_session.commit()

    return f"New potential response for !stapler added: '{new_message}'"

@db_session
def new_weapoj(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_message = match.group(1)

    db_session.add(Weapoj(message=new_message))
    db_session.commit()

    return f"New potential response for !weapoj added: '{new_message}'"

@db_session
def new_smack_patrick(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_message = match.group(1)

    db_session.add(SmackPatrick(message=new_message))
    db_session.commit()

    return f"New potential response for !smackPatrick added: '{new_message}'"

@db_session
def new_throw_joey(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_message = match.group(1)

    db_session.add(ThrowJoey(message=new_message))
    db_session.commit()

    return f"New potential response for !throwJoey added: '{new_message}'"

@db_session
def new_plank(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    new_template = match.group(1)

    if '{target_first_name}' in new_template or '{target_last_name}' in new_template:
        can_self_plank = True
    else:
        can_self_plank = False

    db_session.add(Plank(template=new_template, is_self_plank_compatible=can_self_plank))
    db_session.commit()

    return f"New template for !walkThePlank added: '{new_template}'"

@db_session
def new_shanty(message, command, db_session=None):
    match = command.pattern.match(message['text'])

    if match is not None:
        new_link = match.group(1)

        db_session.add(Shanty(link=new_link))
        db_session.commit()
        return f"New potential link for !shanty added: '{new_link}'"
    else:
        return "That's not a valid YouTube link!"

def reload_(message, command):
    return {'reload' : True}

def refresh_users_command(message, command):
    return {'refresh_users' : True}

def sort(db_session, user):
    new_pirate_info = Pirate()
    new_pirate_info.user = user
    new_pirate_info.user_id = user.user_id

    new_pirate_info.current_points = 0
    new_pirate_info.total_points = 0
    new_pirate_info.doubloons = 0
    new_pirate_info.times_planked = 0
    new_pirate_info.plank_sniper_charges = 0
    new_pirate_info.mutiny_charges = 0
    new_pirate_info.rum = 3
    new_pirate_info.enable_polly_cmd = False

    names = db_session.query(PirateName).filter(PirateName.pirate_id==None).all()
    name = names[randint(0, len(names) - 1)]
    name.pirate = new_pirate_info
    new_pirate_info.pirate_name_id = name.pirate_name_id

    ships = db_session.query(Ship).all()
    ship = ships[0]
    for s in ships:
        if len(s.pirates) <= len(ship.pirates):
            ship = s

    new_pirate_info.ship = ship
    new_pirate_info.ship_id = ship.ship_id

@db_session
def refresh_users(slack_client, db_session=None):
    print('Full user refresh requested, this might take a minute...')

    members = slack_client.api_call(
        'users.list'
    )
    members = members['members']

    members = [m for m in members if not m['is_bot'] and not m['is_app_user']]

    slack_users = []

    print("Beginning phase 1: Slack user retrieval")
    name_pattern = re.compile(r'([\w\-]+)\.([\w\-]+)')
    i = 0
    for member in members:
        id_ = member['id']
        name = member['name']
        deleted = member['deleted']
        email = member.get('profile')
        if email is not None:
            email = email.get('email')
        dm_channel = slack_client.api_call('im.open', user=id_)['channel']['id']

        existing_record = db_session.query(User).filter(User.slack_id==id_).first()
        if existing_record is None:
            existing_record = User()
            existing_record.slack_id = id_
            existing_record.in_pirate_channel = False
            db_session.add(existing_record)

        slack_users.append(existing_record)
        name_matcher = name_pattern.match(name)

        existing_record.email = email

        existing_record.is_deleted = deleted
        existing_record.dm_channel_id = dm_channel
        if name_matcher is not None:
            existing_record.slack_first_name = name_matcher.group(1).title()
            existing_record.slack_last_name = name_matcher.group(2).title()
            if not existing_record.display_first_name_locked:
                existing_record.display_first_name = name_matcher.group(1).title()
            if not existing_record.display_last_name_locked:
                existing_record.display_last_name = name_matcher.group(2).title()
        else:
            if not existing_record.display_last_name_locked:
                existing_record.display_last_name = name
            print(f'Error processing user with Slack ID {id_} and name {name}; manual processing may be required')

        i += 1
        if i % 25 is 0:
            print(f'{str(i).zfill(4)} Slack records processed...')
    print(f'{str(i).zfill(4)} total Slack records processed.')

    channel_member_ids = slack_client.api_call('channels.info', channel=__pirate_channel)
    channel_member_ids = channel_member_ids['channel']['members']
    print('Beginning phase 2: verifying channel membership...')
    for user in slack_users:
        user.in_pirate_channel = user.slack_id in channel_member_ids

    print('Beginning phase 3: verifying presence of pirate info')
    for user in [su for su in slack_users if su.in_pirate_channel]:
        if user.pirate_info is None:
            print(f'Sorting {user.display_first_name} {user.display_last_name}…')
            sort(db_session, user)
    print(f'Available pirate names remaining: {len(db_session.query(PirateName).filter(PirateName.pirate_id==None).all())}')

    db_session.commit()

    print('Full user refresh completed!')

def generate_help_docs(message, command):
    from . import council
    from . import general
    from . import restricted
    from . import dumb
    all_commands = []
    for module in [
        council,
        general,
        restricted,
        dumb
    ]:
        if hasattr(module, 'commands'):
            all_commands += module.commands

    all_commands += commands

    admin_commands = [c for c in all_commands if c._class.lower() == 'administration']
    council_commands = [c for c in all_commands if c._class.lower() == 'council']
    restricted_commands = [c for c in all_commands if c._class.lower() == 'restricted']
    general_commands = [c for c in all_commands if c._class.lower() == 'general']
    top_pirate_commands = [c for c in all_commands if c._class.lower() == 'top pirates']
    island_commands = [c for c in all_commands if c._class.lower() == 'island']
    captain_commands = [c for c in all_commands if c._class.lower() == 'captain']

    admin_commands.sort(key=lambda c: c.name)
    council_commands.sort(key=lambda c: c.name)
    restricted_commands.sort(key=lambda c: c.name)
    general_commands.sort(key=lambda c: c.name)
    top_pirate_commands.sort(key=lambda c: c.name)
    island_commands.sort(key=lambda c: c.name)
    captain_commands.sort(key=lambda c: c.name)

    help_document = []

    help_document += ['#General Commands#']
    help_document += [c.get_help() for c in general_commands]
    help_document += ['#Top Pirate Commands#']
    help_document += [c.get_help() for c in top_pirate_commands]
    help_document += ['#Island Commands#']
    help_document += [c.get_help() for c in island_commands]
    help_document += ['#Captain Commands#']
    help_document += [c.get_help() for c in captain_commands]
    help_document += ['#Restricted Commands#']
    help_document += [c.get_help() for c in restricted_commands]
    help_document += ['#Council Commands#']
    help_document += [c.get_help() for c in council_commands]
    help_document += ['#Administration Commands#']
    help_document += [c.get_help() for c in admin_commands]

    return "\n\n".join(help_document)

@db_session
def set_help_link(message, command, db_session=None):
    match = command.pattern.match(message['text'])

    if match is not None:
        new_link = match.group(1)

        config_item = db_session.query(ConfigItem).filter(ConfigItem.key=='help_link').first()
        if config_item is None:
            config_item = ConfigItem(key='help_link')
            db_session.add(config_item)

        config_item.value = new_link
        db_session.commit()
        return f"Help link set: '{new_link}'"

@db_session
def add_Restricted_Command_grant(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    first_name = match.group(1)
    last_name = match.group(2)
    restricted_command_key = match.group(3)

    restricted_command = db_session.query(RestrictedCommand).filter(RestrictedCommand.command_key==restricted_command_key).first()
    if restricted_command is None:
        restricted_command = RestrictedCommand(command_key=restricted_command_key)
        db_session.add(restricted_command)

    user = db_session.query(User).filter(User.slack_first_name==first_name).filter(User.slack_last_name==last_name).first()
    if user is None:
        return f'No user found, please check your spelling: {first_name} {last_name}'

    for grant in user.restricted_command_grants:
        if grant.command.command_key == restricted_command_key:
            return f'{first_name} {last_name} already has access to that command.'

    user.restricted_command_grants.append(RestrictedCommandGrant(user_id=user.user_id, restricted_command_id=restricted_command.restricted_command_id))
    db_session.commit()
    return f'{first_name} {last_name} granted access to {restricted_command_key}.'

@db_session
def remove_Restricted_Command_grant(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    first_name = match.group(1)
    last_name = match.group(2)
    restricted_command_key = match.group(3)

    restricted_command = db_session.query(RestrictedCommand).filter().first()
    if restricted_command is None:
        return f'No restricted command with key \'{restricted_command_key}\' found.'

    user = db_session.query(User).filter(User.slack_first_name==first_name).filter(User.slack_last_name==last_name).first()
    if user is None:
        return f'No user found, please check your spelling: {first_name} {last_name}'

    for grant in user.restricted_command_grants:
        if grant.command.command_key == restricted_command_key:
            db_session.delete(grant)
            db_session.commit()
            return f'Access to {restricted_command_key} has been revoked for {first_name} {last_name}.'

    return f'{first_name} {last_name} doesn\'t have permission to {restricted_command_key}.'

@db_session
def list_restricted_command_keys(message, command, db_session=None):
    restricted_commands = db_session.query(RestrictedCommand).all()
    return '\n'.join(['Here are all the restricted command keys:'] + [rc.command_key for rc in restricted_commands])

@db_session
def dump_user(message, command, db_session=None):
    match = command.pattern.match(message['text'])
    name = [match.group(1), match.group(2)]
    user = db_session.query(User).filter(User.slack_first_name==name[0]).filter(User.slack_last_name==name[1]).first()
    return str(user)

def bulk_commands(message, command):
    from sprinkles import handle_message

    match = command.pattern.match(message['text'])
    bulk_command_set = match.group(1)

    user = message['user']
    channel = message['channel']
    for command in [x.strip() for x in bulk_command_set.split('\n')]:
        print(f'Bulk command: \'{command}\'')
        handle_message({'text' : command, 'user' : user, 'channel' : channel})

    return "Bulk commands executed."

commands = [
    Command(
        pattern=r'^(?i)~newBlaymon (.+)$',
        method=new_blaymon,
        threaded=False,
        enabled=True,
        name='Add New Blaymon Message',
        syntax='~newBlaymon message',
        description='Adds a new potential response for !blaymon.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newHackThePlanet (.+)$',
        method=new_hack_the_planet,
        threaded=False,
        enabled=True,
        name='Add New "Hackers" Quote',
        syntax='~newHackThePlanet quote',
        description='Adds a new potential response for !hackThePlanet.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newStapler (.+)$',
        method=new_stapler,
        threaded=False,
        enabled=True,
        name='Add New "Office Space" Quote',
        syntax='~newStapler quote',
        description='Adds a new potential response for !stapler.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newWeapoj (.+)$',
        method=new_weapoj,
        threaded=False,
        enabled=True,
        name='Add New Weapoj Message',
        syntax='~newWeapoj message',
        description='Adds a new way to make fun of Josh\'s spelling.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newPlank (.+)$',
        method=new_plank,
        threaded=False,
        enabled=True,
        name='Add New "Walk the Plank" Message',
        syntax='~newPlank message',
        description='Adds a new potential response for !walkThePlank.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newShanty (.+)$',
        method=new_shanty,
        threaded=False,
        enabled=True,
        name='Add New Shanty',
        syntax='~newShanty link',
        description='Adds a new potential response video for !shanty.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newSmackPatrick (.+)$',
        method=new_smack_patrick,
        threaded=False,
        enabled=True,
        name='Add New Smack Patrick',
        syntax='~newSmackPatrick message',
        description='Adds a new potential response video for !smackPatrick.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~newThrowJoey (.+)$',
        method=new_throw_joey,
        threaded=False,
        enabled=True,
        name='Add New Throw Joey',
        syntax='~newThrowJoey message',
        description='Adds a new potential response video for !throwJoey.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~shutdown$',
        method=shutdown,
        threaded=False,
        enabled=True,
        name='Shutdown',
        syntax='~shutdown',
        description='Gracefully shuts Sprinkles down.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~exit$',
        method=shutdown,
        threaded=False,
        enabled=True,
        name='Exit',
        syntax='~exit',
        description='Gracefully shuts Sprinkles down.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~reload$',
        method=reload_,
        threaded=False,
        enabled=True,
        name='Reload',
        syntax='~reload',
        description='Reloads all available command modules.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~refreshUsers$',
        method=refresh_users_command,
        threaded=False,
        enabled=True,
        name='Refresh Users',
        syntax='~refreshUsers',
        description='Invokes a full user refresh from Slack.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~generateHelpDocs$',
        method=generate_help_docs,
        threaded=False,
        snippet=True,
        enabled=True,
        name='Generate Help Docs',
        syntax='~generateHelpDocs',
        description='Generates this help document for Sprinkles.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~setHelpLink (.+)$',
        method=set_help_link,
        threaded=False,
        snippet=False,
        enabled=True,
        name='Set Help Link',
        syntax='~setHelpLink link',
        description='Sets the link provided when !help is used',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~addRestrictedCommandGrant (.+) (.+) (.+)$',
        method=add_Restricted_Command_grant,
        threaded=False,
        snippet=False,
        enabled=True,
        name='Add Restricted Command Grant For User',
        syntax='~addRestrictedCommandGrant  firstName lastName command',
        description='Grants a user the ability to perform the given restricted command',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~removeRestrictedCommandGrant (.+) (.+) (.+)$',
        method=remove_Restricted_Command_grant,
        threaded=False,
        snippet=False,
        enabled=True,
        name='Remove Restricted Command Grant For User',
        syntax='~removeRestrictedCommandGrant firstName lastName command',
        description='Removes a user\'s ability to perform the given restricted command',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~listRestrictedCommandKeys$',
        method=list_restricted_command_keys,
        threaded=True,
        snippet=False,
        enabled=True,
        name='List Restricted Command Keys',
        syntax='~listRestrictedCommandKeys',
        description='Lists all stored keys for  restricted commands.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?i)~dumpUser (.+) (.+)$',
        method=dump_user,
        threaded=False,
        snippet=False,
        enabled=True,
        name='Dump User Info',
        syntax='~dumpUser firstName lastName',
        description='Dumps all information stored about a user.',
        _class='Administration'
    ),
    Command(
        pattern=r'^(?si)~bulkCommands(.+)$',
        method=bulk_commands,
        threaded=False,
        enabled=True,
        name='Bulk Command Entry',
        syntax='~bulkCommands\n!command1\n!command2\n...',
        description='Allows for bulk command entry, one command per line.',
        _class='Administration'
    )
]
