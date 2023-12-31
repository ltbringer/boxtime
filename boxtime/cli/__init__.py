from boxtime.cli.main_screen.box_time import BoxTime
from boxtime.db.schema import People, TaskType, EmotionLog


def main():
    People.create_table()
    TaskType.create_table()
    EmotionLog.create_table()
    app = BoxTime()
    app.run()
