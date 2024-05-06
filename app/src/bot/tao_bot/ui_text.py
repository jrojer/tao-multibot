import re

from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.gpt.gpt_conf import GptConf

SET_TEMPERATURE = 'st'
SET_TOP_P = "stp"
SET_MAX_TOKENS = "smt"
SET_PRESENCE_PENALTY = "spp"
SET_FREQUENCY_PENALTY = "sfp"
CONFIG = "cfg"
START_MESSAGE = rf"TAO online 🟢 -> /{CONFIG}"
START = "start"
ENABLE_IN_CURRENT_GROUP = '1'
DISASBLE_IN_CURRENT_GROUP = '0'
UPDATE_ACCESS = 'access'
SET_NUMBER_OF_MESSAGES_PER_COMPLETION = 'snmfc'

def _escape_markdown(text):
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

def cfg_message(tao_bot_conf: TaoBotConf, gpt_conf: GptConf):
    bot_name = _escape_markdown(tao_bot_conf.username())
    return f'''
`model: {gpt_conf.model()}` 
`max_tokens:        {gpt_conf.max_tokens()}` /{SET_MAX_TOKENS}@{bot_name}
`temperature:       {gpt_conf.temperature()}` /{SET_TEMPERATURE}@{bot_name}
`top_p:             {gpt_conf.top_p()}` /{SET_TOP_P}@{bot_name}
`presence_penalty:  {gpt_conf.presence_penalty()}` /{SET_PRESENCE_PENALTY}@{bot_name}
`frequency_penalty: {gpt_conf.frequency_penalty()}` /{SET_FREQUENCY_PENALTY}@{bot_name}

`number_of_messages_per_completion: {tao_bot_conf.number_of_messages_per_completion()}` /{SET_NUMBER_OF_MESSAGES_PER_COMPLETION}@{bot_name}

/{CONFIG}@{bot_name}
'''
