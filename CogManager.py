import os
from nextcord import Interaction
from nextcord.ext.commands import Bot
from nextcord.ext.commands import errors as nc_errors
from typing import Mapping, List


class CogManager:
    def __init__(self, bot: Bot):
        self.bot = bot

    def get_extentions(self) -> List[str]:
        for root, dirs, files in os.walk('cogs'):
            return [f"{root}.{dir}" for dir in dirs]

    def get_active_extentions(self) -> Mapping:
        return self.bot.extensions

    def load_extention(self, ext: str) -> str:
        """Loads an extension.

        An extension is a python module that contains commands, cogs, or
        listeners.

        An extension must have a global function, ``setup`` defined as
        the entry point on what to do when the extension is loaded. This entry
        point must have a single argument, the ``bot``.

        Parameters
        ----------
        name: :class:`str`
            The extension name to load. It must be dot separated like
            regular Python imports if accessing a sub-module. e.g.
            ``foo.test`` if you want to import ``foo/test.py``.

        Raises
        ------
        ExtensionNotFound
            The extension could not be imported.
            This is also raised if the name of the extension could not
            be resolved using the provided ``package`` parameter.
        ExtensionAlreadyLoaded
            The extension is already loaded.
        NoEntryPointError
            The extension does not have a setup function.
        ExtensionFailed
            The extension or its setup function had an execution error.
        InvalidSetupArguments
            ``load_extension`` was given ``extras`` but the ``setup``
            function did not take any additional arguments.
        """

        responce = f"Successfully loaded: '{ext}'"
        try:
            self.bot.load_extension(ext)
        except nc_errors.ExtensionNotFound:
            responce = f"Extention: '{ext}' not found."
        except nc_errors.ExtensionAlreadyLoaded:
            responce = f"Extention: '{ext}' already loaded."
        except nc_errors.NoEntryPointError:
            responce = f"Extention: '{ext}' does not have a setup function."
        except nc_errors.ExtensionFailed:
            responce = f"Extention: '{ext}' the extention or setup function had an execution error."
        finally:
            return responce

        self.bot.load_extension(ext)

    def load_extentions(self, exts: List[str]) -> List[str]:
        return [self.bot.load_extension for ext in exts]

    def unload_extention(self, ext: str) -> str:
        responce = "Successfully unloaded: '{ext}'"
        try:
            self.bot.unload_extension(ext)
        except nc_errors.ExtensionNotFound:
            responce = f"Extention: '{ext}' not found."
        except nc_errors.ExtensionNotLoaded:
            responce = f"Extention: '{ext}' is not currently loaded."
        finally:
            return responce

    def unload_extentions(self, exts: List[str]) -> List[str]:
        return [self.unload_extention(ext) for ext in exts]

    def reload_extention(self, ext: str):
        """Raises
        ------
        ExtensionNotLoaded
            The extension was not loaded.
        ExtensionNotFound
            The extension could not be imported.
            This is also raised if the name of the extension could not
            be resolved using the provided ``package`` parameter.
        NoEntryPointError
            The extension does not have a setup function.
        ExtensionFailed
            The extension setup function had an execution error.
        """

        responce = f"Successfully reloaded: '{ext}'"
        try:
            self.bot.reload_extension(ext)
        except nc_errors.ExtensionNotLoaded:
            responce = f"Extention: '{ext}' is not currently loaded."
        except nc_errors.ExtensionNotFound:
            responce = f"Extention: '{ext}' not found."
        except nc_errors.NoEntryPointError:
            responce = f"Extention: '{ext}' does not have a setup function."
        except nc_errors.ExtensionFailed:
            responce = f"Extention: '{ext}' the extention or setup function had an execution error."
        finally:
            return responce

    def load_all_cogs(self) -> List[str]:
        return self.bot.load_extensions(self.get_extentions())
