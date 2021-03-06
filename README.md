# couleur - ANSI terminal tool for python, colored shell and other handy fancy features
__Version 0.5.0__

__Couleur__ is a handy tool to play around with ANSI features in a
unix terminal

## installing

    user@machine:~$ sudo pip install git+git://github.com/gabrielfalcao/couleur.git

## features

+ Single python file
+ 100% tested
+ comes with syntax sugar

## nutshell

### file-like objects filter

![stdout filter](http://gnu.gabrielfalcao.com/couleur_filter.png)

#### further

```python
import sys, couleur

couleur.proxy(sys.stdout).enable()
print("#{bold}#{blue}#{on:black}This is#{normal} a test")
couleur.proxy(sys.stdout).ignore()

print("#{green}#{on:black}This is#{normal} a test")
couleur.proxy(sys.stdout).disable()
```

### dynamic methods

couleur has a syntax sugar that is semantically nice:

```python
import couleur
sh = couleur.Shell(indent=4)

sh.bold_black_on_white('Nice highlight')
# prints '\033[47m\033[1m\033[30mNice highlight\033[0m'

sh.indent()
# will increase a internal indentation factor in couleur.Shell instance

sh.green('Just green')
# prints indented as well '    \033[32mJust Green\033[0m'

sh.dedent()
# will decrease that indentation factor (above)

# syntax sugar
sh.green_and_normal_and_blue('this will be printed in green| and |this in blue')
# see: '\033[32mthis will be printed in green\033[0m and \033[34mthis in blue\033[0m'
```

couleur can overwrite output, so that you can make things like printing progress bars, show percentage and so on:

```python
import time
import couleur

shell = couleur.Shell(linebreak=True, bold=True)

for num in range(101):
    if num == 0:
        print

    shell.yellow_and_red("Downloading file: |%d%%" % num, replace=True)
    time.sleep(0.01)

shell.white_and_green("Downloading file: |DONE!", replace=True)
```

#### Writing to other streams

Simply pass the output as first argument of the `Shell`
```python
import couleur

with open('output.log', 'w') as output:
    shell = couleur.Shell(output, linebreak=True, bold=True)
    shell.white_and_green("done with | Some task")
```


### furthermore

With couleur you can mix modifiers and colors.

Available modifiers:

+ reset - resets from the current point to the end
+ bold - make text bold
+ blink - it may blink the text or make it slighly lighten, depending on the terminal
+ italic - make text italic
+ underline - add underline on text
+ inverse - invert colors
+ strikethrough - draws a line through the text
+ up - does the same than passing replace=True to the output function: carriage return and one line up

Available colors:

+ normal
+ black
+ red
+ green
+ yellow
+ blue
+ magenta
+ cyan
+ white

Example chaining modifiers:

```python
import couleur

shell = couleur.Shell(linebreak=True)
shell.bold_italic_underline_green_on_black_and_italic_black_on_white("WOO| HOO")
```

## free software

To contribute back with this project, all you need to do is write code, and test code that proofs its functionallity

### cloning and running tests

You will need to install [nose](http://somethingaboutorange.com/mrl/projects/nose/0.11.3/ "a pretty way for testing in python").

And run:

```shell
user@machine:~/Projects$ git clone git://github.com/gabrielfalcao/couleur.git
user@machine:~/Projects$ cd couleur
user@machine:~/Projects$ pip install -r requirements.pip
user@machine:~/Projects/couleur$ make
```

## nomenclature

  "couleur" stands for "color" in French, I like french, hence the name

## Licensing

    Copyright (c) 2010-2013 Gabriel Falcão
    Licensed under Apache License 2.0
    http://www.apache.org/licenses/LICENSE-2.0.html


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/gabrielfalcao/couleur/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

