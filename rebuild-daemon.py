"""
Start this to automatically build the app using Brunch (not using Brunch's watching, but using own file change
recognition of any file in the "src" folder) and (optionally) to copy it to the Android project. This only triggers
for changed files (modification date), not for deletions.

Pass the "--target=android" parameter to copy the result to the Android project (to "assets/www" folder). Existing files
in that directory are deleted.

For iOS, the "--target=ios" parameter copies the result to the "www" folder in the iOS project.

@author:
    Andreas Sommer
@license:
    New BSD license (http://www.opensource.org/licenses/BSD-3-Clause)

    Downloadable under http://bazaar.launchpad.net/~andidog/dogsync/trunk/view/head:/LICENSE.txt
@note:
    Base of the rebuild daemon taken from DogSync and modified
"""

from __future__ import print_function

from datetime import datetime
from distutils import dir_util
from itertools import chain
from optparse import OptionParser
import os
import shutil
import sys
import time
import traceback
from subprocess import Popen
try:
    import gntp.notifier
except ImportError:
    gntp = None

cwd = os.path.abspath(os.path.dirname(__file__))
assert(all(os.path.exists(os.path.join(cwd, dirName)) for dirName in ("src", "android", "ios", "extra_assets", "i18n")))

parser = OptionParser()
parser.add_option("--target", default=None, help="Target platform", metavar="android|ios|web")
parser.add_option("--debug", default=False, action="store_true", help="Debug mode (no minification)", metavar="true|false")
(options, args) = parser.parse_args()
assert(not args)

target = options.target
debug = options.debug

if target not in ("android", "ios", "web"):
    raise AssertionError("Invalid target specified")


def copy_build_output(friendlyPlatformName, platformName, outputPathList):
    if outputPathList is not None:
        # Assume that the parent directory of "www" exists
        os.path.join(cwd, *(outputPathList[:-1]))

        print("%s: Copying to %s project..." % (format_date(time.time()), friendlyPlatformName))
        output_directory = os.path.join(cwd, *outputPathList)

        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)

        shutil.copytree(os.path.join(cwd, "src", "public"), output_directory)
    else:
        output_directory = os.path.join(cwd, "src", "public")

    extra_assets_directory = os.path.join(cwd, "extra_assets", platformName)

    if os.path.exists(extra_assets_directory):
        dir_util.copy_tree(extra_assets_directory,
                           output_directory,
                           update=False)

    # i18n directory copied as "i18n" folder to work with i18next directory structure defined in application.coffee
    # (see also http://jamuhl.github.com/i18next/)
    if not os.path.isdir(os.path.join(output_directory, "i18n")):
        os.mkdir(os.path.join(output_directory, "i18n"))
    dir_util.copy_tree(os.path.join(cwd, "i18n"),
                       os.path.join(output_directory, "i18n"),
                       update=True)


def copy_build_output_to_android_project():
    copy_build_output("Android", "android", ("android", "assets", "www"))


def copy_build_output_to_ios_project():
    copy_build_output("iOS", "ios", ("ios", "www"))


def copy_build_output_to_web_project():
    copy_build_output("Web (browser testing)", "web", None)


def create_target_specific_config_files():
    with open(os.path.join(cwd, "src", "config.coffee.template"), "rU") as f:
        template = f.read().decode("utf-8")

    for target in ("android", "ios", "web"):
        if "<MAGIC>\n" not in template:
            raise AssertionError

        target_variables = ("TARGET = '%s'\n"
                            "DEBUG = %s\n"
                            % (target, "true" if debug else "false"))

        content = ("# WARNING: AUTOGENERATED FILE. DO NOT CHANGE\n\n" +
                   target_variables +
                   template[template.index("<MAGIC>\n") + 8:])

        with open(get_target_specific_config_filename(target), "wb") as outFile:
            outFile.write(content.encode("utf-8"))


def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S")


