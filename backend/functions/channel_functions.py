from .data import *


def channels_create(token, name, is_public):
    #if not is_logged_in(token):
    #    return f"User: {decode_token(token)} not logged in"
    if len(name) > 20:
        return "Name of channel is longer than 20 characters."
    data = get_data()
    owner_id = decode_token(token)
    print(owner_id)
    get_user_name(owner_id)
    print(f"owner's name is: {get_user_name(owner_id)}")

    # Give the channel an ID which corresponds to the number created e.g. 1st channel is ID1 ...
    new_channel_id = len(data['channels']) + 1
    # Create a dictionary with all the relevant info and append to data
    dict = {
        'channel_id': new_channel_id,
        'name': name,
        'owner_members': [{
            'u_id': owner_id,
            'name_first': get_first_name(owner_id),
            'name_last': get_last_name(owner_id)
        }],
        'all_members': [{
            'u_id': owner_id,
            'name_first': get_first_name(owner_id),
            'name_last': get_last_name(owner_id)
        }],
        'is_public': is_public,
        'messages': []
    }
    data['channels'].append(dict)
    print(data['channels'])
    return {
        'channel_id': new_channel_id
    }

# Provide a list of all channels (and their associated details)
def channels_listall(token):
    #if not is_logged_in(token):
    #    return f"User: {decode_token(token)} is not logged in"
    data = get_data()
    channels_list = []
    for channels in data['channels']:
        dict = {}
        dict.update({
            'channel_id': channels['channel_id'], 'name': channels['name']
        })
        channels_list.append(dict)
    return channels_list

# Return a list of channels the user has already joined or is a owner of
def channels_list(token):
    #if not is_logged_in(token):
    #    return f"User: {decode_token(token)} is not logged in"

    data = get_data()
    u_id = decode_token(token)
    channels_list = []
    for channels in data['channels']:
        if is_member(u_id, channels['channel_id']) or is_owner(u_id, channels['channel_id']):
            channels_list.append({
                'channel_id': channels['channel_id'],
                'name': channels['name']
            })
    return channels_list


def channel_leave(token, channel_id):
    if not is_logged_in(token):
        return f"User: {decode_token(token)} is not logged in"
    if not is_joined(token, channel_id):
        return f"User: {decode_token(token)} has not joined channel: {channel_id} yet"
    if not is_valid_channel(channel_id):
        return f"Channel ID: {channel_id} is invalid"

    channel = channel_dict(channel_id)
    u_id = decode_token(token)
    # loop through owner_members
    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            channel['owner_members'].remove(member)
    # loop through members
    for member in channel['all_members']:
        if member['u_id'] == u_id:
            channel['all_members'].remove(member)
    return {}

def channel_addowner(token, channel_id, u_id):
    if not is_logged_in(token):
        return f"User: {decode_token(token)} is not logged in"
    #if not is_logged_in(generate_token(u_id)):
    #    return ff"User: {u_id} is not logged in"
    if not is_valid_channel(channel_id):
        return f"Channel ID: {channel_id} is invalid"
    if is_owner(u_id, channel_id):
        return f"User: {u_id} is already an owner"
    if not is_owner(decode_token(token), channel_id):
        return f"User: {decode_token(token)} does not have privileges to promote others"

    channel = channel_dict(channel_id)
    name_first = get_first_name(u_id)
    name_last = get_last_name(u_id)
    # append user to list of owners
    channel['owner_members'].append({
        'u_id' : u_id,
        'name_first' : name_first,
        'name_last' : name_last
    })

    return {}


def channel_removeowner(token, channel_id, u_id):
    if not is_logged_in(token):
        return f"User: {decode_token(token)} is not logged in"
    #if not is_logged_in(generate_token(u_id)):
    #    return ff"User: {u_id} is not logged in"
    if not is_valid_channel(channel_id):
        return f"Channel ID: {channel_id} is invalid"
    if not is_owner(u_id, channel_id):
        return f"User: {u_id} is not an owner"
    if not is_owner(decode_token(token), channel_id):
        return f"User: {decode_token(token)} does not have privileges to demote others"

    channel = channel_dict(channel_id)

    for member in channel['owner_members']:
        if u_id == member['u_id']:
            channel['owner_members'].remove(member)
            break
    # remove user from list of owners
    

    return {}

def channel_invite(token, channel_id, u_id):
    inviter_u_id = decode_token(token)
    user = user_dict(u_id)
    if u_id == inviter_u_id:
        return 'cannot invite self'

    channel = channel_dict(channel_id)
    if channel == None:
        return 'channel id does not exist'

    for member in channel['all_members']:
        if member['u_id'] == u_id:
            return 'user already part of channel'

    invitee_token = user['tokens'][0]
    channel_join(invitee_token, channel_id)

    return {}


def channel_join(token, channel_id):
    u_id = decode_token(token)

    channel = channel_dict(channel_id)
    user = user_dict(u_id)
    if user == None or channel == None:
        return 'channel id/ user id does not exist'

    if user['permission_id'] != 3:
        channel['owner_members'].append({
            'u_id' : u_id,
            'name_first' : user['name_first'],
            'name_last' : user['name_last']
        })
    elif user['permission_id'] == 3 and channel['is_public'] == True:
        channel['all_members'].append({
            'u_id' : u_id,
            'name_first' : user['name_first'],
            'name_last' : user['name_last']
        })
    else:
        return 'user does not have rights'

    return {}

def channel_details(token, channel_id):
    channel = channel_dict(channel_id)
    if channel == None:
        return "channel id does not exist"

    u_id = decode_token(token)
    if is_member(u_id, channel_id) is False:
        return "authorised user not member of channel"
    
    details = {
        'name' : channel['name'],
        'owner_members' : channel['owner_members'],
        'all_members' : channel['all_members']
    }

def get_user_name(u_id):
    data = get_data()
    for user in data['users']:
        if u_id == user['u_id']:
            return {user['name_first'], user['name_last']}
    return None
