from audioop import reverse
import logging
import os
from xmlrpc.client import boolean
from telegram import *
from telegram.ext import *
from threading import Timer
import pyrebase

PORT = int(os.environ.get('PORT', 5000))

firebaseConfig = {'apiKey': "AIzaSyAs9HemS9WTckbxSofzQvH0_B6SgKKtTfQ",
  'authDomain': "nerdhelperr.firebaseapp.com",
  'databaseURL': "https://nerdhelperr-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "nerdhelperr",
  'storageBucket': "nerdhelperr.appspot.com",
  'messagingSenderId': "502568196964",
  'appId': "1:502568196964:web:7793a70c695e1c98367871",
  'measurementId': "G-1MDH1DBETP"}
firebase=pyrebase.initialize_app(firebaseConfig)


# enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# global variables
TOKEN = os.environ['TELETOKEN']
db=firebase.database()
todo_dictionary = {"default": "To-do List:"}
boolean_dictionary = {}
boolean_messagedict = {}
chatid = 0
task_name = ''
UpdatableNumber = 0
timerObject = Timer


def start_command(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    name = user['first_name']
    update.message.reply_text(
        f'Hi {name}!, use me as a to-do list for your tasks! ' +
        'To get started, use /addtask followed by the name of your task to add a new task to your list, and ' +
        '/list to view your current list.\n' +
        '/starttimer to start a customisable timer.\n\n'
        'Do go to /help to look at how to use the other commands!'
    )


def help_command(update: Update, _:CallbackContext) -> None:
  update.message.reply_text('This bot is basically a to-do list for your tasks, implemented with a priority system! Commands:\n' +
        '/start to start the bot\n\n' 
        '/addtask followed by your task to add your new task\n\n' + 
        '/donetask followed by the number of that task on the list to remove that task.\n\n' + 
        '/list to view your current to-do list\n\n' + 
        '/newlist to delete your current list and start a new one\n\n' +
        '/reminder to set a reminder for a specific task at a specific date \n\n'
        '/starttimer to start a customisable timer\n' +
        '- this is just a regular timer that will send a message when the timer is up!\n' +
        '- according to the Pomodoro technique, the recommended timer for doing a task is 25 minutes per session! For more information on this technique, please go to https://todoist.com/productivity-methods/pomodoro-technique \n\n' +
        '/help to look at the bot commands again!'
  )


def show_list(update: Update, context:CallbackContext) -> None:
  # update chat id
  chatid = update.message.chat.id
  user = db.child('tasklist').child(f'{chatid}').get()

  if user.val() != None:
    str = 'To-do List:\n'
    index = 1
    todo_list = []
    for task in user.each():
      todo_list.append((task.val().get('priority'), task.val().get('task')))
    
    todo_list.sort(reverse=False)

    for i in range (0, len(todo_list)):
      str += f'{index}. ' + f'{todo_list[i][1]}\n'
      index += 1
    update.message.reply_text(f'{str}')
    
  else:
    boolean_dictionary[chatid] = True
    update.message.reply_text("To-do List:")


def add_task(update: Update, context:CallbackContext):
  text = update.message.text
  task_arr = text.split(' ')[1:]

  if len(task_arr) < 1:
    # show error message if no words are after the command
    update.message.reply_text('Add your task again by typing /addtask followed by the name of the task in the same message!')
  else:
    # get the intended task to add as a string stored in task_str
    task_str = ''
    for i in range (len(task_arr)):
      task_str += f'{task_arr[i]} '
  
    # update chat id and task name
    global task_name, chatid
    chatid = update.message.chat.id
    boolean_dictionary[chatid] = True
    task_name = f'{task_str}'

    buttons = [[InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="1")], [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="2")], 
    [InlineKeyboardButton("⭐⭐⭐", callback_data="3")], [InlineKeyboardButton("⭐⭐", callback_data="4")], 
    [InlineKeyboardButton("⭐", callback_data="5")], [InlineKeyboardButton("None", callback_data="6")]]
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="What is the priority of this task?")


def done_task(update: Update, context:CallbackContext) -> None:
  text = update.message.text
  numbers = text.split(' ')[1:]
  number = int(numbers[0])

  if len(numbers) == 1  and isinstance(number, int):
    # update chat id
    chatid = update.message.chat.id

    # remove the task from the list
    user = db.child('tasklist').child(f'{chatid}').get()
    if user.val() != None:
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      deletevalue = ''
      if 0 <= number <= len(todo_list):
        index = number - 1
        deletevalue = todo_list[index][1]

        deletekey = ''
        for task in user.each():
          if task.val().get('task') == deletevalue:
            deletekey = task.key()
            db.child('tasklist').child(f'{chatid}').child(deletekey).remove()

        # show the updated list
        return show_list(update, context)
        
      else:
        update.message.reply_text('Put in a valid task number!')

    else:
       update.message.reply_text('Your list is empty!')

  else:
    update.message.reply_text('Remove your task again by typing /donetask followed by the number of the task it corresponds to!')



