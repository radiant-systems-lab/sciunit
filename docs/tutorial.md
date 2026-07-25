# A Brief Introduction to Sciunit

**This page might have outdated information. The most updated Sciunit documentation can be found at:**
**https://github.com/radiant-systems-lab/sciunit/wiki**

From time to time, you may find that it is hard to verify or reproduce someone
else's research, even though it is only programs, data, and output.
Programs may be built in different ways, may behave differently if not running
in the author's environment, and can accept different arguments at runtime.
All these factors contribute to the difficulties of trying out, if not
reproducing, others work.
How about, starting from your next paper, you publish the article along with a
'sciunit' research object to encapsulate all the workflows you plan to
demonstrate, allowing your readers and reviewer to try out your work?

## Basic concepts

### Sciunit

'Sciunit' is both the name of the reusable research object we defined and also
the name of command-line tool that creates, manages, and shares *sciunits*.  A
sciunit consists of multiple *executions*.  Each execution refers to an
execution of a command under Linux.  The command may be a single binary, may
start with the name of a specific virtual machine for managed languages, such
as Java, or may be a shell script that contains multiple commands. An
execution may also be a series of terminal inputs that capture your
interaction with a UNIX shell. In all cases, the execution have its runtime
dependencies determined during an *auditing* phase, saved to a sciunit, and
can be *repeated* later on a different machine without pulling in any
dependencies of the execution.

Each execution is assigned an execution id, starting from `e1`.  In your
paper, you describe each workflow you want to discuss and reference it using
its corresponding execution id in a sciunit -- just like referencing a figure
using a numerical figure id.

### Workspace

The *sciunit*(1) command-line tool owns the directory `~/sciunit`.  A
workspace for a sciunit is a subdirectory under `~/sciunit`.  The command

> `sciunit create Project1`

creates and opens an empty sciunit called "Project1," where
`~/sciunit/Project1` is its workspace.  You can verify these with

```shell
> sciunit show
sciunit: show: sciunit 'Project1' is empty
```

You can switch among multiple workspaces with the `open` command:

> `sciunit open Project2`

You can also load a sciunit into a workspace and then open it.  The following
chapters describe more forms of the `open` command.

## Capturing and testing your program

Let's start with a "Hello World" program in a shell script.

```shell
> cat hello.sh
#!/bin/sh
echo 'hello, world'
```

We can run this program

```shell
> ./hello.sh
hello, world
```

Now let's try to capture this program with `sciunit`.  Assume that we just
created a new sciunit called "Project1."  Rerun the program with `sciunit
exec`:

```shell
> sciunit exec ./hello.sh
hello, world
```

Now this program, along with its all its dependencies, has been captured as
`e1` in "Project1."  The "show" command can display the details of the last
captured execution:

```shell
> sciunit show
     id: e1
sciunit: Project1
command: ./hello.sh
   size: 2.82 MB
started: 2017-10-10 08:42
```

As we claimed, this execution can be repeated on a different machine.  We will
do so in the remaining chapters, but before that, we should test it locally:

```shell
> sciunit repeat e1
hello, world
```

If you investigate the workspace

```shell
> ls ~/sciunit/Project1/
cde-package  e1.json  sciunit.db  vvpkg.bin  vvpkg.db
```

, you will find a directory named "cde-package" and a few other files.  The
"cde-package" is a temporary directory that consists of all necessary files
for this execution to repeat; for example, you can even find a "libc.so.6"
somewhere under this directory.  The rest of the files are the underlying
implementation of the conceptual "sciunit."

Now let's try a different way to capture an execution -- capture as you go:

```shell
> sciunit exec -i
Interactive capturing started; press Ctrl-D to end
>
```

Wait, that's it?  No, you are merely inside a subshell: all the commands you
run from now on will be captured.  For example:

```shell
> echo 'hello'
hello
> ./hello.sh
hello, world
```

Now press "Ctrl-D":

```shell
> exit
Interactive capturing ended
```

These commands all become execution `e2`, and you can repeat it as well.

So far, we created two executions within the sciunit.  You can list them with
the `list` command

```shell
> sciunit list
   e1 Oct 10 08:42 ./hello.sh
   e2 Oct 10 11:00
```

, or remove one of them with the `rm` command.  Note that after a removal all
the remaining executions retain their current execution ids, and new
executions will be assigned ids which are higher than the remaining ones.

## Continue your work on another machine

While developing your paper, you might want to capture more executions on
another machine, testing your sciunit in another environment, or maybe share
the sciunit with a coauthor.  Conceptually, you want to copy & paste,
remotely.  The easiest way is to use the `copy` command:

```shell
> sciunit copy
mSLLTj#
```

Give it a second, and it returns a code.  You can then "paste" the sciunit
over the Internet by running

