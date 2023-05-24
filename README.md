# TranscriptAI

## About
If you're like me and can't get enough of Kevin Harlan and Reggie Miller then you've come to the right place. Generate a transcript for any NBA game using play-by-play data from one of the NBA's stats endpoints. 

## Setup
    python3 -m venv transcriptai
    source venv/bin/activate
    pip install -r requirements.txt

## Example Usage
To run with the default model (gpt-3.5-turbo), pass in the game ID and the period you'd like to generate a transcript for:

    python -m transcriptai --game_id 0042200211 --period 1

If you want to change the temperature:

    python -m transcriptai --game_id 0042200211 --period 1 --temperature 0

To change the model:

    python -m transcriptai --game_id 0042200211 --period 1 --model gpt-4

## Sample Output
An example of a transcript produced for the following values:

    game_id=0042200211
    period=1
    temperature=0
    model=gpt-3.5-turbo

### Output

> [0:00] Kevin Harlan: And we're underway here in Boston as the Celtics host the 76ers.

> [0:26] Reggie Miller: It's always exciting to see two Eastern Conference powerhouses go head to head.

> [0:40] Kevin Harlan: Horford and Reed at center court for the jump ball.

> [0:49] Reggie Miller: And it's Harden who comes up with the ball.

> [1:02] Kevin Harlan: Harden with a quick 10-foot step back jumper and the 76ers are on the board.

> [1:12] Reggie Miller: Harden is such a scoring threat from anywhere on the court.

> [1:22] Kevin Harlan: Tatum with a nice cut to the basket and Smart finds him for the easy dunk.

> [1:33] Reggie Miller: That was a great pass by Smart, he's always looking to make his teammates better.

> [1:44] Kevin Harlan: Maxey with a miss from beyond the arc.

> [1:51] Reggie Miller: Maxey has been struggling with his shot lately, he's going to need to find his rhythm soon.

> [2:03] Kevin Harlan: Tatum with the rebound and the Celtics are back on the attack.

> [2:12] Reggie Miller: Tatum is a great two-way player, he can score and defend with the best of them.

> [2:23] Kevin Harlan: Horford with a nice cut to the basket and Brown finds him for the layup.

> [2:34] Reggie Miller: The Celtics are doing a great job of moving without the ball and finding the open man.

> [2:46] Kevin Harlan: Reed with a driving layup but Horford with the block!

> [2:55] Reggie Miller: Horford is one of the best defensive big men in the league, he's always a threat to block shots.


## Roadmap
* Transcribe full games where Kevin Harlan and Reggie Miller were the announcers and use this data to fine-tune model. Maybe categorize by 'EVENTMSGTYPE' 
* Migrate to fine-tune model
* Generate transcript for complete NBA game and not just specific periods
* Add support for getting play-by-play data from different sources e.g. CSV, JSON
* Add support for different commentators. I mainly want to focus on Kevin Harlan and Reggie Miller right now and then move on to allowing different people to be announcers, including non-NBA personalities

