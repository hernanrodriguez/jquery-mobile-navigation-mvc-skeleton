# Brunch skeleton aimed at mobile apps, using CoffeeScript, jQuery Mobile, Backbone, Handlebars, Stylus, MVC pattern
This is a skeleton for [Brunch](http://brunch.io/) based on the work of Paul Millr
([simple-coffee-skeleton](https://github.com/brunch/simple-coffee-skeleton)) and my previously released skeleton
([jquery-mobile-bootstrap-mvc-skeleton](https://github.com/AndiDog/jquery-mobile-bootstrap-mvc-skeleton)).

[CoffeeScript](http://coffeescript.org/) is the main language, while [Stylus](http://learnboost.github.com/stylus/) and
[Handlebars](http://handlebarsjs.com/) were chosen for design and views (can be replaced easily).

## Getting started

Clone this repo or download the ZIP file (you won't need the history). Installing Brunch globally is recommended
(`npm install -g brunch`). Then run `npm install` in the skeleton directory, followed by `brunch build` (or
`brunch w -s` for automatic rebuilding on changes and Brunch's integrated web server). See more info on the [official
site of Brunch](http://brunch.io).

## License
[Public domain](http://creativecommons.org/publicdomain/zero/1.0/) – use it however you want. Exceptions are files that
explicitly state (or are obviously under) another license.

iOS tab icons taken from the wonderful [iconza](http://www.iconza.com/) icon set.

## Overview

TODO: update this

    config.coffee
    README.md
    /app/
      /assets/
        index.html
        images/
      /lib/
      models/
      styles/
      views/
        templates/
      application.coffee
      initialize.coffee
    /vendor/
      scripts/
        backbone.js
        jquery.js
        console-helper.js
        underscore.js
      styles/
        normalize.css
        helpers.css

* `config.coffee` contains configuration of your app. You can set plugins /
languages that would be used here.
* `app/assets` contains images / static files. Contents of the directory would
be copied to `build/` without change.
Other `app/` directories could contain files that would be compiled. Languages,
that compile to JS (coffeescript, roy etc.) or js files and located in app are
automatically wrapped in module closure so they can be loaded by
`require('module/location')`.
* `app/models` & `app/views` contain base classes your app should inherit from.
* `app/controllers` contains example controllers using Backbone's hashbang routing
* `test/` contains feature & unit tests.
* `vendor/` contains all third-party code. The code wouldn’t be wrapped in
modules, it would be loaded instantly instead.

This all will generate `public/` (by default) directory when `brunch build` or `brunch watch` is executed.

## Other
Versions of software the skeleton uses:

* jQuery 1.8.2
* Backbone 0.9.2 (only event system, rest stripped out)
* Underscore 1.3.3
* jQuery Mobile 1.2.0 (with default theme)
* i18next 1.5.7 (for translations)

## Building

### Web application
Run `rebuild-daemon.py --target=web --debug` and the app will be built in the folder `src\public`. The scripts
`Start development server.*` serve this folder if the right tools are installed (take a look inside the scripts, Python
and Twisted on Windows, for example). Of course you can serve it using your own web server instead.

### Android app
Import the project in `android` and all projects in `dependencies/android` into your Eclipse workspace. Open the
properties of the "Mobile Skeleton" project and check whether the builder "Force rebuild Mobile Skeleton" is configured
correctly.

Run `rebuild-daemon.py --target=android --debug` and the app will be rebuilt on any changes. Then simply start the app
from Eclipse.

### iOS app
Update the CordovaLib project reference using `update_cordova_subproject path/to/MobileSkeleton.xcodeproj`.

Remaining instructions: TODO ;)

## Unit testing
Install jsdom by executing `npm install jsdom` in the `src` directory. That will try to install contextify as well which
requires a binary module. For Windows, you can find binaries [here](https://github.com/AndiDog/contextify-binaries) or
you can try to compile them yourself (npm will try it for you). If you want to use the binaries, first run `npm install
contextify` to install its dependencies (e.g. "bindings" library) and then copy over the binaries to the `node_modules`
folder.

If you get an error like `TypeError: Cannot call method 'querySelectorAll' of undefined`, contextify is missing from
your `node_modules` folder.

All test specs must have a filename like `src/test/view_test.coffee`, note that `view.coffee` won't work.