> `sciunit open mSLLTj#`

on the target machine.  The heavy lifting utilizes the
[file.io](https://file.io) service.  The code is only valid for one day.  Once
pasted, the code is gone.

If you investigate the `~/sciunit` directory on the machine in which you
initiated the copy,

```shell
> ls ~/sciunit
Project1  Project1.zip
```

you will find a new zip file.  As you can imagine, it is a zipped version of
the sciunit "Project1."  The `open` command can also open a zipped sciunit.
So if you do not want to use [file.io](https://file.io), you can instead use
the `sciunit copy -n` command to generate this file, and deliver the file to
some other machine or to someone else.

## Prepare your paper for review

The zip file mentioned above is the research object you are going to publish
along with your paper.  You can manually select and upload such a file on
websites that host sharing of research objects, however, if you are using
[HydroShare](https://www.hydroshare.org/), maintaining and updating your draft
articles can be drastically simplified with the *sciunit*(1) tool.

Issue the following command to create a new article for the current sciunit:

> `sciunit push my_new_article --setup hs`

"my\_new\_article" is a codename for your article.  Codenames are useful for
maintaining multiple articles you created from the same sciunit, and you
should pick a codename that describes an article's use, such as "debug."  "hs"
is short for "hydroshare" to indicate the service you are talking to.

The above command prompts you for

    Please go to the following link and authorize access:

    https://www.hydroshare.org/o/authorize/?response_type=code&client_id=vG5R4zZFO6uJZBj3m0DWtUK6Va44jTQ4KoqtaLpn&redirect_uri=https:%2F%2Fsciunit.run%2Fcb&state=RCeAb6zxbEuw6yHQPDpWu26iHQIcan

    Paste the authorization code:

Here we are running OAuth2 flow for HydroShare.  After you have authorized
the *sciunit* tool in a web browser and pasted in the auth code,

    Paste the authorization code: AoxTbXnjzTfIa3OP5d5unxImPn0Noc
    Logged in as "Yuan, Zhihao <lichray@gmail.com>"
    Title for the new article: New Article for Project1
    new: 8.93MB [00:01, 4.72MB/s]

input the title for the article and wait for the upload to finish.  Now you
can go to <https://www.hydroshare.org/my-resources/> to view your new article
on HydroShare.  A newly-created article lacks information for publication and
is private.

After each successful "push," the codename involved is recorded for the next

> `sciunit push`

command to pick up.  So after you make a few changes to the current sciunit,
such as capturing a new execution, the above command can silently keep your
article on HydroShare up-to-date.  However, if you run

```shell
> sciunit push my_new_article --setup hs
Logged in as "Yuan, Zhihao <lichray@gmail.com>"
Create a new version of the article "New Article for Project1"? [y/N]
```

again, you are creating another new article rather than updating the existing
one.  If you answer '`y`', the article will be a new "version" (HydroShare
feature) of the existing one; if you answer '`n`', the new article can have a
different title.  In case you accidentally run into this query and cannot
answer it, just press "Ctrl-D" to cancel the operation.

## Testing your Sciunit on HydroShare JupyterHub

If your resource is **public** on HydroShare, right-clicking the zip file in
the "Content" browser, you can obtain a link to that zipped sciunit via the
"Get file URL" option, then you may use `sciunit open` to download and open
the sciunit locally.  However, before you finish the paper, it is very likely
that you want to keep your article private and to give it more tests.
HydroShare JupyterHub is the platform you immediately have access to right
after having your Sciunit uploaded to HydroShare, for exactly that purpose.

In the top-right corner on your article page, open the article with "JupyterHub."

![](https://i.imgur.com/acds9oq.png)

You will be redirected to the Welcome notebook of HydroShare JupyterHub.  By
clicking the " Run" button a few times, you will be prompted to enter your
HydroShare password.  After seeing the message "Successfully established a
connection with HydroShare," click the " Run" button a few more times until
seeing a "Path to resource content: " message.  Copy the path to clipboard.

![](https://i.imgur.com/XMPhfPY.png)

Now go to the "Control Panel" via the button in the top-right corner of the
page,

![](https://i.imgur.com/8KBxpat.png)

access the "Terminal" by creating one in the control panel.

![](https://i.imgur.com/IsOw3qC.png)

What stands behind the terminal is an isolated, full-fledged Linux
environment, which should not surprise you if you are familiar with
[JupyterHub](http://jupyter.org/).  Change the working directory to the
resource path you copied before,

![](https://i.imgur.com/1HunWAv.png)

and now you can open the zipped sciunit you just uploaded regardless whether
the article is private.  Of course, HydroShare JupyterHub is also an ideal
place for everyone to read the sciunit manpage with

    man sciunit

and exercise more sciunit commands.
