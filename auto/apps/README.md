# Apps on Avenew One

[Avenew One](https://www.avenew.one) uses an extensive phone and computer system, with an interface usable in-game.  This interface, called AvenOS, is a very simple text-based mobile interface that is meant to be flexible and as easy to use as a smartphone interface.  Smartphones in Avenew One can access these apps.  You can easily create new apps: be aware that creating an app is doable through code editing.  Although the process has been simplified, coding a new Aven app still involves some coding in Python.  The steps needed to code an app will be explained further in this document, along with other linked documents.  If you have a basic understanding of the Python syntax, if you know what is a variable, a function, a condition, a loop, an exception, a class, and the syntax to manipulate them; if you understand the basic concept of inheritance, then you should be fine just following this document.

## Getting strted

The first step is to install a copy of Avenew on your system.  In order to do so, you will need [Evennia](www.evennia.com) installed.

You can follow the [quick start to installing Avenew](https://github.com/vlegoff/avenew/blob/master/README.md).

When the system has been set up, you should be able to run `evennia start` in the "avenew" folder.  You will be asked to create a superuser (with a username, optional email address, and a password).  When you have done so, you should be able to connect to `localhost` on port `4000` through your favorite MU* client, or go to http://localhost:4001 and click on the "play online" link.

When you have connected to your new copy of Avenew, you will be placed in a single room with not much created.  You can create a demonstration of the game (which will create more rooms and objects, including a smartphone) by running the following command:

    @batchcode demo

It might take a couple of seconds for the command to respond.  If it has succeeded, you should see a smartphone on the ground, right at your character's feet.  You will see it if you enter `look`.  You can pick it up (`get phone`).  You can open the Aven interface by typing `use phone`.

You should now be in the phone interface.  You can open an app by entering its name (like `text`).  If you have played, or are playing, on Avenew, this should look familiar.  The difference is that you can create your own app and request that it be added to the Avenew game.

## Creating a basic app

An app is easy to add in your code.  In the "avenew" folder, open the "auto" folder, then the "apps" folder.  In it, there is one file per app.  To create a new app, just create a file with the `.py` extension and put some default code in it (see below).  That's as simple as that.

### Basic code of an app

Let's say you want to create an app called "memo" to allow to create and edit memos (short text notes).  The first step is to create a file called "memo.py" in the "auto/apps" folder.

In it, you should write the following code (modify depending on your application name, obviously):

```
"""
Memo app: store short text messages for the application user.

Give more details on what it does here.  You can write several lines.  Remember
to keep your lines shorter than 75 characters.  Take a look at the other files
for examples of what should be included here.

"""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

class Memo(BaseApp):

    """
    Memo app.

    You can add more technical details here, on how to use it for a developer,
    the possible methods and such.

    """

    app_name = "memo"
    display_name = "Memo"
```

Let's quickly go over this code.  If it looks obscure to you, there are really good Python tutorials on the Internet that would help you understand the Python syntax more easily.  I highly recommend reading one of them before going on.

1. We begin by several lines wrapped in `"""` quotes.  This is a **docstring**, and at this point it serves to explain what the file is.  Since our file will contain an app, it's a good moment to explain about the app: what it does, who did it, how it works.  Don't write a novel in it either, documentation is good, but over-doing it might be a bad idea.
2. We then import from the `auto.apps.base` module.  This module contains several things that we will need for our application.  For the time being, we just use `BaseApp`.  We'll explore the other classes in the following sections of this document.
3. We then define the app structure.  In order to have a working app, we need to define a class inheriting from `BaseApp` with a valid `app_name` class variable.  So we define the `Memo` class, inheriting from `BaseApp`.  Remember some documentation in the class itself too, it will not hurt.
4. We define some class variables that will be used by the system: `app_name` contains, strangely enough, the name of your application.  It should be a lower-case string identifying your application.  Two applications cannot have the same `app_name`.  `display_name` contains a prettier version of your app name, the one that will be shown to users.  It's usually the application name with an upper-case letter at the beginning.  This is not an identifier, and several apps can have the same display name, although it might get confusing for users.

### That's it, let's run!

You can close this file for the time being.  Reload Evennia (or restart it).  Connect to it.  Before using your phone, you need to add your application: a phone doesn't have all possible applications, it would be confusing.  You can do that really quickly using `@py`:

    @py self.search("phone").types.get("computer").apps.add("memo")

> Wow, what did that do?

I won't detail the behavior of the line here, though you might understand it more with time and practice.  Basically, it gets the phone you should have in your inventory, get the "computer" type in the phone (that's a type where applications are defined), access the installed apps on this device and add one (again, substitute your application name instead of `memo`, you have to specify your application's `app_name`, the lower-case identifier).

And then type `use phone`.  The Aven interface should open but this time, you should see your new application's display name in it.

> I can't launch my application.  If I enter the application's name, I get a funny error about a "missing screen".

Correct.  That was the real minimum, and we're far from done.  That was the basic code to have you add an application, and I hope you'll agree, it's not too difficult.  From here, things are getting a bit more difficult and interesting.

## The structure of every app

A basic app is structured around three important concepts:

- The app class: this is the class we created just above.  It contains some information on the application.  It might not contain anything else and is often the shortest class in the file.  However, without it, nothing would work.
- One or more screen classes: a screen describes what is displayed on the interface at a given point.  For instance, if you enter "use phone", then "text", the text app will open.  The screen will show you the list of messages you have received and offer you to create a new message.  This is a screen.  If you type "new", a new screen will appear to create a new message.  If you type "send" after having typed a message, you will go back to the previous screen (showing you your messages).  This concept of screen is really important.  An application could have only one screen, but it usually has more than just one.
- Some commands: when you open a screen, you get access to some command.  When you entered "use phone" and "text" in the previous example, the main screen of the text app appeared.  It defines the "new" command.  You can enter "new" to create a new message.  If you do, you will go to a different screen and will have other commands: "send", "cancel", "to" and so on.  A command in your app is just an [Evennia command](https://github.com/evennia/evennia/wiki/Commands) with some default values.

So in summary: an app has an app class, and one or more screen classes.  A screen can have some commands.

If you're okay with this, let's move on.  If not, you can read this section again, or if you prefer, just look at one of the defined apps in the "auto/apps" folder.  Open the "auto/apps/contact.py" file to see the contact app, for instance.

### The first screen

An app cannot work without at least one screen.  For the purpose of this example, we'll keep things simple.  A screen displays some information (a text-based dialog box, for instance) and offers some commands.  Let's add a very, very simple screen (you can run this code in your "memo" app, here is the full code).

```python
"""
Memo app: store short text messages for the application user.

Give more details on what it does here.  You can write several lines.  Remember
to keep your lines shorter than 75 characters.  Take a look at the other files
for examples of what should be included here.

"""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

## Application class

class Memo(BaseApp):

    """
    Memo app.

    You can add more technical details here, on how to use it for a developer,
    the possible methods and such.

    """

    app_name = "memo"
    display_name = "Memo"
    start_screen = "MainScreen"

## Screens

class MainScreen(BaseScreen):

    """Main screen, displaying hello!."""

    def get_text(self):
        """Return the text to be displayed."""
        return """
                Memo app!

                This is my first application, doesn't it look good?

                Of course it doesn't do much at this point.

                Memo app, by me, BSD license
            """
```

> Do I need to run the complicated `@py` command again?

No, this was just to add the app.  Just reload (using `@reload` for instance), open the interface again (`use phone`) and then, enter `memo` to open the memo application.  This time, it opens, and what do you see?

```
Memo app! (BACK to go back, EXIT to exit, HELP to get help)

This is my first application, doesn't it look good?
Of course it doesn't do much at this point.

Memo app, by me, BSD license
```

You see the text you have entered in `get_text` with some alterations:

1. At the first line of your text (usually the screen name), a header has been added.  This header contains three commands (or links): back, exit, and help.  These commands are accessible out-of-the-box, you don't have to create them.  `back` allows you to go back to the previous screen.  `exit` closes the interface.  `help` gives you more information on the screen.  This header can be disabled, but in most cases, you will need it (keep the first line of `get_text` purposefully short).
2. Although the text was entered with some indentation, it has been removed.  Actually, it is not (try to enter a line with greater indentation), but the method that displays the text and calls `get_text` removes some of the initial indentation to make it easier to edit and visually nicer.  (Take a look at (textwrap.dedent)(https://docs.python.org/2/library/textwrap.html) if you want to know how it works.)

There's something else that we did, and it's important.  Our app must know what screen to open (it cannot guess, as I mentioned, there is often more than one screen).  This is done through another class variable in our `Memo` class.  Here is a reminder:

```python
class Memo(BaseApp):

    """..."""

    app_name = "memo"
    display_name = "Memo"
    start_screen = "MainScreen"
```

The `start_screen` class variable of our app class contains the name of the screen to open.  It has to be the name of the class.  It can be a full path if the screen is in a different file, like `"auto.apps.base.mainScreen"`.  It is most common to simply specify the class name like here: `" MainScreen"`.  A class of this name will be sought in the same module.

For the time being, our screen doesn't do anything, except displaying some information.  Obviously, a screen must do something, probably have some buttons (commands).

## A working example

### Designing the app structure

It's a good time to think about what we want our app to look like.  Here, we will create a simple `memo` app that allows to add, remove and edit memos.  A memo is simply a note with some text.  So our main screen could look like this:

```
Memos (BACK to go back, EXIT to exit, HELP to get help)

Create a NEW memo.

(Insert the list of current memos here).

Memos: 15
```

This is a rough draft, of course, but it will allow us to see the screen and command process.

In other words, we want a command, named `new`, that creates a new memo.  We also want to open memos to edit them.  And perhaps, after that, we should add a command to delete a memo, that might be good!

So the first question we ought to ask ourselves is: how many screens should we need?  Only one?  Well, if we create a new memo, we want it to happen in a new screen where we can edit text.  It will still be more comfortable than doing so in the main screen.  You can do it all in one screen, this really depends on your app structure.  For the example, we'll split it into two screens: the main screen, and the memo screen (to add/edit a memo).

Next question: what commands should we need?  Well, the new command, obviously, to go from the main screen to the memo screen.  And a command to open an existing memo... perhaps "edit"?  It's a possibility.  However, it would make more sense to have an app like this:

```
Memos (BACK to go back, EXIT to exit, HELP to get help)

Create a NEW memo.

 1 - Don't forget to feed the animals and plants before we leave tomorrow.
 2 - Stella's phone is 000-0000, call before Saturday.
 3 - Electricity bill due on 3/12, no more delay!

Memos: 3
```

If you enter "new", you can add a memo.  If you enter a number, you can open an existing memo to edit it.  we could create commands for every memo, but we'll do it another way, by redirecting user input to check that a number was entered or not.

### Let's consider storage

Here is a question you may have wondered: where will we store our memos?  It's a valid question.  The app system provides several ways to quickly store information in different places.  We can store information on the app or on the screen.

> What's the difference?

Usually, we store on the app when we:

1. Want information that might be accessed by several screens.
2. Want to keep information about the app itself.
3. Need persistent and accurate information that should remain until we remove it.

We store on the screen when we:

1. Want information that will only be true for this screen.
2. Don't need vital information, we could do if it's lost by accident.

So it would make more sense to create our memos in the app: memos would be accessible from different screens, but we don't want them to get deleted or replaced by accident.

> What could we store on screens then?

Field editing is a very common case.  In our `MemoScreen`, we will edit the text field.  So we'll need to temporarily store the memo to quickly modify it.  You will find a lot of examples.

In both cases, storage is accessible through the `db` property, either on the app or the screen.  It will return a dictionary (or a `_SaverDict`, actually) in which you can write information that will be saved automatically.  It will be persistent data: if you reload or restart Evennia, the data will persist.  The downside is that you cannot store anything in it.  We'll avoid storing objects, for instance, we'll simply store dictionaries.  Look at this example:

```python
class MainScreen(BaseScreen):

    """Main screen, displaying hello!."""

    def get_text(self):
        """Return the text to be displayed."""
        memos = self.app.db.get("memos", [])
        string = "Memos"
        string += "\n\nCreate a NEW memo."
        string += "\n"

        # Add the existing memos
        i = 1
        for line in memos:
            text = line.get("text")
            string += "\n {i} - {text}".format(i=i, text=text)
             i += 1

        # Display the bottom line
        string += "\n\nMemos: {}".format(len(memos))
        return string
```

We have changed the way our text is displayed.  This is less readable and less pretty, but it allows us to simply add information on the current memos, and that's the part that really interests us right now.

Our first line in `get_text` might be worth a second look: `memos = self.app.db.get("memos", [])` .  `self.app` contains the app (an object created on our `Memo` class).  So `self.app.db` contains a dictionary of persistent information stored on the app.  So we use it like a normal dictionary: here, we get a value (called `memos`) and specify a default value (it might be empty, it will always be if you don't add new memos).

So `memos` contains a list.  A list of what?  Well, a list... of dictionaries!  Remember, we will avoid storing objects here, though that would be nicer.  So we're going to store a dictionary for each memo.  A few lines below, we browse through the list and get the dictionaries inside.  We get the `"text"` key in the dictionary and display it.

> Can I try this code?

You can... but I would suggest adding a memo beforehand: that will make things more interesting.

Update the `MainScreen` class with the code I provided just above.  Reload Evennia (with `@reload` for instance).  If you haven't done so already, open the interface (`use phone`).

Before you open the `memo` app, however, we're going to add a memo.  This code will do the trick (copy/paste it as is in your client).

    @py self.search("phone").types.get("computer").apps.get("memo").db["memos"] = [{"text": "Don't forget to feed the animals and plants before we leave tomorrow."}]

Then, open the memo app by entering: "memo".

```
Memos (BACK to go back, EXIT to exit, HELP to get help)

Create a NEW memo.

 1 - Don't forget to feed the animals and plants before we leave tomorrow.

Memos: 1
```

> Wow, it works!  Can I add other memos to test?

Sure, go ahead!  Use the same command I gave you above and change the text at the end (since there are some symbols, I advise copy/pasting and simply editing the text between the double quotes at the end).

> I add memos, but I have to go back and open the memo app to see them again.

Yes, you can update the screen by entering "back", then "memo" again to open the app.  However, you can simply press your RETURN key without any text, and the screen will update.

### Let's add a second screen

> All that is good... but we still can't add new memos and edit existing ones, except using the ugly shortcut with the `@py` command.

That's what we're going to do in this section.  And to do so, we'll add a new screen!

> Why a new screen?  Couldn't we edit our memos right in the main screen?

We could.  You could do so.  But users might appreciate a different screen.  Your application isn't that big for the time being, but if you add other fields, a new screen will just be easier.  And it's not that hard to do, really.  Besides, when you create a new memo, you will use the same screen, so that makes more sense in the end.

So what to do in our screen?

I propose a very simple screen: it will open on a memo and will allow to edit its text.  If you type text in the screen, it will update the text in the memo and close the screen.

Let's code a rough screen to do just that.  In the file, below your `MainScreen` class, add a new screen:

```python
class MemoScreen(BaseScreen):

    """Add or edit a memo.

    This screen will allow to add or edit an existing memo.  If you
    type text in it, the text of the memo will be updated and the
    screen will close.

    """

    back_screen = MainScreen

    def get_text(self):
        """Return the text to be displayed by the screen."""
        memo = self.db.get("memo", {})
        if memo:
            title = "Memo editing"
        else:
            title = "New memo"
        text = memo.get("text", "(Enter the text of the memo here.)")
        if "text" in self.db:
            text = self.db["text"]

        return """
            {title}

            Text:
                {text}

                    SAVE
        """.format(title=title, text=text)
```

It doesn't look too different from what we have had so far.  Notice a few things, however:

1. This time, we add a class variable named `back_screen` to our class.  It contains the screen to which we should go back if we type "back".  This is a good habit to take, to always have a `back_screen`, except for the app `start_screen` to which it's not necessary.  The `back_screen` is normally not used: whenever you browse through applications, the screens that opened are kept and typing "back" always goes back to the previous screen.  In some cases, however, there's no explicit back screen, hence this class variable.
2. We assume our memo is stored on the screen itself, under the key `"memo"`.  This memo should be a dictionary.  If the screen doesn't have any, it will simply assume an empty memo.  The title will vary: if the memo exists, it will mark "editing", if not it will indicate "new memo".  Which is quite correct.
3. The text can also be stored on the screen.  We'll see why later, for the time being, just notice that the text can be stored on `self.db` too.

Okay, our screen works... but how can we access it to check?  The only connected screen we have is `MainScreen` for the time being.

### Changing screen

There are three main ways to change between screens, and all of them are screen methods:

- `back()`: this method will just close the current screen and go back to the previous screen.  It's a very common feature and you'll see it used before long.
- `move_to()`: this allows to change from screen to screen.  It needs to know to which screen we need to go.  It has some options we'll discuss later.  Interestingly, this is not the method we use most often.
- `next`: this has exactly the same effect has `move_to`, and the same options, except that it keeps track of the new screen in the screen tree.

Remember, the screen tree is there to remember what screen you opened.  When you use your phone, it creates an element in the screen tree.  When you open the `text` application, it creates another element.  If you type `new` to create a new text, it opens a new screen ands add a new element to the screen tree.  If then you type "back", the screen tree will be read to know what was the previous screen.  We don't need to trouble ourselves that much about the screen tree, we just need to know that `next` will write in it and remember the screens we have opened, that's why we prefer to use it except in some cases.

> Why would I want to redirect to a screen without it being accessible through "back"?

This doesn't often happen.  Usually, you will use the `next()` method.  But when you use a very generic screen, like displaying a "yes or no" dialog, you don't mean to store this dialog in the screen tree.

So let's look at `next` in more details now.  Remember that `move_to` has the same options:

- `screen`: the new screen (either a screen class, or a path leading to this class).
- `app`: the application for this new screen.  By default, it will be the same application in which the current screen is opened, and we don't often need to change it.
- `db`: an optional dictionary containing data to be sent to the new screen.  This data will be stored in the screen `.db` property.

In our example, the screen will be `MemoScreen`, since we want to redirect to the memo screen.  However, `MemoScreen` needs some data, remember?

- `memo` is a dictionary containing the memo to be edited.
- `text` is an optional text string containing the current text of the memo.

So we'll use `.next` like this:

```python
screen.next("MemoScreen", db=dict(memo=memo, text=text))
```

Let's put this code where it belongs.

### Redirecting user input

Perhaps you remember that I suggested, for the main screen, that we could add to the memo, to edit it, just by entering a number.  "Entering a number" means we need to catch user input and do something.  There's a really simple method in the screen you can override to achieve just that.  Its name is `no_match`, and it expects one argument: the string entered by the user.

So we will add this method to our `MainScreen` and redirect to the `MemoScreen` if the entered string is a valid number.

```python
# ...
## Screens
class MainScreen(BaseScreen):

    """Main screen, displaying hello!."""

    def get_text(self):
        """Return the text to be displayed."""
        memos = self.app.db.get("memos", [])
        string = "Memos"
        string += "\n\nCreate a NEW memo."
        string += "\n"

        # Add the existing memos
        i = 1
        for line in memos:
            text = line.get("text")
            string += "\n {i} - {text}".format(i=i, text=text)
            i += 1

        # Display the bottom line
        string += "\n\nMemos: {}".format(len(memos))
        return string

    def no_match(self, string):
        """Called when no command matches the user input.

        We need to test `string` to see if it's a valid number, and,
        if so, redirect to the memo screen to edit this memo.

        """
        # Remember the memos, the list of dictionaries, should be in `self.db`
        memos = self.app.db.get("memos", [])

        # Try to convert input
        try:
            number = int(string)
            assert number > 0
            memo = memos[number - 1]
        except (ValueError, AssertionError, IndexError):
            self.user.msg("Invalid number.")
        else:
            text = memo.get("text")
            # Open the MemoScreen
            self.next("MemoScreen", db=dict(memo=memo, text=text))

        return True

# ...
```

I give you the entire class of the `MainScreen`.  Remember that you also need the `Memo` class (above the `MainScreen`) and `MemoScreen` (below the `MainScreen`).

Reload the game again, then open the app: `use phone`, then `memo`.  Then press `1`.  If you have at least one memo, the first one should open and you will see the `MemoScreen`:

```
Memo editing (BACK to go back, EXIT to exit, HELP to get help)

Text:
    Don't forget to feed the animals and plants before we leave tomorrow.

        SAVE
```

It works!  The new screen opens and we see the text of our memo... we cannot edit it yet, but one step at a time.  Let's go back to the `no_match` method beforehand, for there might be some things that are not self-explanatory:

- Once again, notice that `no_match` takes one argument besides `self`: the string entered by the user.  This method is called if no command matches the user input.
- We get the `memos` the same way as before.  It will be a list of dictionaries.  It may not exist (so we get an empty list if not).
- We then convert the user input and do some additional things.  The user input will be a number between ` and N, but we have to check it's a number, it's not too low, and it's not too high.  Doing it in a `try/except` like this is a Pythonic way of testing the input.
- If an error occurs, we send it to `self.user`.  This contains the object (character) using the device at this point.  You have already seen `self.app` which points to the application.
- If the conversion was successful, we have a `memo` variable that contains one of the list element.  Remember that `memos` contains a list of dictionaries, so `memo` will contain a dictionary.  We create the `text` variable as well, which will contain the text of the memo to be edited.
- Finally we call `self.next` to redirect to a different screen.  The parameters shouldn't surprise you at this point, I hope.
- The `no_match` method has to return `True` or `False`.  `True` means "I handled the input`, `False` means "I didn't handle it, display an error".  Since in our case we display the error right in our `no_match` method, we return `True` no matter what.

And that's it!  We can now edit a memo (at least see its content and open the new screen).

You could try to use the `no_match` method on the `MemoScreen` to try and update the memo text right away.  It's not too difficult to do, and will offer you a good exercise.  You already have everything to code this method.  I advise you to try and code it yourself before you look at the solution below.  But don't hesitate to do so if you're stuck.

Again, what should we want in our `MemoScreen`?  If we enter some text, we could just modify the memo text... that would be simple!  Let's do that first, and we'll update it later.

```python
class MemoScreen(BaseScreen):

    """Add or edit a memo.

    This screen will allow to add or edit an existing memo.  If you
    type text in it, the text of the memo will be updated and the
    screen will close.

    """

    back_screen = MainScreen

    def get_text(self):
        """Return the text to be displayed by the screen."""
        memo = self.db.get("memo", {})
        if memo:
            title = "Memo editing"
        else:
            title = "New memo"
        text = memo.get("text", "(Enter the text of the memo here.)")
        if "text" in self.db:
            text = self.db["text"]

        return """
            {title}

            Text:
                {text}

                    SAVE
        """.format(title=title, text=text)

    def no_match(self, string):
        """Called when no command matches the user input."""
        memo = self.db.get("memo", {})
        memo["text"] = string

        # Close the screen and go back to the previous one
        self.back()
        return True
```

> Wow, our `no_match` method is really short!

- We get the memo.  Again, remember, it's stored in the screen's `db`.  It's a dictionary.
- We just put the text in the dictionary's `text` key.
- And then we call `self.back()` to close the screen and go back.
- Don't forget to return `True`!

> And that's it?

That's it.  Reload, edit a memo, type in some text, hit RETURN, and your text will be saved, the memo changed, and you should find yourself back in `MainScreen` with the updated memos.

> We just changed a dictionary... how could that be stored?

Everything that is stored in `.db` (in an app or screen) is persistent.  Modifying just a key of this dictionary will save the dictionary automatically.  You don't have to worry about that much, it's a nice feature of Evennia itself.

### And a screen command

For our app to be usable, we should also create a command: the "new" command that will be used to create a new memo.  Creating a command in a screen is just creating an Evennia command, but we use `AppCommand` as a parent.  The rest remains the same, mostly.  At the bottom of our file, add a new section and create this command:

```python
# ...

## Commands

class CmdNew(AppCommand):

    """
    Create a new memo.

    Usage:
      new
    """

    key = "new"

    def func(self):
        """Command body."""
        screen = self.screen
        screen.next("MemoScreen")
```

If you know Evennia commands, nothing much should surprise you... except something: what is this `self.screen`?  It's something that is specific to the `AppCommand`: they know from what screen they have been called.  And that will make our life way easier.  So now that we have the screen, we can just redirect to the `MemoScreen`.

> Why don't we provide arguments in `db` this time?

Good question: since we want to create a new memo, the memo itself doesn't exist yet.  We'll need to create it when we hit RETURN.

There's one last thing: we need to tell the screen that it has access to the command.  This is another class variable in the screen class: `commands` is a list that contains the names of the commands to be added for this screen.  In which screen do we need the "new" command?  The `MainScreen`:

```python
class MainScreen(BaseScreen):

    """Main screen, displaying hello!."""

    commands = ["CmdNew"]

    # ...
```

If you have difficulty in finding the right places to update, you will find the full application in a following section.

All we did was to define the `commands` class variable in our screen, with the list of commands.  Here, we just have `CmdNew`,  so we have `commands = ["CmdNew"] .

Let's reload and open the app again!

Use your phone, then enter `memo`, then `new` to create a new memo.  You should see the following text:

```
New memo (BACK to go back, EXIT to exit, HELP to get help)

Text:
    (Enter the text of the memo here.)

        SAVE
```

> If I enter some text, nothing happens, the screen closes!

That's because our `MemoScreen` wants a memo, and since the memo isn't created yet, we don't have it.  So nothing happens.  Let's modify the `no_match` method in the `MemoScreen`:

```python
class MemoScreen(BaseScreen):

    """Add or edit a memo.

    This screen will allow to add or edit an existing memo.  If you
    type text in it, the text of the memo will be updated and the
    screen will close.

    """

    back_screen = MainScreen

    # ...
    def no_match(self, string):
        """Called when no command matches the user input."""
        memo = self.db.get("memo", {})

        if memo:
            memo["text"] = string
        else:
            # If the memo is empty, create a new one
            if "memos" not in self.app.db:
                self.app.db["memos"] = []
            self.app.db["memos"].insert(0, {"text": string})

        # Close the screen and go back to the previous one
        self.back()
        return True
```

> What is different in the new `no_match` method?

Instead of changing the memo text, we check that the memo exist (if it doesn't, it's an empty dictionary).  If it doesn't exist, we add the memo to the app, in `self.app.db["memos"]`.  If you reload and try to create a new memo and edit an existing one, both should now work!

### To conclude this example

This is just a first example, but it showed you the application class, the screen classes, the command classes, how they worked together, and how to store data.  Don't hesitate to look at the code for some other applications.  Be aware that they might be much longer in the end.  Here is the complete code of our `auto/apps/memo.py` file for reference:

```python
"""
Memo app: store short text messages for the application user.

Give more details on what it does here.  You can write several lines.  Remember
to keep your lines shorter than 75 characters.  Take a look at the other files
for examples of what should be included here.

"""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

## Application class

class Memo(BaseApp):

    """
    Memo app.

    You can add more technical details here, on how to use it for a developer,
    the possible methods and such.

    """

    app_name = "memo"
    display_name = "Memo"
    start_screen = "MainScreen"

## Screens

class MainScreen(BaseScreen):

    """Main screen, displaying hello!."""

    commands = ["CmdNew"]

    def get_text(self):
        """Return the text to be displayed."""
        memos = self.app.db.get("memos", [])
        string = "Memos"
        string += "\n\nCreate a NEW memo."
        string += "\n"

        # Add the existing memos
        i = 1
        for line in memos:
            text = line.get("text")
            string += "\n {i} - {text}".format(i=i, text=text)
            i += 1

        # Display the bottom line
        string += "\n\nMemos: {}".format(len(memos))
        return string

    def no_match(self, string):
        """Called when no command matches the user input.

        We need to test `string` to see if it's a valid number, and,
        if so, redirect to the memo screen to edit this memo.

        """
        # Remember the memos, the list of dictionaries, should be in `self.db`
        memos = self.app.db.get("memos", [])

        # Try to convert input
        try:
            number = int(string)
            assert number > 0
            memo = memos[number - 1]
        except (ValueError, AssertionError, IndexError):
            self.user.msg("Invalid number.")
        else:
            text = memo.get("text")
            # Open the MemoScreen
            self.next("MemoScreen", db=dict(memo=memo, text=text))

        return True


class MemoScreen(BaseScreen):

    """Add or edit a memo.

    This screen will allow to add or edit an existing memo.  If you
    type text in it, the text of the memo will be updated and the
    screen will close.

    """

    back_screen = MainScreen

    def get_text(self):
        """Return the text to be displayed by the screen."""
        memo = self.db.get("memo", {})
        if memo:
            title = "Memo editing"
        else:
            title = "New memo"
        text = memo.get("text", "(Enter the text of the memo here.)")
        if "text" in self.db:
            text = self.db["text"]

        return """
            {title}

            Text:
                {text}

                    SAVE
        """.format(title=title, text=text)

    def no_match(self, string):
        """Called when no command matches the user input."""
        memo = self.db.get("memo", {})

        if memo:
            memo["text"] = string
        else:
            # If the memo is empty, create a new one
            if "memos" not in self.app.db:
                self.app.db["memos"] = []
            self.app.db["memos"].insert(0, {"text": string})

        # Close the screen and go back to the previous one
        self.back()
        return True


## Commands

class CmdNew(AppCommand):

    """
    Create a new memo.

    Usage:
      new
    """

    key = "new"

    def func(self):
        """Command body."""
        screen = self.screen
        screen.next("MemoScreen")
```

Notice that we didn't do everything we had planned: there's no way to delete a memo.  When you type text in the `MemoScreen`, it edits the memo text directly, there's no way to type several lines and the "save" button is never used.  But you can now do that on your own, that will be good practice!  The rest of this documentation focuses on more advanced and specific details that you do not need to create your applications, but that might become useful in some cases.

## Advanced features

This section contains more specific explanations on various topics.  You might not need them in your app, but if you do, you will find the process explained here.  As usual, for a complete reference, read the code itself which is heavily documented.

### Generic screens
### A screen for app settings
### Notifications and app status

An app can send notifications to alert the device of incoming information.  The text app, for instance, sends a notification to the recipients of a text when it is sent.  Additionally, an app can have a status (mark the number of items that should be read).  It is usually done through the app's display name (like "Text(3)" to say that 3 texts ought to be read).

Both systems (notifications and status) are independent.  An app can have none, either, or both of them.

#### The app status in its display name

Changing the app status is quite simple: we used `display_name` as a class variable so far, defined on the app itself.  However, it can also have a `get_display_name` method that will return the name to be displayed.  This allows to display a name that will vary depending on the context.  Here, for instance, is the `Text` application `get_display_name` to give you an example:

```python
class TextApp(BaseApp):

    """Text applicaiton."""

    app_name = "text"
    display_name = "Text"
    start_screen = "MainScreen"

    def get_display_name(self):
        """Return the display name for this app."""
        number = self.get_phone_number(self.obj)
        unread = Text.objects.get_nb_unread(number)
        if unread:
            return "Text({})".format(unread)

        return "Text"
```

Don't worry about the two first lines of this method: it will simply get the phone number of the object and then, query the number of unread messages.  You will definitely adapt this example.  The next lines show you how to return a different name depending on status (the number of unread texts, in our case).

#### Sending notifications


### Games and invitations
### Paying within an app
## Developing apps
### Troubleshooting
### Testing apps for stability
### Send an app to the main Avenew code
