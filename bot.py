import logging
import os
from xmlrpc.client import boolean
from telegram import *
from telegram.ext import *
import time

PORT = int(os.environ.get('PORT', 5000))

# enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# global variables
TOKEN = os.environ['TELETOKEN']
todo_dictionary = {"default": "To-do List:"}
boolean_dictionary = {}
chatid = 0
task_name = ''
pomodoro = 25*60

def start_command(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    name = user['first_name']
    update.message.reply_text(
        f'Hi {name}!, use me as a to-do list for your tasks! ' +
        'To get started, use /addtask followed by the name of your task to add a new task to your list, and ' +
        '/list to view your current list.\n' +
        '/startpomo to start a pomodoro timer of 25 minutes\n\n'
        'Do go to /help to look at how to use the other commands!'
    )


def help_command(update: Update, _:CallbackContext) -> None:
  update.message.reply_text('This bot is basically a to-do list for your tasks, implemented with a priority system! Commands:\n' +
        '/start to start the bot\n' 
        '/addtask followed by your task to add your new task\n' + 
        '/donetask followed by the number of that task on the list to remove that task.\n' + 
        '/list to view your current to-do list\n' + 
        '/newlist to delete your current list and start a new one\n' +
        '/startpomo to start a pomodoro timer of 25mins\n'
        '/help to look at the bot commands again!'
  )


def show_list(update: Update, _:CallbackContext) -> None:
  # update chat id
  chatid = update.message.chat.id
  if chatid in todo_dictionary:
    # show list if the chat id exists in the dictionary as a key
    todo_list = todo_dictionary.get(chatid)
    str = f'{todo_list[0][1]}\n'
    for i in range (1, len(todo_list)):
      str += f'{i}. ' + f'{todo_list[i][1]}\n'
    update.message.reply_text(f'{str}')
  else:
    # or else show default empty list 
    defaultPrintable = todo_dictionary.get("default")
    boolean_dictionary[chatid] = True
    update.message.reply_text(f'{defaultPrintable}')


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

    buttons = [[InlineKeyboardButton("Most Important", callback_data="1")], [InlineKeyboardButton("Important", callback_data="2")], 
    [InlineKeyboardButton("Average", callback_data="3")], [InlineKeyboardButton("Not So Important", callback_data="4")], 
    [InlineKeyboardButton("Least Important", callback_data="5")], [InlineKeyboardButton("Miscellaneous", callback_data="6")]]
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="What is the priority of this task?")


def done_task(update: Update, _:CallbackContext) -> None:
  text = update.message.text
  numbers = text.split(' ')[1:]

  if len(numbers) != 1:
    # show error message if there is more or less than 1 number after the command
    update.message.reply_text('Remove your task again by typing /donetask followed by the number of the task it corresponds to!')
  else:
    # update chat id
    chatid = update.message.chat.id

    # access todo array
    todo_list = todo_dictionary.get(chatid)

    # remove the task from the list
    number = int(numbers[0])
    if (number > (len(todo_list) - 1)) or (number < 1):
      update.message.reply_text('Repeat command with a valid number to successfully complete task!')
    else:
      todo_list.pop(number)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      update.message.reply_text(f'{str}')


def create_new(update: Update, context:CallbackContext):
  chatid = update.message.chat.id
  boolean_dictionary[chatid] = True
  buttons = [[InlineKeyboardButton("Yes 👍🏽", callback_data="yes")], [InlineKeyboardButton("No 👎🏽", callback_data="no")]]
  context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Are you sure?")


def pomodoro_timer(update: Update, context:CallbackContext):
  global pomodoro
  timeleft = pomodoro
  context.bot.send_message(chat_id=update.effective_chat.id, text=f'Pomodoro timer of 25minutes started!')
  while timeleft:
    time.sleep(25*60)
    timeleft -= 25*60

  # when the pomodoro timer ends
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text=f'Pomodoro timer of 25 minutes have finished! /startpomo to start another cycle of 25mins!')

