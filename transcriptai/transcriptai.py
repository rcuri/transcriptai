import os
import openai
import json
import time
import pandas as pd
import tiktoken
from nba_api.stats.endpoints import playbyplayv2, boxscoresummaryv2
from nba_api.stats.static import teams
from typing import List, Dict


openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-3.5-turbo"


def get_play_by_play_events(game_id: str, period: int) -> List[Dict]:
    """
    Retrieve play-by-play data for a specific game using the nba_api module
    Clean up data and format it to provide the gpt model with accurate context
    """
    pbp_response = playbyplayv2.PlayByPlayV2(game_id)
    pbp_df = pbp_response.play_by_play.get_data_frame()
    # Score in play-by-play data is only included if the score has changed so we 
    # need to go through the dataframe and explicitly add the score if missing
    current_score = ""
    for index in pbp_df.index:
        if pbp_df.loc[index, 'SCORE'] != None:
            # Score has changed so we update current score
            current_score = pbp_df.loc[index, 'SCORE']
        elif pbp_df.loc[index, 'SCORE'] == None and \
                pbp_df.loc[index, 'PERIOD'] == 1 and \
                pbp_df.loc[index, 'EVENTMSGTYPE'] == 12:
            # Start of game
            pbp_df.loc[index, 'SCORE'] = "0-0"
            current_score = "0-0"
        elif pbp_df.loc[index, 'SCORE'] == None:
            # Score has not changed so we update with last recorded score
            pbp_df.loc[index, 'SCORE'] = current_score

    pbp_df = pbp_df[pbp_df['PERIOD'] == period]
    pbp_df['EVENTMSGTYPE'] = pbp_df['EVENTMSGTYPE'].map(lambda x: event_message_type_mapping(x))

    # Keep only columns we want and rename to more descriptive names
    columns = [
        "EVENTMSGTYPE", "PERIOD", "WCTIMESTRING", "PCTIMESTRING", 
        "HOMEDESCRIPTION", "NEUTRALDESCRIPTION", "VISITORDESCRIPTION", 
        "SCORE", "PLAYER1_NAME","PLAYER1_TEAM_NICKNAME", "PLAYER2_NAME", 
        "PLAYER2_TEAM_NICKNAME", "PLAYER3_NAME", "PLAYER3_TEAM_NICKNAME"
    ]
    column_map = {
        'EVENTMSGTYPE': 'event_type',
        'PERIOD': 'period',
        'WCTIMESTRING': 'live_time',
        'PCTIMESTRING': 'playclock_time',
        'HOMEDESCRIPTION': 'home_description',
        'VISITORDESCRIPTION': 'visitor_description',
        'NEUTRALDESCRIPTION': 'neutral_description',
        'SCORE': 'score',
        'PLAYER1_NAME': 'player1_name',
        'PLAYER1_TEAM_NICKNAME': 'player1_team',
        'PLAYER2_NAME': 'player2_name',
        'PLAYER2_TEAM_NICKNAME': 'player2_team',
        'PLAYER3_NAME': 'player3_name',
        'PLAYER3_TEAM_NICKNAME': 'player3_team'
    }    
    converted_df = pbp_df[columns].rename(columns=column_map)
    # Omit null values to save on token usage. Fields with possible null values 
    # are specified to model as optional
    events = [ {k:v for k,v in m.items() if pd.notnull(v)} for m in converted_df.to_dict(orient='records')]
    return events


def event_message_type_mapping(message_type: int) -> str:
    """
    Mapping to convert from NBA's format for event types to a human 
    (or AI lol) readable format
    """
    event_mapping = {
        1: "SCORING",
        2: "MISS",
        3: "FREE_THROW",
        4: "REBOUND",
        5: "TURNOVER",
        6: "FOUL",
        7: "VIOLATION",
        8: "SUBSTITUTION",
        9: "TIMEOUT",
        10: "JUMP_BALL",
        12: "START_OF_PERIOD",
        13: "END_OF_PERIOD",
        18: "INSTANT_REPLAY"
    }
    return event_mapping[message_type]


