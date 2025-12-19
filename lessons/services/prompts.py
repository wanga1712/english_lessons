from lessons.services.prompts_single import get_system_prompt, get_user_prompt_with_repetition
from lessons.services.prompts_analysis import get_analysis_system_prompt, get_analysis_user_prompt
from lessons.services.prompts_generation import get_card_generation_system_prompt, get_card_generation_user_prompt

__all__ = [
    'get_system_prompt',
    'get_user_prompt_with_repetition',
    'get_analysis_system_prompt',
    'get_analysis_user_prompt',
    'get_card_generation_system_prompt',
    'get_card_generation_user_prompt',
]