def reminder_command(update: Update, context: CallbackContext):
  chatid = update.message.chat.id
  reminderbuttons = []
  b = []
  # error when no task in to_do list
  if chatid not in todo_dictionary:
    update.message.reply_text('There is no tasks in your list to set a reminder for! Add a task before setting a reminder')

  else:
    todo_list = todo_dictionary.get(chatid)
    for k, v in todo_list:
      b.append(v)
    flatten = [str(task) for task in b]
    for i in range(1, len(flatten)):
      newbutton = [InlineKeyboardButton((f'{flatten[i]}'), callback_data=f'{flatten[i]}')]
      reminderbuttons.append(newbutton)
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(reminderbuttons),
                               text="Which task do you want to set a reminder for?")


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
      # access todo array if it is present in the dictionary,
      # else create a new todo array
      if chatid in todo_dictionary:
        todo_list = todo_dictionary.get(chatid)
      else:
        todo_list = [(0, 'To-do List:')]
        todo_dictionary[chatid] = todo_list

      # add the new task to the todo array
      todo_list.append((1, '(⭐⭐⭐⭐⭐) ' + f'{task_name}'))
      todo_list.sort(reverse=False)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False
    
      
  if "2" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      # access todo array if it is present in the dictionary,
      # else create a new todo array
      if chatid in todo_dictionary:
        todo_list = todo_dictionary.get(chatid)
      else:
        todo_list = [(0, 'To-do List:')]
        todo_dictionary[chatid] = todo_list

      # add the new task to the todo array
      todo_list.append((2, '(⭐⭐⭐⭐) ' + f'{task_name}'))
      todo_list.sort(reverse=False)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False
    

  if "3" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      # access todo array if it is present in the dictionary,
      # else create a new todo array
      if chatid in todo_dictionary:
        todo_list = todo_dictionary.get(chatid)
      else:
        todo_list = [(0, 'To-do List:')]
        todo_dictionary[chatid] = todo_list

      # add the new task to the todo array
      todo_list.append((3, '(⭐⭐⭐) ' + f'{task_name}'))
      todo_list.sort(reverse=False)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "4" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      # access todo array if it is present in the dictionary,
      # else create a new todo array
      if chatid in todo_dictionary:
        todo_list = todo_dictionary.get(chatid)
      else:
        todo_list = [(0, 'To-do List:')]
        todo_dictionary[chatid] = todo_list

      # add the new task to the todo array
      todo_list.append((4, '(⭐⭐) ' + f'{task_name}'))
      todo_list.sort(reverse=False)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "5" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      # access todo array if it is present in the dictionary,
      # else create a new todo array
      if chatid in todo_dictionary:
        todo_list = todo_dictionary.get(chatid)
      else:
        todo_list = [(0, 'To-do List:')]
        todo_dictionary[chatid] = todo_list

      # add the new task to the todo array
      todo_list.append((5, '(⭐) ' + f'{task_name}'))
      todo_list.sort(reverse=False)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False


  if "6" in query:
    chatid = update.effective_chat.id
    if boolean_dictionary[chatid] == True:
      # access todo array if it is present in the dictionary,
      # else create a new todo array
      if chatid in todo_dictionary:
        todo_list = todo_dictionary.get(chatid)
      else:
        todo_list = [(0, 'To-do List:')]
        todo_dictionary[chatid] = todo_list

      # add the new task to the todo array
      todo_list.append((10, '(✨) ' + f'{task_name}'))
      todo_list.sort(reverse=False)

      # show the updated list
      str = f'{todo_list[0][1]}\n'
      for i in range (1, len(todo_list)):
        str += f'{i}. ' + f'{todo_list[i][1]}\n'
      context.bot.send_message(chat_id=update.effective_chat.id, text=f'{str}')

      # set boolean to False to prevent multiple clicks of button
      boolean_dictionary[chatid] = False



def main() -> None:
  updater = Updater(token= TOKEN, use_context=True)

  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler('start', start_command))
  dispatcher.add_handler(CommandHandler('help', help_command))
  dispatcher.add_handler(CommandHandler('list', show_list))
  dispatcher.add_handler(CommandHandler('addtask', add_task))
  dispatcher.add_handler(CommandHandler('donetask', done_task))
  dispatcher.add_handler(CommandHandler('newlist', create_new))
  dispatcher.add_handler(CommandHandler('startpomo', pomodoro_timer))
  dispatcher.add_handler(CommandHandler('reminder', reminder_command))

  dispatcher.add_handler(CallbackQueryHandler(queryHandler))


  updater.start_webhook(listen="0.0.0.0", 
  port=int(PORT),
  url_path=TOKEN, 
  webhook_url='https://nerdhelperr.herokuapp.com/' + TOKEN)
  updater.idle()
  

if __name__ == '__main__':
  main()