def get_matchup_data(game_id: str) -> Dict:
    """Get context for the game from NBA's box score endpoint"""
    box_score = boxscoresummaryv2.BoxScoreSummaryV2(game_id)
    bs_df = box_score.get_data_frames()[0]
    home_team_id = bs_df.iloc[0]['HOME_TEAM_ID']
    visitor_team_id = bs_df.iloc[0]['VISITOR_TEAM_ID']
    gamecode = bs_df.iloc[0]['GAMECODE'].replace("/", "")
    broadcasting_network = bs_df.iloc[0]['NATL_TV_BROADCASTER_ABBREVIATION']
    
    nba_teams = teams.get_teams()    
    home_team = [team for team in nba_teams if team['id'] == home_team_id]
    visitor_team = [team for team in nba_teams if team['id'] == visitor_team_id]

    matchup_data = {}
    matchup_data['gamecode'] = gamecode
    matchup_data['natl_tv_broadcaster'] = broadcasting_network
    matchup_data['home_team'] = {
        "city": home_team[0]['city'],
        "nickname": home_team[0]['nickname'],
        "abbreviation": home_team[0]['abbreviation']
    }
    matchup_data['visitor_team'] = {
        "city": visitor_team[0]['city'],
        "nickname": visitor_team[0]['nickname'],
        "abbreviation": visitor_team[0]['abbreviation']
    }    
    return matchup_data


def create_user_prompt(
        events: List[Dict], matchup_data: Dict, time_started: int) -> str:
    """
    Create the user prompt to send to GPT model using the template .txt file.
    Save prompt to .txt file
    """
    # load user template and replace variables with matchup data
    with open(os.path.join(os.path.dirname(__file__), "..",
            "message_template.txt"), "r") as f:
        prompt = f.read()   
    prompt_keys = {
        "home_city": matchup_data['home_team']['city'],
        "home_nickname": matchup_data['home_team']['nickname'],
        "home_abbreviation": matchup_data['home_team']['abbreviation'],
        "visitor_city": matchup_data['visitor_team']['city'],
        "visitor_nickname": matchup_data['visitor_team']['nickname'],
        "visitor_abbreviation": matchup_data['visitor_team']['abbreviation'],
        "natl_tv_broadcaster": matchup_data['natl_tv_broadcaster']
    }
    modified_prompt = prompt.format(**prompt_keys)

    # Add play-by-play events to user prompt until token limit reached
    acceptable_token_prompt = modified_prompt
    for pbp_event in events:
        for key, value in pbp_event.items():
            modified_prompt = modified_prompt + f"{key}: {value}\n"
        modified_prompt = modified_prompt + "\n"
        num_of_tokens = count_tokens_from_string(modified_prompt)
        if num_of_tokens < 2000:
            acceptable_token_prompt = modified_prompt
        else:
            break

    # Write user prompt to text file
    file_name = f"{time_started}_{matchup_data['gamecode']}_user_prompt.txt"
    with open(file_name, "w") as outfile:
        outfile.write(acceptable_token_prompt)    
    return acceptable_token_prompt


def count_tokens_from_string(string: str) -> int:
    """Counts tokens for a specified string"""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens    


def save_openai_output(
        gamecode: str, openai_response: Dict, time_started: int) -> None:
    """
    Write openai responses to text file. This includes the whole response
    returned by OpenAI model as well as the transcript generated by the model
    """
    # Convert whole response returned by openai to json and write to json file
    json_response_dict = json.dumps(openai_response)
    file_name = f"{time_started}_{gamecode}_transcript_openai_response.json"
    with open(file_name, "w") as outfile:
        outfile.write(json_response_dict)

    # Extract generated transcript and write to text file
    first_choice = openai_response['choices'][0]
    generated_transcript_text = first_choice['message']['content']
    file_name = f"{time_started}_{gamecode}_transcript.txt"
    with open(file_name, "w") as outfile:
        outfile.write(generated_transcript_text)     


def generate_transcript(
        game_id: str, period: int, model: str, temperature: float) -> Dict:
    """Generate the announcer's transcript for a period of a specific game"""
    time_started = int(time.time())
    events = get_play_by_play_events(game_id, period)
    team_data = get_matchup_data(game_id)
    user_prompt = create_user_prompt(events, team_data, time_started)
    
    with open(os.path.join(os.path.dirname(__file__), "..",
            "system_prompt.txt"), "r") as f:
        system_prompt = f.read()    
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    response_dict = response.to_dict_recursive()
    save_openai_output(team_data['gamecode'], response_dict, time_started)
    return response_dict


def main(
        game_id: str, period: int, model: str=DEFAULT_MODEL, 
        temperature: int=0.5):
    generate_transcript(game_id, period, model, temperature)
