class BotUtils():
    def __init__(self):
        self.RUDE_QA_CHAT_ID = -1001424452281

    @staticmethod
    def prepare_query(message):
        """
        Get message without command

        example: prepare_query("/getUser rudeboy from rude qa") -> returns "rudeboy from rude qa"
        """
        return ' '.join(message.text.split()[1:])

    @staticmethod
    def minutes_ending(count):
        last_digit = count % 10
        if last_digit == 0:
            ending = 'минуту'
        elif last_digit in range(1, 4):
            ending = 'минуты'
        else:
            ending = 'минут'
        return f'{count} {ending}'