def create_new(update: Update, context:CallbackContext):
  chatid = update.message.chat.id
  boolean_dictionary[chatid] = True
  buttons = [[InlineKeyboardButton("Yes 👍🏽", callback_data="yes")], [InlineKeyboardButton("No 👎🏽", callback_data="no")]]
  context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Are you sure?")


def start_timer(update: Update, context: CallbackContext):
  text = update.message.text
  num_arr = text.split(' ')[1:]
  # check if there is any input
  if len(num_arr) < 1:
    update.message.reply_text(
      'Please input a number after /starttimer to set a timer of that specific number of minutes!')
  else:
    try:
      # check if text entry is valid
      num_arr = int(num_arr[0])
    except ValueError:
      update.message.reply_text('Please input a valid number for the timer')
    else:
      global timerObject
      timer = int(num_arr) * 60
      update.message.reply_text(f'⏰ Timer of {int(num_arr)} mins started! Stay focused! ⏰')
      timerObject = Timer(timer, timer_done, [update])
      timerObject.start()


def timer_done(update: Update):
  update.message.reply_text('🚨 Timer has ended! 🚨')


def end_timer(update: Update, context: CallbackContext):
  global timerObject
  timerObject.cancel()
  update.message.reply_text('❗️ Timer cancelled! ❗️')


def reminder_command(update: Update, context: CallbackContext):
  text = update.message.text
  numbers = text.split(' ')[1:]

  if len(numbers) != 1:
    # show error message if there is more or less than 1 number after the command
    update.message.reply_text('Select your task for reminder again by typing /reminder followed by the number of the task it corresponds to!')
  else:
    # update chat id
    chatid = update.message.chat.id

    # access todo array
    todo_list = todo_dictionary.get(chatid)

    # add the reminder
    number = int(numbers[0])
    if (number > (len(todo_list) - 1)) or (number < 1):
      update.message.reply_text('Repeat command with a valid number to successfully complete task!')
    else:
      pass



def task_update(update: Update, context:CallbackContext) -> None:
  text = update.message.text
  numbers = text.split(' ')[1:]

  if len(numbers) != 1:
    # show error message if there is more or less than 1 number after the command
    update.message.reply_text('Update your task again by typing /updatetask followed by the number of the task that you want to change!')
  else:
    # update chat id
    chatid = update.message.chat.id

    # access todo array
    todo_list = todo_dictionary.get(chatid)

    # remove the task from the list
    number = int(numbers[0])
    if (number > (len(todo_list) - 1)) or (number < 1):
      update.message.reply_text('Repeat command with a valid number to successfully update the task!')
    else:
      global UpdatableNumber
      UpdatableNumber = number
      update.message.reply_text('What do you want to rename/update this task to?')
      boolean_messagedict[chatid] = True


def updatetask(int, update: Update, context:CallbackContext):
  chatid = update.message.chat.id
  text = update.message.text
  text_arr = text.split(' ')

  todo_list = todo_dictionary.get(chatid)
  todo_list.pop(int)
  # get the intended task to add as a string stored in task_str
  task_str = ''
  for i in range (len(text_arr)):
    task_str += f'{text_arr[i]} '

  chatid = update.message.chat.id
  boolean_dictionary[chatid] = True
  global task_name
  task_name = f'{task_str}'

  buttons = [[InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="1")], [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="2")], 
  [InlineKeyboardButton("⭐⭐⭐", callback_data="3")], [InlineKeyboardButton("⭐⭐", callback_data="4")], 
  [InlineKeyboardButton("⭐", callback_data="5")], [InlineKeyboardButton("None", callback_data="6")]]
  context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="What is the priority of this task?")


