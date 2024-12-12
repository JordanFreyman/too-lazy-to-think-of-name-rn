import datetime, time, random
class Islander:
    def __init__(self, name, aptNum, gender, age, height, hair=None, eyes=None, voice=None, sleeping_tonight=True):
        self.name = name
        self.aptNum = aptNum
        self.gender = gender
        self.age = age
        self.height = height
        self.hair = hair
        self.eyes = eyes
        self.voice = voice
        self.sleeping_tonight = sleeping_tonight  # Default value or loaded from DB

        self.bedtime = None
        self.waketime = None
        self.set_bedtime_waketime()

    def set_bedtime_waketime(self):
        # Set bedtime and waketime (doesn't randomize every time now)
        startbed_seconds = 21 * 3600 + 30 * 60  # 9:30 PM in seconds
        endbed_seconds = (1 + 24) * 3600 + 30 * 60  # 1:30 AM (next day) in seconds
        bed_rand_seconds = random.randint(startbed_seconds, endbed_seconds)
        self.bedtime = datetime.timedelta(seconds=bed_rand_seconds % (24 * 3600))  # Wrap to 24 hours

        start_seconds = 6 * 3600 + 30 * 60  # 6:30 AM in seconds
        end_seconds = 10 * 3600  # 10:00 AM in seconds
        rand_seconds = random.randint(start_seconds, end_seconds)
        self.waketime = datetime.timedelta(seconds=rand_seconds)

    def randomize_sleeping_tonight(self):
        """Randomize sleeping_tonight if certain conditions are met (e.g., time of day or game state)."""
        chances = random.randint(0, 4)
        if chances == 4:
            self.sleeping_tonight = False
