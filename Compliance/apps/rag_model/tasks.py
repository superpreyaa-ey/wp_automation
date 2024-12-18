from celery import shared_task
from time import sleep

from celery.signals import task_postrun


from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time


filename = 'celery_text.txt'
content = 'celery is working in python'

# Open the file in write mode and write the content


# @shared_task(bind=True)
# def my_task(self, seconds):
#     progress_recorder = ProgressRecorder(self)
#     result = 0
#     for i in range(seconds):
#         time.sleep(1)
#         result += i
#         progress_recorder.set_progress(i + 1, seconds)
#     return result

@shared_task
def go_to_sleep(tp):

    time.sleep(tp)
    print("Worker is working>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    return 'Done'

# @shared_task(bind=True)
# def test_func(filename, content):
#     try:
#         print(">>>>>>>>worker Test >>>>>>>>>>>>")
#         time.sleep(10)
#         print("Worker is working>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
#         with open(filename, 'w') as file:
#             file.write(content)
#         # self.logger.info(f"File '{filename}' has been created with the content: {content}")
#         return 'Done'
#     except Exception as e:
#         # self.logger.error(f"An error occurred: {e}")
#         print("????>>>>>>>>",e)
#         raise