def queryHandler(update: Update, context:CallbackContext):
  query = update.callback_query.data
  update.callback_query.answer()

  if "yes" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      todo_dictionary[chatid] = [(0, 'To-do List:')]
      defaultPrintable = todo_dictionary.get("default")
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{defaultPrintable}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "no" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      context.bot.send_message(chat_id=update.effective_chat.id, text='Keep up with the good work and completing of tasks! You can do it! :)')
      
      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "1" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
    # add the new task to the todo array
      data = {'priority': 1, 'task': '(⭐⭐⭐⭐⭐)\n' + f'    {task_name}'}
      db.child('tasklist').child(f'{chatid}').push(data) 

      # show list
      user = db.child('tasklist').child(f'{chatid}').get()
      todo_list = user.val()
      str = 'To-do List:\n'
      index = 1
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      for i in range (0, len(todo_list)):
        str += f'{index}. ' + f'{todo_list[i][1]}\n'
        index += 1
      context.bot.send_message(chatid, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False
        
      
  if "2" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
     # add the new task to the todo array
      data = {'priority': 2, 'task': '(⭐⭐⭐⭐)\n' + f'    {task_name}'}
      db.child('tasklist').child(f'{chatid}').push(data) 

      # show list
      user = db.child('tasklist').child(f'{chatid}').get()
      todo_list = user.val()
      str = 'To-do List:\n'
      index = 1
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      for i in range (0, len(todo_list)):
        str += f'{index}. ' + f'{todo_list[i][1]}\n'
        index += 1
      context.bot.send_message(chatid, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False
    

  if "3" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
     # add the new task to the todo array
      data = {'priority': 3, 'task': '(⭐⭐⭐)\n' + f'    {task_name}'}
      db.child('tasklist').child(f'{chatid}').push(data) 

      # show list
      user = db.child('tasklist').child(f'{chatid}').get()
      todo_list = user.val()
      str = 'To-do List:\n'
      index = 1
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      for i in range (0, len(todo_list)):
        str += f'{index}. ' + f'{todo_list[i][1]}\n'
        index += 1
      context.bot.send_message(chatid, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "4" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
     # add the new task to the todo array
      data = {'priority': 4, 'task': '(⭐⭐)\n' + f'    {task_name}'}
      db.child('tasklist').child(f'{chatid}').push(data)  

      # show list
      user = db.child('tasklist').child(f'{chatid}').get()
      todo_list = user.val()
      str = 'To-do List:\n'
      index = 1
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      for i in range (0, len(todo_list)):
        str += f'{index}. ' + f'{todo_list[i][1]}\n'
        index += 1
      context.bot.send_message(chatid, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "5" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
     # add the new task to the todo array
      data = {'priority': 5, 'task': '(⭐)\n' + f'    {task_name}'}
      db.child('tasklist').child(f'{chatid}').push(data)  

      # show list
      user = db.child('tasklist').child(f'{chatid}').get()
      todo_list = user.val()
      str = 'To-do List:\n'
      index = 1
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      for i in range (0, len(todo_list)):
        str += f'{index}. ' + f'{todo_list[i][1]}\n'
        index += 1
      context.bot.send_message(chatid, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "6" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
     # add the new task to the todo array
      data = {'priority': 10, 'task': '(Misc)\n' + f'    {task_name}'}
      db.child('tasklist').child(f'{chatid}').push(data)  

      # show list
      user = db.child('tasklist').child(f'{chatid}').get()
      todo_list = user.val()
      str = 'To-do List:\n'
      index = 1
      todo_list = []
      for task in user.each():
        todo_list.append((task.val().get('priority'), task.val().get('task')))
    
      todo_list.sort(reverse=False)

      for i in range (0, len(todo_list)):
        str += f'{index}. ' + f'{todo_list[i][1]}\n'
        index += 1
      context.bot.send_message(chatid, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False

      
def prompts(update: Update, context: CallbackContext):
    chatid = update.effective_chat.id
    if boolean_messagedict[chatid] == True:
        return updatetask(UpdatableNumber, update, context)
        boolean_messagedict[chatid] = False
    else:
        pass


def main() -> None:
  updater = Updater(token= TOKEN, use_context=True)

  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler('start', start_command))
  dispatcher.add_handler(CommandHandler('help', help_command))
  dispatcher.add_handler(CommandHandler('list', show_list))
  dispatcher.add_handler(CommandHandler('addtask', add_task))
  dispatcher.add_handler(CommandHandler('donetask', done_task))
  dispatcher.add_handler(CommandHandler('newlist', create_new))
  dispatcher.add_handler(CommandHandler('starttimer', start_timer))
  dispatcher.add_handler(CommandHandler('endtimer', end_timer))
  dispatcher.add_handler(CommandHandler('reminder', reminder_command))
  dispatcher.add_handler(CommandHandler('updatetask', task_update))

  dispatcher.add_handler(MessageHandler(Filters.text, prompts))

  dispatcher.add_handler(CallbackQueryHandler(queryHandler))


  updater.start_webhook(listen="0.0.0.0", 
  port=int(PORT),
  url_path=TOKEN, 
  webhook_url='https://nerdhelperr.herokuapp.com/' + TOKEN)
  updater.idle()
  

if __name__ == '__main__':
  main()