def get_target_specific_config_filename(target):
    return os.path.join(cwd, "src", "config-%s.autogen.coffee" % target)


def notify_error():
    if gntp is None:
        return

    growl.notify(
        noteType='error',
        title='BUILD FAILED!',
        description='',
        icon='http://i.imgur.com/yYlIE.png',
        sticky=False,
        priority=1
    )


def notify_register():
    if gntp is None:
        return

    global growl
    growl = gntp.notifier.GrowlNotifier(
        applicationName='Rebuild daemon',
        notifications=('success', 'error'),
        defaultNotifications=('success', 'error')
    )
    growl.register()


def notify_success():
    if gntp is None:
        return

    growl.notify(
        noteType='success',
        title='Build succeeded',
        description='',
        icon='http://i.imgur.com/TBvmb.png',
        sticky=False,
        priority=-1,
    )


def rebuild():
    try:
        print("%s: Rebuilding..." % format_date(time.time()))
        command_line = ["brunch.cmd" if os.name == "nt" else "brunch",
                        "b",
                        "--config",
                        get_target_specific_config_filename(target)]
        if not debug:
            command_line.append("-m")

        try:
            proc = Popen(command_line,
                         cwd=os.path.join(cwd, "src"))
        except OSError as e:
            if e.errno == 2:
                raise Exception("Brunch not installed? (npm install -g brunch)")
            raise

        proc.communicate()

        if proc.returncode != 0:
            raise Exception("Brunch failed with return value %d, see errors above" % proc.returncode)

        if os.path.getsize(os.path.join(cwd, "src", "public", "javascripts", "vendor.js")) < 200000:
            print("Error: That weird bug happened again! (TODO: check why Brunch is creating an incomplete vendor.js file)",
                  file=sys.stderr)
            sys.exit(2)

        if target == "android":
            copy_build_output_to_android_project()
        elif target == "ios":
            copy_build_output_to_ios_project()
        elif target == "web":
            copy_build_output_to_web_project()
        else:
            raise AssertionError()
    except Exception as e:
        notify_error()
        print("%s: Failed to rebuild: %s" % (format_date(time.time()), e))
        return False
    except:
        print("%s: Quitting, rebuild might be inconsistent" % format_date(time.time()))
        raise
    else:
        notify_success()
        print("%s: Finished rebuilding" % format_date(time.time()))
        return True


try:
    notify_register()

    last_filenames_reload = -999999
    last_force_rebuild_attempt = -999999
    last_max_modification_time = -999999
    filenames = None

    def filename_filter(filename):
        return (not filename.startswith(os.path.join("src", "public", "")) and
                not filename.startswith(os.path.join("src", "node_modules", "")))

    firstTime = True
    force_rebuild = False

    create_target_specific_config_files()

    while True:
        if time.time() - last_filenames_reload > 20:
            filenames = []
            for root, unused_dirnames, foundFilenames in chain(os.walk("src"), os.walk("extra_assets"), os.walk("i18n")):
                for filename in foundFilenames:
                    filename = os.path.join(root, filename)
                    if os.path.isfile(filename) and filename_filter(filename):
                        filenames.append(filename)

            last_filenames_reload = time.time()

        must_rebuild = False

        for filename in filenames:
            try:
                modification_time = os.stat(filename).st_mtime
            except os.error:
                print("Warning: Ignoring exception in os.stat: %s" % traceback.format_exc(), file=sys.stderr)

            if modification_time > last_max_modification_time:
                if not firstTime:
                    print("%s: Changed %s" % (format_date(time.time()), filename[len("src") + 1:]))

                last_max_modification_time = modification_time

                must_rebuild = True

        if must_rebuild or (force_rebuild and time.time() - last_force_rebuild_attempt > 10):
            if force_rebuild:
                last_force_rebuild_attempt = time.time()

            if rebuild():
                force_rebuild = False
            else:
                force_rebuild = True

        time.sleep(1)
except KeyboardInterrupt:
    print("\nQuit by user.")
