# MUCTR-BOT

A Telegram bot for students of the Mendeleev University of Chemical Technology of Russia
(MUCTR) — check your grades, share homework with your group, and find your way around
campus without leaving Telegram.

> The bot's interface is in Russian, since that is what its users speak. This README is in
> English.

## About

MUCTR runs a student portal called EIOS, which holds your grades, checkpoint scores and
exam results. Reading them means logging into a web portal — awkward on a phone, between
classes, which is exactly when you want to check them.

MUCTR-BOT moves that into Telegram. You register once with your EIOS credentials, and from
then on your grades are a couple of taps away. Around that core it grew the other things a
group of students kept needing: somewhere to put the homework, a way to tell everyone what
the canteen is serving, and floor plans for buildings that are genuinely easy to get lost
in.

This is my first programming project. I built it while learning Python — partly from
tutorials, and partly by watching what the university portal sent over the network and
working out how to ask it the same questions.

## Features

| Command | What it does |
| --- | --- |
| `/start` | Registration: consent screen, then your EIOS login and password |
| `/journal` | Your grades from EIOS — pick a course, a semester, then a subject |
| `/sethomework` · `/viewhomework` | Shared homework for your study group, with photos, documents and voice notes |
| `/menu` · `/setmenu` | The dorm canteen menu, kept up to date by whoever gets there first |
| `/schedule` | Today's timetable |
| `/map` | Floor plans for the Miusskaya and Tushino buildings |
| `/an` | Broadcast an announcement to everyone in your group |
| `/loggs` · `/DROPDATABASE` | Admin only — fetch the log files, or wipe the database |

## How it works

### Talking to the EIOS API

EIOS has no public API and no documentation for one. The endpoints below were worked out by
inspecting the requests the portal's own web interface makes:

1. `POST /accounts/authenticate/login/` with your username and password returns a token.
2. Every subsequent request carries `Authorization: Token <token>`.
3. `GET /education/students/student/` returns your enrolment — from it the bot takes your
   EIOS education ID and your study group.
4. `GET /education/students/education/{id}/journal/full/` returns the entire journal as
   JSON.
5. The bot walks that JSON — courses → semesters → subjects — and pulls out the semester
   rating, exam score, checkpoint values and control type for whichever subject you picked.

Requests go through a single `requests.Session()` with a randomised user agent.

### Storing credentials

Fetching your grades means holding your EIOS password, so the bot encrypts it. Each user
gets their own key from `cryptography.fernet`, generated at registration; the password is
encrypted before it reaches the database and decrypted only when a request to EIOS is
actually made.

Registration begins with an explicit consent step that links to the bot's privacy page.
Declining is a valid choice — `/map`, `/menu` and `/setmenu` keep working without an
account, since none of them touch EIOS.

### Conversation state

Most of what the bot does is a conversation rather than a single command: `/sethomework`
asks for a subject, then a caption, then the task itself. Each of these flows is a finite
state machine built on aiogram's FSM — `SignUpState`, `JournalState`, `HomeworkState`,
`MapState`, `СomboState` and `AnnounceState` in `states/states.py` — so the bot always
knows which answer it is waiting for, per user.

### Database access

A middleware (`middlewares/db.py`) opens an async SQLAlchemy session for every incoming
update and hands it to the handler, so no handler has to manage a connection itself. All
the actual queries live in one place, `database/orm_querry.py`, rather than being scattered
through the handlers.

Three tables (`database/models.py`): `UserInfo` for registered users, `homework` for tasks
posted per group, and `combo` for the canteen menu.

## Project structure

```
main.py              Entry point — creates the bot, registers routers and middleware
common/              Bot commands, the EIOS API client, the timetable
handlers/            One router per feature area
  Journal/           Grades: menus and journal parsing
  Homework/          Posting and reading homework
  UserSave/          Registration, encryption, group announcements
  admin.py           Admin-only commands
  menu.py            Canteen menu
  simple.py          Maps and timetable
  ExceptionHandler.py
database/            Engine, models, and all ORM queries
middlewares/         Database session injection
states/              FSM state groups
filters/             Admin check
kbds/                Inline keyboards
LOGGING/             Logger configuration
```

## Tech stack

- **Python 3.12**
- **aiogram 3.4.1** — Telegram bot framework, using routers and FSM
- **SQLAlchemy 2.0.27** (async) with **aiosqlite** — ORM over SQLite
- **cryptography 42.0.1** — Fernet encryption for stored passwords
- **requests** + **fake-useragent** — EIOS API client
- **python-dotenv** — configuration

## Running it locally

You need Python 3.12 and a bot token from [@BotFather](https://t.me/BotFather).

```bash
git clone https://github.com/sasha720709/MUCTR-BOT.git
cd MUCTR-BOT

python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file next to `main.py`:

```
TOKEN=your-token-from-botfather
```

Then start it:

```bash
python main.py
```

The SQLite database is created automatically on first run, at `database/dbase.db`.

Note that `/journal` and `/schedule` only do anything useful against real MUCTR
credentials — the rest of the bot works for anyone.

## License

[MIT](LICENSE)
