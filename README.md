# Welcome to the Avenew game folder for Evennia

This is the free and open-source [Avenew game](https://github.com/vlegoff/avenew), providing most of the gameplay which ought to be used in the Avenew game.

## What is Avenew?

Avenew is a MUD based on modern days (or slightly in the future), with a system of vehicles to drive, firearms, and a complete gang system.

## Installing

In order to have Avenew running on your local machine, you would need to install [Evennia](https://github.com/evennia/evennia/wiki/Evennia-Introduction).  You can find the [installation instructions for Evennia here](https://github.com/evennia/evennia/wiki/Getting-Started).

### Additional dependencies

Avenew needs some more dependencies in order to run properly.

* [django-wiki](https://github.com/django-wiki/django-wiki): to support a wiki feature on the main website.  To install, run: `pip install wiki`
* SSL support: Evennia provides a SSL support which is enabled on Avenew.  To install: `pip install pyopenssl`
* You could turn SSL off by editing your `server/conf/secret_settings.py` file.  The settings in this file will overri8de these in `server/conf/settings.py`, so you could write something like:

```python
# Deactivate SSL protocol (SecureSocketLibrary)
SSL_ENABLED = False
```

This will turn SSL off for the instance of Avenew that is running on your local system.
