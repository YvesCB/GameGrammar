import json
import requests


class TwitchException(Error):
    """Raised when there is an error in the TwitchAPI Wrapper"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Wrapper():
    def __init__(self, client_id, oauth2_token, gg_id):
        self.Headers = {
                'Authorization': oauth2_token,
                'Client-Id': client_id,
                'Content-Type': 'application/json'
                }
        self.all_scopes = ['analytics:read:extensions', 'analytics:read:games', 'bits:read', 'channel:edit:commercial', 'channel:manage:broadcast', 'channel:manage:extensions', 'channel:manage:polls', 'channel:manage:predictions', 'channel:manage:redemptions', 'channel:manage:videos', 'channel:read:editors', 'channel:read:predictions', 'channel:read:redemptions', 'channel:read:stream_key', 'channel:read:subscriptions', 'clips:edit', 'moderation:read', 'moderator:manage:automod', 'user:edit', 'user:edit:follows', 'user:manage:blocked_users', 'user:read:blocked_users', 'user:read:broadcast', 'user:read:follows', 'user:read:subscriptions', 'channel:moderate', 'chat:edit']
        self.gg_id = gg_id
        

    def refresh_headers(self, oauth2_token, client_id):
        self.Headers['Authorization'] = oauth2_token
        self.Headers['Client-Id'] = client_id


    # Authorization
    """
    Returns the URL needed to authorize the bot.
    """
    def get_auth_url(self, scope):
        if scope == 'all':
            scopes = ' '.join(self.all_scopes)
        else:
            scopes = ' '.join(scope)

        return f'https://id.twitch.tv/oauth2/authorize?client_id={self.Headers["Client-Id"]}&redirect_uri=https://localhost&response_type=code&scope={scopes}'


    """
    Returns the data required to authorize the bot with the TwichAPI.

    Requires the code one gets from get_auth_url.

    Returns:
        {
          "access_token": String,
          "refresh_token": String,
          "expires_in": int (Seconds),
          "scope": list of Strings,
          "token_type": "bearer"
        }
    """
    def get_oauth2_token(self, code, client_secret):
        params = {
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://localhost'
                }
        data = requests.post(f'https://id.twitch.tv/oauth2/token', params=params)

        return data.status_code, json.loads(data.text)


    """
    Requires a Refresh Token and a Client-Secret.

    Returns the refreshed OAuth2 Token by using the Refresh Token.

        {
          "access_token": String,
          "refresh_token": String,
          "expires_in": int (Seconds),
          "token_type": "bearer"
        }
    """
    def refresh_oauth2_token(self, refresh_token, client_secret):
        params = {
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'client_secret': client_secret
                }
        data = requests.post(f'https://id.twitch.tv/oauth2/token', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Runs a commercial on the channel. 

    Requires the lenght. Valid lengths are 30, 60, 90, 120, 150, 180. Default is 30s.
    Requires the channel:edit:commercial scope

    https://dev.twitch.tv/docs/api/reference#start-commercial
    """
    def run_commercial(self, length=30):
        params = {
                'broadcaster_id': self.gg_id,
                'lenght': lenght
                }
        data = requests.post(f'https://api.twitch.tv/helix/channels/commercial', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Get the Bits Leaderboard.

    Requires bits:read scope. 

    Optional parameters:
        count:      Number of returned results (Max: 100, Default: 10)
        period:     Time period, interacts with started_at. Options:
                    "day", "week", "month", "year", "all". Default: "all"
        started_at: Timestamp for when the period should start. Must be in RFC 3339 format.
        user_id:    ID of th user whose results are returned; i.e., the person who paid for the Bits

        https://dev.twitch.tv/docs/api/reference#get-bits-leaderboard
    """
    def get_bits_leaderboard(self, count=10, period='all', started_at=None, user_id=None):
        params = {
                'count': count,
                'period': period
                }

        if started_at is not None:
            params['started_at'] = started_at
        if user_id is not None:
            params['user_id'] = user_id

        data = requests.get(f'https://api.twitch.tv/helix/bits/leaderboard', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Gets channel information for users.

    Requires the ID of the user. Default is the on of the GameGrammar channel.

    https://dev.twitch.tv/docs/api/reference#get-channel-information
    """
    def get_channel_info(self, broadcaster_id=None):
        params = {
                'broadcaster_id': broadcaster_id
                }
        if broadcaster_id is None:
            params['broadcaster_id'] = self.gg_id

        data = requests.get(f'https://api.twitch.tv/helix/channels', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Update the channel information. 

    Requires the ID of the user and the channel:manage:broadcast scope.

    Optional parameters:
        game_id:                The ID of the game being played. 0 to "unset"
        broadcaster_langauge:   The language of the channel. ISO 639-1 two-letter code or "other".
        title:                  Title of the stream.
        delay:                  Stream delay in seconds. Partner feature

    https://dev.twitch.tv/docs/api/reference#get-channel-information
    """
    def set_channel_info(self, broadcaster_id=None, game_id=None, broadcaster_langauge=None, title=None, delay=None):
        params = {
                'broadcaster_id': broadcaster_id
                }
        if broadcaster_id is None:
            params['broadcaster_id'] = self.gg_id

        if game_id is not None:
            params['game_id'] = game_id
        if broadcaster_langauge is not None:
            params['broadcaster_langauge'] = broadcaster_langauge
        if title is not None:
            params['title'] = title
        if delay is not None:
            params['delay'] = delay

        data = requests.patch(f'https://api.twitch.tv/helix/channels', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Create a clip. Clip creation takes some time. It is recommende to query Get Clips with
    the ID that was retured to check if a clip was created successfully.

    Requires the broadcaster_id and the clips:edit scope.

    https://dev.twitch.tv/docs/api/reference#create-clip
    """
    def create_clip(self, broadcaster_id=None, has_delay=False):
        params = {
                'broadcaster_id': broadcaster_id,
                'has_delay': has_delay
                }
        if broadcaster_id is None:
            params['broadcaster_id'] = self.gg_id

        data = requests.post(f'https://api.twitch.tv/helix/channels', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Get Clips by ID. Can return one or more.

    Requires the broadcaster_id, the game_id or the clip id. At least one or more need to be specified.

    Optional parameters:
        "after":        Cursor for pagination
        "before":       Cursor for backwards pagination
        "ended_at":     End date for returned clips
        "started_at":   Start date for returned clips   
        "first":        Max number of objects to return. Max:100, Default:20

    https://dev.twitch.tv/docs/api/reference#get-clips
    """
    def get_clips(self, broadcaster_id=None, game_id=None, clip_id=None, after=None, before=None, ended_at=None, started_at=None, first=20):
        params = {
                'broadcaster_id': broadcaster_id,
                'first': first
                }
        if broadcaster_id is None:
            params['broadcaster_id'] = self.gg_id
        if game_id is not None:
            params['game_id'] = game_id
        if clip_id is not None:
            params['clip_id'] = clip_id
        if after is not None:
            params['after'] = after
        if before is not None:
            params['before'] = before
        if ended_at is not None:
            params['ended_at'] = ended_at
        if started_at is not None:
            params['started_at'] = started_at

        data = requests.get(f'https://api.twitch.tv/helix/channels', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)



    """
    Get list of games on Twitch sorted by current view count.

    Optional parameters:
        "after":        Cursor for pagination
        "before":       Cursor for backwards pagination
        "first":        Max number of objects to return. Max: 100, Default:20

    https://dev.twitch.tv/docs/api/reference#get-top-games
    """
    def get_top_games(self, after=None, before=None, first=20):
        params = {
            "first": first
        }
    if after is not None:
            params['after'] = after
        if before is not None:
            params['before'] = before

        data = requests.get(f'https://api.twitch.tv/helix/games/top', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Gets game information by game ID or name

    Requires an ID and/or a name

    https://dev.twitch.tv/docs/api/reference#get-games
    """
    def get_games(self, game_id=None, game_name=None):
        params = {}
        if game_id is not None:
            params['id'] = game_id
        if game_name is not None:
            params['name'] = game_name

        if game_id is None and game_name is None:
            raise TwitchException('At least one out of the values: game_id, game_name need to be specified!')

        data = requests.get(f'https://api.twitch.tv/helix/games', params=params, headers=self.Headers)
        
        return data.status_code, json.loads(data.text)


    """
    Get channel stream schedule for a given channel

    Requires OAuth Token and broadcaster_id

    Optional parameters:
        "id":           The ID of the stream segment to return
        "start_time":   A timestamp in RFC3339 format to start returning stream segments from. Default: Current datetime
        "utc_offset":   Timezone offset in minutes
        "first":        Max number of stream segments to return. Max: 25, Default: 20
        "after":        Cursor for pagination

    https://dev.twitch.tv/docs/api/reference#get-channel-stream-schedule
    """
    def get_channel_schedule(self, broadcaster_id, segment_id=None, start_time=None, utc_offset=None, first=20, after=None):
        params = {
            'broadcaster_id' = broadcaster_id
            'first' = first
        }
        if segment_id is not None:
            params['id'] = segment_id
        if start_time is not None:
            params['start_time'] = start_time
        if utc_offset is not None:
            params['utc_offset'] = utc_offset
        if after is not None:
            params['after'] = after

        data = requests.get(f'https://api.twitch.tv/helix/schedule', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    """
    Search categories returns a list of games or cateogires that match the query via name

    Requires a query

    Optional parameters:
        "first":        Max number of objects to return. Max. 100, Default: 20
        "after":        Cursfor for forward pagination

    https://dev.twitch.tv/docs/api/reference#search-categories
    """
    def search_categories(self, query, first=20, after=None):
        params = {
                'query': query
                'first': first
                }
        if after is not None:
            params['after'] = after

        data = requests.get(f'https://api.twitch.tv/helix/search/categories ', params=params, headers=self.Headers)

        return data.status_code, json.loads(data.text)


    
